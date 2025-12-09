import React, { useState } from "react";
import "../CSS/SignUp.css";
import API from "../api";
import { Link, useNavigate } from "react-router-dom";

export default function SignUp() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const navigate = useNavigate();

  const handleSignup = async (e) => {
    e.preventDefault(); // prevent form reload

    if (password !== confirmPassword) {
      alert("Passwords do not match!");
      return;
    }

    try {
      await API.post("/auth/signup", {
        name,
        email,
        password,
      });
      alert("Signup successful!");
      navigate("/login");
    } catch (error) {
      if (!error.response) {
        // Network / backend not reachable
        alert("Cannot reach backend. Make sure the server is running!");
      } else {
        alert(error.response.data?.message || "Signup failed");
      }
    }
  };

  return (
    <div className="signup-page">
      <div className="signup-card">
        <img src="/Logo.png" alt="Pot Your Progress" className="signup-logo" />

        <form className="signup-form" onSubmit={handleSignup}>
          <label>Email</label>
          <input
            type="email"
            className="signup-input"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />

          <label>Username</label>
          <input
            type="text"
            className="signup-input"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />

          <label>Password</label>
          <input
            type="password"
            className="signup-input"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          <label>Confirm Password</label>
          <input
            type="password"
            className="signup-input"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
          />

          <button type="submit" className="signup-btn">
            Sign Up
          </button>
        </form>

        <div style={{ marginTop: "10px" }}>
          <Link to="/login">Already have an account? Log In</Link>
        </div>
      </div>
    </div>
  );
}
