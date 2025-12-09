import React, { useState, useEffect } from "react";
import "../CSS/Dashboard.css";
import AddHabitPopup from "./AddHabitPopup";
import EditHabitPopup from "./EditHabitPopup";
import DeleteHabitPopup from "./DeleteHabitPopup";
import LogoutPopup from "./LogoutPopup";
import ReminderPopup from "./ReminderPopup";
import { useNavigate } from "react-router-dom";
import API from "../api";

export default function Dashboard() {
  const MAX_POTS = 8;
  const [habits, setHabits] = useState(Array(MAX_POTS).fill(null));
  const [showAddPopup, setShowAddPopup] = useState(false);
  const [showDeletePopup, setShowDeletePopup] = useState(false);
  const [editingHabitIndex, setEditingHabitIndex] = useState(null);
  const [showLogoutPopup, setShowLogoutPopup] = useState(false);
  const [deleteMode, setDeleteMode] = useState(false);
  const [habitToDeleteIndex, setHabitToDeleteIndex] = useState(null);
  const [showReminderPopup, setShowReminderPopup] = useState(false);
  // store reminders by habit index
  const [reminders, setReminders] = useState({});
  const [user, setUser] = useState(null);

  const navigate = useNavigate();

  const padHabits = (list) => {
    const filled = [...list];
    while (filled.length < MAX_POTS) filled.push(null);
    return filled.slice(0, MAX_POTS);
  };

  const isHabitPending = (habit) => {
    if (!habit) return false;
    const freq = habit.frequency || "daily";
    if (freq === "weekly") {
      // Treat undefined as pending so new habits show a droplet
      return habit.is_completed_this_week !== true;
    }
    return habit.is_completed_today !== true;
  };

  useEffect(() => {
    // load user from localStorage; if missing, send to login
    const stored = localStorage.getItem("user");
    if (stored) {
      setUser(JSON.parse(stored));
    } else {
      navigate("/login");
      return;
    }

    const fetchHabits = async () => {
      try {
        const res = await API.get("/habits");
        setHabits(padHabits(res.data.habits || []));
      } catch (err) {
        console.error("Failed to load habits", err);
        if (err.response?.status === 401) {
          localStorage.removeItem("user");
          navigate("/login");
        } else {
          alert(
            "Could not load habits. Make sure backend is running and you are logged in."
          );
        }
      }
    };
    fetchHabits();
  }, [navigate]);

  useEffect(() => {
    document.body.style.cursor = deleteMode
      ? "url('/Shovel.cur'), auto"
      : "default";
    return () => {
      document.body.style.cursor = "default";
    };
  }, [deleteMode]);

  // Add new habit
  const handleAddHabit = async (newHabit) => {
    try {
      const res = await API.post("/habits", {
        habit_name: newHabit.name,
        frequency: newHabit.frequency,
      });
      const updated = habits.filter(Boolean);
      updated.push(res.data.habit);
      setHabits(padHabits(updated));
    } catch (err) {
      console.error("Failed to add habit", err);
      alert(err.response?.data?.message || "Failed to add habit");
    }
  };

  // Edit existing habit
  const handleEditHabit = async (updatedHabit) => {
    try {
      const target = habits[editingHabitIndex];
      const res = await API.put(`/habits/${target.habit_id}`, {
        habit_name: updatedHabit.habit_name,
        frequency: updatedHabit.frequency,
      });
      const updatedHabits = [...habits];
      updatedHabits[editingHabitIndex] = res.data.habit;
      setHabits(updatedHabits);
      setEditingHabitIndex(null);
    } catch (err) {
      console.error("Failed to edit habit", err);
      alert(err.response?.data?.message || "Failed to edit habit");
    }
  };

  // Delete habit
  const handleDeleteOne = async () => {
    try {
      const target = habits[habitToDeleteIndex];
      await API.delete(`/habits/${target.habit_id}`);
      const updated = habits.filter(
        (h, idx) => idx !== habitToDeleteIndex && h !== null
      );
      setHabits(padHabits(updated));
    } catch (err) {
      console.error("Failed to delete habit", err);
      alert(err.response?.data?.message || "Failed to delete habit");
    }

    // reset states
    setHabitToDeleteIndex(null);
    setShowDeletePopup(false);
    setDeleteMode(false);
  };

  const handleTrackHabit = async (index) => {
    const habit = habits[index];
    if (!habit) return;
    try {
      const res = await API.post(`/habits/${habit.habit_id}/complete`);
      const updated = [...habits];
      updated[index] = res.data.habit || habit;
      setHabits(updated);
    } catch (err) {
      console.error("Failed to track habit", err);
      if (err.response?.status === 401) {
        localStorage.removeItem("user");
        navigate("/login");
      } else {
        alert(err.response?.data?.message || "Failed to track habit");
      }
    }
  };

  return (
    <div className="dashboard-container">
      <nav className="dashboard-navbar">
        <div className="nav-left">
          <div className="profile-circle"></div>
          <span className="username">{user?.name || "username"}</span>
          <img src="/Logo.png" alt="logo" className="nav-logo" />
          <h1 className="app-title">Pot Your Progress</h1>
        </div>
        <div className="nav-right">
          <button
            className="icon-button"
            onClick={() => setShowReminderPopup(true)}
          >
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
                  setHabitToDeleteIndex(i); // store which plant is selected
                  setShowDeletePopup(true); // open popup
                  return;
                } else {
                  setEditingHabitIndex(i); // open edit popup
                }
              }}
              disabled={!h}
            >
              <div className="habit-card-wrapper">
                <img src="/Pot.png" alt="pot" className="pot-img" />
                {h && (
                  <img
                    src="/AlivePlant.png"
                    alt="plant"
                    className="plant-img"
                  />
                )}
                {h && <p className="habit-title">{h.habit_name || h.name}</p>}
                {h && isHabitPending(h) && (
                  <div
                    className="droplet-btn"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleTrackHabit(i);
                    }}
                    role="button"
                    tabIndex={0}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" || e.key === " ") {
                        e.preventDefault();
                        handleTrackHabit(i);
                      }
                    }}
                  >
                    <img
                      src="/Droplet.png"
                      alt="track habit"
                      className="droplet-img"
                      onError={(ev) => {
                        ev.currentTarget.src = "/Droplet.png";
                      }}
                    />
                  </div>
                )}
              </div>
            </button>
          ))}
        </div>

        <div className="sidebar">
          <div className="sidebar-card">
            <button
              className={`icon-button ${deleteMode ? "delete-active" : ""}`}
              onClick={() => setDeleteMode((prev) => !prev)}
            >
              <img src="/Shovel.png" alt="shovel" className="sidebar-icon" />
            </button>

            {showDeletePopup && (
              <DeleteHabitPopup
                onClose={() => {
                  setShowDeletePopup(false);
                  setHabitToDeleteIndex(null);
                  setDeleteMode(false);
                }}
                onDelete={handleDeleteOne}
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
          onLogout={async () => {
            try {
              await API.post("/auth/logout");
            } catch (err) {
              console.error("Logout failed", err);
            }
            setShowLogoutPopup(false);
            navigate("/login");
          }}
        />
      )}

      {showReminderPopup && (
        <ReminderPopup
          habits={habits.filter((h) => h !== null)}
          onClose={() => setShowReminderPopup(false)}
          onAddReminder={(habit) => console.log("Add reminder for:", habit)}
          onDeleteReminder={(habit) =>
            console.log("Delete reminder for:", habit)
          }
        />
      )}
    </div>
  );
}
