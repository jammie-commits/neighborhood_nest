// src/components/Dashboard.js
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';

const Dashboard = () => {
    const [data, setData] = useState([]);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchData = async () => {
            const token = localStorage.getItem('token');
            if (!token) {
                navigate('/login');
                toast.error('Please login first');
                return;
            }

            try {
                const response = await axios.get('http://localhost:5000/neighborhoods', {
                    headers: { Authorization: `Bearer ${token}` },
                });
                setData(response.data);
            } catch (error) {
                toast.error('Failed to fetch data');
                navigate('/login');
            }
        };

        fetchData();
    }, [navigate]);

    return (
        <div className="p-4">
            <h1 className="text-3xl mb-4">Dashboard</h1>
            <ul>
                {data.map((neighborhood) => (
                    <li key={neighborhood.id}>{neighborhood.name}</li>
                ))}
            </ul>
        </div>
    );
};

export default Dashboard;
