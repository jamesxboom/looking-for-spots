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
from xml.etree import ElementTree as ET
from html.parser import HTMLParser

PORT = int(os.environ.get("PORT", 5555))
DIR = Path(__file__).parent
_subscribers_file = DIR / "subscribers.json"

# ── Shared data store (written by background thread, read by HTTP handler) ──
_flow_data = {}          # { usgs_site_id: { cfs, tempF, source, updatedAt } }
_dreamflows_data = {}    # { df_site_id: { name, place, cfs, flow_class } }
_trend_data = {}         # { usgs_site_id: { trend: "rising"|"falling"|"stable", change_cfs, change_pct, hours } }
_weather_data = {}       # { spot_id: { temp_f, wind_mph, wind_dir, short_forecast, precip_pct } }
_reports_data = []       # [ { title, date, snippet, source, url, rivers_mentioned } ]
_cdec_data = {}          # { station_id: { cfs, updatedAt, station_name } }
_last_usgs_fetch = None
_last_df_fetch = None
_last_weather_fetch = None
_last_reports_fetch = None
_last_cdec_fetch = None
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
# Fishing Reports — RSS/Atom feed aggregation
# ══════════════════════════════════════════════════════════════

# Feed sources config
REPORT_FEEDS = [
    {
        "name": "Trout Creek Outfitters",
        "url": "https://www.troutcreekoutfitters.com/blogs/fishing-reports.atom",
        "type": "atom",
        "base_url": "https://www.troutcreekoutfitters.com",
    },
    {
        "name": "Reno Fly Shop",
        "url": "https://renoflyshop.com/blogs/blog.atom",
        "type": "atom",
        "base_url": "https://renoflyshop.com",
    },
    # The Fly Shop stream reports are scraped separately (not via RSS — their /feed is a blog, not stream reports)
]

# River names to match in report titles/content (lowercase)
RIVER_KEYWORDS = [
    "truckee", "carson", "east carson", "west carson", "walker", "east walker",
    "west walker", "little truckee", "yuba", "american", "feather", "sacramento",
    "mccloud", "pit", "hat creek", "fall river", "upper sac", "lower sac",
    "trinity", "klamath", "stanislaus", "tuolumne", "merced", "kings",
    "kern", "kaweah", "owens", "hot creek", "pyramid", "tahoe",
    "donner", "prosser", "stampede", "boca", "independence", "truckee river",
    "carson river", "mammoth", "crowley", "bridgeport", "convict",
    "san joaquin", "mokelumne", "calaveras", "cosumnes", "deer creek",
    "mill creek", "battle creek", "clear creek",
]


class HTMLStripper(HTMLParser):
    """Simple HTML tag stripper for feed content."""
    def __init__(self):
        super().__init__()
        self.text = []
    def handle_data(self, data):
        self.text.append(data)
    def get_text(self):
        return " ".join(self.text).strip()


def strip_html(html_str):
    """Remove HTML tags from a string."""
    if not html_str:
        return ""
    stripper = HTMLStripper()
    try:
        stripper.feed(html_str)
        return stripper.get_text()
    except Exception:
        return re.sub(r'<[^>]+>', '', html_str)


def _match_rivers(text):
    """Find river names mentioned in text. Returns list of matched keywords."""
    if not text:
        return []
    text_lower = text.lower()
    return [kw for kw in RIVER_KEYWORDS if kw in text_lower]


def _parse_atom_feed(xml_text, source_name, base_url):
    """Parse Shopify Atom feed XML into report entries."""
    entries = []
    try:
        root = ET.fromstring(xml_text)
        # Atom namespace
        ns = {"atom": "http://www.w3.org/2005/Atom"}

        for entry in root.findall("atom:entry", ns):
            title_el = entry.find("atom:title", ns)
            published_el = entry.find("atom:published", ns)
            updated_el = entry.find("atom:updated", ns)
            content_el = entry.find("atom:content", ns)
            summary_el = entry.find("atom:summary", ns)
            link_el = entry.find("atom:link[@rel='alternate']", ns)
            if link_el is None:
                link_el = entry.find("atom:link", ns)

            title = title_el.text if title_el is not None else "Untitled"
            date_str = (published_el.text if published_el is not None
                        else updated_el.text if updated_el is not None
                        else "")
            link = link_el.get("href", "") if link_el is not None else ""
            if link and not link.startswith("http"):
                link = base_url.rstrip("/") + "/" + link.lstrip("/")

            # Get snippet from content or summary
            raw_content = ""
            if content_el is not None and content_el.text:
                raw_content = content_el.text
            elif summary_el is not None and summary_el.text:
                raw_content = summary_el.text

            snippet = strip_html(raw_content)[:300]
            if len(strip_html(raw_content)) > 300:
                snippet += "..."

            # Match rivers
            full_text = f"{title} {raw_content}"
            rivers = _match_rivers(full_text)

            entries.append({
                "title": title,
                "date": date_str[:10] if date_str else "",
                "snippet": snippet,
                "source": source_name,
                "url": link,
                "rivers_mentioned": rivers,
            })

    except ET.ParseError as e:
        print(f"  [reports] XML parse error for {source_name}: {e}")

    return entries


