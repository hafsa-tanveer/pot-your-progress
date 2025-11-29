import React, { useState } from "react";
import "../CSS/Dashboard.css";
import AddHabitPopup from "./AddHabitPopup";
import EditHabitPopup from "./EditHabitPopup";
import DeleteHabitPopup from "./DeleteHabitPopup";
import LogoutPopup from "./LogoutPopup";

export default function Dashboard({ goTo }) {
  const [habits, setHabits] = useState(Array(8).fill(null));
  const [showAddPopup, setShowAddPopup] = useState(false);
  const [showDeletePopup, setShowDeletePopup] = useState(false);
  const [editingHabitIndex, setEditingHabitIndex] = useState(null);
  const [showLogoutPopup, setShowLogoutPopup] = useState(false);
  const [deleteMode, setDeleteMode] = useState(false);

  React.useEffect(() => {
    return () => {
      document.body.style.cursor = "default";
    };
  }, []);

  //cursor logic
  if (deleteMode) {
    document.body.style.cursor = "url('/Shovel.png') 16 16, pointer";
  } else {
    document.body.style.cursor = "default";
  }

  // Add new habit
  const handleAddHabit = (newHabit) => {
    const firstEmptyIndex = habits.findIndex((h) => h === null);
    if (firstEmptyIndex === -1) return;
    const updatedHabits = [...habits];
    updatedHabits[firstEmptyIndex] = newHabit;
    setHabits(updatedHabits);
  };

  // Edit existing habit
  const handleEditHabit = (updatedHabit) => {
    const updatedHabits = [...habits];
    updatedHabits[editingHabitIndex] = updatedHabit;
    setHabits(updatedHabits);
    setEditingHabitIndex(null);
  };

  // Delete all habits
  const handleDeleteAll = () => {
    setHabits(Array(8).fill(null));
    setShowDeletePopup(false);
  };

  return (
    <div className="dashboard-container">
      <nav className="dashboard-navbar">
        <div className="nav-left">
          <div className="profile-circle"></div>
          <span className="username">username</span>
          <img src="/Logo.png" alt="logo" className="nav-logo" />
          <h1 className="app-title">Pot Your Progress</h1>
        </div>
        <div className="nav-right">
          <button className="icon-button">
            <img src="/notif.png" alt="reminder" className="nav-icon"/>
          </button>

          <button 
            className="icon-button"
            onClick={() => setShowLogoutPopup(true)}
          >
            <img src="/logout.png" alt="logout" className="nav-icon"/>
          </button>
        </div>
      </nav>

      <div className="dashboard-main">
        <div className="habits-grid">
          {habits.map((h, i) => (
            <button
              key={i}
              className={`habit-card ${!h ? "disabled" : ""}`}
              onClick={() => {
                if (!h) return;

                if (deleteMode) {
                // delete this ONE habit
                  const updated = [...habits];
                  updated[i] = null;
                  setHabits(updated);
                  setDeleteMode(false); // exit delete mode after deleting
                } else {
                // normal: open edit popup
                  setEditingHabitIndex(i);
                }
              }}

              disabled={!h}
            >
              <img
                src={h ? "/AlivePlant.png" : "/Pot.png"}
                alt="plant"
                className="plant-img"
              />
              {h && <p className="habit-title">{h.name}</p>}
            </button>
          ))}
        </div>

        <div className="sidebar">
          <div className="sidebar-card">
        <button
          className={`icon-button ${deleteMode ? "delete-active" : ""}`}
          onClick={() => setDeleteMode(!deleteMode)}
        >
          <img src="/Shovel.png" alt="shovel" className="sidebar-icon" />
        </button>

            {showDeletePopup && (
              <DeleteHabitPopup
                onClose={() => setShowDeletePopup(false)}
                onDelete={handleDeleteAll}
              />
            )}

            <button
              className="add-button"
              onClick={() => setShowAddPopup(true)}
            >
              <img
                src="/AlivePlant.png"
                alt="plant"
                className="sidebar-plant"
              />
            </button>
          </div>
        </div>
      </div>

      {showAddPopup && (
        <AddHabitPopup
          onClose={() => setShowAddPopup(false)}
          onAddHabit={handleAddHabit}
        />
      )}

      {editingHabitIndex !== null && (
        <EditHabitPopup
          habit={habits[editingHabitIndex]}
          onClose={() => setEditingHabitIndex(null)}
          onEditHabit={handleEditHabit}  
        />
      )}

      {showLogoutPopup && (
        <LogoutPopup
          onClose={() => setShowLogoutPopup(false)}
          onLogout={() => {
            setShowLogoutPopup(false);
            goTo("home"); // switches back to HomePage
          }}      
          />
       )}


    </div>
  );
}
