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
_last_usgs_fetch = None
_last_df_fetch = None
_data_lock = threading.Lock()


# ══════════════════════════════════════════════════════════════
# USGS Fetch — primary, most reliable data source
# ══════════════════════════════════════════════════════════════

def fetch_usgs(site_ids):
    """Fetch real-time discharge + temperature from USGS IV service."""
    if not site_ids:
        return {}

    site_param = ",".join(site_ids)
    url = (
        f"https://waterservices.usgs.gov/nwis/iv/?format=json"
        f"&sites={site_param}&parameterCd=00060,00010&siteStatus=active"
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
        elif param_code == "00010":
            result[site_code]["tempF"] = round(val * 9 / 5 + 32, 1)

    return result


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
    global _flow_data, _dreamflows_data, _last_usgs_fetch, _last_df_fetch

    site_ids = _load_site_ids()
    print(f"  [data] Found {len(site_ids)} USGS site IDs in config")

    while True:
        # ── USGS ──
        try:
            usgs = fetch_usgs(site_ids)
            with _data_lock:
                _flow_data = usgs
                _last_usgs_fetch = datetime.now(timezone.utc).isoformat()
            print(f"  [data] USGS: {len(usgs)} sites fetched")
        except Exception as e:
            print(f"  [data] USGS error: {e}")

        # ── DreamFlows ──
        try:
            df = scrape_dreamflows()
            with _data_lock:
                _dreamflows_data = df
                _last_df_fetch = datetime.now(timezone.utc).isoformat()
            print(f"  [data] DreamFlows: {len(df)} sites scraped")
        except Exception as e:
            print(f"  [data] DreamFlows error: {e}")

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
            payload = {
                "usgs": {k: v for k, v in _flow_data.items()},
                "lastUsgsFetch": _last_usgs_fetch,
                "lastDreamflowsFetch": _last_df_fetch,
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
                "last_usgs_fetch": _last_usgs_fetch,
                "last_df_fetch": _last_df_fetch,
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
    print(f"  [data] Background fetcher started (every 15 min)")

    server = http.server.HTTPServer(("0.0.0.0", PORT), Handler)

    print(f"  Server: http://localhost:{PORT}")
    print(f"  API:    http://localhost:{PORT}/api/flows")
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
