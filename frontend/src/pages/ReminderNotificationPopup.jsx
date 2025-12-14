import React from "react";
import "../CSS/AddHabitPopup.css"; // using same styling as OTP popup

export default function ReminderNotificationPopup({ reminder, onClose, onDismiss }) {
  return (
    <div className="popup-overlay">
      <div className="popup-content">
        <h2>🌱 Plant Reminder</h2>
        <div
          style={{
            marginBottom: "15px",
            padding: "15px",
            backgroundColor: "#fff3cd",
            borderRadius: "5px",
            border: "1px solid #ffc107",
          }}
        >
          <p style={{ margin: 0, color: "#856404", fontSize: "14px", lineHeight: "1.6" }}>
            {reminder.message}
          </p>
        </div>
        <p style={{ marginBottom: "15px", color: "#666", fontSize: "12px" }}>
          Log in to Pot Your Progress and track your habit to save your plant!
        </p>
        <div style={{ display: "flex", gap: "10px", marginTop: "15px" }}>
          <button className="add-habit-button" onClick={onDismiss}>
            Got it!
          </button>
          <button className="cancel-button" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

