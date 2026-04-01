# NorCal Flows Backend - Quick Start

Get the API running in 2 minutes.

## Prerequisites

- Python 3.11+
- pip (Python package manager)
- 5-10 MB disk space
- Internet connection (for API calls)

## Installation & Run

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

This installs:
- fastapi (web framework)
- uvicorn (ASGI server)
- httpx (async HTTP client)
- apscheduler (task scheduling)
- pydantic (data validation)

### 2. Start the Server
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Expected output:
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
2026-04-01 12:00:00,000 - app.main - INFO - NorCal Flows API starting up...
2026-04-01 12:00:00,000 - app.main - INFO - Performing initial data fetch...
...
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### 3. Open Browser
Visit: **http://localhost:8000/docs**

You'll see the interactive Swagger UI where you can:
- See all available endpoints
- Test the API live
- View request/response examples

## Quick API Tests

### Get All Rivers (with status)
```bash
curl http://localhost:8000/api/rivers | python -m json.tool
```

### Get Specific River
```bash
curl http://localhost:8000/api/rivers/lower_sacramento | python -m json.tool
```

### Get River History
```bash
curl "http://localhost:8000/api/rivers/lower_sacramento/history?days=7" | python -m json.tool
```

### Health Check
```bash
curl http://localhost:8000/api/health
```

## Response Examples

### Rivers List
```json
[
  {
    "id": "lower_sacramento",
    "name": "Lower Sacramento River",
    "river_type": "tailwater",
    "status": "red",
    "current_cfs": null,
    "water_temp_f": null,
    "trend": "stable",
    "updated_at": "2026-04-01T12:00:00Z"
  },
  ...
]
```

### Single River Detail
```json
{
  "id": "lower_sacramento",
  "name": "Lower Sacramento River",
  "river_type": "tailwater",
  "latitude": 40.5865,
  "longitude": -122.4458,
  "status": "red",
  "status_reason": "No flow data available",
  "current_cfs": null,
  "water_temp_f": null,
  "cfs_change_6hr": null,
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

## File Structure

```
backend/
├── app/
│   ├── main.py              ← Main app + endpoints
│   ├── config.py            ← River definitions
│   ├── models.py            ← API schemas
│   └── services/
│       ├── usgs.py          ← USGS data fetcher
│       ├── cdec.py          ← CDEC data fetcher
│       └── traffic_light.py ← Status calculator
├── requirements.txt         ← Dependencies
├── README.md               ← Full documentation
├── ARCHITECTURE.md         ← Technical deep-dive
└── DEPLOYMENT.md           ← Production deployment
```

## What the API Does

1. **Fetches data every 15 minutes** from:
   - USGS Instantaneous Values API (flow + temperature)
   - CDEC (fallback/supplement)

2. **Calculates status** using the traffic light algorithm:
   - Temperature >68°F = RED (lethal)
   - Flow compared to thresholds
   - Rate of change modifier
   - Trend calculation

3. **Returns clean JSON** with:
   - Current CFS (cubic feet per second)
   - Water temperature (Fahrenheit)
   - Status color + explanation
   - 6-hour trend (rising/stable/falling)
   - Historical data for 7 days

## Common Tasks

### View Current Status of All Rivers
```bash
curl -s http://localhost:8000/api/rivers | python -m json.tool
```

### Check API Health
```bash
curl http://localhost:8000/api/health
```

### Get Data for Frontend
```bash
curl http://localhost:8000/api/rivers | jq '.[] | {id, name, status, current_cfs, water_temp_f}'
```

### Check Logs
- Server logs appear in terminal where you ran `uvicorn`
- API request logs show USGS/CDEC calls
- Look for "ERROR" entries if something fails

### Stop the Server
Press `Ctrl+C` in the terminal where uvicorn is running

### Restart the Server
```bash
# Stop with Ctrl+C, then run again
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Development Mode (Auto-reload)

For development, enable auto-reload so changes are reflected immediately:

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Now when you edit Python files, the server automatically restarts.

## Troubleshooting

### Port Already in Use
If port 8000 is already in use, try a different port:
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

### Import Errors
Make sure you're in the `backend` directory and have installed requirements:
```bash
cd backend
pip install -r requirements.txt
```

### No Data Showing (All CFS = null)
- This is expected - USGS APIs sometimes don't have data available
- Check the `/api/health` endpoint to see when data was last fetched
- Wait 15 minutes for the scheduler to refresh
- Check logs for any error messages

### API Not Responding
- Make sure server is running (check terminal)
- Check if using correct port (default 8000)
- Try `curl http://localhost:8000/docs` to verify

### CDEC API Errors (500 responses in logs)
- CDEC API is unreliable - this is expected
- The app falls back to USGS data automatically
- No action needed

## Next Steps

1. **Integrate with Frontend**
   - Frontend calls `http://localhost:8000/api/rivers`
   - Gets JSON response with current status
   - Displays as color-coded cards

2. **Deploy to Cloud**
   - See DEPLOYMENT.md for options (Railway, Render, AWS, etc.)
   - Takes ~5 minutes to deploy

3. **Add Database (Future)**
   - Replace in-memory storage with PostgreSQL
   - Enables historical analysis and analytics
   - Required for production

4. **Monitor in Production**
   - Set up uptime monitoring
   - Monitor `/api/health` endpoint
   - Log errors to external service (Sentry, etc.)

## Documentation

For more details:
- **API Reference**: See Swagger UI at `/docs`
- **Full README**: See `README.md`
- **Architecture**: See `ARCHITECTURE.md`
- **Deployment**: See `DEPLOYMENT.md`
- **Project Spec**: See `PROJECT-SPEC.md` in parent directory

## Key Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/rivers` | GET | All rivers with current status |
| `/api/rivers/{id}` | GET | Single river with details |
| `/api/rivers/{id}/history` | GET | 7-day history for charts |
| `/api/health` | GET | Health check |
| `/docs` | GET | Swagger UI (browser) |
| `/redoc` | GET | ReDoc UI (browser) |

## That's It!

You now have a fully functional fly fishing conditions API running locally. The API will:
- Fetch fresh data every 15 minutes automatically
- Return Green/Yellow/Red status for each river
- Provide 7-day historical data for charts
- Handle errors gracefully

For questions or issues, refer to the full documentation files.

Happy fishing! 🎣

---

**Last updated**: March 31, 2026
**Status**: Ready to Run
