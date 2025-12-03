import React, { useState } from "react";
import "../CSS/AddHabitPopup.css"; // using same popup styling

export default function ReminderPopup({
  habits,
  onClose,
  onAddReminder,
  onDeleteReminder,
}) {
  const validHabits = habits.filter((h) => h !== null);

  const [selectedHabit, setSelectedHabit] = useState(
    validHabits.length > 0 ? validHabits[0].name : ""
  );

  const handleAdd = () => {
    if (!selectedHabit) return;
    onAddReminder(selectedHabit);
    onClose();
  };

  const handleDelete = () => {
    if (!selectedHabit) return;
    onDeleteReminder(selectedHabit);
    onClose();
  };

  return (
    <div className="popup-overlay">
      <div className="popup-content">
        <h2>Reminders</h2>

        {validHabits.length > 0 ? (
          <>
            <label style={{ marginBottom: "8px", display: "block" }}>
              Select a Habit:
            </label>

            <select
              className="input-habit"
              value={selectedHabit}
              onChange={(e) => setSelectedHabit(e.target.value)}
              style={{ marginBottom: "15px" }}
            >
              {validHabits.map((h, i) => (
                <option key={i} value={h.name}>
                  {h.name}
                </option>
              ))}
            </select>

            {/* ACTION BUTTONS */}
            <div style={{ display: "flex", justifyContent: "center" }}>
              <button className="add-habit-button"
                onClick={handleAdd}
                style={{
                  marginRight: "10px",
                }}
              >
                Add Reminder
              </button>

              <button className="cancel-button"
                onClick={handleDelete}
              >
                Delete Reminder
              </button>
            </div>
          </>
        ) : (
          <p style={{ marginTop: "10px" }}>No habits available.</p>
        )}

        <button
          onClick={onClose}
          className="cancel-button"
          style={{
            marginTop: "15px",
          }}
        >
          Cancel
        </button>
      </div>
    </div>
  );
}
