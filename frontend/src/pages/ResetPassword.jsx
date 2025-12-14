import React, { useState } from "react";
import "../CSS/ResetPassword.css";
import API from "../api";
import { Link, useNavigate } from "react-router-dom";
import OTPPopup from "./OTPPopup";

export default function ResetPassword({ goTo }) {
  const navigate = useNavigate();
  const [step, setStep] = useState("forget"); // "forget", "verify", "reset"
  const [email, setEmail] = useState("");
  const [otpCode, setOtpCode] = useState("");
  const [showOTPPopup, setShowOTPPopup] = useState(false);
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const handleForgetPassword = async (e) => {
    e.preventDefault();
    if (!email.trim()) {
      alert("Please enter your email address");
      return;
    }
    try {
      const response = await API.post("/auth/forget-password", { email });
      setOtpCode(response.data.otp || "");
      // Show OTP in alert and open popup
      alert(response.data.message);
      setShowOTPPopup(true);
    } catch (error) {
      if (!error.response) {
        alert("Cannot reach backend. Make sure the server is running!");
      } else {
        alert(error.response.data?.message || "Failed to send OTP");
      }
    }
  };

  const handleOTPVerify = async (otp) => {
    try {
      const response = await API.post("/auth/verify-otp", { email, otp });
      setShowOTPPopup(false);
      setStep("reset");
    } catch (error) {
      if (!error.response) {
        alert("Cannot reach backend. Make sure the server is running!");
      } else {
        alert(error.response.data?.message || "OTP verification failed");
      }
    }
  };

  const handleResetPassword = async (e) => {
    e.preventDefault(); // prevent form reload

    if (newPassword !== confirmPassword) {
      alert("Passwords do not match");
      return;
    }

    try {
      const response = await API.post(
        "/auth/reset-password",
        { email, new_password: newPassword, confirm_password: confirmPassword },
        { withCredentials: true } // if your backend requires cookies
      );

      console.log("Password reset success:", response.data);
      alert("Password has been successfully updated!");
      if (goTo) {
        goTo("login");
      } else {
        navigate("/login");
      }
    } catch (error) {
      if (!error.response) {
        alert("Cannot reach backend. Make sure the server is running!");
      } else {
        alert(error.response.data?.message || "Password reset failed");
      }
    }
  };

  if (step === "forget") {
    return (
      <div className="reset-page">
        <div className="reset-card">
          <img src="/Logo.png" alt="Pot Your Progress" className="reset-logo" />

          <form className="reset-form" onSubmit={handleForgetPassword}>
            <h2>Forgot Password?</h2>
            <p style={{ marginBottom: "15px", color: "#666", fontSize: "14px" }}>
              Enter your email address and we'll send you an OTP code to reset your password.
            </p>
            <label>Email</label>
            <input
              type="email"
              className="reset-input"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Enter your email"
            />

            <button type="submit" className="reset-btn">
              Send OTP
            </button>

            <Link to="/login" style={{ marginTop: "10px", display: "block" }}>
              Back to Login
            </Link>
          </form>
        </div>

        {showOTPPopup && (
          <OTPPopup
            onClose={() => {
              setShowOTPPopup(false);
              setOtpCode("");
            }}
            onSubmit={handleOTPVerify}
          />
        )}
      </div>
    );
  }

  return (
    <div className="reset-page">
      <div className="reset-card">
        <img src="/Logo.png" alt="Pot Your Progress" className="reset-logo" />

        <form className="reset-form" onSubmit={handleResetPassword}>
          <h2>Reset Password</h2>
          <p style={{ marginBottom: "15px", color: "#666", fontSize: "14px" }}>
            Enter your new password below.
          </p>
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

          <button type="submit" className="reset-btn">
            Reset Password
          </button>

          <Link to="/login" style={{ marginTop: "10px", display: "block" }}>
            Back to Login
          </Link>
        </form>
      </div>
    </div>
  );
}
