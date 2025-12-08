import React, { useState } from "react";
import "../CSS/LogIn.css";
import API from "../api";
import { Link } from "react-router-dom";

export default function LogIn({ goTo }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleLogin = async (e) => {
    e.preventDefault(); // prevent form reload
    try {
      const response = await API.post("/auth/login", { email, password });
      console.log("Login success:", response.data);
      alert("Logged in!");
      goTo("dashboard"); // navigate after successful login
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

          <Link to="/dashboard" className="signin-btn">
            Log In
          </Link>
        </form>
      </div>
    </div>
  );
}
