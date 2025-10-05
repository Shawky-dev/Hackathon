import pandas as pd
import requests
from typing import Dict, List


def parse_airnow_data_to_dataframe(historical_data: Dict) -> pd.DataFrame:
    """
    Parse AirNow .dat format to DataFrame

    AirNow format (pipe-delimited):
    ValidDate|ValidTime|AQSID|SiteName|GMTOffset|ParameterName|ReportingUnits|Value|DataSource
    Example:
    01/01/2024|13:00|01-003-0010|Birmingham|-6|OZONE|PPB|42|AirNow
    """
    rows = []

    for result in historical_data.get("results", []):
        if "data" not in result:
            continue

        for line in result["data"]:
            if not line.strip():
                continue

            parts = line.split("|")
            if len(parts) < 9:
                print(f"Skipping malformed line: {line}")
                continue

            valid_date = parts[0]
            valid_time = parts[1]
            aqsid = parts[2]
            site_name = parts[3]
            parameter = parts[5]
            value = parts[7]

            # Try to parse the value as float
            try:
                value_float = float(value)
            except ValueError:
                print(f"Skipping non-numeric value: {value}")
                continue

            # Find or create row for this timestamp
            row_key = (aqsid, site_name, valid_date, valid_time)

            # Create base row if not exists
            existing_row = next((r for r in rows if r["AQSID"] == aqsid and r["ValidDate"] == valid_date and r["ValidTime"] == valid_time), None)

            if existing_row is None:
                existing_row = {
                    "AQSID": aqsid,
                    "SiteName": site_name,
                    "Latitude": 0.0,  # Not in .dat file
                    "Longitude": 0.0,  # Not in .dat file
                    "ValidDate": valid_date,
                    "ValidTime": valid_time,
                    "OZONE_Measured": 0.0,
                    "NO2_Measured": 0.0,
                    "CO": 0.0,
                    "SO2": 0.0,
                    "PM25_Measured": 0.0,
                    "PM10_Measured": 0.0,
                }
                rows.append(existing_row)

            # Map parameter names to DataFrame columns
            param_mapping = {
                "OZONE": "OZONE_Measured",
                "NO2": "NO2_Measured",
                "CO": "CO",
                "SO2": "SO2",
                "PM2.5": "PM25_Measured",
                "PM10": "PM10_Measured",
            }

            if parameter in param_mapping:
                existing_row[param_mapping[parameter]] = value_float

    return pd.DataFrame(rows)


def test_with_real_data():
    """Test parser with real AirNow data"""
    print("Fetching real AirNow data...")

    # Fetch from your data API
    response = requests.get("http://127.0.0.1:8000/data/past-data?hours=3")

    if response.status_code != 200:
        print(f"Failed to fetch data: {response.status_code}")
        return

    historical_data = response.json()

    print(f"\nRaw data structure:")
    print(f"- requested_hours: {historical_data.get('requested_hours')}")
    print(f"- results count: {len(historical_data.get('results', []))}")

    # Show sample raw lines
    print("\nSample raw lines:")
    for i, result in enumerate(historical_data.get("results", [])[:2]):
        if "data" in result:
            print(f"\nResult {i}:")
            for line in result["data"][:3]:
                print(f"  {line}")

    # Parse to DataFrame
    print("\n" + "=" * 50)
    print("Parsing to DataFrame...")
    df = parse_airnow_data_to_dataframe(historical_data)

    print(f"\nDataFrame shape: {df.shape}")
    print(f"\nDataFrame columns: {df.columns.tolist()}")
    print(f"\nFirst few rows:")
    print(df.head())

    print(f"\nData types:")
    print(df.dtypes)

    print(f"\nNon-zero values per column:")
    for col in df.columns:
        if col not in ["AQSID", "SiteName", "ValidDate", "ValidTime"]:
            non_zero = (df[col] != 0).sum()
            print(f"  {col}: {non_zero}/{len(df)}")

    return df


if __name__ == "__main__":
    df = test_with_real_data()
