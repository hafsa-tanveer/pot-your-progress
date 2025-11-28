import React from "react";
import "../CSS/AddHabitPopup.css"; // you can reuse the same popup CSS

export default function DeleteHabitPopup({ onClose, onDelete }) {
  return (
    <div className="popup-overlay">
      <div className="popup-content">
        <h2>Delete this habit?</h2>
        <div style={{ marginTop: "15px" }}>
          <button
            onClick={onDelete}
            style={{
              backgroundColor: "#e74c3c",
              color: "white",
              padding: "8px 20px",
              border: "none",
              borderRadius: "5px",
              cursor: "pointer",
              marginRight: "10px",
            }}
          >
            Delete
          </button>
          <button
            onClick={onClose}
            style={{
              padding: "8px 20px",
              border: "none",
              borderRadius: "5px",
              cursor: "pointer",
            }}
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}
