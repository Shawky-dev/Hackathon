const express = require("express")
const router = express.Router()
const { validateData }  = require( '../middleware/validationMiddleware')
const { requestForcastRequest} = require('../schemas/requests/forcast')

const {requestForcast} = require('../controllers/forcast.controller')

router.post('/request-forcast',validateData(requestForcastRequest),requestForcast)


module.exports = router