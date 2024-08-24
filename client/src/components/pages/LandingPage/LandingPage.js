// src/LandingPage.js

import React from 'react';
import { Link } from 'react-router-dom';
import './LandingPage.css'; // Optional: create a CSS file for styling

const LandingPage = () => {
    return (
        <div className="landing-page">
            <header className="landing-header">
                <h1>Welcome to Neighborhood App</h1>
                <p>Your gateway to managing and connecting with your neighborhood.</p>
                <nav>
                    <Link to="/login">Login</Link>
                    <Link to="/register">Register</Link> {/* Assuming you have a register route */}
                </nav>
            </header>
        </div>
    );
};

export default LandingPage;
