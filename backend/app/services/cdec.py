"""
CDEC (California Data Exchange Center) API adapter.
Fetches discharge (sensor 20) and water temperature (sensor 25) data.
"""

import httpx
from typing import Optional, List
from datetime import datetime, timedelta, timezone
import logging
import csv
from io import StringIO

logger = logging.getLogger(__name__)


class CDECData:
    """Container for CDEC data point."""

    def __init__(self, cfs: Optional[float] = None, temp_fahrenheit: Optional[float] = None,
                 timestamp: Optional[datetime] = None):
        self.cfs = cfs
        self.temp_fahrenheit = temp_fahrenheit
        self.timestamp = timestamp


class CDECHistoryPoint:
    """Container for historical data point."""

    def __init__(self, timestamp: datetime, cfs: Optional[float] = None,
                 temp_fahrenheit: Optional[float] = None):
        self.timestamp = timestamp
        self.cfs = cfs
        self.temp_fahrenheit = temp_fahrenheit


async def fetch_cdec_current(station_id: str) -> CDECData:
    """
    Fetch current discharge and temperature for a CDEC station.

    Args:
        station_id: CDEC Station ID (e.g., "HTH" for Hat Creek)

    Returns:
        CDECData with current CFS and temperature (in Fahrenheit)
    """
    try:
        # Fetch both flow (sensor 20) and temperature (sensor 25)
        cfs = await _fetch_sensor(station_id, 20)
        temp_f, temp_timestamp = await _fetch_sensor_with_timestamp(station_id, 25)

        timestamp = temp_timestamp if temp_timestamp else (cfs[1] if isinstance(cfs, tuple) else None)

        return CDECData(
            cfs=cfs[0] if isinstance(cfs, tuple) else cfs,
            temp_fahrenheit=temp_f,
            timestamp=timestamp
        )

    except Exception as e:
        logger.warning(f"Failed to fetch CDEC current data for station {station_id}: {e}")
        return CDECData()


async def fetch_cdec_history(station_id: str, days: int = 7) -> List[CDECHistoryPoint]:
    """
    Fetch historical discharge and temperature data for a CDEC station.

    Args:
        station_id: CDEC Station ID
        days: Number of days of history to fetch

    Returns:
        List of CDECHistoryPoint objects
    """
    try:
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)

        # Format dates as YYYY-MM-DD
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")

        # Fetch flow history (sensor 20, hourly)
        flow_data = await _fetch_sensor_history(station_id, 20, start_str, end_str)
        # Fetch temperature history (sensor 25, hourly)
        temp_data = await _fetch_sensor_history(station_id, 25, start_str, end_str)

        # Merge data by timestamp
        readings_by_time = {}

        for timestamp, cfs_value in flow_data.items():
            if timestamp not in readings_by_time:
                readings_by_time[timestamp] = {}
            readings_by_time[timestamp]["cfs"] = cfs_value

        for timestamp, temp_value in temp_data.items():
            if timestamp not in readings_by_time:
                readings_by_time[timestamp] = {}
            readings_by_time[timestamp]["temp_f"] = temp_value

        # Convert to list of CDECHistoryPoint, sorted by time
        history = [
            CDECHistoryPoint(
                timestamp=ts,
                cfs=data.get("cfs"),
                temp_fahrenheit=data.get("temp_f")
            )
            for ts, data in sorted(readings_by_time.items())
        ]

        return history

    except Exception as e:
        logger.warning(f"Failed to fetch CDEC history for station {station_id}: {e}")
        return []


async def _fetch_sensor(station_id: str, sensor_number: int) -> Optional[float]:
    """
    Fetch latest value for a sensor.

    Args:
        station_id: CDEC Station ID
        sensor_number: Sensor number (20=flow, 25=temperature)

    Returns:
        Latest sensor value or None
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            params = {
                "station_id": station_id,
                "sensor_num": sensor_number,
                "time_interval": "event",
                "data_type": "A",
                "count": 1,
                "format": "csv"
            }
            response = await client.get(
                "https://cdec.water.ca.gov/dynamicapp/req/CSVDataServlet",
                params=params
            )
            response.raise_for_status()

            # Parse CSV
            lines = response.text.strip().split("\n")
            if len(lines) > 2:
                # Skip header lines, get last data row
                reader = csv.reader(lines[2:])
                for row in reader:
                    if row and len(row) >= 4:
                        try:
                            value = float(row[2])
                            return value
                        except (ValueError, IndexError):
                            continue

        return None

    except Exception as e:
        logger.debug(f"Failed to fetch CDEC sensor {sensor_number} for {station_id}: {e}")
        return None


async def _fetch_sensor_with_timestamp(station_id: str, sensor_number: int) -> tuple[Optional[float], Optional[datetime]]:
    """
    Fetch latest value and timestamp for a sensor.

    Returns:
        Tuple of (value, timestamp) or (None, None)
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            params = {
                "station_id": station_id,
                "sensor_num": sensor_number,
                "time_interval": "event",
                "data_type": "A",
                "count": 1,
                "format": "csv"
            }
            response = await client.get(
                "https://cdec.water.ca.gov/dynamicapp/req/CSVDataServlet",
                params=params
            )
            response.raise_for_status()

            lines = response.text.strip().split("\n")
            if len(lines) > 2:
                reader = csv.reader(lines[2:])
                for row in reader:
                    if row and len(row) >= 4:
                        try:
                            value = float(row[2])
                            # Parse timestamp: format is typically "YYYY-MM-DD HH:MM"
                            ts_str = row[1]  # Assuming datetime is in column 1
                            timestamp = datetime.strptime(ts_str, "%Y-%m-%d %H:%M")
                            return (value, timestamp)
                        except (ValueError, IndexError):
                            continue

        return (None, None)

    except Exception as e:
        logger.debug(f"Failed to fetch CDEC sensor with timestamp {sensor_number} for {station_id}: {e}")
        return (None, None)


async def _fetch_sensor_history(station_id: str, sensor_number: int,
                                start_date: str, end_date: str) -> dict[datetime, float]:
    """
    Fetch historical sensor data.

    Args:
        station_id: CDEC Station ID
        sensor_number: Sensor number
        start_date: Start date as YYYY-MM-DD
        end_date: End date as YYYY-MM-DD

    Returns:
        Dict mapping datetime to float values
    """
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            params = {
                "station_id": station_id,
                "sensor_num": sensor_number,
                "start_date": start_date,
                "end_date": end_date,
                "time_interval": "hour",  # Hourly data
                "data_type": "A",
                "format": "csv"
            }
            response = await client.get(
                "https://cdec.water.ca.gov/dynamicapp/req/CSVDataServlet",
                params=params
            )
            response.raise_for_status()

            readings = {}
            lines = response.text.strip().split("\n")

            # Skip header lines (typically first 2-3 lines)
            if len(lines) > 2:
                reader = csv.reader(lines[2:])
                for row in reader:
                    if row and len(row) >= 4:
                        try:
                            value = float(row[2])
                            ts_str = row[1]
                            # Parse timestamp
                            timestamp = datetime.strptime(ts_str, "%Y-%m-%d %H:%M")
                            readings[timestamp] = value
                        except (ValueError, IndexError):
                            continue

            return readings

    except Exception as e:
        logger.debug(f"Failed to fetch CDEC history for {station_id} sensor {sensor_number}: {e}")
        return {}
