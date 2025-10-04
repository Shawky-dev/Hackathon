import os
import numpy as np
import pandas as pd
from darts import TimeSeries
from darts.dataprocessing.transformers import MissingValuesFiller
from darts.models import NBEATSModel
from typing import Dict, List
from pathlib import Path

from utils.preprocessing_utils import preprocess_input_data
from ai_api.utils.forecast_utils import get_raw_prediction

BASE = Path(__file__).resolve().parent

# PATHS
GASSES_MODEL_PATH = BASE / "static" / "co_no2_co3_no2_nbeats.pth"
PARTICULATES_MODEL_PATH = BASE / "static" / "pm25frm_pm10mass_pmc_mass_nbeats.pth"

# Load models once at startup
model_gasses = NBEATSModel.load(str(GASSES_MODEL_PATH))
model_particulates = NBEATSModel.load(str(PARTICULATES_MODEL_PATH))

def ai_api():
    pass