import axios from "axios";

// Centralized axios instance for backend calls
// Keep baseURL at backend root (not /auth) so routes compose correctly
const API = axios.create({
  baseURL: "http://localhost:5000",
  withCredentials: true, // allow session cookie for auth
});

export default API;
