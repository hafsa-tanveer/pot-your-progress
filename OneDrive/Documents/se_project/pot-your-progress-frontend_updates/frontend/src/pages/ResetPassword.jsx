import React, { useState } from "react";
import "../CSS/ResetPassword.css";
import API from "../api";
import { Link } from "react-router-dom";

export default function ResetPassword({ goTo }) {
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const handleResetPassword = async (e) => {
    e.preventDefault(); // prevent form reload

    if (newPassword !== confirmPassword) {
      alert("Passwords do not match");
      return;
    }

    try {
      const response = await API.post(
        "/resetpassword",
        { new_password: newPassword, confirm_password: confirmPassword },
        { withCredentials: true } // if your backend requires cookies
      );

      console.log("Password reset success:", response.data);
      alert("Password has been successfully updated!");
      goTo("login"); // redirect after success
    } catch (error) {
      if (!error.response) {
        alert("Cannot reach backend. Make sure the server is running!");
      } else {
        alert(error.response.data?.message || "Password reset failed");
      }
    }
  };

  return (
    <div className="reset-page">
      <div className="reset-card">
        <img src="/Logo.png" alt="Pot Your Progress" className="reset-logo" />

        <form className="reset-form" onSubmit={handleResetPassword}>
          <label>New Password</label>
          <input
            type="password"
            className="reset-input"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
          />

          <label>Confirm Password</label>
          <input
            type="password"
            className="reset-input"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
          />

          <Link to="/login" className="reset-btn">
            Reset Password
          </Link>
        </form>
      </div>
    </div>
  );
}
