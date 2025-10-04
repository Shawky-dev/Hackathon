const express = require("express")
const router = express.Router()
const { validateData }  = require( '../middleware/validationMiddleware')
const { requestForecastRequest} = require('../schemas/requests/forecast')

const {requestForecast, checkForecastRequest} = require('../controllers/forcast.controller')

router.post('/request-forecast',validateData(requestForecastRequest),requestForecast)
router.post('/check-forecast-request',checkForecastRequest)


module.exports = router