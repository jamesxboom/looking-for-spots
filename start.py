#!/usr/bin/env python3
"""
Looking For Spots — Local Server
Scrapes DreamFlows for real-time river conditions and serves a map dashboard.

Usage:
    python3 start.py

Then open http://localhost:5555 in your browser.
"""

import http.server
import json
import os
import re
import sys
import threading
import time
import webbrowser
from urllib.request import urlopen, Request
from urllib.parse import urlparse
from pathlib import Path
from datetime import datetime

PORT = 5555
DIR = Path(__file__).parent

# ============================================================
# DreamFlows Site IDs for our rivers
# ============================================================
SITES = {
    '183': 'upper_truckee',
    '252': 'truckee_nr_truckee',
    '714': 'wf_carson',
    '127': 'ef_carson_markleeville',
    '108': 'ef_carson_gardnerville',
    '032': 'putah_hwy29',
    '486': 'putah_berryessa',
}

# DreamFlows trigger levels (from triggerLevels.php)
# Format: [min_good, min_opt, max_opt, max_good]
TRIGGER_LEVELS = {
    '183': [250, None, None, 500],         # Upper Truckee
    '252': [400, 675, 925, 1000],          # Truckee near Truckee
    '714': [250, None, None, 400],         # W Fork Carson
    '127': [400, 1000, 1400, 4000],        # E Fork Carson Markleeville
    '108': [600, 1275, 1725, 5000],        # E Fork Carson Gardnerville
    '032': [1000, 2500, 3500, 6000],       # Putah below Hwy 29
    '486': [450, None, None, 900],         # Putah below Berryessa
}

# Cached data
cached_data = {'rivers': [], 'fetched_at': None}

def fetch_dreamflows():
    """Scrape DreamFlows real-time map page for our rivers."""
    url = 'https://dreamflows.com/flows.php?page=real&zone=canv&form=maps'
    req = Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
    })

    try:
        with urlopen(req, timeout=15) as resp:
            html = resp.read().decode('utf-8', errors='replace')
    except Exception as e:
        print(f"  ERROR fetching DreamFlows: {e}")
        return []

    # Parse createMarker() calls
    markers = re.findall(r"createMarker\((.*?)\);", html, re.DOTALL)
    rivers = []

    for m in markers:
        # Parse the comma-separated arguments
        # Format: 'siteId', regionNum, index, 'lat', 'lng', 'status', "hoverHtml", "clickHtml"
        try:
            # Extract site ID (first quoted string)
            site_match = re.match(r"'(\d+)'", m.strip())
            if not site_match:
                continue
            site_id = site_match.group(1)

            if site_id not in SITES:
                continue

            # Extract lat/lng
            # Quoted numeric args: 'siteId', 'index', 'lat', 'lng' (regionNum is unquoted)
            coords = re.findall(r"'([\d\.-]+)'", m)
            if len(coords) < 4:
                continue
            lat = float(coords[2])
            lng = float(coords[3])

            # Extract DreamFlows status (Lo, Ok, Hi, Fz, Na)
            status_match = re.search(r"'(Lo|Ok|Hi|Fz|Na)'", m)
            df_status = status_match.group(1) if status_match else 'Na'

            # Extract CFS from hover text
            cfs_match = re.search(r'([\d,]+)\s*cfs', m)
            cfs = None
            if cfs_match:
                cfs = float(cfs_match.group(1).replace(',', ''))

            # Extract temperature
            temp_match = re.search(r'(\d+)&deg;F', m)
            temp_f = float(temp_match.group(1)) if temp_match else None

            # Extract stage height
            stage_match = re.search(r'([\d.]+)\s*ft', m)
            stage_ft = float(stage_match.group(1)) if stage_match else None

            # Extract time
            time_match = re.search(r'(\d{1,2}:\d{2}\s*[ap]m)', m)
            reading_time = time_match.group(1) if time_match else None

            # Extract elevation
            elev_match = re.search(r'Elev:\s*(\d+)\s*ft', m)
            elevation = int(elev_match.group(1)) if elev_match else None

            # Extract river name from hover HTML
            name_match = re.search(r"<span class='Flow\w+'>(.*?)</span>", m)
            name = name_match.group(1) if name_match else f"Site {site_id}"

            # Get trigger levels
            triggers = TRIGGER_LEVELS.get(site_id, [None, None, None, None])
            min_good, min_opt, max_opt, max_good = triggers

            # Calculate our traffic light from DreamFlows status + trigger levels
            if cfs is None:
                status = 'red'
                reason = 'No flow data available'
            elif df_status == 'Hi':
                status = 'red'
                reason = f'High water ({cfs:,.0f} cfs)'
                if max_good:
                    reason += f' — max good: {max_good:,} cfs'
            elif df_status == 'Lo':
                status = 'yellow'
                reason = f'Low water ({cfs:,.0f} cfs)'
                if min_good:
                    reason += f' — min good: {min_good:,} cfs'
            elif df_status == 'Ok':
                # Check if in optimal range
                if min_opt and max_opt and min_opt <= cfs <= max_opt:
                    status = 'green'
                    reason = f'Optimal range ({cfs:,.0f} cfs)'
                elif min_good and max_good and min_good <= cfs <= max_good:
                    status = 'green'
                    reason = f'Good range ({cfs:,.0f} cfs)'
                else:
                    status = 'green'
                    reason = f'Runnable ({cfs:,.0f} cfs)'
            else:
                status = 'red'
                reason = 'No data'

            # Temperature override
            if temp_f and temp_f > 68:
                status = 'red'
                reason = f'Water too warm ({temp_f:.0f}°F)'
            elif temp_f and temp_f > 65 and status == 'green':
                status = 'yellow'
                reason = f'Good flow but water warming ({temp_f:.0f}°F) — fish early'

            river_key = SITES[site_id]
            rivers.append({
                'id': river_key,
                'siteId': site_id,
                'name': name,
                'lat': lat,
                'lng': lng,
                'cfs': cfs,
                'tempF': temp_f,
                'stageFt': stage_ft,
                'elevation': elevation,
                'readingTime': reading_time,
                'status': status,
                'reason': reason,
                'dfStatus': df_status,
                'triggers': {
                    'minGood': min_good,
                    'minOpt': min_opt,
                    'maxOpt': max_opt,
                    'maxGood': max_good,
                },
                'hydrograph': f'https://www.dreamflows.com/graphs/day.{site_id}.php',
            })

            print(f"  {status.upper():6s} | {name:40s} | {cfs:>8,.0f} cfs" if cfs else f"  {'RED':6s} | {name:40s} | — cfs")

        except Exception as e:
            print(f"  WARN: Failed to parse site {site_id if 'site_id' in dir() else '?'}: {e}")
            continue

    return rivers


