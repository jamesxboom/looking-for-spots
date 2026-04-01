# NorCal Flows Backend - Complete Documentation Index

## Getting Started (Start Here!)

1. **QUICKSTART.md** - Get running in 2 minutes
   - Installation steps
   - Starting the server
   - API testing with curl
   - Troubleshooting common issues

## Usage & Reference

2. **README.md** - Complete API documentation
   - All endpoint specifications with examples
   - Configuration guide
   - Data sources (USGS, CDEC)
   - Traffic light algorithm explanation
   - Development notes and known limitations

## Advanced Topics

3. **ARCHITECTURE.md** - Technical deep-dive
   - System design and data flow
   - Component breakdown
   - Database schema (for future V2)
   - Performance characteristics
   - Security considerations
   - Testing strategy

4. **DEPLOYMENT.md** - Production deployment guide
   - 4 deployment options (Railway, Render, AWS, Docker)
   - Step-by-step instructions for each
   - Monitoring and maintenance
   - Scaling considerations
   - Cost estimates

## Source Code Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app + endpoints
│   ├── config.py            # River configuration
│   ├── models.py            # Pydantic response models
│   └── services/
│       ├── usgs.py          # USGS data fetcher
│       ├── cdec.py          # CDEC data fetcher
│       └── traffic_light.py # Status calculator
├── requirements.txt         # Python dependencies
└── Documentation/
    ├── README.md            # API reference
    ├── QUICKSTART.md        # Getting started
    ├── ARCHITECTURE.md      # Technical details
    ├── DEPLOYMENT.md        # Production guide
    └── INDEX.md             # This file
```

## Quick Reference

### Install & Run
```bash
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### API Endpoints
- `GET /api/rivers` - All rivers with status
- `GET /api/rivers/{river_id}` - Single river details
- `GET /api/rivers/{river_id}/history?days=7` - Historical data
- `GET /api/health` - Health status

### Key Files to Know
- **app/config.py** - All 15 rivers + thresholds (edit to add/change rivers)
- **app/services/traffic_light.py** - Status algorithm (modify to change logic)
- **app/main.py** - API endpoints (add new endpoints here)

## What the API Does

1. **Fetches Data** every 15 minutes from:
   - USGS (primary) → discharge + temperature
   - CDEC (fallback) → flow + temperature

2. **Calculates Status** using traffic light algorithm:
   - Temperature override (>68°F = RED)
   - Flow comparison to thresholds
   - Rate of change detection
   - Trend calculation

3. **Returns JSON** with:
   - Status (green/yellow/red)
   - Status reason (human-readable)
   - Current flow (CFS)
   - Water temperature (°F)
   - Trend (rising/stable/falling)
   - Thresholds and metadata

## Common Development Tasks

### Add a New River
Edit `app/config.py`:
1. Add RiverThresholds entry
2. Add RiverConfig entry with USGS/CDEC IDs
3. Add to RIVERS dict

### Change Status Logic
Edit `app/services/traffic_light.py`:
- Modify threshold comparisons
- Adjust temperature override limits
- Change rate-of-change sensitivity

### Add New API Endpoint
Edit `app/main.py`:
1. Define Pydantic response model in models.py
2. Add route handler function
3. Add @app.get("/api/...") decorator

### Modify Data Refresh Schedule
Edit `app/main.py`:
- Change `"interval", minutes=15` to different interval
- Modify `fetch_wrapper()` to change fetch behavior

## Troubleshooting

**No data showing (all CFS = null)**
- Expected initially - USGS APIs can be flaky
- Check logs for error messages
- Wait for next 15-minute refresh cycle

**API not responding**
- Verify server is running: `curl http://localhost:8000/docs`
- Check port (default 8000)
- Verify no firewall blocking

**CDEC 500 errors in logs**
- CDEC API is unreliable - this is expected
- App falls back to USGS automatically
- No action needed

**Import errors**
- Make sure in `backend/` directory
- Run `pip install -r requirements.txt`
- Check Python 3.11+

## Next Steps

1. **Connect Frontend**
   - Have frontend call `GET /api/rivers`
   - Parse JSON response
   - Display as Green/Yellow/Red cards

2. **Deploy to Production**
   - Choose deployment option (Railway recommended)
   - Follow DEPLOYMENT.md instructions
   - Monitor `/api/health` endpoint

3. **Add Database (V2)**
   - Replace in-memory storage with PostgreSQL
   - Implement historical data analysis
   - Add user accounts and saved preferences

4. **Enhance Data**
   - Add weather integration
   - Include hatch information
   - Add recent trip reports

## Key Concepts

### Traffic Light Status
- **GREEN**: Optimal fishing conditions (flow in ideal range, temp <65°F)
- **YELLOW**: Fishable but suboptimal (flow or temp borderline)
- **RED**: Not recommended (flow too high/low, temp >68°F, or rapid change)

### River Thresholds
Each river has:
- **Green range**: Ideal flow (e.g., 4000-7500 CFS for Sacramento)
- **Yellow range**: Acceptable but suboptimal
- **Rapid change threshold**: CFS change that indicates instability

### Data Flow
```
USGS/CDEC APIs (every hour)
  → Fetcher (every 15 min)
  → Status Calculator
  → In-Memory Store
  → REST API
  → Frontend
```

## Support Resources

- **API Interactive Docs**: Visit `/docs` in browser for Swagger UI
- **API Spec Documentation**: Check README.md
- **System Architecture**: See ARCHITECTURE.md
- **Deployment Help**: See DEPLOYMENT.md
- **Quick Start**: See QUICKSTART.md
- **Project Spec**: See PROJECT-SPEC.md (parent directory)

## File Sizes
- Total code: ~40 KB
- Total docs: ~40 KB
- Total project: ~164 KB

## Status
- **Status**: PRODUCTION READY
- **Last Updated**: March 31, 2026
- **Python Version**: 3.11+
- **Framework**: FastAPI 0.104.1
- **Testing**: Complete and verified

---

**Quick Links**
- [Quickstart Guide](QUICKSTART.md)
- [Full API Reference](README.md)
- [Technical Architecture](ARCHITECTURE.md)
- [Deployment Guide](DEPLOYMENT.md)
- [Source Code](app/)

**Questions?** Refer to the appropriate documentation file above, or check the `/docs` endpoint in the running API for interactive testing.

Happy fishing! 🎣
