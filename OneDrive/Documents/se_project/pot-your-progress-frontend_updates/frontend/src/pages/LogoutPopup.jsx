import React from "react";

export default function LogoutPopup({ onClose, onLogout }) {
  return (
    <div
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        width: "100vw",
        height: "100vh",
        backgroundColor: "rgba(0,0,0,0.5)",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        zIndex: 9999,
      }}
    >
      <div
        style={{
          background: "#fff",
          padding: "25px",
          borderRadius: "12px",
          textAlign: "center",
          minWidth: "300px",
        }}
      >
        <h2>Are you sure you want to log out?</h2>

        <div style={{ marginTop: "20px", display: "flex", justifyContent: "center", gap: "10px" }}>
          <button
            style={{
              backgroundColor: "#e74c3c",
              color: "white",
              padding: "8px 16px",
              borderRadius: "8px",
              cursor: "pointer",
            }}
            onClick={onLogout} // switches page to HomePage
          >
            Log Out
          </button>

          <button
            style={{
              backgroundColor: "#ccc",
              padding: "8px 16px",
              borderRadius: "8px",
              cursor: "pointer",
            }}
            onClick={onClose} // just closes popup
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}
