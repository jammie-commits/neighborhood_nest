import React from 'react';
import { Link, useNavigate } from 'react-router-dom';

const Navbar = () => {
    const navigate = useNavigate();

    const handleLogout = () => {
        // Clear local storage
        localStorage.removeItem('token');
        localStorage.removeItem('neighborhood_id');

        // Redirect to the login page
        navigate('/login');
    };

    return (
        <nav className="bg-blue-600 text-white p-4 flex justify-between items-center">
            <ul className="flex space-x-4">
                <li>
                    <Link to="/dashboard">Dashboard</Link>
                </li>
                <li>
                    <Link to="/residents">Residents</Link>
                </li>
                <li>
                    <Link to="/news">News</Link>
                </li>
                <li>
                    <Link to="/events">Events</Link>
                </li>
                <li>
                    <Link to="/notifications">Notifications</Link>
                </li>
            </ul>
            <button
                onClick={handleLogout}
                className="bg-red-600 text-white py-2 px-4 rounded"
            >
                Logout
            </button>
        </nav>
    );
};

export default Navbar;
