import React, { useState } from "react";
import HomePage from "./pages/HomePage";
import LogIn from "./pages/LogIn";
import SignUp from "./pages/SignUp";
import ResetPassword from "./pages/ResetPassword";
import Dashboard from "./pages/Dashboard";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

export default function App() {
  //const [page, setPage] = useState("dashboard"); // start at Dashboard

  return (
    /*<div>
      {page === "dashboard" && <Dashboard goTo={setPage} />}
      {page === "home" && <HomePage goTo={setPage} />}
    </div>
    */
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LogIn />} />
        <Route path="/signup" element={<SignUp />} />
        <Route path="/resetpassword" element={<ResetPassword />} />
        <Route path="/dashboard" element={<Dashboard />} />
      </Routes>
    </Router>
  );

  /*
  const [page, setPage] = useState("home"); 

  return (
    <div>
      {page === "home" && <HomePage goTo={setPage} />}
      {page === "login" && <LogIn goTo={setPage} />}
      {page === "signup" && <SignUp goTo={setPage} />}
      {page === "reset" && <ResetPassword goTo={setPage} />}
      {page === "dashboard" && <Dashboard goTo={setPage} />}
    </div>
  ); */
}
