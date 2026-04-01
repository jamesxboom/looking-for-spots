"""
NorCal Flows FastAPI Backend
Main application entry point with API endpoints and scheduled data fetching.
"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler

from app.config import RIVERS
from app.models import (
    RiverStatusResponse,
    RiverDetailResponse,
    RiverHistoryResponse,
    HealthResponse,
    HistoryPoint,
    ThresholdsResponse,
    ModeStatusResponse,
)
from app.services.usgs import fetch_usgs_current, fetch_usgs_history
from app.services.cdec import fetch_cdec_current, fetch_cdec_history
from app.services.traffic_light import (
    calculate_traffic_light,
    calculate_dual_mode,
    GREEN,
    YELLOW,
    RED,
    TEMP_RED_F,
    TEMP_YELLOW_F,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="NorCal Flows API",
    description="Real-time fly fishing conditions for Northern California rivers",
    version="1.0.0"
)

# Add CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# In-memory data storage (prototype only — not a database)
# ============================================================================

class RiverData:
    """Container for a river's current data and history."""

    def __init__(self):
        self.current_cfs: Optional[float] = None
        self.current_temp_f: Optional[float] = None
        self.timestamp: Optional[datetime] = None
        self.cfs_6hr_ago: Optional[float] = None
        self.history: List[HistoryPoint] = []
        self.status: str = "red"
        self.status_reason: str = "No data"
        self.trend: str = "stable"
        self.trend_context: str = ""
        self.updated_at: datetime = datetime.now(timezone.utc)
        # Dual-mode support
        self.mode_statuses: Optional[List[dict]] = None


# Global state dictionary: river_id -> RiverData
river_data: Dict[str, RiverData] = {
    river_id: RiverData() for river_id in RIVERS.keys()
}

# Track last fetch time for health endpoint
last_fetch_at: Optional[datetime] = None


# ============================================================================
# Data fetching functions
# ============================================================================

async def fetch_and_update_single_river(river_id: str) -> None:
    """Fetch data for a single river from USGS/CDEC and update status."""
    try:
        river_config = RIVERS[river_id]
        cfs = None
        temp_f = None

        # Try USGS first (primary source)
        if river_config.usgs_site_id:
            usgs_data = await fetch_usgs_current(river_config.usgs_site_id)
            if usgs_data.cfs is not None:
                cfs = usgs_data.cfs
            if usgs_data.temp_fahrenheit is not None:
                temp_f = usgs_data.temp_fahrenheit

        # Fall back to CDEC if no USGS data
        if cfs is None and river_config.cdec_station_id:
            cdec_data = await fetch_cdec_current(river_config.cdec_station_id)
            if cdec_data.cfs is not None:
                cfs = cdec_data.cfs
            if cdec_data.temp_fahrenheit is not None:
                temp_f = cdec_data.temp_fahrenheit

        # Update river data
        data = river_data[river_id]
        data.current_cfs = cfs
        data.current_temp_f = temp_f
        data.updated_at = datetime.now(timezone.utc)

        # Calculate 6-hour change
        cfs_change_6hr = None
        if data.current_cfs is not None and data.cfs_6hr_ago is not None:
            cfs_change_6hr = data.current_cfs - data.cfs_6hr_ago

        # Calculate traffic light status (with dual-mode if applicable)
        if river_config.wade_thresholds or river_config.drift_thresholds:
            dual_result = calculate_dual_mode(
                river_config,
                data.current_cfs,
                data.current_temp_f,
                cfs_change_6hr,
                data.cfs_6hr_ago,
            )
            status_result = dual_result.primary
            # Store mode-specific statuses
            mode_statuses = []
            if dual_result.wade:
                mode_statuses.append({
                    "mode": "wade",
                    "status": dual_result.wade.status,
                    "status_reason": dual_result.wade.status_reason,
                })
            if dual_result.drift:
                mode_statuses.append({
                    "mode": "drift",
                    "status": dual_result.drift.status,
                    "status_reason": dual_result.drift.status_reason,
                })
            data.mode_statuses = mode_statuses if mode_statuses else None
        else:
            status_result = calculate_traffic_light(
                river_config.thresholds,
                data.current_cfs,
                data.current_temp_f,
                cfs_change_6hr,
                data.cfs_6hr_ago,
                blown_out_cfs=river_config.blown_out_cfs,
                dangerous_wade_cfs=river_config.dangerous_wade_cfs,
            )
            data.mode_statuses = None

        data.status = status_result.status
        data.status_reason = status_result.status_reason
        data.trend = status_result.trend
        data.trend_context = status_result.trend_context

        cfs_str = f"{cfs:.0f}" if cfs is not None else "N/A"
        logger.info(f"{river_config.name}: {status_result.status.upper()} - {cfs_str} cfs")

    except Exception as e:
        logger.error(f"Error fetching data for river {river_id}: {e}")


