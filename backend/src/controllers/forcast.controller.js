const requestForecast = async (req, res) => {
  try {
    // Example mock data
    const current = {
      aqi: 82,
      category: "Moderate",
      dominant_pollutant: "PM2.5",
      pm25: 18.4,
      pm10: 29.1,
      no2: 22.7,
      o3: 45.3,
      co: 0.4,
      temperature_c: 26.5,
      humidity_percent: 58,
      wind_speed_mps: 3.2,
      wind_direction_deg: 245,
      precipitation_mm: 0,
    };

    const forecastList = [
      {
        datetime: "2025-10-04T15:00:00Z",
        aqi: 90,
        category: "Moderate",
        dominant_pollutant: "O3",
        pm25: 20.1,
        o3: 51.2,
        no2: 19.5,
        temperature_c: 28.1,
        humidity_percent: 50,
        wind_speed_mps: 2.9,
      },
    ];

    const response = createForecastResponse(current, forecastList);
    res.json(response);
  } catch (err) {
    res.status(500).json({ error: "Internal error" });
  }
};

module.exports = { requestForecast };

function createForecastResponse(current, forecastList) {
  return {
    current_conditions: {
      aqi: current.aqi,
      category: current.category,
      dominant_pollutant: current.dominant_pollutant,
      pollutants: {
        pm25: current.pm25,
        pm10: current.pm10,
        no2: current.no2,
        o3: current.o3,
        co: current.co,
      },
      weather: {
        temperature_c: current.temperature_c,
        humidity_percent: current.humidity_percent,
        wind_speed_mps: current.wind_speed_mps,
        wind_direction_deg: current.wind_direction_deg,
        precipitation_mm: current.precipitation_mm,
      },
    },
    forecast: forecastList.map((item) => ({
      datetime: item.datetime,
      aqi: item.aqi,
      category: item.category,
      dominant_pollutant: item.dominant_pollutant,
      pollutants: {
        pm25: item.pm25,
        o3: item.o3,
        no2: item.no2,
      },
      weather: {
        temperature_c: item.temperature_c,
        humidity_percent: item.humidity_percent,
        wind_speed_mps: item.wind_speed_mps,
      },
    })),
  };
}
