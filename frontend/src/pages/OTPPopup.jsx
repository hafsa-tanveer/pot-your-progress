import React, { useState } from "react";
import "../CSS/AddHabitPopup.css"; // using same styling

export default function OTPPopup({ onClose, onSubmit }) {
  const [otp, setOtp] = useState("");
  const [error, setError] = useState("");

  const handleChange = (e) => {
    const value = e.target.value.replace(/\D/g, ""); // Only allow digits
    if (value.length <= 6) {
      setOtp(value);
      setError("");
    }
  };

  const handleSubmit = () => {
    if (!otp.trim()) {
      setError("Please enter the OTP code");
      return;
    }
    if (otp.length !== 6) {
      setError("OTP must be 6 digits");
      return;
    }
    onSubmit(otp);
  };

  return (
    <div className="popup-overlay">
      <div className="popup-content">
        <h2>Enter OTP Code</h2>
        <p style={{ marginBottom: "15px", color: "#666", fontSize: "14px" }}>
          Please enter the 6-digit OTP code that was displayed to verify your email.
        </p>
        {error && (
          <div
            style={{
              color: "#d32f2f",
              marginBottom: "15px",
              fontSize: "14px",
              padding: "10px",
              backgroundColor: "#ffebee",
              borderRadius: "5px",
            }}
          >
            {error}
          </div>
        )}
        <input
          className="input-habit"
          type="text"
          maxLength={6}
          placeholder="Enter 6-digit OTP"
          value={otp}
          onChange={handleChange}
          style={{
            textAlign: "center",
            letterSpacing: "8px",
            fontSize: "20px",
            fontWeight: "bold",
          }}
        />
        <div style={{ display: "flex", gap: "10px", marginTop: "15px" }}>
          <button className="add-habit-button" onClick={handleSubmit}>
            Verify OTP
          </button>
          <button className="cancel-button" onClick={onClose}>
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}

