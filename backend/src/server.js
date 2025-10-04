// ___ Import Packages
const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv').config();
const bodyParser = require('body-parser');

// ___ Import Routes
const forcastRoutes = require('./routes/forcast.routes');

// ___ Initialize
const app = express();
const port = process.env.PORT || 8000;

// ___ Middlewares
app.use(bodyParser.json());

app.use(
  cors({
    origin: ['http://localhost:5173'], // React dev server URL
    methods: ['GET', 'POST', 'PUT', 'DELETE'],
    credentials: true, // if using cookies or auth headers
  })
);

// Parse JSON requests
app.use(express.json());

// ___ Routes
app.use('/api/forcast', forcastRoutes);

// ___ Start Server
app.listen(port, () => {
  console.log(`✅ Server running on port ${port}`);
});
