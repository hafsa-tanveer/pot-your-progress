import React, { useState, useEffect } from "react";
import "../CSS/AddHabitPopup.css"; // reuse same CSS

export default function EditHabitPopup({ habit, onClose, onEditHabit }) {
  const [habitName, setHabitName] = useState("");
  const [frequency, setFrequency] = useState("daily");

  // Pre-fill the inputs when popup opens
  useEffect(() => {
    if (habit) {
      setHabitName(habit.name);
      setFrequency(habit.frequency);
    }
  }, [habit]);

  const handleEdit = () => {
    if (!habitName.trim()) return;
    onEditHabit({ ...habit, name: habitName, frequency });
    onClose();
  };

  return (
    <div className="popup-overlay">
      <div className="popup-content">
        <h2>Edit Habit</h2>
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
        <button onClick={handleEdit}>Save Changes</button>
        <button onClick={onClose} style={{ marginLeft: "10px" }}>
          Cancel
        </button>
      </div>
    </div>
  );
}
