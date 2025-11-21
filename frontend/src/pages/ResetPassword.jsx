import React from "react"
import "../CSS/ResetPassword.css"
import { Link } from "react-router-dom";

export default function ResetPassword({goTo}) {
  return (
    <div className="reset-page">
      <div className="reset-card">

        <img src="/Logo.png" alt="Pot Your Progress" className="reset-logo" />

        <form className="reset-form">

          <label>New Password</label>
          <input type="password" className="reset-input" />

          <label>Confirm Password</label>
          <input type="password" className="reset-input" />

          <button className="reset-btn" onClick={() => goTo("login")}>Reset Password</button>
        </form>

      </div>
    </div>
  );
}
