import React from 'react';
import { useNavigate } from 'react-router-dom';

const Logout = () => {
    const navigate = useNavigate();

    const handleLogout = () => {
        // Clear the local storage
        localStorage.removeItem('token');
        localStorage.removeItem('neighborhood_id');

        // Optionally, you can also make a request to your backend to inform it of the logout
        // Example: 
        // axios.post('http://localhost:5000/logout', {}, {
        //     headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        // }).then(() => {
        //     // Handle successful logout
        // }).catch((error) => {
        //     // Handle error
        // });

        // Redirect to the login page
        navigate('/login');
    };

    return (
        <div className="flex justify-center items-center h-screen">
            <button
                onClick={handleLogout}
                className="bg-red-600 text-white py-2 px-4 rounded"
            >
                Logout
            </button>
        </div>
    );
};

export default Logout;
