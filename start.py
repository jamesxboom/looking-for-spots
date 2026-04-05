#!/usr/bin/env python3
"""
Looking For Spots — Server with Live Data

Serves the fly fishing conditions dashboard and provides a /api/flows
endpoint that aggregates data from USGS + DreamFlows on a background
schedule. The frontend fetches from /api/flows instead of hitting
external APIs directly.

Usage:
    python3 start.py

On Render, the PORT env var is set automatically.
"""

import http.server
import json
import os
import re
import sys
import threading
import time
import traceback
import webbrowser
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from urllib.error import URLError

PORT = int(os.environ.get("PORT", 5555))
DIR = Path(__file__).parent

# ── Shared data store (written by background thread, read by HTTP handler) ──
_flow_data = {}          # { usgs_site_id: { cfs, tempF, source, updatedAt } }
_dreamflows_data = {}    # { df_site_id: { name, place, cfs, flow_class } }
_trend_data = {}         # { usgs_site_id: { trend: "rising"|"falling"|"stable", change_cfs, change_pct, hours } }
_weather_data = {}       # { spot_id: { temp_f, wind_mph, wind_dir, short_forecast, precip_pct } }
_last_usgs_fetch = None
_last_df_fetch = None
_last_weather_fetch = None
_data_lock = threading.Lock()


# ══════════════════════════════════════════════════════════════
# USGS Fetch — primary, most reliable data source
# ══════════════════════════════════════════════════════════════

def fetch_usgs(site_ids):
    """Fetch real-time discharge + temperature from USGS IV service (last 6 hours)."""
    if not site_ids:
        return {}

    site_param = ",".join(site_ids)
    url = (
        f"https://waterservices.usgs.gov/nwis/iv/?format=json"
        f"&sites={site_param}&parameterCd=00060,00010&siteStatus=active"
        f"&period=PT6H"
    )
    req = Request(url, headers={"User-Agent": "LookingForSpots/1.0"})
    resp = urlopen(req, timeout=30)
    raw = json.loads(resp.read().decode("utf-8"))

    result = {}
    for ts in raw.get("value", {}).get("timeSeries", []):
        site_code = ts["sourceInfo"]["siteCode"][0]["value"]
        param_code = ts["variable"]["variableCode"][0]["value"]
        values = ts.get("values", [{}])[0].get("value", [])
        if not values:
            continue

        latest = values[-1]
        val = float(latest["value"])
        if val < 0:
            continue

        if site_code not in result:
            result[site_code] = {"source": "usgs", "updatedAt": latest.get("dateTime")}

        if param_code == "00060":
            result[site_code]["cfs"] = val
            # Store full time-series values for discharge (for trend analysis)
            result[site_code]["values"] = [
                (v.get("dateTime"), float(v["value"]))
                for v in values
                if float(v["value"]) >= 0
            ]
        elif param_code == "00010":
            result[site_code]["tempF"] = round(val * 9 / 5 + 32, 1)

    return result


# ══════════════════════════════════════════════════════════════
# Trend Analysis
# ══════════════════════════════════════════════════════════════

def calculate_trends(usgs_data_raw):
    """
    Analyze discharge trends for each USGS site.

    Args:
        usgs_data_raw: Dict from fetch_usgs() with "values" key containing [(dateTime, cfs), ...]

    Returns:
        { site_id: { trend: "rising"|"falling"|"stable", change_cfs: float, change_pct: float, hours: float } }
    """
    trends = {}

    for site_id, site_data in usgs_data_raw.items():
        values = site_data.get("values", [])

        # Need at least 2 data points to calculate trend
        if not values or len(values) < 2:
            continue

        # Get oldest and newest readings
        oldest_time, oldest_cfs = values[0]
        newest_time, newest_cfs = values[-1]

        # Calculate change
        change_cfs = newest_cfs - oldest_cfs

        # Calculate percentage change (avoid division by zero)
        if oldest_cfs > 0:
            change_pct = (change_cfs / oldest_cfs) * 100
        else:
            change_pct = 0.0

        # Determine trend direction
        if change_pct > 5:
            trend = "rising"
        elif change_pct < -5:
            trend = "falling"
        else:
            trend = "stable"

        # Calculate time span in hours
        # Parse ISO 8601 datetime strings
        try:
            from datetime import datetime
            oldest_dt = datetime.fromisoformat(oldest_time.replace("Z", "+00:00"))
            newest_dt = datetime.fromisoformat(newest_time.replace("Z", "+00:00"))
            hours = (newest_dt - oldest_dt).total_seconds() / 3600.0
        except (ValueError, AttributeError):
            hours = 0.0

        trends[site_id] = {
            "trend": trend,
            "change_cfs": round(change_cfs, 2),
            "change_pct": round(change_pct, 2),
            "hours": round(hours, 2),
        }

    return trends


