import React from "react";
import "../CSS/AddHabitPopup.css"; // can reuse or extend this CSS

export default function LogoutPopup({ onClose, onLogout }) {
  return (
    <div className="popup-overlay">
      <div className="popup-content">
        <h2>Are you sure you want to log out?</h2>

          <button className="add-habit-button" onClick={onLogout}>
            Log Out
          </button>
          <button className="cancel-button" onClick={onClose} style={{ marginLeft: "10px" }}>
            Cancel
          </button>

      </div>
    </div>
  );
}
