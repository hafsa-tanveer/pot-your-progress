import axios from "axios";

const API = axios.create({
  baseURL: "http://localhost:5000", // Changed from /auth to root
});

export default API;