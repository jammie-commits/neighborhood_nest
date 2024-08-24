// src/components/Notifications.js
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { toast } from 'react-toastify';

const Notifications = () => {
    const [notifications, setNotifications] = useState([]);

    useEffect(() => {
        const fetchNotifications = async () => {
            try {
                const token = localStorage.getItem('token');
                const response = await axios.get('http://localhost:5000/notifications', {
                    headers: { Authorization: `Bearer ${token}` },
                });
                setNotifications(response.data);
            } catch (error) {
                toast.error('Failed to fetch notifications');
            }
        };

        fetchNotifications();
    }, []);

    return (
        <div className="p-4">
            <h2 className="text-2xl mb-4">Notifications</h2>
            <ul>
                {notifications.map((notification) => (
                    <li key={notification.id} className="mb-4 border-b pb-2">
                        <p>{notification.message}</p>
                        <span className="text-gray-600 text-sm">{notification.timestamp}</span>
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default Notifications;
