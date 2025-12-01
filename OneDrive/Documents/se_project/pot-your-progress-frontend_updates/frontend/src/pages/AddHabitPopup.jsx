import React, { useState } from "react";
import "../CSS/AddHabitPopup.css";

export default function AddHabitPopup({ onClose, onAddHabit }) {
  const [habitName, setHabitName] = useState("");
  const [frequency, setFrequency] = useState("daily");

  const handleAdd = () => {
    if (!habitName.trim()) return;
    onAddHabit({ name: habitName, frequency });
    onClose();
  };

  return (
    <div className="popup-overlay">
      <div className="popup-content">
        <h2>Add New Habit</h2>
        <input
          type="text"
          placeholder="Enter habit name"
          value={habitName}
          onChange={(e) => setHabitName(e.target.value)}
        />
        <div style={{ margin: "10px 0" }}>
          <button
            style={{
              backgroundColor: frequency === "daily" ? "#4caf50" : "#ccc",
              marginRight: "10px",
            }}
            onClick={() => setFrequency("daily")}
          >
            Daily
          </button>
          <button
            style={{
              backgroundColor: frequency === "weekly" ? "#4caf50" : "#ccc",
            }}
            onClick={() => setFrequency("weekly")}
          >
            Weekly
          </button>
        </div>
        <button onClick={handleAdd}>Add Habit</button>
        <button onClick={onClose} style={{ marginLeft: "10px" }}>
          Cancel
        </button>
      </div>
    </div>
  );
}
