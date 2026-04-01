# NorCal Flows Frontend - Quick Start Guide

## One-Minute Setup

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:3000`

## What You'll See

A beautiful map-centric UI showing:
- Full-screen map of Northern California with color-coded river markers
- Left sidebar (desktop) with river list, sort controls, and status cards
- Click any marker or card to see detailed river information
- 7-day flow trend chart with optimal range reference bands
- Responsive design that works on mobile, tablet, and desktop

## Backend Requirement

The app needs a backend API running at `http://localhost:8000` with these endpoints:

```
GET /api/rivers
GET /api/rivers/{id}
GET /api/rivers/{id}/history?days=7
```

See the backend directory for implementation, or use mock data for testing.

## Testing Without Backend

To test with mock data, you can temporarily modify `src/lib/api.js` to return mock rivers:

```javascript
import { mockRivers, mockHistory } from './mockData'

export const fetchRivers = async () => {
  return mockRivers
}

export const fetchRiverHistory = async (riverId) => {
  return { readings: mockHistory[riverId] || [] }
}
```

Or see `src/lib/mockData.js` for sample river and history data.

## File Structure

```
src/
├── App.jsx                 # Main layout
├── components/
│   ├── Sidebar.jsx        # River list sidebar
│   ├── Map.jsx            # Leaflet map with markers
│   ├── RiverDetail.jsx    # Detail panel
│   ├── RiverCard.jsx      # River card component
│   ├── FlowChart.jsx      # 7-day trend chart
│   ├── StatusBadge.jsx    # Green/Yellow/Red badge
│   └── TrendArrow.jsx     # Trend indicator
├── hooks/
│   └── useRivers.js       # Data fetching hooks
├── lib/
│   ├── api.js             # API client
│   └── mockData.js        # Sample test data
└── index.css              # Global styles
```

## Key Features

### Status Colors
- **Green** (#22c55e) - Good fishing
- **Yellow** (#eab308) - Marginal
- **Red** (#ef4444) - Not recommended

### Interactive Elements
- Click markers to select rivers
- Sort by status, name, or region
- Zoom/pan the map
- View 7-day flow trends
- See current flow vs optimal range

### Auto-Refresh
Rivers update every 5 minutes automatically.

## Customization

### API Base URL
Set in `.env`:
```
VITE_API_BASE_URL=http://localhost:8000
```

### Colors
Edit `tailwind.config.js`:
```javascript
colors: {
  status: {
    green: '#22c55e',
    yellow: '#eab308',
    red: '#ef4444',
  },
}
```

### Map Center & Zoom
In `src/components/Map.jsx`:
```javascript
<MapContainer
  center={[39.8, -121.0]}  // Change latitude, longitude
  zoom={7}                  // Change zoom level
```

## Common Issues

### "Cannot GET /" error
- Build the app: `npm run build`
- Serve it: `npm run preview`

### Map not showing
- Check browser console for errors
- Verify backend is running on port 8000
- Ensure river data has `latitude` and `longitude`

### Rivers not refreshing
- Check Network tab in DevTools
- Verify `/api/rivers` returns valid data
- Check for CORS errors (backend needs to allow requests)

## Build for Production

```bash
npm run build
```

This creates a `dist/` folder ready for deployment to Vercel, Netlify, or any static host.

## Next Steps

1. Start backend: `cd ../backend && python main.py`
2. Start frontend: `npm run dev`
3. Open browser: `http://localhost:3000`
4. Click a marker and explore!

## Support

See `README.md` for full documentation.
