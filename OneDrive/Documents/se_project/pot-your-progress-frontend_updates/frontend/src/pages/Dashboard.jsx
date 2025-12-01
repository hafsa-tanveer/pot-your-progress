import React, { useState, useEffect } from "react";
import API from "../api"; // Make sure this imports your axios instance
import "../CSS/Dashboard.css";
import AddHabitPopup from "./AddHabitPopup";
import EditHabitPopup from "./EditHabitPopup";
import DeleteHabitPopup from "./DeleteHabitPopup";
import LogoutPopup from "./LogoutPopup";

export default function Dashboard({ goTo }) {
  // We still use the Array(8) structure for the UI grid
  const [habits, setHabits] = useState(Array(8).fill(null));
  
  const [showAddPopup, setShowAddPopup] = useState(false);
  const [showDeletePopup, setShowDeletePopup] = useState(false);
  const [editingHabitIndex, setEditingHabitIndex] = useState(null);
  const [showLogoutPopup, setShowLogoutPopup] = useState(false);
  const [deleteMode, setDeleteMode] = useState(false);

  // --- INTEGRATION: Fetch Data on Load ---
  useEffect(() => {
    fetchHabits();
    
    return () => {
      document.body.style.cursor = "default";
    };
  }, []);

  const fetchHabits = async () => {
    try {
      const response = await API.get("/habits/");
      const data = response.data;
      
      // Map backend list to your 8-pot grid
      const newSlots = Array(8).fill(null);
      data.forEach((habit, index) => {
        if (index < 8) {
          // Backend sends {id, name, ...}, matches your UI expectation
          newSlots[index] = habit; 
        }
      });
      setHabits(newSlots);
    } catch (error) {
      console.error("Failed to load habits", error);
    }
  };

  //cursor logic
  if (deleteMode) {
    document.body.style.cursor = "url('/Shovel.png') 16 16, pointer";
  } else {
    document.body.style.cursor = "default";
  }

  // --- INTEGRATION: Add new habit ---
  const handleAddHabit = async (newHabit) => {
    // Check if grid is full
    const firstEmptyIndex = habits.findIndex((h) => h === null);
    if (firstEmptyIndex === -1) {
        alert("Garden is full!");
        return;
    }

    try {
        // Call Backend
        await API.post("/habits/add", {
            name: newHabit.name || newHabit, // Handle object or string
            schedule: newHabit.schedule || "daily"
        });
        
        // Refresh grid from server
        setShowAddPopup(false);
        fetchHabits(); 
    } catch (error) {
        console.error("Error adding habit", error);
    }
  };

  // --- INTEGRATION: Edit existing habit ---
  const handleEditHabit = async (updatedHabit) => {
    const habitIndex = editingHabitIndex;
    const originalHabit = habits[habitIndex];
    
    if (!originalHabit) return;

    try {
        // Call Backend
        await API.put(`/habits/${originalHabit.id}`, {
            name: updatedHabit.name || updatedHabit
        });

        setEditingHabitIndex(null);
        fetchHabits();
    } catch (error) {
        console.error("Error editing habit", error);
    }
  };

  // --- INTEGRATION: Delete Single Habit ---
  const handleSingleDelete = async (index) => {
      const habitToDelete = habits[index];
      if (!habitToDelete) return;

      try {
          await API.delete(`/habits/${habitToDelete.id}`);
          
          setDeleteMode(false); // exit delete mode after deleting (Original behavior)
          fetchHabits();
      } catch (error) {
          console.error("Error deleting habit", error);
      }
  };

  // --- INTEGRATION: Delete all habits ---
  const handleDeleteAll = async () => {
    try {
        // Simple loop to delete all visible habits
        const activeHabits = habits.filter(h => h !== null);
        for (const habit of activeHabits) {
            await API.delete(`/habits/${habit.id}`);
        }
        setShowDeletePopup(false);
        fetchHabits();
    } catch (error) {
        console.error("Error clearing garden", error);
    }
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
            <img src="/notif.png" alt="reminder" className="nav-icon" />
          </button>

          <button
            className="icon-button"
            onClick={() => setShowLogoutPopup(true)}
          >
            <img src="/logout.png" alt="logout" className="nav-icon" />
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
                  // INTEGRATION: Call our new async delete handler
                  handleSingleDelete(i);
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