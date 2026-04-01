# NorCal Flows Frontend

A modern React web app for real-time fly fishing river conditions in Northern California.

## Quick Start

### Installation

```bash
cd frontend
npm install
```

### Development

```bash
npm run dev
```

The app will open at `http://localhost:3000`

### Build for Production

```bash
npm build
```

## Architecture

### Map-Centric UI

The application uses a full-screen Leaflet map with an interactive sidebar:

- **Desktop**: Left sidebar (380px) with river list + full-width map + right detail panel
- **Mobile**: Full-screen map with bottom sheet detail panel and sidebar navigation

### Key Components

#### Core Layout
- **App.jsx** - Main layout container managing state and routing
- **Sidebar.jsx** - Scrollable list of rivers with sort controls
- **Map.jsx** - Leaflet map with circle markers for each river

#### River Details
- **RiverDetail.jsx** - Full detail panel with thresholds, trends, and charts
- **FlowChart.jsx** - 7-day Recharts area chart with reference bands
- **RiverCard.jsx** - Individual river card in sidebar
- **StatusBadge.jsx** - Green/Yellow/Red status indicator
- **TrendArrow.jsx** - Direction arrow with 6hr change

#### Data
- **hooks/useRivers.js** - React hooks for data fetching and caching
- **lib/api.js** - Axios-based API client

## API Integration

The app expects a backend at `http://localhost:8000` (configurable via `VITE_API_BASE_URL`).

### Required Endpoints

```
GET /api/rivers
  Returns: [{id, name, latitude, longitude, status, currentCfs, waterTempF,
             trend, cfsChange6hr, statusReason, region, riverType}, ...]

GET /api/rivers/{riverId}
  Returns: {id, name, status, statusReason, currentCfs, waterTempF, trend,
            cfsChange6hr, thresholds: {greenFloor, greenCeiling},
            notes, riverType, gaugeId, updatedAt}

GET /api/rivers/{riverId}/history?days=7
  Returns: {readings: [{timestamp, cfs, flow, tempF}, ...]}

GET /api/health
  Returns: {status, lastFetchTime}
```

## Styling

### Design System

- **Colors**: Green #22c55e, Yellow #eab308, Red #ef4444
- **Background**: Light #f8fafc with card tints
- **Font**: Inter (from Google Fonts)
- **Spacing**: 12px border radius on cards, 8px on buttons

### Tailwind Configuration

All colors defined in `tailwind.config.js`:
- `text-status-{green|yellow|red}`
- `bg-{light|green|yellow|red}`
- `text-{primary|muted}`

## Features

### River Status
- Real-time traffic light system (Green/Yellow/Red)
- Current flow (CFS) and water temperature
- 6-hour trend with direction arrow
- Intuitive status reason text

### Interactive Map
- OpenStreetMap tiles (free, no API key)
- Color-coded circle markers
- Click-to-view details
- Smooth animations on selection
- Respects bounds to show all rivers

### Responsive Design
- Desktop: Side-by-side layout
- Tablet: Sidebar + map
- Mobile: Full-screen map + bottom sheet

### Performance
- Lazy loading of river details
- Memoized state to prevent re-renders
- 5-minute auto-refresh of data
- Efficient chart rendering with Recharts

## Environment Variables

Create `.env` (from `.env.example`):

```
VITE_API_BASE_URL=http://localhost:8000
```

For production:
```
VITE_API_BASE_URL=https://api.norcalflows.com
```

## Deployment

### Vercel (Recommended)

```bash
npm install -g vercel
vercel
```

### Docker

```bash
docker build -t norcal-flows-frontend .
docker run -p 3000:3000 norcal-flows-frontend
```

### Static Hosting

```bash
npm run build
# Deploy contents of dist/ to any static host
```

## Dependencies

- **react** - UI framework
- **react-leaflet** - Map component
- **leaflet** - Map library
- **recharts** - Chart library
- **axios** - HTTP client
- **tailwindcss** - CSS framework
- **vite** - Build tool

## Testing

Currently no test suite, but structure supports:
- Unit tests via Vitest
- E2E tests via Playwright
- Visual regression tests via Percy

## Known Limitations

1. Data is provisional and delayed 15+ minutes
2. Not all rivers have temperature data
3. Some remote gauges may be offline
4. Chart performance on >100 data points

## Future Enhancements

- User accounts and saved preferences
- Push notifications for status changes
- Fishing hatch predictions
- Historical comparisons
- Weather integration
- Offline support via Service Worker

## Troubleshooting

### Map not showing
- Check browser console for CORS errors
- Verify backend is running on port 8000
- Ensure API responses match expected format

### Markers not appearing
- Verify rivers have `latitude` and `longitude`
- Check that status is one of: green, yellow, red

### Chart not rendering
- Ensure history data has `timestamp` and `cfs` fields
- Check for NaN values in data

## Support

For issues or questions, see the main project README.