# ══════════════════════════════════════════════════════════════
# DreamFlows Scrape — supplemental data
# ══════════════════════════════════════════════════════════════

def scrape_dreamflows():
    """
    Scrape the DreamFlows realtime report for California + Nevada.
    Returns { df_site_id: { name, place, cfs (float|None), flow_class, section } }
    """
    url = "https://dreamflows.com/flows.php?zone=canv&page=real&form=norm&mark=All"
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    resp = urlopen(req, timeout=20)
    html = resp.read().decode("utf-8", errors="replace")

    if "internal error" in html.lower() and len(html) < 1000:
        raise RuntimeError("DreamFlows returned internal error page")

    # Parse section headers
    section_positions = []
    for m in re.finditer(r"class='SecHeader'\s*name='([^']+)'>([^<]+)</a>", html):
        section_positions.append((m.start(), m.group(2)))
    section_positions.append((len(html), "END"))

    def section_for_pos(pos):
        for i, (start, name) in enumerate(section_positions):
            if i + 1 < len(section_positions) and pos < section_positions[i + 1][0]:
                return name
        return "Unknown"

    # Parse site entries
    pattern = re.compile(
        r"name='Site(\d+)'[^>]*class='River'[^>]*>([^<]+)</a>"
        r".*?class='Place'[^>]*>([^<]+)</a>"
        r".*?class='Flow(\w+)'>([^<]*)</td>",
        re.DOTALL,
    )

    result = {}
    for m in pattern.finditer(html):
        site_id, river, place, flow_class, flow_str = m.groups()
        # Parse CFS — handle "1,234", "Low", empty, etc.
        flow_str = flow_str.strip().replace(",", "")
        try:
            cfs = float(flow_str)
        except (ValueError, TypeError):
            cfs = None

        result[site_id] = {
            "name": river.strip(),
            "place": place.strip(),
            "cfs": cfs,
            "flow_class": flow_class,
            "section": section_for_pos(m.start()),
        }

    return result


# ══════════════════════════════════════════════════════════════
# Weather Fetch — NWS API integration
# ══════════════════════════════════════════════════════════════

def _load_spots_with_coords():
    """
    Parse spot IDs and coordinates from HTML config.
    Returns list of (spot_id, lat, lng) tuples.
    """
    html_path = DIR / "norcal-flows.html"
    if not html_path.exists():
        return []

    text = html_path.read_text(encoding="utf-8", errors="replace")
    spots = []

    # Find all river key patterns and their corresponding lat/lng
    # Look for pattern: key: { ... lat: XX.XXXX, lng: -YYY.YYYY ... }
    pattern = re.compile(
        r'(\w+):\s*\{[^}]*lat:\s*([\d.-]+),\s*lng:\s*([\d.-]+)',
        re.DOTALL
    )

    for match in pattern.finditer(text):
        spot_id = match.group(1)
        try:
            lat = float(match.group(2))
            lng = float(match.group(3))
            spots.append((spot_id, lat, lng))
        except (ValueError, IndexError):
            continue

    return spots


