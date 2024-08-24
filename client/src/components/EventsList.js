import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';

const EventsList = () => {
    const [events, setEvents] = useState([]);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchEvents = async () => {
            try {
                const token = localStorage.getItem('token');
                const neighborhoodId = localStorage.getItem('neighborhood_id');

                if (!neighborhoodId) {
                    throw new Error('Neighborhood ID not found');
                }

                const response = await axios.get(`http://localhost:5000/neighborhoods/${neighborhoodId}/events`, {
                    headers: { Authorization: `Bearer ${token}` },
                });

                setEvents(response.data);
            } catch (error) {
                toast.error('Failed to fetch events');
                console.error('Error fetching events:', error);
            }
        };

        fetchEvents();
    }, []);

    const handleDelete = async (id) => {
        try {
            const token = localStorage.getItem('token');
            await axios.delete(`http://localhost:5000/events/${id}`, {
                headers: { Authorization: `Bearer ${token}` },
            });
            setEvents(events.filter((event) => event.id !== id));
            toast.success('Event deleted successfully');
        } catch (error) {
            toast.error('Failed to delete event');
            console.error('Error deleting event:', error);
        }
    };

    return (
        <div className="p-4">
            <h2 className="text-2xl mb-4">Events List</h2>
            <button
                className="mb-4 bg-blue-600 text-white py-2 px-4 rounded"
                onClick={() => navigate('/add-event')}
            >
                Add Event
            </button>
            <ul>
                {events.map((event) => (
                    <li key={event.id} className="mb-4 border-b pb-2">
                        <h3>{event.name}</h3>
                        <p>{event.date}</p>
                        <p>{event.location}</p>
                        <button
                            className="ml-4 text-red-600"
                            onClick={() => handleDelete(event.id)}
                        >
                            Delete
                        </button>
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default EventsList;
