// src/api/axios.js
import axios from 'axios';

// Create an Axios instance with default settings
const api = axios.create({
  baseURL: 'http://localhost:8000/api/',
    withCredentials: true, 
  timeout: 10000, // optional: 10 seconds
  headers: {
    'Content-Type': 'application/json',
  },
});
export default api;