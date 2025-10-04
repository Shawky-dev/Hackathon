import os
import numpy as np
import pandas as pd
from darts import TimeSeries
from darts.dataprocessing.transformers import MissingValuesFiller
from darts.models import NBEATSModel
from typing import Dict, List
from pathlib import Path

# from utils.preprocessing_utils import preprocess_input_data

# todo where to put this?
from preprocessing_utils import preprocess_input_data

BASE = Path(__file__).resolve().parent

# PATHS
GASSES_MODEL_PATH = BASE / "../static" / "co_no2_co3_no2_nbeats.pth"
PARTICULATES_MODEL_PATH = BASE / "../static" / "pm25frm_pm10mass_pmc_mass_nbeats.pth"

# Load models once at startup
model_gasses = NBEATSModel.load(str(GASSES_MODEL_PATH))
model_particulates = NBEATSModel.load(str(PARTICULATES_MODEL_PATH))
# ----


def get_raw_prediction(raw_data: pd.DataFrame, site_id: str = "", forecast_horizon: int = 12) -> Dict[str, np.ndarray]:
    """
    Real-time forecasting API for air quality pollutants.

    Args:
        raw_data: DataFrame with raw pollutant measurements. Must contain:
                 - datetime_utc (or Date GMT + Time GMT)
                 - Pollutant measurements: co_ppm, no2_ppm, o3_ppm, so2_ppm,
                   pm25frm_ppm, pm10mass_ppm, pmc_mass_ppm
                 - Latitude, Longitude
                 - site_id (optional, for filtering)
                 - POC (optional, for filtering duplicates)
        site_id: Optional site_id to forecast for a specific monitoring station
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
            # Note: pmc_mass is NOT returned (only used during training)
        }
    """
    # Validate forecast horizon
    if forecast_horizon > 12:
        raise ValueError("forecast_horizon cannot exceed 12 (model's output_chunk_length)")

    gas_pollutants = ["co_ppm", "no2_ppm", "o3_ppm", "so2_ppm"]

    # Check if all gas pollutants exist in raw_data
    missing_gases = [p for p in gas_pollutants if p not in raw_data.columns]
    if missing_gases:
        raise ValueError(f"Missing gas pollutant columns: {missing_gases}")

    gas_series, gas_past_cov = preprocess_input_data(raw_data.copy(), pollutant_cols=gas_pollutants, site_id=site_id)

    particulate_pollutants = ["pm25frm_ppm", "pm10mass_ppm", "pmc_mass_ppm"]

    # Check if all particulate pollutants exist in raw_data
    missing_particulates = [p for p in particulate_pollutants if p not in raw_data.columns]
    if missing_particulates:
        raise ValueError(f"Missing particulate columns: {missing_particulates}")

    particulate_series, particulate_past_cov = preprocess_input_data(raw_data.copy(), pollutant_cols=particulate_pollutants, site_id=site_id)

    # ============================================
    # 3. RUN PREDICTIONS
    # ============================================
    gas_predictions = model_gasses.predict(n=forecast_horizon, series=gas_series, past_covariates=gas_past_cov)
    particulate_predictions = model_particulates.predict(n=forecast_horizon, series=particulate_series, past_covariates=particulate_past_cov)

    # ============================================
    # 4. EXTRACT PREDICTIONS
    # ============================================
    # Convert TimeSeries predictions to numpy arrays
    results = {
        "co": gas_predictions["co_ppm"].values().flatten(),
        "no2": gas_predictions["no2_ppm"].values().flatten(),
        "o3": gas_predictions["o3_ppm"].values().flatten(),
        "so2": gas_predictions["so2_ppm"].values().flatten(),
        "pm25frm": particulate_predictions["pm25frm_ppm"].values().flatten(),
        "pm10mass": particulate_predictions["pm10mass_ppm"].values().flatten(),
        # Note: pmc_mass is NOT included in results (only used during training)
    }

    return results


if __name__ == "__main__":
    print("yo")
    example_raw_data = pd.DataFrame(
        {
            "datetime_utc": pd.date_range("2024-01-01", periods=200, freq="h"),
            "site_id": ["01_003_0010"] * 200,
            "co_ppm": np.random.rand(200) * 0.5,
            "no2_ppm": np.random.rand(200) * 0.03,
            "o3_ppm": np.random.rand(200) * 0.05,
            "so2_ppm": np.random.rand(200) * 0.01,
            "pm25frm_ppm": np.random.rand(200) * 20,
            "pm10mass_ppm": np.random.rand(200) * 30,
            "pmc_mass_ppm": np.random.rand(200) * 10,
            "Latitude": [33.5] * 200,
            "Longitude": [-86.8] * 200,
            "POC": [1] * 200,
        }
    )

    # Get 12-hour forecast
    forecasts = get_raw_prediction(raw_data=example_raw_data, site_id="01_003_0010", forecast_horizon=12)

    print("12-hour forecasts:")
    for pollutant, values in forecasts.items():
        print(f"{pollutant}: {values}")
