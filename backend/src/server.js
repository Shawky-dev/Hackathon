//___Import Packages
const express = require('express')
const cors = require("cors")
const dotenv = require("dotenv").config()
const bodyParser = require('body-parser')
//__import routes
const forcastRoutes = require('./routes/forcast.routes')
//___Intialize
const app = express()
const port = 8000

//___Middlewares
// app.use(bodyParser.json());
app.use(cors()) //ALL CORS REQUESTS ARE ENABLED⚠️⚠️
app.use(express.json())


//___Routes

app.use('/api/forcast/',forcastRoutes)

app.listen(port, () => {
  console.log(`Example app listening on port ${port}`)
})
