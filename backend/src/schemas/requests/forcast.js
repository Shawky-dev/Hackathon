const { z } = require('zod');

const requestForcastRequest = z.object({
  long: z.number(),
  lat: z.number()
});

module.exports = { requestForcastRequest };
