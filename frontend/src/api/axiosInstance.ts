import axios from 'axios';

const API_URL = process.env.NODE_ENV === 'development' 
  ? 'http://127.0.0.1:8000' 
  : 'https://advice-project.onrender.com';
const axiosInstance = axios.create({
  baseURL: API_URL,
  withCredentials: true
});

export default axiosInstance;