def refresh_data():
    """Fetch fresh data from DreamFlows."""
    global cached_data
    print("\n  Fetching river conditions from DreamFlows...")
    rivers = fetch_dreamflows()
    if rivers:
        # Sort: green first, then yellow, then red
        order = {'green': 0, 'yellow': 1, 'red': 2}
        rivers.sort(key=lambda r: (order.get(r['status'], 3), r['name']))
        cached_data = {
            'rivers': rivers,
            'fetched_at': datetime.now().isoformat(),
        }
        print(f"  Done! {len(rivers)} rivers loaded.\n")
    else:
        print("  WARNING: No data returned from DreamFlows.\n")


class LookingForSpotsHandler(http.server.SimpleHTTPRequestHandler):
    """Serves the app + provides a JSON API with scraped DreamFlows data."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIR), **kwargs)

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == '/' or parsed.path == '':
            self.path = '/norcal-flows.html'
            return super().do_GET()

        if parsed.path == '/api/rivers':
            self.send_json(cached_data)
            return

        if parsed.path == '/api/refresh':
            refresh_data()
            self.send_json(cached_data)
            return

        return super().do_GET()

    def send_json(self, data):
        body = json.dumps(data).encode()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        if '/api/' in str(args[0]):
            print(f"  -> API: {args[0]}")


def main():
    print()
    print("  ╔═══════════════════════════════════════╗")
    print("  ║     🎣  Looking For Spots  🎣        ║")
    print("  ║    Fly Fishing Conditions Dashboard   ║")
    print("  ╚═══════════════════════════════════════╝")
    print()

    html_path = DIR / 'norcal-flows.html'
    if not html_path.exists():
        print(f"  ERROR: norcal-flows.html not found in {DIR}")
        sys.exit(1)

    # Fetch initial data
    refresh_data()

    # Auto-refresh every 15 minutes in background
    def auto_refresh():
        while True:
            time.sleep(15 * 60)
            refresh_data()

    threading.Thread(target=auto_refresh, daemon=True).start()

    server = http.server.HTTPServer(('0.0.0.0', PORT), LookingForSpotsHandler)

    print(f"  Server: http://localhost:{PORT}")
    print(f"  Press Ctrl+C to stop\n")

    def open_browser():
        time.sleep(1)
        webbrowser.open(f'http://localhost:{PORT}')

    threading.Thread(target=open_browser, daemon=True).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Tight lines! 🐟")
        server.shutdown()


if __name__ == '__main__':
    main()
