//___Import
const express = require('express')
const cors = require("cors")
const dotenv = require("dotenv").config()
//___Intialize
const app = express()
const port = 8000


//___Middlewares
app.use(cors()) //ALL CORS REQUESTS ARE ENABLED⚠️⚠️
app.use(express.json())
app.use(cookieParser())


//___Routes
app.get('/', (req, res) => {
  res.send('Hello World!')
})

app.listen(port, () => {
  console.log(`Example app listening on port ${port}`)
})
