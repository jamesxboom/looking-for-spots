# NorCal Flows — Project Specification v1.0

**A fly fishing conditions app that answers: "Where should I fish today?"**

*Draft for review — March 31, 2026*

---

## Product Vision

NorCal Flows is a mobile-first web app that gives NorCal fly fishermen a single-glance answer to "which rivers are fishing well right now?" It pulls real-time flow and temperature data from public government APIs, applies expert-defined fishability thresholds per river, and displays a simple Green/Yellow/Red traffic light for each river. Think Surfline, but for trout streams.

The core insight: every existing flow app shows raw CFS numbers and expects anglers to interpret them. Nobody translates the data into a go/no-go decision per river. That's the gap.

---

## MVP Scope — "Phase 0"

### Target: Demoable prototype

**15 NorCal trout rivers** with real-time traffic light conditions. No accounts, no login, no push notifications. Just a dashboard that answers the question.

### Rivers

| # | River | Type | Primary Gauge Source | USGS Site ID | CDEC Station |
|---|-------|------|---------------------|-------------|--------------|
| 1 | Lower Sacramento (below Keswick) | Tailwater | USGS + CDEC | 11370500 | KWK |
| 2 | Upper Sacramento (above Shasta) | Freestone | USGS + CDEC | 11342000 | DLT |
| 3 | McCloud River | Spring-fed | USGS | 11367500 | — |
| 4 | Hat Creek (Wild Trout) | Spring creek | CDEC | — | HTH |
| 5 | Fall River | Spring creek | CDEC | — | — |
| 6 | Pit River (Pit 3) | Dam-controlled | USGS + CDEC | 11359500 | PIT |
| 7 | Trinity River (Lewiston) | Tailwater | USGS | 11525500 | — |
| 8 | Truckee River | Dam-controlled | USGS | 10346000 | — |
| 9 | Little Truckee River | Tailwater | USGS | 10340500 | — |
| 10 | East Walker River | Dam-controlled | USGS | 10293000 | — |
| 11 | Lower Owens River | Managed | USGS | 10251300 | — |
| 12 | Upper Owens River | Freestone | USGS | 10250800 | — |
| 13 | North Yuba River | Freestone | USGS | 11413000 | — |
| 14 | Lower American River | Tailwater | USGS + CDEC | 11446500 | AFO |
| 15 | Hot Creek | Spring creek | USGS | 10265150 | — |

> **Note for developers:** USGS Site IDs and CDEC Station IDs above are best-known values from research. The first coding task should validate every ID against live API responses. Some IDs may need correction or the nearest alternative station.

---

## Traffic Light System

### Algorithm

```
function getTrafficLight(river, currentCFS, waterTempF, cfsChange6hr):

  // TEMPERATURE OVERRIDES — non-negotiable
  if waterTempF is available:
    if waterTempF > 68: return RED, "Water too warm for trout"
    if waterTempF > 65: tempWarning = true

  // FLOW STATUS
  if currentCFS >= river.greenFloor AND currentCFS <= river.greenCeiling:
    status = GREEN
  else if currentCFS >= river.yellowFloor AND currentCFS <= river.yellowCeiling:
    status = YELLOW
  else:
    status = RED

  // RATE OF CHANGE — bump to yellow if flows shifting fast
  if abs(cfsChange6hr) > river.rapidChangeThreshold:
    status = max(status, YELLOW)

  // TEMPERATURE WARNING — downgrade green to yellow
  if tempWarning AND status == GREEN:
    status = YELLOW, "Good flow but water warming — fish early morning"

  return status
```

### River Thresholds