async def fetch_and_update_all_rivers() -> None:
    """Fetch data for all rivers in parallel."""
    global last_fetch_at

    logger.info("Starting fetch cycle for all rivers...")

    # Fetch all rivers in parallel
    tasks = [fetch_and_update_single_river(river_id) for river_id in RIVERS.keys()]
    await asyncio.gather(*tasks, return_exceptions=True)

    # Now fetch history for each river (for sparklines)
    for river_id in RIVERS.keys():
        try:
            river_config = RIVERS[river_id]
            history_data = {}

            # Fetch history from USGS
            if river_config.usgs_site_id:
                usgs_history = await fetch_usgs_history(river_config.usgs_site_id, days=7)
                for point in usgs_history:
                    if point.timestamp not in history_data:
                        history_data[point.timestamp] = {}
                    if point.cfs is not None:
                        history_data[point.timestamp]["cfs"] = point.cfs
                    if point.temp_fahrenheit is not None:
                        history_data[point.timestamp]["temp_f"] = point.temp_fahrenheit

            # Fetch history from CDEC (fallback)
            if not history_data and river_config.cdec_station_id:
                cdec_history = await fetch_cdec_history(river_config.cdec_station_id, days=7)
                for point in cdec_history:
                    if point.timestamp not in history_data:
                        history_data[point.timestamp] = {}
                    if point.cfs is not None:
                        history_data[point.timestamp]["cfs"] = point.cfs
                    if point.temp_fahrenheit is not None:
                        history_data[point.timestamp]["temp_f"] = point.temp_fahrenheit

            # Convert to HistoryPoint list
            history = [
                HistoryPoint(
                    timestamp=ts,
                    cfs=data.get("cfs"),
                    temp_f=data.get("temp_f")
                )
                for ts, data in sorted(history_data.items())
            ]

            river_data[river_id].history = history

            # Extract 6-hour-ago value for next cycle
            now = datetime.now(timezone.utc)
            six_hours_ago = now - timedelta(hours=6)

            for point in history:
                # Make timestamp timezone-aware if it isn't already
                pt = point.timestamp
                if pt.tzinfo is None:
                    pt = pt.replace(tzinfo=timezone.utc)

                if abs((pt - six_hours_ago).total_seconds()) < 3600:  # Within 1 hour
                    if point.cfs is not None:
                        river_data[river_id].cfs_6hr_ago = point.cfs
                    break

        except Exception as e:
            logger.error(f"Error fetching history for river {river_id}: {e}")

    last_fetch_at = datetime.now(timezone.utc)
    logger.info("Fetch cycle complete")


