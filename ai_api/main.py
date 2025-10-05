from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any
from contextlib import asynccontextmanager
import pandas as pd
import numpy as np

# Import your actual model and AQI calculator
from src.model_utils import get_raw_prediction
from src.math_utils import calculate_aqi_for_predictions

# Global variable to track if models are loaded
_models_loaded = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager to pre-load ML models on startup.
    This ensures models are loaded once when the service starts,
    not on the first prediction request.
    """
    global _models_loaded
    print("🚀 Starting AI Prediction Service...")
    print("📦 Pre-loading NBEATS models...")

    # Trigger model loading by calling the internal function
    try:
        from src.model_utils import _get_models

        _get_models()
        _models_loaded = True
        print("✅ Models loaded successfully!")
    except Exception as e:
        print(f"⚠️  Warning: Could not pre-load models: {e}")
        print("Models will be loaded on first prediction request.")

    yield

    print("🛑 Shutting down AI Prediction Service...")


app = FastAPI(title="AI Prediction Service", lifespan=lifespan)


class HistoricalDataPoint(BaseModel):
    AQSID: str
    SiteName: str
    Latitude: float
    Longitude: float
    ValidDate: str
    ValidTime: str
    OZONE_Measured: float
    NO2_Measured: float
    CO: float
    SO2: float
    PM25_Measured: float
    PM10_Measured: float


class PredictionRequest(BaseModel):
    task_id: str
    lat: float
    long: float
    historical_data: Dict[str, Any]  # 168 hours of historical data
    prediction_hours: int  # How many future hours to predict


class PredictionResponse(BaseModel):
    task_id: str
    forecasts: Dict[str, List[float]]
    aqi: List[int]  # Added AQI array
    metadata: Dict[str, Any]


def parse_airnow_data_to_dataframe(historical_data: Dict) -> pd.DataFrame:
    """
    Convert structured AirNow data to DataFrame.

    The data fetch API returns:
    {
        "requested_hours": 168,
        "total_records": N,
        "filtered_by": {...},
        "data": [
            {
                "AQSID": "...",
                "SiteName": "...",
                "ValidDate": "...",
                "ValidTime": "...",
                "OZONE_Measured": ...,
                "NO2_Measured": ...,
                "CO": ...,
                "SO2": ...,
                "PM25_Measured": ...,
                "PM10_Measured": ...
            },
            ...
        ]
    }
    """
    records = historical_data.get("data", [])

    if not records:
        raise ValueError("No data records found in historical_data")

    # Data is already in the correct format - just convert to DataFrame
    df = pd.DataFrame(records)

    # Ensure correct data types for numeric columns
    numeric_cols = ["Latitude", "Longitude", "OZONE_Measured", "NO2_Measured", "CO", "SO2", "PM25_Measured", "PM10_Measured"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    print(f"📊 Parsed DataFrame: {df.shape[0]} rows, {df.shape[1]} columns")
    print(f"📍 Columns: {df.columns.tolist()}")

    print(f"Length of dataframe: {len(df)}")
    return df


def run_prediction_model(df: pd.DataFrame, num_predictions: int = 24) -> Dict[str, np.ndarray]:
    """
    Run the actual NBEATS model for air quality predictions.

    Args:
        df: DataFrame with columns AQSID, SiteName, Latitude, Longitude,
            ValidDate, ValidTime, OZONE_Measured, NO2_Measured, CO, SO2,
            PM25_Measured, PM10_Measured
        num_predictions: Number of hours to forecast

    Returns:
        Dictionary with forecasted values for each pollutant:
        {
            "co": np.ndarray,
            "no2": np.ndarray,
            "o3": np.ndarray,
            "so2": np.ndarray,
            "pm25frm": np.ndarray,
            "pm10mass": np.ndarray
        }
    """
    # Extract the site_id (AQSID) from the DataFrame
    # Since data is filtered by nearest station, all rows should have same AQSID
    if df.empty:
        raise ValueError("DataFrame is empty - no data to predict from")

    site_id = df["AQSID"].iloc[0]

    if not site_id:
        raise ValueError("AQSID (site_id) is empty in the data")

    print(f"🤖 Running NBEATS model for site: {site_id}")
    print(f"📈 Forecasting {num_predictions} hours into the future")
    print(f"📊 Using {len(df)} historical data points")

    # Call your actual model
    forecasts = get_raw_prediction(raw_data=df, site_id=site_id, forecast_horizon=num_predictions)

    print(f"✅ Predictions generated successfully!")
    for pollutant, values in forecasts.items():
        print(f"   {pollutant}: {len(values)} predictions")

    return forecasts


@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):
    """
    Receives historical air quality data and returns predictions with AQI.

    Request body:
    {
        "task_id": "unique-task-id",
        "lat": 37.7749,
        "long": -122.4194,
        "prediction_hours": 12,
        "historical_data": {
            "requested_hours": 168,
            "total_records": 168,
            "data": [...]
        }
    }

    Response:
    {
        "task_id": "unique-task-id",
        "forecasts": {
            "co": [val1, val2, ...],
            "no2": [val1, val2, ...],
            "o3": [val1, val2, ...],
            "so2": [val1, val2, ...],
            "pm25frm": [val1, val2, ...],
            "pm10mass": [val1, val2, ...]
        },
        "aqi": [45, 52, 48, ...],
        "metadata": {
            "lat": 37.7749,
            "long": -122.4194,
            "prediction_hours": 12,
            "num_predictions": 12,
            "max_aqi": 52,
            "min_aqi": 45
        }
    }
    """
    try:
        print(f"\n{'='*60}")
        print(f"📥 Received prediction request: {request.task_id}")
        print(f"📍 Location: ({request.lat}, {request.long})")
        print(f"⏰ Prediction hours: {request.prediction_hours}")

        # Convert historical data to DataFrame
        df = parse_airnow_data_to_dataframe(request.historical_data)

        # Run prediction model
        forecasts = run_prediction_model(df, request.prediction_hours)

        # Convert numpy arrays to lists for JSON serialization
        forecasts_serializable = {key: value.tolist() for key, value in forecasts.items()}

        # Calculate AQI from predictions using the black-box function
        print(f"🧮 Calculating AQI values...")
        aqi_values = calculate_aqi_for_predictions(forecasts)
        print(f"✅ AQI calculated: {len(aqi_values)} values")

        # Calculate min/max AQI for metadata
        max_aqi = int(max(aqi_values)) if aqi_values else 0
        min_aqi = int(min(aqi_values)) if aqi_values else 0

        print(f"✅ Request {request.task_id} completed successfully!")
        print(f"📊 AQI range: {min_aqi} - {max_aqi}")
        print(f"{'='*60}\n")

        return PredictionResponse(
            task_id=request.task_id,
            forecasts=forecasts_serializable,
            aqi=aqi_values,  # Include AQI array
            metadata={
                "lat": request.lat,
                "long": request.long,
                "prediction_hours": request.prediction_hours,
                "num_predictions": len(forecasts_serializable["co"]),
                "max_aqi": max_aqi,
                "min_aqi": min_aqi,
            },
        )

    except ValueError as e:
        # Handle validation errors (empty data, missing site_id, etc.)
        print(f"❌ Validation error for {request.task_id}: {e}")
        return PredictionResponse(task_id=request.task_id, forecasts={}, aqi=[], metadata={"error": f"Validation error: {str(e)}"})

    except Exception as e:
        # Handle any other errors
        print(f"❌ Error processing {request.task_id}: {e}")
        import traceback

        traceback.print_exc()
        return PredictionResponse(task_id=request.task_id, forecasts={}, aqi=[], metadata={"error": str(e)})


@app.get("/health")
def health_check():
    """Health check endpoint to verify service is running."""
    return {"status": "healthy", "service": "AI Prediction Service", "models_loaded": _models_loaded}


@app.get("/")
def root():
    """Root endpoint with service information."""
    return {"service": "AI Prediction Service", "version": "1.0.0", "endpoints": {"predict": "POST /predict", "health": "GET /health", "docs": "GET /docs"}}
