import React, { useState, useEffect } from "react";
import "../CSS/AddHabitPopup.css"; // reuse same CSS

export default function EditHabitPopup({ habit, onClose, onEditHabit }) {
  const [habitName, setHabitName] = useState("");
  const [frequency, setFrequency] = useState("daily");

  // Pre-fill the inputs when popup opens
  useEffect(() => {
    if (habit) {
      setHabitName(habit.habit_name || habit.name || "");
      setFrequency(habit.frequency || "daily");
    }
  }, [habit]);

  const handleEdit = () => {
    if (!habitName.trim()) return;
    onEditHabit({ ...habit, habit_name: habitName, frequency });
    onClose();
  };

  return (
    <div className="popup-overlay">
      <div className="popup-content">
        <h2>Edit Habit</h2>
        <input
          className="input-habit"
          type="text"
          placeholder="Enter habit name"
          value={habitName}
          onChange={(e) => setHabitName(e.target.value)}
        />
        <div style={{ margin: "10px 0" }}>
          <button
            className="daily-button"
            style={{
              backgroundColor: frequency === "daily" ? "#294936" : "#F7F3ED",
              marginRight: "10px",
              color: frequency === "daily" ? "#F7F3ED" : "#294936",
            }}
            onClick={() => setFrequency("daily")}
          >
            Daily
          </button>
          <button
            className="daily-button"
            style={{
              backgroundColor: frequency === "weekly" ? "#294936" : "#F7F3ED",
              color: frequency === "weekly" ? "#F7F3ED" : "#294936",
            }}
            onClick={() => setFrequency("weekly")}
          >
            Weekly
          </button>
        </div>
        <button className="add-habit-button" onClick={handleEdit}>
          Save Changes
        </button>
        <button
          className="add-habit-button"
          onClick={onClose}
          style={{ marginLeft: "10px" }}
        >
          Cancel
        </button>
      </div>
    </div>
  );
}
