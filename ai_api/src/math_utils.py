import numpy as np


def calculate_aqi(co_ppm: float, no2_ppm: float, o3_ppm: float, so2_ppm: float, pm25_ugm3: float, pm10_ugm3: float) -> int:
    """
    Calculate Air Quality Index (AQI) using EPA breakpoints.

    Args:
        co_ppm: Carbon monoxide in parts per million
        no2_ppm: Nitrogen dioxide in parts per million
        o3_ppm: Ozone in parts per million
        so2_ppm: Sulfur dioxide in parts per million
        pm25_ugm3: PM2.5 in micrograms per cubic meter
        pm10_ugm3: PM10 in micrograms per cubic meter

    Returns:
        AQI value (0-500+)
    """

    def calculate_sub_aqi(concentration, breakpoints):
        """Calculate sub-AQI for a single pollutant using EPA formula"""
        for i in range(len(breakpoints) - 1):
            c_low, c_high, aqi_low, aqi_high = breakpoints[i]
            if c_low <= concentration <= c_high:
                # EPA AQI formula: I_p = [(I_high - I_low) / (C_high - C_low)] * (C_p - C_low) + I_low
                return int(((aqi_high - aqi_low) / (c_high - c_low)) * (concentration - c_low) + aqi_low)

        # If concentration exceeds all breakpoints, use hazardous category
        c_low, c_high, aqi_low, aqi_high = breakpoints[-1]
        return int(((aqi_high - aqi_low) / (c_high - c_low)) * (concentration - c_low) + aqi_low)

    # EPA AQI Breakpoints: (C_low, C_high, AQI_low, AQI_high)
    # O3 (ppm, 8-hour average)
    o3_breakpoints = [
        (0.000, 0.054, 0, 50),
        (0.055, 0.070, 51, 100),
        (0.071, 0.085, 101, 150),
        (0.086, 0.105, 151, 200),
        (0.106, 0.200, 201, 300),
        (0.201, 0.604, 301, 500),
    ]

    # PM2.5 (µg/m³, 24-hour average)
    pm25_breakpoints = [
        (0.0, 12.0, 0, 50),
        (12.1, 35.4, 51, 100),
        (35.5, 55.4, 101, 150),
        (55.5, 150.4, 151, 200),
        (150.5, 250.4, 201, 300),
        (250.5, 500.4, 301, 500),
    ]

    # PM10 (µg/m³, 24-hour average)
    pm10_breakpoints = [
        (0, 54, 0, 50),
        (55, 154, 51, 100),
        (155, 254, 101, 150),
        (255, 354, 151, 200),
        (355, 424, 201, 300),
        (425, 604, 301, 500),
    ]

    # CO (ppm, 8-hour average)
    co_breakpoints = [
        (0.0, 4.4, 0, 50),
        (4.5, 9.4, 51, 100),
        (9.5, 12.4, 101, 150),
        (12.5, 15.4, 151, 200),
        (15.5, 30.4, 201, 300),
        (30.5, 50.4, 301, 500),
    ]

    # SO2 (ppm, 1-hour average)
    so2_breakpoints = [
        (0.000, 0.035, 0, 50),
        (0.036, 0.075, 51, 100),
        (0.076, 0.185, 101, 150),
        (0.186, 0.304, 151, 200),
        (0.305, 0.604, 201, 300),
        (0.605, 1.004, 301, 500),
    ]

    # NO2 (ppm, 1-hour average)
    no2_breakpoints = [
        (0.000, 0.053, 0, 50),
        (0.054, 0.100, 51, 100),
        (0.101, 0.360, 101, 150),
        (0.361, 0.649, 151, 200),
        (0.650, 1.249, 201, 300),
        (1.250, 2.049, 301, 500),
    ]

    # Calculate sub-AQI for each pollutant
    sub_aqis = []

    if co_ppm >= 0:
        sub_aqis.append(calculate_sub_aqi(co_ppm, co_breakpoints))
    if no2_ppm >= 0:
        sub_aqis.append(calculate_sub_aqi(no2_ppm, no2_breakpoints))
    if o3_ppm >= 0:
        sub_aqis.append(calculate_sub_aqi(o3_ppm, o3_breakpoints))
    if so2_ppm >= 0:
        sub_aqis.append(calculate_sub_aqi(so2_ppm, so2_breakpoints))
    if pm25_ugm3 >= 0:
        sub_aqis.append(calculate_sub_aqi(pm25_ugm3, pm25_breakpoints))
    if pm10_ugm3 >= 0:
        sub_aqis.append(calculate_sub_aqi(pm10_ugm3, pm10_breakpoints))

    # Overall AQI is the maximum of all sub-AQIs
    return max(sub_aqis) if sub_aqis else 0


# Usage with your predictions
def calculate_aqi_for_predictions(predictions: dict) -> list[int]:
    """
    Calculate AQI for each hour in your 12-hour forecast.

    Args:
        predictions: Dictionary with keys 'co', 'no2', 'o3', 'so2', 'pm25frm', 'pm10mass'
                    Each value is a list of 12 hourly predictions

    Returns:
        List of 12 AQI values, one for each hour
    """
    aqi_values = []

    for hour in range(12):
        aqi = calculate_aqi(
            co_ppm=predictions["co"][hour],
            no2_ppm=predictions["no2"][hour],
            o3_ppm=predictions["o3"][hour],
            so2_ppm=predictions["so2"][hour],
            pm25_ugm3=predictions["pm25frm"][hour],
            pm10_ugm3=predictions["pm10mass"][hour],
        )
        aqi_values.append(aqi)

    return aqi_values


# # Example usage
# aqi_forecast = calculate_aqi_for_predictions(your_predictions_dict)  
# print(f"AQI forecast for next 12 hours: {aqi_forecast}")
  