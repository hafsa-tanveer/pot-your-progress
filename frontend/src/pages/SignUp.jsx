import React from "react"
import "../CSS/SignUp.css"
import { Link } from "react-router-dom";

export default function SignUp({goTo}) {
  return (
    <div className="signup-page">
      <div className="signup-card">

        <img src="/Logo.png" alt="Pot Your Progress" className="signup-logo" />

        <form className="signup-form">

          <label>Email</label>
          <input type="email" className="signup-input" />

          <label>Username</label>
          <input type="text" className="signup-input" />

          <label>Password</label>
          <input type="password" className="signup-input" />

          <label>Confirm Password</label>
          <input type="password" className="signup-input" />

          <button className="signup-btn" onClick={() => goTo("dashboard")}>Sign Up</button>
        </form>

      </div>
    </div>
  );
}
