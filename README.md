# Looking For Spots

Real-time fly fishing river conditions dashboard for Northern California. Displays flow data, water temps, and go/no-go status for 7 rivers using a Google Maps-style interface.

## Rivers Tracked

- Upper Truckee at South Lake Tahoe
- Truckee near Truckee
- W. Fork Carson at Woodfords
- E. Fork Carson near Markleeville
- E. Fork Carson near Gardnerville
- Putah Creek below Hwy 29
- Putah Creek below Lake Berryessa

## How It Works

A lightweight Python server scrapes [DreamFlows](https://dreamflows.com) for real-time USGS gauge data, applies trigger-level thresholds, and serves it as JSON. The frontend is a single HTML file with a Leaflet map, sidebar cards, and detail panels — all color-coded green/yellow/red.

## Quick Start

```bash
cd "FlyFishing App"
python3 start.py
```

Opens `http://localhost:5555` in your browser. That's it — no dependencies beyond Python 3.

## Screenshot

Traffic-light status (green = fishable, yellow = caution, red = don't go) based on DreamFlows trigger levels. Click any river for details including flow range bars, water temp warnings, and hydrograph links.

## Data Source

All flow data comes from [DreamFlows](https://dreamflows.com), which aggregates USGS, CDEC, and USBR gauges. Data auto-refreshes every 15 minutes.
