// utils/axios.js
const axios = require('axios');

const api = axios.create({
  baseURL: 'http://master-api:9000', // ✅ your base URL
  timeout: 5000, // optional timeout (in ms)
  headers: {
    'Content-Type': 'application/json',
  },
});

module.exports = api;
