import React from "react"
import "../CSS/LogIn.css"
import { Link } from "react-router-dom"

export default function LogIn() {
  return (
    <div className="signin-page">
      <div className="signin-card">

        <img src="/Logo.png" alt="Pot Your Progress" className="signin-logo" />

        <form className="signin-form">

          <label>username/email</label>
          <input type="text" className="signin-input" />

          <label>password</label>
          <input type="password" className="signin-input" />

          <p className="forgot-text">Forgot Password?</p>

          <button className="signin-btn">Log In</button>
        </form>

      </div>
    </div>
  );
}