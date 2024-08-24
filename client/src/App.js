// src/App.js
import React from 'react';
import { Routes, Route } from 'react-router-dom';
import LandingPage from './components/pages/LandingPage/LandingPage';
import Login from './components/Login';
import Logout from './components/Logout';
import Dashboard from './components/Dashboard';
import AddResident from './components/AddResident';
import ResidentsList from './components/ResidentsList';
import AddNews from './components/AddNews';
import NewsList from './components/NewsList';
import AddEvent from './components/AddEvent';
import EventsList from './components/EventsList';
import Notifications from './components/Notifications';
import Navbar from './components/Navbar';

function App() {
  return (
    <div className="App">
      <Navbar />
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<Login />} />
        <Route path="/logout" element={<Logout />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/residents" element={<ResidentsList />} />
        <Route path="/add-resident" element={<AddResident />} />
        <Route path="/news" element={<NewsList />} />
        <Route path="/add-news" element={<AddNews />} />
        <Route path="/events" element={<EventsList />} />
        <Route path="/add-event" element={<AddEvent />} />
        <Route path="/notifications" element={<Notifications />} />
      </Routes>
    </div>
  );
}

export default App;
