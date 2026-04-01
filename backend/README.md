# NorCal Flows Backend API

A FastAPI backend for real-time fly fishing river conditions in Northern California.

## Features

- Real-time flow and water temperature data from USGS and CDEC APIs
- Traffic light status (Green/Yellow/Red) for 15 NorCal rivers
- REST API endpoints for current conditions and historical data
- Automatic data refresh every 15 minutes
- Full CORS support for frontend integration
- Graceful error handling and fallback mechanisms

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Run the Application

```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

For development with auto-reload:
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Interactive API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Get All Rivers
```
GET /api/rivers
```

Returns a list of all 15 rivers with current status, sorted by status (green first, then yellow, then red).

**Response:**
```json
[
  {
    "id": "lower_sacramento",
    "name": "Lower Sacramento River",
    "river_type": "tailwater",
    "status": "green",
    "current_cfs": 5200,
    "water_temp_f": 56,
    "trend": "stable",
    "updated_at": "2026-04-01T12:00:00Z"
  },
  ...
]
```

### Get Single River Details
```
GET /api/rivers/{river_id}
```

Returns detailed information including thresholds and gauges.

**Response:**
```json
{
  "id": "lower_sacramento",
  "name": "Lower Sacramento River",
  "river_type": "tailwater",
  "latitude": 40.5865,
  "longitude": -122.4458,
  "status": "green",
  "status_reason": "Optimal range for fishing",
  "current_cfs": 5200,
  "water_temp_f": 56,
  "cfs_change_6hr": 150,
  "trend": "stable",
  "thresholds": {
    "green_floor": 4000,
    "green_ceiling": 7500,
    "yellow_floor": 3000,
    "yellow_ceiling": 10000,
    "rapid_change_threshold": 1000,
    "notes": "Wading best below 7500. Drift boat above that."
  },
  "notes": "Wading best below 7500. Drift boat above that.",
  "gauge_info": "USGS 11370500 | CDEC KWK",
  "updated_at": "2026-04-01T12:00:00Z"
}
```

### Get River History
```
GET /api/rivers/{river_id}/history?days=7
```

Returns time-series data for the last N days (default 7).

**Response:**
```json
{
  "id": "lower_sacramento",
  "name": "Lower Sacramento River",
  "readings": [
    {
      "timestamp": "2026-03-31T12:00:00Z",
      "cfs": 5100,
      "temp_f": 55.5
    },
    {
      "timestamp": "2026-04-01T00:00:00Z",
      "cfs": 5200,
      "temp_f": 56
    }
  ]
}
```

### Health Check
```
GET /api/health
```

Returns API health status and last fetch timestamp.

**Response:**
```json
{
  "status": "healthy",
  "last_fetch_at": "2026-04-01T12:00:00Z",
  "rivers_count": 15
}
```

## Configuration

River thresholds and station IDs are defined in `app/config.py`. This includes:

- 15 Northern California trout rivers
- Green/Yellow/Red flow thresholds for each river
- USGS Site IDs (primary data source)
- CDEC Station IDs (fallback data source)
- River coordinates and metadata

## Data Sources

### USGS Instantaneous Values API
- Endpoint: `https://waterservices.usgs.gov/nwis/iv/`
- Parameters: 00060 (discharge/CFS), 00010 (water temperature in Celsius)
- No authentication required
- Converted to Fahrenheit for consistency

### CDEC (California Data Exchange Center)
- Endpoint: `https://cdec.water.ca.gov/dynamicapp/req/CSVDataServlet`
- Sensors: 20 (flow), 25 (temperature in Fahrenheit)
- Fallback for rivers without USGS coverage
- CSV format

## Traffic Light Algorithm

Status is determined by:

1. **Temperature Override** (highest priority)
   - >68°F: RED (lethal for trout)
   - >65°F: YELLOW warning (even if flow is green)

2. **Flow-Based Status**
   - Green if within river's optimal range
   - Yellow if within acceptable but suboptimal range
   - Red if outside acceptable thresholds

3. **Rate of Change Modifier**
   - Bumps status to yellow if 6-hour change exceeds rapid change threshold
   - Indicates unstable conditions

4. **Trend**
   - Rising, Stable, or Falling based on 6-hour change

## Automatic Data Refresh

The API automatically fetches data from USGS and CDEC every 15 minutes using APScheduler. This happens in the background and doesn't block API requests.

On startup, an immediate fetch is performed so the API has current data right away.

## Error Handling

- Missing or invalid data is handled gracefully
- Individual river fetch failures don't crash the entire API
- CDEC API failures (500 errors) are logged and skipped
- Falls back to previous data if fetch fails

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app, endpoints, scheduling
│   ├── config.py            # River config, thresholds, coordinates
│   ├── models.py            # Pydantic response models
│   └── services/
│       ├── __init__.py
│       ├── usgs.py          # USGS API adapter
│       ├── cdec.py          # CDEC API adapter
│       └── traffic_light.py # Status calculation logic
├── requirements.txt
└── README.md
```

## Development Notes

### Data Storage

For the prototype, all data is stored in-memory using Python dictionaries. This means:
- Data is lost when the server restarts
- Not suitable for production
- Good for rapid development and testing

For production, implement a database (PostgreSQL + TimescaleDB recommended) and persistent storage layer.

### Testing the API

```bash
# Get all rivers
curl http://localhost:8000/api/rivers

# Get a specific river
curl http://localhost:8000/api/rivers/lower_sacramento

# Get health status
curl http://localhost:8000/api/health

# Get river history
curl "http://localhost:8000/api/rivers/lower_sacramento/history?days=7"
```

## Known Limitations

1. **CDEC API Instability**: The CDEC API occasionally returns 500 errors. The app handles this gracefully by falling back to USGS data only.

2. **No Temperature Data for Some Rivers**: Several rivers (McCloud, Hat Creek, Fall River, etc.) don't have reliable temperature data. The status will be based on flow alone.

3. **History Data**: Some stations may have limited history availability. The history endpoint will return whatever data is available from USGS.

4. **Real-time Delay**: USGS data is updated hourly, not truly real-time. CDEC is slightly more frequent.

## Next Steps (V2)

- [ ] Implement PostgreSQL database for persistent storage
- [ ] Add user accounts and saved preferences
- [ ] Implement push notifications for significant changes
- [ ] Add Mapbox integration for map view
- [ ] Integrate weather data for forecasting
- [ ] Add hatch information and recent reports
- [ ] Implement USBR API for dam release data
- [ ] Add admin dashboard for threshold management
- [ ] Performance optimization with caching layer
- [ ] Deployment to Railway/Render/AWS

## License

(Add your license here)

## Support

For issues or questions, refer to the project specification in `PROJECT-SPEC.md`.
