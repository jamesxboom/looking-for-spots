"""
Pydantic models for API responses.
Uses camelCase aliases for JSON output to match frontend expectations.
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime


def to_camel(string: str) -> str:
    """Convert snake_case to camelCase."""
    parts = string.split("_")
    return parts[0] + "".join(word.capitalize() for word in parts[1:])


class CamelModel(BaseModel):
    """Base model that outputs camelCase JSON."""
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        serialize_by_alias=True,  # Always output camelCase
    )


class ThresholdsResponse(CamelModel):
    """River thresholds for API response."""

    green_floor: float
    green_ceiling: float
    yellow_floor: float
    yellow_ceiling: float
    rapid_change_threshold: float
    notes: str


class ModeStatusResponse(CamelModel):
    """Status for a specific fishing mode (wade or drift)."""
    mode: str  # 'wade' or 'drift'
    status: str  # 'green', 'yellow', 'red'
    status_reason: str
    thresholds: Optional[ThresholdsResponse] = None


class RiverStatusResponse(CamelModel):
    """Current status for a river (used in list endpoint)."""

    id: str
    name: str
    river_type: str
    latitude: float
    longitude: float
    status: str  # 'green', 'yellow', 'red'
    status_reason: str
    current_cfs: Optional[float] = None
    water_temp_f: Optional[float] = None
    trend: str  # 'rising', 'stable', 'falling'
    trend_context: str = ""  # fishing-specific trend meaning
    updated_at: datetime
    # Dual-mode support
    fishing_modes: List[str] = ["wade"]
    mode_statuses: Optional[List[ModeStatusResponse]] = None


class RiverDetailResponse(CamelModel):
    """Detailed information for a single river."""

    id: str
    name: str
    river_type: str
    latitude: float
    longitude: float
    status: str
    status_reason: str
    current_cfs: Optional[float] = None
    water_temp_f: Optional[float] = None
    cfs_change_6hr: Optional[float] = None
    trend: str
    trend_context: str = ""
    thresholds: ThresholdsResponse
    notes: str
    gauge_info: str
    updated_at: datetime
    # Dual-mode support
    fishing_modes: List[str] = ["wade"]
    mode_statuses: Optional[List[ModeStatusResponse]] = None
    blown_out_cfs: Optional[float] = None
    dangerous_wade_cfs: Optional[float] = None
    # Temperature context
    temp_status: Optional[str] = None  # 'ok', 'warming', 'danger'


class HistoryPoint(CamelModel):
    """Single data point in history."""

    timestamp: datetime
    cfs: Optional[float] = None
    temp_f: Optional[float] = None


class RiverHistoryResponse(CamelModel):
    """History data for a river."""

    id: str
    name: str
    readings: List[HistoryPoint]


class HealthResponse(CamelModel):
    """Health check response."""

    status: str
    last_fetch_at: Optional[datetime] = None
    rivers_count: int