def _parse_rss_feed(xml_text, source_name, base_url):
    """Parse WordPress RSS feed XML into report entries."""
    entries = []
    try:
        root = ET.fromstring(xml_text)
        for item in root.findall(".//item"):
            title_el = item.find("title")
            pub_date_el = item.find("pubDate")
            desc_el = item.find("description")
            content_el = item.find("{http://purl.org/rss/1.0/modules/content/}encoded")
            link_el = item.find("link")

            title = title_el.text if title_el is not None else "Untitled"
            date_str = pub_date_el.text if pub_date_el is not None else ""
            link = link_el.text if link_el is not None else ""

            # Parse RSS date format (e.g., "Mon, 04 Apr 2026 12:00:00 +0000")
            parsed_date = ""
            if date_str:
                try:
                    from email.utils import parsedate_to_datetime
                    dt = parsedate_to_datetime(date_str)
                    parsed_date = dt.strftime("%Y-%m-%d")
                except Exception:
                    parsed_date = date_str[:10]

            # Get content
            raw_content = ""
            if content_el is not None and content_el.text:
                raw_content = content_el.text
            elif desc_el is not None and desc_el.text:
                raw_content = desc_el.text

            snippet = strip_html(raw_content)[:300]
            if len(strip_html(raw_content)) > 300:
                snippet += "..."

            full_text = f"{title} {raw_content}"
            rivers = _match_rivers(full_text)

            entries.append({
                "title": title,
                "date": parsed_date,
                "snippet": snippet,
                "source": source_name,
                "url": link,
                "rivers_mentioned": rivers,
            })

    except ET.ParseError as e:
        print(f"  [reports] RSS parse error for {source_name}: {e}")

    return entries


def _scrape_fly_shop_stream_reports():
    """
    Scrape The Fly Shop's stream report page for individual river reports.
    Returns list of report dicts matching the standard format.
    """
    url = "https://www.theflyshop.com/streamreport.html"
    entries = []
    try:
        req = Request(url, headers={"User-Agent": "LookingForSpots/1.0"})
        resp = urlopen(req, timeout=20)
        html = resp.read().decode("utf-8", errors="replace")

        # Parse each river report tab pane
        # Pattern: <h4>River Name - Updated: Date</h4> ... <div class="report">...</div>
        report_pattern = re.compile(
            r'<h4>\s*([^<]+?)\s*-\s*Updated:\s*&nbsp;([^<]+?)\s*</h4>'
            r'.*?<div class="report">(.*?)</div>',
            re.DOTALL
        )

        for match in report_pattern.finditer(html):
            river_name = match.group(1).strip()
            date_str = match.group(2).strip()
            raw_content = match.group(3).strip()

            # Parse date (e.g., "April 7, 2026" → "2026-04-07")
            parsed_date = ""
            try:
                dt = datetime.strptime(date_str, "%B %d, %Y")
                parsed_date = dt.strftime("%Y-%m-%d")
            except ValueError:
                parsed_date = date_str

            snippet = strip_html(raw_content)[:400]
            if len(strip_html(raw_content)) > 400:
                snippet += "..."

            full_text = f"{river_name} {raw_content}"
            rivers = _match_rivers(full_text)

            entries.append({
                "title": f"{river_name} Stream Report",
                "date": parsed_date,
                "snippet": snippet,
                "source": "The Fly Shop",
                "url": f"{url}",
                "rivers_mentioned": rivers,
            })

        print(f"  [reports] The Fly Shop (scrape): {len(entries)} stream reports found")
    except Exception as e:
        print(f"  [reports] Error scraping The Fly Shop stream reports: {e}")
        traceback.print_exc()

    return entries


