import React, { useState, useEffect } from "react";
import "../CSS/LogIn.css";
import API from "../api";
import { Link, useNavigate } from "react-router-dom";

export default function LogIn() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  // If user navigates back to login, clear session to prevent forward navigation into dashboard
  useEffect(() => {
    const logoutOnLoad = async () => {
      try {
        await API.post("/auth/logout");
      } catch (err) {
        // ignore logout errors
      }
      localStorage.removeItem("user");
    };
    logoutOnLoad();
  }, []);

  const handleLogin = async (e) => {
    e.preventDefault(); // prevent form reload
    try {
      const response = await API.post("/auth/login", { email, password });
      // persist minimal user info for UI/route guards
      localStorage.setItem("user", JSON.stringify(response.data.user));
      navigate("/dashboard"); // navigate after successful login
    } catch (error) {
      if (!error.response) {
        alert("Cannot reach backend. Make sure the server is running!");
      } else {
        alert(error.response.data?.message || "Login failed");
      }
    }
  };

  return (
    <div className="signin-page">
      <div className="signin-card">
        <img src="/Logo.png" alt="Pot Your Progress" className="signin-logo" />

        <form className="signin-form" onSubmit={handleLogin}>
          <label>username/email</label>
          <input
            type="text"
            className="signin-input"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />

          <label>password</label>
          <input
            type="password"
            className="signin-input"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          <Link to="/resetpassword">Forgot Password?</Link>

          <button type="submit" className="signin-btn">
            Log In
          </button>
        </form>
      </div>
    </div>
  );
}
