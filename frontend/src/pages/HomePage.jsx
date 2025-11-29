import React from "react";
import "../CSS/HomePage.css";
import { Link } from "react-router-dom";

export default function HomePage({ goTo }) {
  return (
    <div className="page-container">
      <img src="/Flower branch.png" className="branches right" alt="" />
      <img src="/Flower branch.png" className="branches left" alt="" />
      <div className="scattered-flowers">
        <img src="/Flowers.png" className="flower f1" alt="" />
        <img src="/Flowers.png" className="flower f2" alt="" />
        <img src="/Flowers.png" className="flower f3" alt="" />
        <img src="/Flowers.png" className="flower f4" alt="" />
        <img src="/Flowers.png" className="flower f5" alt="" />
        <img src="/Flowers.png" className="flower f6" alt="" />
      </div>
      <div className="card">
        <h1 className="welcome-text">Welcome!</h1>

        <img src="/Logo.png" className="logo" alt="Pot Your Progress" />

        <div className="button-row">
          <button className="btn" onClick={() => goTo("login")}>
            Log In
          </button>
          <button className="btn" onClick={() => goTo("signup")}>
            Sign Up
          </button>
        </div>
      </div>
    </div>
  );
}