```json
{
  "lower_sacramento": {
    "greenFloor": 4000, "greenCeiling": 7500,
    "yellowFloor": 3000, "yellowCeiling": 10000,
    "rapidChangeThreshold": 1000,
    "notes": "Wading best below 7500. Drift boat above that."
  },
  "upper_sacramento": {
    "greenFloor": 800, "greenCeiling": 1200,
    "yellowFloor": 500, "yellowCeiling": 2000,
    "rapidChangeThreshold": 300,
    "notes": "Sweet spot ~1100 at Delta gauge."
  },
  "mccloud": {
    "greenFloor": 170, "greenCeiling": 1000,
    "yellowFloor": 100, "yellowCeiling": 1500,
    "rapidChangeThreshold": 200,
    "notes": "Holy Water section wadeable 170-250. Full river opens at 600+."
  },
  "hat_creek": {
    "greenFloor": 380, "greenCeiling": 650,
    "yellowFloor": 125, "yellowCeiling": 800,
    "rapidChangeThreshold": 100,
    "notes": "Wild Trout section below Powerhouse 2."
  },
  "fall_river": {
    "greenFloor": 0, "greenCeiling": 99999,
    "yellowFloor": 0, "yellowCeiling": 99999,
    "rapidChangeThreshold": 99999,
    "notes": "Spring creek. Flow rarely an issue. Temp and hatch matter more. Always boat/tube fishing."
  },
  "pit_river": {
    "greenFloor": 300, "greenCeiling": 430,
    "yellowFloor": 200, "yellowCeiling": 600,
    "rapidChangeThreshold": 100,
    "notes": "Difficult wading at any flow. Wading staff essential."
  },
  "trinity": {
    "greenFloor": 300, "greenCeiling": 1000,
    "yellowFloor": 200, "yellowCeiling": 1700,
    "rapidChangeThreshold": 500,
    "notes": "Most comfortable 450-550. Spring restoration pulses can spike flows."
  },
  "truckee": {
    "greenFloor": 200, "greenCeiling": 600,
    "yellowFloor": 100, "yellowCeiling": 1000,
    "rapidChangeThreshold": 200,
    "notes": "Upper section 200-300 optimal. Canyon section handles 1000+."
  },
  "little_truckee": {
    "greenFloor": 130, "greenCeiling": 350,
    "yellowFloor": 47, "yellowCeiling": 500,
    "rapidChangeThreshold": 100,
    "notes": "Perfect at ~350. Tailwater with consistent temps."
  },
  "east_walker": {
    "greenFloor": 80, "greenCeiling": 250,
    "yellowFloor": 50, "yellowCeiling": 350,
    "rapidChangeThreshold": 75,
    "notes": "Miracle Mile. Nymphing best 50-300, streamers above 300."
  },
  "lower_owens": {
    "greenFloor": 80, "greenCeiling": 280,
    "yellowFloor": 50, "yellowCeiling": 300,
    "rapidChangeThreshold": 50,
    "notes": "Wading dangerous above 300."
  },
  "upper_owens": {
    "greenFloor": 100, "greenCeiling": 140,
    "yellowFloor": 70, "yellowCeiling": 200,
    "rapidChangeThreshold": 30,
    "notes": "Small stream. Below Hot Creek confluence ~140."
  },
  "north_yuba": {
    "greenFloor": 50, "greenCeiling": 200,
    "yellowFloor": 30, "yellowCeiling": 800,
    "rapidChangeThreshold": 100,
    "notes": "Low-flow freestone. Best after spring runoff drops."
  },
  "lower_american": {
    "greenFloor": 1500, "greenCeiling": 3000,
    "yellowFloor": 1000, "yellowCeiling": 5000,
    "rapidChangeThreshold": 500,
    "notes": "Primarily boat-fished. Fish get spooky below 1500 (too clear)."
  },
  "hot_creek": {
    "greenFloor": 8, "greenCeiling": 50,
    "yellowFloor": 5, "yellowCeiling": 70,
    "rapidChangeThreshold": 10,
    "notes": "Tiny spring creek. Very technical. Fishable year-round."
  }
}
```

---

## Data Architecture

### Sources (in priority order)

**1. USGS Instantaneous Values API (primary)**
- Endpoint: `https://waterservices.usgs.gov/nwis/iv/`
- Parameters: `sites={siteID}&parameterCd=00060,00010&format=json`
  - 00060 = discharge (CFS)
  - 00010 = water temperature (C — convert to F)
- Update frequency: every 15 min, transmitted hourly
- No API key required. No documented rate limits.
- Python package: `dataretrieval` (official USGS)

> **Important:** Legacy API sunsetting early 2027. New API: `api.waterdata.usgs.gov`. Build adapters that can swap. For the prototype, legacy is fine.

**2. CDEC (California Data Exchange Center)**
- Endpoint: `https://cdec.water.ca.gov/dynamicapp/wsSensorData`
- Key sensors: 20 (discharge CFS), 25 (water temp F), 1 (stage ft)
- Duration codes: E=event, H=hourly, D=daily
- Formats: JSON, CSV
- Max 8,192 data points per query
- Data is provisional (not official record)
- Python package: `CDECRetrieve` (community)

