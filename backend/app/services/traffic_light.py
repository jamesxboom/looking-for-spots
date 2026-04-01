"""
Traffic light status calculator for fly fishing conditions.

Implements GREEN/YELLOW/RED status based on:
1. Temperature override (>68°F = hard RED for trout stress)
2. Flow-based status from river-specific thresholds
3. Rate of change modifier
4. Trend direction context (falling/clearing = good, rising/muddying = bad)
5. Dual-mode support for wade vs. drift boat rivers
"""

from typing import Optional, Tuple, List
from app.config import RiverThresholds, RiverConfig, WADE_THRESHOLDS, DRIFT_THRESHOLDS

# Status constants
GREEN = "green"
YELLOW = "yellow"
RED = "red"

# Trend constants
RISING = "rising"
STABLE = "stable"
FALLING = "falling"

# Temperature thresholds (trout stress)
TEMP_RED_F = 68.0    # Hard caution / red flag — trout stress threshold
TEMP_YELLOW_F = 65.0  # Warming warning — fish early morning


class TrafficLightResult:
    """Container for traffic light calculation result."""

    def __init__(self, status: str, status_reason: str, trend: str,
                 trend_context: str = ""):
        self.status = status
        self.status_reason = status_reason
        self.trend = trend
        self.trend_context = trend_context  # e.g. "Falling — clearing, good for fishing"


class DualModeResult:
    """Container for dual-mode (wade + drift) traffic light results."""

    def __init__(self, wade: Optional[TrafficLightResult],
                 drift: Optional[TrafficLightResult],
                 primary: TrafficLightResult,
                 fishing_modes: List[str]):
        self.wade = wade
        self.drift = drift
        self.primary = primary  # The default/combined status
        self.fishing_modes = fishing_modes


def calculate_traffic_light(
    thresholds: RiverThresholds,
    current_cfs: Optional[float],
    water_temp_f: Optional[float],
    cfs_change_6hr: Optional[float],
    cfs_6hr_ago: Optional[float],
    blown_out_cfs: Optional[float] = None,
    dangerous_wade_cfs: Optional[float] = None,
) -> TrafficLightResult:
    """
    Calculate traffic light status for a river.

    Algorithm:
    1. Temperature override (>68°F = RED, >65°F = YELLOW warning)
    2. Blown-out override (above blown_out_cfs = RED)
    3. Flow-based status (GREEN/YELLOW/RED from thresholds)
    4. Rate of change modifier
    5. Temperature warning on GREEN
    6. Trend context (falling = good for fishing, rising = bad)

    Args:
        thresholds: RiverThresholds configuration
        current_cfs: Current discharge in CFS
        water_temp_f: Water temperature in Fahrenheit
        cfs_change_6hr: Change in CFS over 6 hours
        cfs_6hr_ago: CFS from 6 hours ago (for trend calculation)
        blown_out_cfs: Hard red above this CFS (river-specific)
        dangerous_wade_cfs: Wading danger threshold

    Returns:
        TrafficLightResult with status, reason, trend, and trend_context
    """

    # Calculate trend
    trend = _calculate_trend(cfs_change_6hr, cfs_6hr_ago, current_cfs)
    trend_context = _trend_fishing_context(trend)

    # No data case
    if current_cfs is None:
        return TrafficLightResult(
            status=RED,
            status_reason="No flow data available",
            trend=trend,
            trend_context=trend_context
        )

    # TEMPERATURE OVERRIDES — non-negotiable for trout
    temp_warning = False

    if water_temp_f is not None:
        if water_temp_f >= TEMP_RED_F:
            return TrafficLightResult(
                status=RED,
                status_reason=f"Water too warm for trout ({water_temp_f:.1f}°F ≥ {TEMP_RED_F:.0f}°F stress threshold) — stop fishing",
                trend=trend,
                trend_context=trend_context
            )
        if water_temp_f >= TEMP_YELLOW_F:
            temp_warning = True

    # BLOWN OUT override
    if blown_out_cfs is not None and current_cfs > blown_out_cfs:
        return TrafficLightResult(
            status=RED,
            status_reason=f"Blown out ({current_cfs:,.0f} cfs, above {blown_out_cfs:,.0f} limit)",
            trend=trend,
            trend_context=trend_context
        )

    # FLOW STATUS
    status = RED
    status_reason = ""

    if thresholds.green_floor <= current_cfs <= thresholds.green_ceiling:
        status = GREEN
        status_reason = "Optimal range for fishing"
    elif thresholds.yellow_floor <= current_cfs <= thresholds.yellow_ceiling:
        status = YELLOW
        status_reason = "Fishable but outside optimal range"
    else:
        # RED
        if current_cfs < thresholds.yellow_floor:
            status_reason = f"Flow too low ({current_cfs:,.0f} cfs, optimal {thresholds.green_floor:,.0f}–{thresholds.green_ceiling:,.0f})"
        else:
            status_reason = f"Flow too high ({current_cfs:,.0f} cfs, optimal {thresholds.green_floor:,.0f}–{thresholds.green_ceiling:,.0f})"

    # WADING DANGER warning
    if dangerous_wade_cfs is not None and current_cfs > dangerous_wade_cfs:
        if status == GREEN:
            status = YELLOW
            status_reason = f"Good flow but dangerous wading above {dangerous_wade_cfs:,.0f} cfs — use caution"
        elif status == YELLOW:
            status_reason += f" — wading dangerous above {dangerous_wade_cfs:,.0f} cfs"

    # RATE OF CHANGE — bump to yellow if flows shifting fast
    if cfs_change_6hr is not None and abs(cfs_change_6hr) > thresholds.rapid_change_threshold:
        if status == GREEN:
            direction = "rising" if cfs_change_6hr > 0 else "dropping"
            status = YELLOW
            status_reason = f"Good flow but {direction} rapidly ({cfs_change_6hr:+,.0f} cfs in 6 hrs) — conditions may shift"
        elif status == RED:
            status_reason += f" (changing {cfs_change_6hr:+,.0f} cfs in 6 hrs)"

    # TEMPERATURE WARNING — downgrade green to yellow if warming
    if temp_warning and status == GREEN:
        status = YELLOW
        status_reason = f"Good flow but water warming ({water_temp_f:.1f}°F) — fish early morning"

    return TrafficLightResult(
        status=status,
        status_reason=status_reason,
        trend=trend,
        trend_context=trend_context
    )


