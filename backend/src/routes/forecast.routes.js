const express = require("express")
const router = express.Router()
const { validateData }  = require( '../middleware/validationMiddleware')
const { requestForecastRequest} = require('../schemas/requests/forecast')

const {requestForecast} = require('../controllers/forcast.controller')

router.post('/request-forecast',validateData(requestForecastRequest),requestForecast)


module.exports = router