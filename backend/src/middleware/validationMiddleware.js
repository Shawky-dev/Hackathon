const { ZodError } = require('zod')
const { StatusCodes } = require('http-status-codes')

function validateData(schema) {
  return (req, res, next) => {
    try {
      schema.parse(req.body);
      next();
    } catch (error) {
      if (error instanceof ZodError) {
      const errorMessages = (error.errors || []).map((issue) => ({
        message: `${issue.path.join('.')} is ${issue.message}`,
      }))
      res.status(StatusCodes.BAD_REQUEST).json({ error: 'Invalid data', details: errorMessages });
    } else {
      console.error("Unexpected error in validateData:", error);
      res.status(StatusCodes.INTERNAL_SERVER_ERROR).json({ error: 'Internal Server Error' });
    }
    }
  };
}

module.exports = { validateData }