**3. USBR RISE (Bureau of Reclamation) — for dam releases**
- Endpoint: `https://data.usbr.gov` (REST API)
- Covers: Shasta, Folsom, New Melones, Oroville
- JSON/CSV output, OpenAPI spec available
- Use for: reservoir outflow data on dam-controlled rivers

### Data Flow

```
                    ┌─────────────────┐
                    │   Cron Job       │
                    │   (every 15 min) │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
         USGS API       CDEC API       USBR API
              │              │              │
              └──────────────┼──────────────┘
                             ▼
                    ┌─────────────────┐
                    │  Normalize &     │
                    │  Deduplicate     │
                    │  (some stations  │
                    │  report to both  │
                    │  USGS + CDEC)    │
                    └────────┬────────┘
                             ▼
                    ┌─────────────────┐
                    │  PostgreSQL /    │
                    │  TimescaleDB     │
                    │                  │
                    │  Tables:         │
                    │  - rivers        │
                    │  - stations      │
                    │  - readings      │
                    │  - thresholds    │
                    └────────┬────────┘
                             ▼
                    ┌─────────────────┐
                    │  REST API        │
                    │  (FastAPI)       │
                    │                  │
                    │  GET /rivers     │
                    │  GET /rivers/:id │
                    │  GET /rivers/:id │
                    │      /history    │
                    └────────┬────────┘
                             ▼
                    ┌─────────────────┐
                    │  React Frontend  │
                    │  (Next.js or     │
                    │   Vite + React)  │
                    └─────────────────┘
```

### Database Schema (simplified)

```sql
-- River definitions with thresholds
CREATE TABLE rivers (
  id TEXT PRIMARY KEY,           -- e.g. 'lower_sacramento'
  name TEXT NOT NULL,            -- e.g. 'Lower Sacramento River'
  region TEXT,                   -- e.g. 'Shasta County'
  latitude DOUBLE PRECISION,
  longitude DOUBLE PRECISION,
  river_type TEXT,               -- tailwater, freestone, spring_creek
  green_floor NUMERIC,
  green_ceiling NUMERIC,
  yellow_floor NUMERIC,
  yellow_ceiling NUMERIC,
  rapid_change_threshold NUMERIC,
  notes TEXT
);

-- Gauge stations linked to rivers
CREATE TABLE stations (
  id TEXT PRIMARY KEY,           -- e.g. 'usgs_11370500'
  river_id TEXT REFERENCES rivers(id),
  source TEXT NOT NULL,          -- 'usgs', 'cdec', 'usbr'
  source_id TEXT NOT NULL,       -- the external ID
  parameter TEXT NOT NULL,       -- 'discharge', 'temperature'
  name TEXT,
  latitude DOUBLE PRECISION,
  longitude DOUBLE PRECISION,
  is_primary BOOLEAN DEFAULT true
);

-- Time-series readings
CREATE TABLE readings (
  station_id TEXT REFERENCES stations(id),
  timestamp TIMESTAMPTZ NOT NULL,
  value NUMERIC NOT NULL,
  unit TEXT NOT NULL,            -- 'cfs', 'fahrenheit', 'feet'
  quality_flag TEXT,             -- 'provisional', 'approved'
  PRIMARY KEY (station_id, timestamp)
);

-- Computed current status (materialized or cached)
CREATE TABLE river_status (
  river_id TEXT REFERENCES rivers(id) PRIMARY KEY,
  status TEXT NOT NULL,          -- 'green', 'yellow', 'red'
  status_reason TEXT,
  current_cfs NUMERIC,
  water_temp_f NUMERIC,
  cfs_change_6hr NUMERIC,
  trend TEXT,                    -- 'rising', 'stable', 'falling'
  updated_at TIMESTAMPTZ NOT NULL
);
```

---

## Frontend Specification

### Tech Stack

- **Framework:** React 18 + Vite (fast builds, no SSR needed for prototype)
- **Styling:** Tailwind CSS
- **Charts:** Recharts (sparklines on dashboard, 7-day history on detail)
- **Maps:** None for MVP (conditions-first, not map-first — add Mapbox in V2)
- **Deployment:** Vercel (free tier, instant deploys)

### Screens

#### 1. Dashboard (the main screen)

A vertical list of all 15 rivers. Each river card shows:

