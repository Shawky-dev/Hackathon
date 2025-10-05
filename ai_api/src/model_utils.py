import os
import numpy as np
import pandas as pd
from darts import TimeSeries
from darts.dataprocessing.transformers import MissingValuesFiller
from darts.models import NBEATSModel
from typing import Dict, List
from pathlib import Path

# PATHS
BASE = Path(__file__).resolve().parent
# PATHS
GASSES_MODEL_PATH = "../static/co_no2_co3_no2_nbeats.pth"
PARTICULATES_MODEL_PATH = "../static/pm25frm_pm10mass_pmc_mass_nbeats.pth"

# Load models once at module level (not inside function)
_model_gasses = None
_model_particulates = None


def _get_models():
    """Lazy load models on first use"""
    global _model_gasses, _model_particulates
    if _model_gasses is None:
        _model_gasses = NBEATSModel.load(GASSES_MODEL_PATH)
    if _model_particulates is None:
        _model_particulates = NBEATSModel.load(PARTICULATES_MODEL_PATH)
    return _model_gasses, _model_particulates


def _fill_missing_values(series, fill="auto"):
    """Helper function to interpolate missing values"""
    filler = MissingValuesFiller(fill=fill)
    return filler.transform(series)


def _create_timeseries_from_df(df: pd.DataFrame, pollutant_cols: List[str], site_id: str) -> tuple[TimeSeries, TimeSeries]:
    """
    Convert preprocessed DataFrame to TimeSeries objects.

    Returns:
        (target_series, past_covariates)
    """
    # Filter for specific site
    df = df[df["site_id"] == site_id].copy()

    # Create temporal features
    df["hour"] = df["datetime_utc"].dt.hour
    df["dow"] = df["datetime_utc"].dt.dayofweek
    df["month"] = df["datetime_utc"].dt.month

    # Cyclic encodings
    df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24)
    df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24)
    df["dow_sin"] = np.sin(2 * np.pi * df["dow"] / 7)
    df["dow_cos"] = np.cos(2 * np.pi * df["dow"] / 7)
    df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12)
    df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12)
    df["dayofyear"] = df["datetime_utc"].dt.dayofyear

    # Sort by time
    df = df.sort_values("datetime_utc").reset_index(drop=True)

    # Create target TimeSeries
    target_series = TimeSeries.from_dataframe(
        df,
        time_col="datetime_utc",
        value_cols=pollutant_cols,
        static_covariates=pd.DataFrame({"Latitude": [df["Latitude"].iloc[0]], "Longitude": [df["Longitude"].iloc[0]]}),
        fill_missing_dates=True,
        freq="h",
        fillna_value=None,
    )

    # Create past covariates
    past_cov = TimeSeries.from_dataframe(
        df, time_col="datetime_utc", value_cols=["hour_sin", "hour_cos", "dow_sin", "dow_cos", "month_sin", "month_cos", "dayofyear"], fill_missing_dates=True, freq="h"
    )

    # Fill missing values
    target_series = _fill_missing_values(target_series, fill="auto")
    past_cov = _fill_missing_values(past_cov, fill="auto")

    return target_series, past_cov