def fetch_fishing_reports():
    """
    Fetch fishing reports from all configured RSS/Atom feeds + The Fly Shop scrape.
    Returns list of report dicts sorted by date (newest first), limited to 50.
    """
    all_reports = []

    # RSS/Atom feeds (Trout Creek, Reno Fly Shop)
    for feed in REPORT_FEEDS:
        try:
            req = Request(feed["url"], headers={
                "User-Agent": "LookingForSpots/1.0",
                "Accept": "application/atom+xml, application/rss+xml, application/xml, text/xml",
            })
            resp = urlopen(req, timeout=15)
            xml_text = resp.read().decode("utf-8", errors="replace")

            if feed["type"] == "atom":
                entries = _parse_atom_feed(xml_text, feed["name"], feed["base_url"])
            else:
                entries = _parse_rss_feed(xml_text, feed["name"], feed["base_url"])

            all_reports.extend(entries)
            print(f"  [reports] {feed['name']}: {len(entries)} reports fetched")

        except Exception as e:
            print(f"  [reports] Error fetching {feed['name']}: {e}")

    # The Fly Shop stream reports (scraped from HTML page)
    try:
        tfs_reports = _scrape_fly_shop_stream_reports()
        all_reports.extend(tfs_reports)
    except Exception as e:
        print(f"  [reports] Error with The Fly Shop scrape: {e}")

    # Sort by date descending, take latest 50
    all_reports.sort(key=lambda r: r.get("date", ""), reverse=True)
    return all_reports[:50]


# ══════════════════════════════════════════════════════════════
# CDEC — California Data Exchange Center flow data
# ══════════════════════════════════════════════════════════════

# CDEC stations to monitor (station_id → friendly name)
CDEC_STATIONS = {
    "DLT": "Delta",
    "MSS": "McCloud River (above Shasta)",
    "MCA": "McCloud River (at Ah-Di-Na)",
    "MC7": "McCloud River (below McCloud Dam)",
}


