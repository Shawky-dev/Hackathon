from fastapi import APIRouter, Query
from datetime import datetime, timedelta
import requests, pytz
import csv
from io import StringIO
from typing import List, Dict, Optional, Tuple
import math
from concurrent.futures import ThreadPoolExecutor, as_completed

router = APIRouter()
BASE_URL = "https://s3-us-west-1.amazonaws.com/files.airnowtech.org"


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two coordinates in kilometers using Haversine formula"""
    R = 6371
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def parse_airnow_csv_line(line: str) -> Dict:
    """Parse a single CSV line from AirNow data"""
    reader = csv.reader(StringIO(line))
    row = next(reader)
    if len(row) < 33:
        return None
    try:
        return {
            "AQSID": row[0],
            "SiteName": row[1],
            "Latitude": float(row[4]) if row[4] else 0.0,
            "Longitude": float(row[5]) if row[5] else 0.0,
            "ValidDate": row[10],
            "ValidTime": row[11],
            "OZONE_Measured": float(row[24]) if row[24] else 0.0,
            "NO2_Measured": float(row[26]) if row[26] else 0.0,
            "CO": float(row[28]) if row[28] else 0.0,
            "SO2": float(row[30]) if row[30] else 0.0,
            "PM25_Measured": float(row[22]) if row[22] else 0.0,
            "PM10_Measured": float(row[32]) if row[32] else 0.0,
        }
    except (ValueError, IndexError):
        return None


def fetch_single_hour(target_time: datetime, hour_index: int) -> Tuple[int, List[Dict]]:
    """
    Fetch and parse data for a single hour.
    Returns tuple of (hour_index, list_of_records) to maintain order.
    """
    year = target_time.strftime("%Y")
    date = target_time.strftime("%Y%m%d")
    hour = target_time.strftime("%H")

    file_url = f"{BASE_URL}/airnow/{year}/{date}/HourlyAQObs_{date}{hour}.dat"
    print(f"Fetching URL: {file_url}")

    records = []
    try:
        response = requests.get(file_url, timeout=10)
        if response.status_code == 200:
            lines = response.text.splitlines()

            for line in lines[1:]:  # Skip header
                if not line.strip():
                    continue

                parsed = parse_airnow_csv_line(line)
                if parsed:
                    records.append(parsed)

            print(f"✓ Fetched {len(records)} records from {file_url}")
        else:
            print(f"✗ Failed to fetch {file_url}: status {response.status_code}")
    except Exception as e:
        print(f"✗ Error fetching {file_url}: {e}")

    return (hour_index, records)


@router.get("/past-data")
def get_realtime_data(
    hours: int = Query(168, description="number of past hours to fetch", gt=0, le=168),
    lat: Optional[float] = Query(None, description="Latitude to filter by nearest station"),
    long: Optional[float] = Query(None, description="Longitude to filter by nearest station"),
    max_distance_km: float = Query(150, description="Maximum distance in km to consider a station"),
    max_workers: int = Query(56, description="Number of parallel workers", gt=1, le=70),
):
    now = datetime.now(pytz.timezone("US/Eastern")) - timedelta(hours=3)

    # Step 1: Fetch all hours in parallel
    print(f"Starting parallel fetch of {hours} hours with {max_workers} workers...")

    # Create list of target times
    fetch_tasks = []
    for i in range(hours):
        target_time = now - timedelta(hours=i)
        fetch_tasks.append((target_time, i))

    # Fetch in parallel using ThreadPoolExecutor
    hour_results = {}  # Dictionary to store results by hour_index

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_hour = {executor.submit(fetch_single_hour, target_time, hour_idx): hour_idx for target_time, hour_idx in fetch_tasks}

        # Collect results as they complete
        for future in as_completed(future_to_hour):
            hour_idx, records = future.result()
            hour_results[hour_idx] = records

    # Step 2: Concatenate results in correct chronological order
    all_records = []
    for i in range(hours):
        if i in hour_results:
            all_records.extend(hour_results[i])

    print(f"Total records fetched: {len(all_records)}")

    # Step 3: If lat/long provided, find nearest station and filter
    if lat is not None and long is not None:
        stations = {}
        for record in all_records:
            aqsid = record["AQSID"]
            if aqsid not in stations:
                stations[aqsid] = {"lat": record["Latitude"], "lon": record["Longitude"], "name": record["SiteName"]}

        nearest_aqsid = None
        min_distance = float("inf")

        for aqsid, station_info in stations.items():
            if station_info["lat"] == 0.0 and station_info["lon"] == 0.0:
                continue

            distance = calculate_distance(lat, long, station_info["lat"], station_info["lon"])

            if distance < min_distance and distance <= max_distance_km:
                min_distance = distance
                nearest_aqsid = aqsid

        if nearest_aqsid:
            filtered_records = [r for r in all_records if r["AQSID"] == nearest_aqsid]

            return {
                "requested_hours": hours,
                "total_records": len(filtered_records),
                "filtered_by": {
                    "user_lat": lat,
                    "user_long": long,
                    "nearest_station": {
                        "AQSID": nearest_aqsid,
                        "name": stations[nearest_aqsid]["name"],
                        "lat": stations[nearest_aqsid]["lat"],
                        "lon": stations[nearest_aqsid]["lon"],
                        "distance_km": round(min_distance, 2),
                    },
                },
                "data": filtered_records,
            }
        else:
            return {"requested_hours": hours, "total_records": 0, "error": f"No stations found within {max_distance_km}km of ({lat}, {long})", "data": []}

    return {"requested_hours": hours, "total_records": len(all_records), "data": all_records}
