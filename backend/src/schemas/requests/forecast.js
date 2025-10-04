const { z } = require('zod');

const requestForecastRequest = z.object({
  long: z.number(),
  lat: z.number(),
  date: z.coerce.date()
});

module.exports = { requestForecastRequest };
