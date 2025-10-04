const { z } = require('zod');

const requestForcastRequest = z.object({
  long: z.number(),
  lat: z.number(),
  date: z.coerce.date()
});

module.exports = { requestForcastRequest };
