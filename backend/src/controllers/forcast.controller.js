const api = require('../config/axios.js');
const requestForecast = async (req, res) => {
try {
  console.log(req.body);
  const response = await api.post('/frontend/submit',{
    long: req.body.long,
    lat: req.body.lat,
    date: req.body.date
  });
  res.status(202).json({ task_id: response.data.task_id });
  console.log(response.data);
} catch (error) {
  res.status(500).json({ error: "Internal error" });
}
};
const checkForecastRequest = async (req, res,) => {
  // const { requestId } = req.body;
  const finished = true;
    try {
      //send api check call to Ai model Api here

    //if api finished processing
    if (finished) {
      // Example mock data
      const current = {
        aqi: 82,
      };

      const forecastList = [
        {
          datetime: "2025-10-06T15:00:00Z",
          aqi: 90,
        },
        {
          datetime: "2025-10-07T15:00:00Z",
          aqi: 86,
        },
      ];

      const response = createForecastResponse(current, forecastList);
      res.status(200).json(response);
    } else {
      res.status(202).json({ message: "Forecast is still being processed" });
    }
  } catch (err) {
    res.status(500).json({ error: "Internal error" });
  }
}
  

function createForecastResponse(current, forecastList) {
  return {
    current_conditions: {
      aqi: current.aqi,
    },
    forecast: forecastList.map((item) => ({
      datetime: item.datetime,
      aqi: item.aqi,
    })),
  };
}
module.exports = { requestForecast,checkForecastRequest };