```
┌──────────────────────────────────────────┐
│  ● Lower Sacramento River         GREEN  │
│    4,200 cfs  |  56°F  |  → stable      │
│    "Optimal range. Great wading below    │
│     Keswick."                            │
└──────────────────────────────────────────┘
┌──────────────────────────────────────────┐
│  ● Upper Sacramento River        YELLOW  │
│    1,850 cfs  |  52°F  |  ↑ rising      │
│    "Above optimal. Fishable but flows    │
│     are high."                           │
└──────────────────────────────────────────┘
┌──────────────────────────────────────────┐
│  ● Trinity River                    RED  │
│    6,200 cfs  |  48°F  |  ↑↑ rising     │
│    "Blown out — spring restoration       │
│     pulse in progress."                  │
└──────────────────────────────────────────┘
```

- Green dot / Yellow dot / Red dot with background tint
- Sort options: By status (green first), by name, by region
- Pull-to-refresh
- "Last updated: 12 min ago" at top

#### 2. River Detail (tap a card)

```
Lower Sacramento River
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STATUS: GREEN — Go Fish

Current Flow:  4,200 cfs
Optimal Range: 4,000 — 7,500 cfs
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Water Temp:    56°F  (optimal < 65°F)
Trend:         → Stable
6hr Change:    +120 cfs

[========== 7-day flow sparkline ==========]

Type: Tailwater (below Keswick Dam)
Notes: Wading best below 7,500 cfs.
       Drift boat recommended above that.

Gauge: USGS 11370500
Last reading: 11:45 AM today

Data is provisional. Not for safety decisions.
```

#### 3. About / Disclaimer

Static page. Includes:
- Data sources attribution (USGS, CDEC, USBR)
- "Data is provisional and not real-time" disclaimer
- "Do not use as sole basis for safety decisions"
- Temperature ethics note re: trout mortality above 68F
- Link to USGS, CDEC for official data

### Design Tokens

```
Colors:
  green:    #22c55e (bg: #f0fdf4)
  yellow:   #eab308 (bg: #fefce8)
  red:      #ef4444 (bg: #fef2f2)
  bg:       #f8fafc
  text:     #1e293b
  muted:    #64748b

Font: Inter (system fallback: -apple-system, sans-serif)
Border radius: 12px (cards), 8px (buttons)
```

---

## Backend Specification

### Tech Stack

- **Framework:** Python 3.11+ with FastAPI
- **Database:** PostgreSQL 15 (TimescaleDB extension optional for V2)
- **Task scheduling:** APScheduler or simple cron
- **Deployment:** Railway, Render, or a small EC2 instance
- **Estimated cost:** $20-50/month for prototype

### API Endpoints

```
GET /api/rivers
  → Returns all rivers with current status
  → Response: [{id, name, status, currentCfs, waterTempF, trend, updatedAt}, ...]

GET /api/rivers/{river_id}
  → Returns detailed river info with thresholds and latest readings
  → Response: {id, name, status, statusReason, currentCfs, waterTempF,
               trend, cfsChange6hr, thresholds: {greenFloor, ...},
               notes, gaugeInfo, updatedAt}

GET /api/rivers/{river_id}/history?days=7
  → Returns time-series readings for sparkline/charts
  → Response: {readings: [{timestamp, cfs, tempF}, ...]}

GET /api/health
  → Returns API health + last successful data fetch timestamp
```

### Data Fetcher (runs every 15 min)

```python
# Pseudocode for the fetch cycle

async def fetch_cycle():
    for station in get_all_stations():
        if station.source == 'usgs':
            data = await fetch_usgs(station.source_id, params=['00060', '00010'])
        elif station.source == 'cdec':
            data = await fetch_cdec(station.source_id, sensors=[20, 25])
        elif station.source == 'usbr':
            data = await fetch_usbr(station.source_id)

        store_readings(station.id, data)

    # After all readings stored, recompute status for each river
    for river in get_all_rivers():
        latest_cfs = get_latest_reading(river.id, 'discharge')
        latest_temp = get_latest_reading(river.id, 'temperature')
        cfs_6hr_ago = get_reading_at(river.id, 'discharge', hours_ago=6)

        change_6hr = latest_cfs - cfs_6hr_ago if cfs_6hr_ago else None
        status = compute_traffic_light(river, latest_cfs, latest_temp, change_6hr)

        update_river_status(river.id, status)
```

---

## Project Structure