def fetch_weather_for_spots(spots):
    """
    Fetch weather data for a list of (spot_id, lat, lng) tuples.
    Calls NWS API with rate limiting (0.5s delay between calls).
    Returns { spot_id: { temp_f, wind_mph, wind_dir, short_forecast, precip_pct } }

    Extracts:
    - temperature (from properties.periods[0].temperature)
    - windSpeed (from properties.periods[0].windSpeed)
    - windDirection (from properties.periods[0].windDirection)
    - shortForecast (from properties.periods[0].shortForecast)
    - precipitationChance (from properties.periods[0].precipitationChance.value)
    """
    if not spots:
        return {}

    result = {}
    nws_user_agent = "LookingForSpots/1.0 (jamesboommacstudio@gmail.com)"

    for spot_id, lat, lng in spots:
        try:
            # Step 1: Get forecast URL from points endpoint
            points_url = f"https://api.weather.gov/points/{lat},{lng}"
            req = Request(points_url, headers={"User-Agent": nws_user_agent})
            resp = urlopen(req, timeout=10)
            points_data = json.loads(resp.read().decode("utf-8"))

            forecast_url = points_data.get("properties", {}).get("forecast")
            if not forecast_url:
                print(f"  [weather] No forecast URL for {spot_id}")
                time.sleep(0.5)
                continue

            # Step 2: Get forecast from forecast endpoint
            req = Request(forecast_url, headers={"User-Agent": nws_user_agent})
            resp = urlopen(req, timeout=10)
            forecast_data = json.loads(resp.read().decode("utf-8"))

            periods = forecast_data.get("properties", {}).get("periods", [])
            if not periods:
                print(f"  [weather] No forecast periods for {spot_id}")
                time.sleep(0.5)
                continue

            period = periods[0]

            # Extract wind speed and direction
            wind_speed_str = period.get("windSpeed", "0 mph")
            wind_mph = 0
            try:
                # Parse "15 mph" -> 15
                wind_mph = int(wind_speed_str.split()[0])
            except (ValueError, IndexError):
                wind_mph = 0

            wind_dir = period.get("windDirection", "")

            # Extract precipitation chance
            precip_obj = period.get("precipitationChance", {})
            if isinstance(precip_obj, dict):
                precip_pct = precip_obj.get("value", 0)
            else:
                precip_pct = 0

            result[spot_id] = {
                "temp_f": period.get("temperature", None),
                "wind_mph": wind_mph,
                "wind_dir": wind_dir,
                "short_forecast": period.get("shortForecast", ""),
                "precip_pct": precip_pct,
            }

            print(f"  [weather] {spot_id}: {period.get('temperature')}F, {wind_mph} mph {wind_dir}")

            # Rate limit: 0.5s delay between NWS API calls
            time.sleep(0.5)

        except URLError as e:
            print(f"  [weather] Error fetching {spot_id}: {e}")
            time.sleep(0.5)
        except Exception as e:
            print(f"  [weather] Unexpected error for {spot_id}: {e}")
            time.sleep(0.5)

    return result


# ══════════════════════════════════════════════════════════════
# Background refresh loop
# ══════════════════════════════════════════════════════════════

def _load_site_ids():
    """Read USGS site IDs from the HTML config (RIVERS object)."""
    html_path = DIR / "norcal-flows.html"
    if not html_path.exists():
        return []
    text = html_path.read_text(encoding="utf-8", errors="replace")
    return list(set(re.findall(r'usgs:\s*"(\d+)"', text)))


def background_refresh():
    """Runs in a daemon thread. Fetches data every 15 minutes."""
    global _flow_data, _dreamflows_data, _trend_data, _weather_data
    global _last_usgs_fetch, _last_df_fetch, _last_weather_fetch

    site_ids = _load_site_ids()
    print(f"  [data] Found {len(site_ids)} USGS site IDs in config")

    spots = _load_spots_with_coords()
    print(f"  [data] Found {len(spots)} spots with coordinates for weather")

    last_weather_time = 0  # Force fetch on first run

    while True:
        # ── USGS ──
        try:
            usgs = fetch_usgs(site_ids)
            # Calculate trends from the full time-series data
            trends = calculate_trends(usgs)
            with _data_lock:
                _flow_data = usgs
                _trend_data = trends
                _last_usgs_fetch = datetime.now(timezone.utc).isoformat()
            print(f"  [data] USGS: {len(usgs)} sites fetched, {len(trends)} trends calculated")
        except Exception as e:
            print(f"  [data] USGS error: {e}")
            traceback.print_exc()

        # ── DreamFlows ──
        try:
            df = scrape_dreamflows()
            with _data_lock:
                _dreamflows_data = df
                _last_df_fetch = datetime.now(timezone.utc).isoformat()
            print(f"  [data] DreamFlows: {len(df)} sites scraped")
        except Exception as e:
            print(f"  [data] DreamFlows error: {e}")

        # ── Weather (every 60 minutes, not every 15 min) ──
        now = time.time()
        if now - last_weather_time >= 60 * 60:  # 3600 seconds = 60 minutes
            try:
                weather = fetch_weather_for_spots(spots)
                with _data_lock:
                    _weather_data = weather
                    _last_weather_fetch = datetime.now(timezone.utc).isoformat()
                print(f"  [data] Weather: {len(weather)} locations fetched")
                last_weather_time = now
            except Exception as e:
                print(f"  [data] Weather error: {e}")
                traceback.print_exc()

        # Sleep 15 minutes
        time.sleep(15 * 60)