def fetch_cdec_flows():
    """
    Fetch latest flow data from CDEC JSON API.
    Sensor 20 = flow (CFS), dur_code E = event (realtime).
    Returns { station_id: { cfs, updatedAt, station_name } }
    """
    result = {}
    from datetime import timedelta as _td
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - _td(days=1)).strftime("%Y-%m-%d")

    for station_id, station_name in CDEC_STATIONS.items():
        try:
            url = (
                f"https://cdec.water.ca.gov/dynamicapp/req/JSONDataServlet"
                f"?Stations={station_id}&SensorNums=20&dur_code=E"
                f"&Start={yesterday}&End={today}"
            )
            req = Request(url, headers={"User-Agent": "LookingForSpots/1.0"})
            resp = urlopen(req, timeout=15)
            data = json.loads(resp.read().decode("utf-8"))

            if data and isinstance(data, list):
                # Find the most recent non-null reading
                for reading in reversed(data):
                    val = reading.get("value")
                    if val is not None and val != -9999 and val != "":
                        try:
                            cfs = float(val)
                            result[station_id] = {
                                "cfs": cfs,
                                "updatedAt": reading.get("date", ""),
                                "station_name": station_name,
                            }
                            print(f"  [cdec] {station_id} ({station_name}): {cfs} CFS")
                            break
                        except (ValueError, TypeError):
                            continue

            time.sleep(0.3)  # Rate limit

        except Exception as e:
            print(f"  [cdec] Error fetching {station_id}: {e}")
            time.sleep(0.3)

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
    global _reports_data, _last_reports_fetch, _cdec_data, _last_cdec_fetch

    site_ids = _load_site_ids()
    print(f"  [data] Found {len(site_ids)} USGS site IDs in config")

    spots = _load_spots_with_coords()
    print(f"  [data] Found {len(spots)} spots with coordinates for weather")

    last_weather_time = 0  # Force fetch on first run
    last_reports_time = 0  # Force fetch on first run
    last_cdec_time = 0     # Force fetch on first run

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

        # ── CDEC (every 15 minutes, same as USGS) ──
        now = time.time()
        if now - last_cdec_time >= 15 * 60:
            try:
                cdec = fetch_cdec_flows()
                with _data_lock:
                    _cdec_data = cdec
                    _last_cdec_fetch = datetime.now(timezone.utc).isoformat()
                print(f"  [data] CDEC: {len(cdec)} stations fetched")
                last_cdec_time = now
            except Exception as e:
                print(f"  [data] CDEC error: {e}")
                traceback.print_exc()

        # ── Fishing Reports (every 2 hours — shops update weekly at most) ──
        now = time.time()
        if now - last_reports_time >= 2 * 60 * 60:
            try:
                reports = fetch_fishing_reports()
                with _data_lock:
                    _reports_data = reports
                    _last_reports_fetch = datetime.now(timezone.utc).isoformat()
                print(f"  [data] Reports: {len(reports)} reports fetched")
                last_reports_time = now
            except Exception as e:
                print(f"  [data] Reports error: {e}")
                traceback.print_exc()

        # ── Weather (every 60 minutes, not every 15 min — slowest, runs last) ──
        now = time.time()
        if now - last_weather_time >= 60 * 60:
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

        # ── /api/reports → fishing reports ──
        if parsed.path == "/api/reports":
            return self._serve_reports()

        # ── /api/cdec → CDEC flow data ──
        if parsed.path == "/api/cdec":
            return self._serve_cdec()

        # ── /api/status → health check ──
        if parsed.path == "/api/status":
            return self._serve_status()

        # ── static files ──
        return super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)

        # ── /api/subscribe → email subscription ──
        if parsed.path == "/api/subscribe":
            return self._handle_subscribe()

        # ── default: 404 ──
        self.send_error(404)

    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _handle_subscribe(self):
        """Handle POST /api/subscribe with email address."""
        try:
            # Read content length and parse JSON body
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode("utf-8"))
            email = data.get("email", "").strip()

            # Validate email has @ sign
            if not email or "@" not in email:
                return self._json_response(
                    {"ok": False, "message": "Invalid email address"},
                    status=400
                )

            # Load existing subscribers
            subscribers = []
            if _subscribers_file.exists():
                try:
                    with open(_subscribers_file, "r") as f:
                        subscribers = json.load(f)
                except (json.JSONDecodeError, IOError):
                    subscribers = []

            # Check for duplicates
            for sub in subscribers:
                if sub.get("email") == email:
                    return self._json_response(
                        {"ok": False, "message": "Already subscribed"},
                        status=409
                    )

            # Add new subscriber with timestamp
            subscribers.append({
                "email": email,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })

            # Save to file
            with open(_subscribers_file, "w") as f:
                json.dump(subscribers, f, indent=2)

            return self._json_response(
                {"ok": True, "message": "Subscribed!"},
                status=200
            )

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            return self._json_response(
                {"ok": False, "message": "Invalid request"},
                status=400
            )
        except Exception as e:
            return self._json_response(
                {"ok": False, "message": "Server error"},
                status=500
            )

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
                "cdec": {k: v for k, v in _cdec_data.items()},
                "lastUsgsFetch": _last_usgs_fetch,
                "lastDreamflowsFetch": _last_df_fetch,
                "lastWeatherFetch": _last_weather_fetch,
                "lastCdecFetch": _last_cdec_fetch,
            }
        self._json_response(payload)

    def _serve_reports(self):
        with _data_lock:
            payload = {
                "reports": list(_reports_data),
                "lastFetch": _last_reports_fetch,
            }
        self._json_response(payload)

    def _serve_cdec(self):
        with _data_lock:
            payload = {
                "stations": {k: v for k, v in _cdec_data.items()},
                "lastFetch": _last_cdec_fetch,
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
                "fishing_reports": len(_reports_data),
                "cdec_stations": len(_cdec_data),
                "last_usgs_fetch": _last_usgs_fetch,
                "last_df_fetch": _last_df_fetch,
                "last_weather_fetch": _last_weather_fetch,
                "last_reports_fetch": _last_reports_fetch,
                "last_cdec_fetch": _last_cdec_fetch,
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

    print(f"  Server:  http://localhost:{PORT}")
    print(f"  API:     http://localhost:{PORT}/api/flows")
    print(f"  Weather: http://localhost:{PORT}/api/weather")
    print(f"  Reports: http://localhost:{PORT}/api/reports")
    print(f"  CDEC:    http://localhost:{PORT}/api/cdec")
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