```
norcal-flows/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entry
│   │   ├── config.py            # River thresholds, station mappings
│   │   ├── models.py            # SQLAlchemy/Pydantic models
│   │   ├── api/
│   │   │   └── rivers.py        # API route handlers
│   │   ├── services/
│   │   │   ├── usgs.py          # USGS API adapter
│   │   │   ├── cdec.py          # CDEC API adapter
│   │   │   ├── usbr.py          # USBR API adapter
│   │   │   └── traffic_light.py # Status computation
│   │   └── tasks/
│   │       └── fetcher.py       # Scheduled data fetcher
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── Dashboard.jsx     # River list with status cards
│   │   │   ├── RiverCard.jsx     # Individual river summary
│   │   │   ├── RiverDetail.jsx   # Full river detail view
│   │   │   ├── FlowChart.jsx     # 7-day sparkline
│   │   │   ├── StatusBadge.jsx   # Green/Yellow/Red indicator
│   │   │   └── TrendArrow.jsx    # Rising/stable/falling
│   │   ├── hooks/
│   │   │   └── useRivers.js      # Data fetching hooks
│   │   ├── lib/
│   │   │   └── api.js            # API client
│   │   └── index.css             # Tailwind imports
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.js
├── data/
│   └── river_config.json         # River thresholds (source of truth)
└── README.md
```

---

## Implementation Order

### Sprint 1: Data Pipeline (build first, demo with CLI)

1. Validate all USGS site IDs — hit the API, confirm each returns discharge data
2. Validate CDEC station IDs — confirm sensor 20 (flow) and sensor 25 (temp) availability
3. Build USGS adapter: fetch current + 7-day history for a station
4. Build CDEC adapter: same
5. Build traffic light calculator with the threshold config above
6. Write a CLI script that prints current status for all 15 rivers (proof of concept)

### Sprint 2: Backend API

7. Set up FastAPI project with PostgreSQL
8. Create database schema and seed river config
9. Implement the three API endpoints
10. Set up the 15-minute fetch cron job
11. Deploy backend (Railway or Render)

### Sprint 3: Frontend

12. Scaffold React + Vite + Tailwind project
13. Build Dashboard with RiverCard components (hardcoded data first)
14. Connect to live API
15. Build RiverDetail page with sparkline chart
16. Add status sorting, pull-to-refresh
17. Deploy frontend (Vercel)
18. Mobile responsiveness pass

### Sprint 4: Polish for Demo

19. Error states (API down, no data, stale data warnings)
20. Loading states and skeleton screens
21. Disclaimer/about page
22. Test with real conditions — compare against The Fly Shop stream report
23. Performance check (should load in <2 seconds on mobile)

---

## Known Risks and Open Questions

**Station ID accuracy:** The USGS site IDs and CDEC station IDs in this spec are from research, not verified against live APIs. First task is validation. Some rivers (Fall River, Hot Creek) may not have obvious gauge stations, or the nearest gauge may be miles from the fishing water.

**Temperature data gaps:** Many stations measure flow but not temperature. For rivers without temp data, the traffic light should note "temp unavailable" rather than assume it's fine. The research suggests McCloud, Hat Creek, Fall River, East Walker, Hot Creek, and Owens may have limited temp coverage.

**Deduplication:** Some locations report to both USGS and CDEC. The backend needs to handle this (prefer USGS for consistency, fall back to CDEC).

**Fall River is special:** As a deep spring creek fished exclusively from boats, flow thresholds are basically irrelevant. Status should be based on temp and hatch conditions, or simply always show Green with a note.

**USGS API migration:** The legacy waterservices.usgs.gov is sunsetting early 2027. The new api.waterdata.usgs.gov should work, but we should build the adapter to be swappable.

**Liability:** The disclaimer needs to be prominent. Data is provisional and delayed. This app is for trip planning, not safety decisions.

---

## Success Criteria for Demo

The prototype is demoable when:

1. A user opens the app on their phone and sees all 15 rivers with current status
2. Each river shows a colored Green/Yellow/Red badge that reflects real, live flow data
3. Tapping a river shows current CFS, the optimal range for context, water temp (where available), and a 7-day trend sparkline
4. The whole experience loads in under 3 seconds
5. Status ratings roughly match what The Fly Shop or Ted Fay would say about current conditions

---

*This document is the source of truth for the build. Review, mark up, and approve — then we code.*