# ══════════════════════════════════════════════════════════════
# HTTP Handler
# ══════════════════════════════════════════════════════════════

class Handler(http.server.SimpleHTTPRequestHandler):
    """Serves static files + /api/flows JSON endpoint."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIR), **kwargs)

    def do_GET(self):
        parsed = urlparse(self.path)

        # ── Root → dashboard ──
        if parsed.path in ("/", ""):
            self.path = "/norcal-flows.html"
            return super().do_GET()

        # ── /api/flows → JSON data ──
        if parsed.path == "/api/flows":
            return self._serve_flows()

        # ── /api/weather → weather data ──
        if parsed.path == "/api/weather":
            return self._serve_weather()

        # ── /api/dreamflows → raw DreamFlows data ──
        if parsed.path == "/api/dreamflows":
            return self._serve_dreamflows()

        # ── /api/status → health check ──
        if parsed.path == "/api/status":
            return self._serve_status()

        # ── static files ──
        return super().do_GET()

    def _serve_flows(self):
        with _data_lock:
            # Build DreamFlows lookup keyed by DF site ID
            df_by_site = {}
            for df_id, df_entry in _dreamflows_data.items():
                if df_entry.get("cfs") is not None:
                    df_by_site[df_id] = {
                        "cfs": df_entry["cfs"],
                        "source": "dreamflows",
                        "updatedAt": _last_df_fetch,
                    }
            payload = {
                "usgs": {k: v for k, v in _flow_data.items()},
                "dreamflows": df_by_site,
                "trends": {k: v for k, v in _trend_data.items()},
                "weather": _weather_data,
                "lastUsgsFetch": _last_usgs_fetch,
                "lastDreamflowsFetch": _last_df_fetch,
                "lastWeatherFetch": _last_weather_fetch,
            }
        self._json_response(payload)

    def _serve_weather(self):
        with _data_lock:
            payload = {
                "weather": _weather_data,
                "lastFetch": _last_weather_fetch,
            }
        self._json_response(payload)

    def _serve_dreamflows(self):
        with _data_lock:
            payload = {
                "sites": _dreamflows_data,
                "lastFetch": _last_df_fetch,
            }
        self._json_response(payload)

    def _serve_status(self):
        with _data_lock:
            payload = {
                "status": "ok",
                "usgs_sites": len(_flow_data),
                "dreamflows_sites": len(_dreamflows_data),
                "weather_locations": len(_weather_data),
                "last_usgs_fetch": _last_usgs_fetch,
                "last_df_fetch": _last_df_fetch,
                "last_weather_fetch": _last_weather_fetch,
            }
        self._json_response(payload)

    def _json_response(self, data, status=200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        path = str(args[0]) if args else ""
        if path.endswith(".html") or path.startswith("GET /api") or "GET / " in path:
            print(f"  -> {path}")


# ══════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════

def main():
    print()
    print("  ╔═══════════════════════════════════════╗")
    print("  ║     🎣  Looking For Spots  🎣        ║")
    print("  ║    Fly Fishing Conditions Dashboard   ║")
    print("  ╚═══════════════════════════════════════╝")
    print()

    html_path = DIR / "norcal-flows.html"
    if not html_path.exists():
        print(f"  ERROR: norcal-flows.html not found in {DIR}")
        sys.exit(1)

    # Start background data fetcher
    t = threading.Thread(target=background_refresh, daemon=True)
    t.start()
    print(f"  [data] Background fetcher started (every 15 min, weather every 60 min)")

    server = http.server.HTTPServer(("0.0.0.0", PORT), Handler)

    print(f"  Server: http://localhost:{PORT}")
    print(f"  API:    http://localhost:{PORT}/api/flows")
    print(f"  Weather: http://localhost:{PORT}/api/weather")
    print(f"  Press Ctrl+C to stop\n")

    # Auto-open browser on local runs only
    if not os.environ.get("PORT"):
        def open_browser():
            time.sleep(1.0)
            webbrowser.open(f"http://localhost:{PORT}")
        threading.Thread(target=open_browser, daemon=True).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Tight lines! 🐟")
        server.shutdown()


if __name__ == "__main__":
    main()