def _preprocess_raw_data(raw_data: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocess raw data into standardized format.
    Handles both training format and API format.
    """
    df = raw_data.copy()

    # If API format, convert to training format
    if "AQSID" in df.columns:
        # Create datetime_utc from ValidDate + ValidTime
        df["datetime_utc"] = pd.to_datetime(df["ValidDate"] + " " + df["ValidTime"])

        # Rename AQSID to site_id
        df["site_id"] = df["AQSID"]

        # Map pollutant measurements WITH UNIT CONVERSION (PPB -> PPM)
        df["o3_ppm"] = df["OZONE_Measured"] / 1000.0
        df["no2_ppm"] = df["NO2_Measured"] / 1000.0
        df["co_ppm"] = df["CO"] / 1000.0
        df["so2_ppm"] = df["SO2"] / 1000.0
        df["pm25frm_ppm"] = df["PM25_Measured"]
        df["pm10mass_ppm"] = df["PM10_Measured"]
        df["pmc_mass_ppm"] = df["pm10mass_ppm"] - df["pm25frm_ppm"]

        # Keep spatial features
        # Latitude and Longitude already exist

    # Ensure datetime_utc exists
    if "datetime_utc" not in df.columns:
        if "Date GMT" in df.columns and "Time GMT" in df.columns:
            df["datetime_utc"] = pd.to_datetime(df["Date GMT"] + " " + df["Time GMT"])

    # Handle potential duplicates
    df = df.groupby(["site_id", "datetime_utc"], as_index=False).mean(numeric_only=True)

    # Ensure required columns exist
    required_cols = ["site_id", "datetime_utc", "Latitude", "Longitude", "co_ppm", "no2_ppm", "o3_ppm", "so2_ppm", "pm25frm_ppm", "pm10mass_ppm", "pmc_mass_ppm"]

    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    return df


def get_raw_prediction(raw_data: pd.DataFrame, site_id: str = "", forecast_horizon: int = 12) -> Dict[str, np.ndarray]:
    """
    Real-time forecasting API for air quality pollutants.

    Args:
        raw_data: DataFrame with raw pollutant measurements. Must contain:
                 - datetime_utc (or Date GMT + Time GMT, or ValidDate + ValidTime)
                 - Pollutant measurements: co_ppm, no2_ppm, o3_ppm, so2_ppm,
                   pm25frm_ppm, pm10mass_ppm, pmc_mass_ppm
                 - Latitude, Longitude
                 - site_id (or AQSID)
        site_id: Site ID to forecast for (required)
        forecast_horizon: Number of hours to forecast (default: 12, max: 12)

    Returns:
        Dictionary with forecasted values for each pollutant:
        {
            'co': np.array of shape (forecast_horizon,),
            'no2': np.array of shape (forecast_horizon,),
            'o3': np.array of shape (forecast_horizon,),
            'so2': np.array of shape (forecast_horizon,),
            'pm25frm': np.array of shape (forecast_horizon,),
            'pm10mass': np.array of shape (forecast_horizon,),
        }
    """
    # Validate inputs
    if not site_id:
        raise ValueError("site_id is required")

    if forecast_horizon > 12:
        raise ValueError(f"forecast_horizon must be <= 12, got {forecast_horizon}")

    # Load models
    model_gasses, model_particulates = _get_models()

    # Step 1: Preprocess raw data
    preprocessed_df = _preprocess_raw_data(raw_data)

    # Step 2: Create TimeSeries for gases
    gas_pollutants = ["co_ppm", "no2_ppm", "o3_ppm", "so2_ppm"]
    gas_series, gas_past_cov = _create_timeseries_from_df(preprocessed_df, gas_pollutants, site_id)

    # Step 3: Create TimeSeries for particulates (including pmc_mass for model input)
    particulate_pollutants = ["pm25frm_ppm", "pm10mass_ppm", "pmc_mass_ppm"]
    particulate_series, particulate_past_cov = _create_timeseries_from_df(preprocessed_df, particulate_pollutants, site_id)

    # Step 4: Generate predictions
    gas_predictions = model_gasses.predict(n=forecast_horizon, series=gas_series, past_covariates=gas_past_cov)

    particulate_predictions = model_particulates.predict(n=forecast_horizon, series=particulate_series, past_covariates=particulate_past_cov)

    # Step 5: Extract predictions as numpy arrays
    forecasts = {
        "co": gas_predictions["co_ppm"].values().flatten(),
        "no2": gas_predictions["no2_ppm"].values().flatten(),
        "o3": gas_predictions["o3_ppm"].values().flatten(),
        "so2": gas_predictions["so2_ppm"].values().flatten(),
        "pm25frm": particulate_predictions["pm25frm_ppm"].values().flatten(),
        "pm10mass": particulate_predictions["pm10mass_ppm"].values().flatten(),
        # Note: pmc_mass is NOT returned (only used during training)
    }

    return forecasts


# Example usage
if __name__ == "__main__":
    # Sample API data
    sample_api_data = pd.DataFrame(
        {
            "AQSID": ["01-003-0010"] * 200,
            "SiteName": ["Birmingham"] * 200,
            "Latitude": [33.5] * 200,
            "Longitude": [-86.8] * 200,
            "ValidDate": pd.date_range("2024-01-01", periods=200, freq="h").strftime("%Y-%m-%d").tolist(),
            "ValidTime": pd.date_range("2024-01-01", periods=200, freq="h").strftime("%H:%M").tolist(),
            "OZONE_Measured": np.random.rand(200) * 50,  # PPB
            "NO2_Measured": np.random.rand(200) * 30,  # PPB
            "CO": np.random.rand(200) * 500,  # PPB
            "SO2": np.random.rand(200) * 10,  # PPB
            "PM25_Measured": np.random.rand(200) * 20,  # µg/m³
            "PM10_Measured": np.random.rand(200) * 30,  # µg/m³
        }
    )

    # Get predictions
    forecasts = get_raw_prediction(raw_data=sample_api_data, site_id="01-003-0010", forecast_horizon=12)

    # Print results
    print("12-hour forecasts:")
    for pollutant, values in forecasts.items():
        print(f"{pollutant}: {values[:3]}... (shape: {values.shape})")