def calculate_dual_mode(
    river_config: RiverConfig,
    current_cfs: Optional[float],
    water_temp_f: Optional[float],
    cfs_change_6hr: Optional[float],
    cfs_6hr_ago: Optional[float],
) -> DualModeResult:
    """
    Calculate traffic light for dual-mode rivers (wade + drift boat).

    Returns separate statuses for each fishing mode.
    """
    wade_result = None
    drift_result = None

    # Calculate wade status if applicable
    if river_config.wade_thresholds:
        wade_result = calculate_traffic_light(
            river_config.wade_thresholds,
            current_cfs, water_temp_f,
            cfs_change_6hr, cfs_6hr_ago,
            blown_out_cfs=river_config.blown_out_cfs,
            dangerous_wade_cfs=river_config.dangerous_wade_cfs,
        )

    # Calculate drift status if applicable
    if river_config.drift_thresholds:
        drift_result = calculate_traffic_light(
            river_config.drift_thresholds,
            current_cfs, water_temp_f,
            cfs_change_6hr, cfs_6hr_ago,
            blown_out_cfs=river_config.blown_out_cfs,
        )

    # Primary = default thresholds (usually the more common fishing mode)
    primary = calculate_traffic_light(
        river_config.thresholds,
        current_cfs, water_temp_f,
        cfs_change_6hr, cfs_6hr_ago,
        blown_out_cfs=river_config.blown_out_cfs,
        dangerous_wade_cfs=river_config.dangerous_wade_cfs,
    )

    return DualModeResult(
        wade=wade_result,
        drift=drift_result,
        primary=primary,
        fishing_modes=river_config.fishing_modes,
    )


def _calculate_trend(cfs_change_6hr: Optional[float], cfs_6hr_ago: Optional[float],
                     current_cfs: Optional[float]) -> str:
    """
    Calculate trend: rising, stable, or falling.

    Uses 6-hour change if available, otherwise comparison with historical value.
    """
    if cfs_change_6hr is not None:
        if cfs_change_6hr > 50:
            return RISING
        elif cfs_change_6hr < -50:
            return FALLING
        else:
            return STABLE

    # Fallback: compare current vs 6hr_ago
    if cfs_6hr_ago is not None and current_cfs is not None:
        change = current_cfs - cfs_6hr_ago
        if change > 50:
            return RISING
        elif change < -50:
            return FALLING
        else:
            return STABLE

    return STABLE


def _trend_fishing_context(trend: str) -> str:
    """
    Return fishing-specific context for the trend direction.

    For fly fishing:
    - Falling/clearing = GOOD (water clarity improving, fish settling)
    - Rising/muddying = BAD (water dirtying, fish off the bite)
    - Stable = GOOD (consistent conditions)
    """
    if trend == FALLING:
        return "Falling — clearing, good for fishing"
    elif trend == RISING:
        return "Rising — may be muddying, fish may be off"
    else:
        return "Stable — consistent conditions"


def trend_to_emoji(trend: str) -> str:
    """Convert trend string to emoji for display."""
    if trend == RISING:
        return "↑"
    elif trend == FALLING:
        return "↓"
    else:
        return "→"
