import os
import numpy as np
import pandas as pd
from darts import TimeSeries
from darts.dataprocessing.transformers import MissingValuesFiller
from darts.models import NBEATSModel
from typing import Dict, List


def fill_missing_values(series, fill="auto"):
    """Helper function to interpolate missing values"""
    filler = MissingValuesFiller(fill=fill)
    return filler.transform(series)


def preprocess_input_data(df: pd.DataFrame, pollutant_cols: List[str], site_id: str = "") -> tuple[TimeSeries | list[TimeSeries], TimeSeries | list[TimeSeries]]:
    """
    Preprocess raw input data into TimeSeries format for prediction.

    Args:
        df: Raw dataframe with pollutant measurements
        pollutant_cols: List of pollutant column names (e.g., ['co_ppm', 'no2_ppm', ...])
        site_id: Optional site_id to filter for a specific site

    Returns:
        tuple of (target_series, past_covariates_series)
    """
    # If site_id provided, filter for that site
    if site_id != "":
        df = df[df["site_id"] == site_id].copy()

    # Ensure datetime column exists
    if "datetime_utc" not in df.columns:
        df["datetime_utc"] = pd.to_datetime(df["Date GMT"] + " " + df["Time GMT"])

    # Filter for POC=1 to handle duplicates (same as training)
    if "POC" in df.columns:
        df = df[df["POC"] == 1].copy()

    # Create temporal features (same as training)
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

    # Create target TimeSeries (pollutant values)
    target_series = TimeSeries.from_dataframe(
        df,
        time_col="datetime_utc",
        value_cols=pollutant_cols,
        static_covariates=pd.DataFrame({"Latitude": [df["Latitude"].iloc[0]], "Longitude": [df["Longitude"].iloc[0]]}) if "Latitude" in df.columns else None,
        fill_missing_dates=True,
        freq="h",
        fillna_value=None,
    )

    # Create past covariates TimeSeries
    past_cov = TimeSeries.from_dataframe(
        df, time_col="datetime_utc", value_cols=["hour_sin", "hour_cos", "dow_sin", "dow_cos", "month_sin", "month_cos", "dayofyear"], fill_missing_dates=True, freq="h"
    )

    # Fill missing values (same as training)
    target_series = fill_missing_values(target_series, fill="auto")
    past_cov = fill_missing_values(past_cov, fill="auto")

    return target_series, past_cov
