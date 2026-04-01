"""
USGS Instantaneous Values API adapter.
Fetches discharge (00060) and water temperature (00010) data.
"""

import httpx
from typing import Optional, Dict, List, Tuple
from datetime import datetime, timedelta, timezone
import logging

logger = logging.getLogger(__name__)


class USGSData:
    """Container for USGS data point."""

    def __init__(self, cfs: Optional[float] = None, temp_fahrenheit: Optional[float] = None,
                 timestamp: Optional[datetime] = None):
        self.cfs = cfs
        self.temp_fahrenheit = temp_fahrenheit
        self.timestamp = timestamp


class USGSHistoryPoint:
    """Container for historical data point."""

    def __init__(self, timestamp: datetime, cfs: Optional[float] = None,
                 temp_fahrenheit: Optional[float] = None):
        self.timestamp = timestamp
        self.cfs = cfs
        self.temp_fahrenheit = temp_fahrenheit


async def fetch_usgs_current(site_id: str) -> USGSData:
    """
    Fetch current discharge and temperature for a USGS site.

    Args:
        site_id: USGS Site ID (e.g., "11370500")

    Returns:
        USGSData with current CFS and temperature (in Fahrenheit)
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            params = {
                "sites": site_id,
                "parameterCd": "00060,00010",  # discharge, temperature
                "format": "json"
            }
            response = await client.get(
                "https://waterservices.usgs.gov/nwis/iv/",
                params=params
            )
            response.raise_for_status()
            data = response.json()

            cfs = None
            temp_f = None
            timestamp = None

            # Parse the nested JSON structure
            if "value" in data and "timeSeries" in data["value"]:
                for time_series in data["value"]["timeSeries"]:
                    param_code = time_series.get("variable", {}).get("variableCode", [{}])[0].get("value")

                    if time_series.get("values"):
                        values_list = time_series["values"][0].get("value", [])
                        if values_list:
                            latest = values_list[-1]
                            raw_val = latest.get("value", "")
                            # Skip ice-affected or missing values
                            try:
                                value = float(raw_val)
                            except (ValueError, TypeError):
                                continue
                            if value < 0:
                                continue

                            ts_str = latest.get("dateTime")
                            if ts_str:
                                timestamp = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))

                            # Identify parameter
                            if param_code == "00060":  # Discharge in CFS
                                cfs = value
                            elif param_code == "00010":  # Temperature in Celsius
                                temp_f = celsius_to_fahrenheit(value)

            return USGSData(cfs=cfs, temp_fahrenheit=temp_f, timestamp=timestamp)

    except Exception as e:
        logger.warning(f"Failed to fetch USGS data for site {site_id}: {e}")
        return USGSData()


async def fetch_usgs_history(site_id: str, days: int = 7) -> List[USGSHistoryPoint]:
    """
    Fetch historical discharge and temperature data for a USGS site.

    Args:
        site_id: USGS Site ID
        days: Number of days of history to fetch

    Returns:
        List of USGSHistoryPoint objects
    """
    try:
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)

        async with httpx.AsyncClient(timeout=15.0) as client:
            # Format dates as ISO 8601 without timezone info (USGS expects naive format)
            params = {
                "sites": site_id,
                "parameterCd": "00060,00010",
                "startDT": start_date.replace(tzinfo=None).isoformat(),
                "endDT": end_date.replace(tzinfo=None).isoformat(),
                "format": "json"
            }
            response = await client.get(
                "https://waterservices.usgs.gov/nwis/iv/",
                params=params
            )
            response.raise_for_status()
            data = response.json()

            # Collect all readings by timestamp
            readings_by_time: Dict[datetime, Dict] = {}

            if "value" in data and "timeSeries" in data["value"]:
                for time_series in data["value"]["timeSeries"]:
                    param_code = time_series.get("variable", {}).get("variableCode", [{}])[0].get("value")

                    if time_series.get("values"):
                        values_list = time_series["values"][0].get("value", [])

                        for value_obj in values_list:
                            ts_str = value_obj.get("dateTime")
                            raw_val = value_obj.get("value", "")
                            try:
                                value = float(raw_val)
                            except (ValueError, TypeError):
                                continue
                            if value < 0:
                                continue

                            if ts_str:
                                timestamp = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                                if timestamp not in readings_by_time:
                                    readings_by_time[timestamp] = {}

                                if param_code == "00060":
                                    readings_by_time[timestamp]["cfs"] = value
                                elif param_code == "00010":
                                    readings_by_time[timestamp]["temp_f"] = celsius_to_fahrenheit(value)

            # Convert to list of USGSHistoryPoint, sorted by time
            history = [
                USGSHistoryPoint(
                    timestamp=ts,
                    cfs=data.get("cfs"),
                    temp_fahrenheit=data.get("temp_f")
                )
                for ts, data in sorted(readings_by_time.items())
            ]

            return history

    except Exception as e:
        logger.warning(f"Failed to fetch USGS history for site {site_id}: {e}")
        return []


def celsius_to_fahrenheit(celsius: float) -> float:
    """Convert Celsius to Fahrenheit."""
    return (celsius * 9/5) + 32


def fahrenheit_to_celsius(fahrenheit: float) -> float:
    """Convert Fahrenheit to Celsius."""
    return (fahrenheit - 32) * 5/9