def schedule_fetcher(app: FastAPI) -> None:
    """Set up scheduled data fetching."""
    scheduler = BackgroundScheduler()

    def fetch_wrapper():
        """Wrapper to run async fetch in sync context."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(fetch_and_update_all_rivers())
        finally:
            loop.close()

    # Schedule to run every 15 minutes
    scheduler.add_job(
        fetch_wrapper,
        "interval",
        minutes=15,
        id="fetch_rivers",
        name="Fetch river data from USGS and CDEC",
        replace_existing=True
    )

    scheduler.start()
    logger.info("Scheduler started: data fetch every 15 minutes")


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        last_fetch_at=last_fetch_at,
        rivers_count=len(RIVERS)
    )


@app.get("/api/rivers", response_model=List[RiverStatusResponse])
async def list_rivers():
    """
    Get all rivers with current status.
    Sorted: green first, then yellow, then red.
    """
    results = []

    for river_id, river_config in RIVERS.items():
        data = river_data[river_id]

        # Build mode statuses for dual-mode rivers
        mode_status_models = None
        if data.mode_statuses:
            mode_status_models = [
                ModeStatusResponse(mode=ms["mode"], status=ms["status"],
                                   status_reason=ms["status_reason"])
                for ms in data.mode_statuses
            ]

        results.append(
            RiverStatusResponse(
                id=river_id,
                name=river_config.name,
                river_type=river_config.river_type,
                latitude=river_config.latitude,
                longitude=river_config.longitude,
                status=data.status,
                status_reason=data.status_reason,
                current_cfs=data.current_cfs,
                water_temp_f=data.current_temp_f,
                trend=data.trend,
                trend_context=data.trend_context,
                updated_at=data.updated_at,
                fishing_modes=river_config.fishing_modes,
                mode_statuses=mode_status_models,
            )
        )

    # Sort: green, yellow, red
    status_order = {GREEN: 0, YELLOW: 1, RED: 2}
    results.sort(key=lambda r: (status_order.get(r.status, 3), r.name))

    return results


@app.get("/api/rivers/{river_id}", response_model=RiverDetailResponse)
async def get_river_detail(river_id: str):
    """Get detailed information for a single river."""
    if river_id not in RIVERS:
        raise HTTPException(status_code=404, detail=f"River '{river_id}' not found")

    river_config = RIVERS[river_id]
    data = river_data[river_id]

    # Calculate 6-hour change
    cfs_change_6hr = None
    if data.current_cfs is not None and data.cfs_6hr_ago is not None:
        cfs_change_6hr = data.current_cfs - data.cfs_6hr_ago

    # Build gauge info string
    gauge_parts = []
    if river_config.usgs_site_id:
        gauge_parts.append(f"USGS {river_config.usgs_site_id}")
    if river_config.cdec_station_id:
        gauge_parts.append(f"CDEC {river_config.cdec_station_id}")

    gauge_info = " | ".join(gauge_parts) if gauge_parts else "No gauge data"

    # Build mode statuses for dual-mode rivers
    mode_status_models = None
    if data.mode_statuses:
        mode_status_models = []
        for ms in data.mode_statuses:
            # Include thresholds for each mode
            mode_thresh = None
            if ms["mode"] == "wade" and river_config.wade_thresholds:
                t = river_config.wade_thresholds
                mode_thresh = ThresholdsResponse(
                    green_floor=t.green_floor, green_ceiling=t.green_ceiling,
                    yellow_floor=t.yellow_floor, yellow_ceiling=t.yellow_ceiling,
                    rapid_change_threshold=t.rapid_change_threshold, notes=t.notes)
            elif ms["mode"] == "drift" and river_config.drift_thresholds:
                t = river_config.drift_thresholds
                mode_thresh = ThresholdsResponse(
                    green_floor=t.green_floor, green_ceiling=t.green_ceiling,
                    yellow_floor=t.yellow_floor, yellow_ceiling=t.yellow_ceiling,
                    rapid_change_threshold=t.rapid_change_threshold, notes=t.notes)
            mode_status_models.append(
                ModeStatusResponse(mode=ms["mode"], status=ms["status"],
                                   status_reason=ms["status_reason"],
                                   thresholds=mode_thresh)
            )

    # Temperature status
    temp_status = None
    if data.current_temp_f is not None:
        if data.current_temp_f >= TEMP_RED_F:
            temp_status = "danger"
        elif data.current_temp_f >= TEMP_YELLOW_F:
            temp_status = "warming"
        else:
            temp_status = "ok"

    return RiverDetailResponse(
        id=river_id,
        name=river_config.name,
        river_type=river_config.river_type,
        latitude=river_config.latitude,
        longitude=river_config.longitude,
        status=data.status,
        status_reason=data.status_reason,
        current_cfs=data.current_cfs,
        water_temp_f=data.current_temp_f,
        cfs_change_6hr=cfs_change_6hr,
        trend=data.trend,
        trend_context=data.trend_context,
        thresholds=ThresholdsResponse(
            green_floor=river_config.thresholds.green_floor,
            green_ceiling=river_config.thresholds.green_ceiling,
            yellow_floor=river_config.thresholds.yellow_floor,
            yellow_ceiling=river_config.thresholds.yellow_ceiling,
            rapid_change_threshold=river_config.thresholds.rapid_change_threshold,
            notes=river_config.thresholds.notes
        ),
        notes=river_config.thresholds.notes,
        gauge_info=gauge_info,
        updated_at=data.updated_at,
        fishing_modes=river_config.fishing_modes,
        mode_statuses=mode_status_models,
        blown_out_cfs=river_config.blown_out_cfs,
        dangerous_wade_cfs=river_config.dangerous_wade_cfs,
        temp_status=temp_status,
    )


@app.get("/api/rivers/{river_id}/history", response_model=RiverHistoryResponse)
async def get_river_history(river_id: str, days: int = 7):
    """Get historical data for a river."""
    if river_id not in RIVERS:
        raise HTTPException(status_code=404, detail=f"River '{river_id}' not found")

    river_config = RIVERS[river_id]
    data = river_data[river_id]

    # Filter history to requested number of days
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=days)

    filtered_history = []
    for point in data.history:
        # Make timestamp timezone-aware if it isn't already
        pt = point.timestamp
        if pt.tzinfo is None:
            pt = pt.replace(tzinfo=timezone.utc)

        if pt >= cutoff:
            filtered_history.append(point)

    return RiverHistoryResponse(
        id=river_id,
        name=river_config.name,
        readings=filtered_history
    )


# ============================================================================
# Application startup/shutdown
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info("NorCal Flows API starting up...")

    # Fetch data immediately on startup
    logger.info("Performing initial data fetch...")
    await fetch_and_update_all_rivers()

    # Start the scheduler for periodic updates
    schedule_fetcher(app)

    logger.info("Application ready!")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info("NorCal Flows API shutting down...")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
