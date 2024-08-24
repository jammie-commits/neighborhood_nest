// src/components/ResidentsList.js
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';

const ResidentsList = () => {
    const [residents, setResidents] = useState([]);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchResidents = async () => {
            const neighborhoodId = localStorage.getItem('neighborhood_id');
            if (!neighborhoodId) {
                toast.error('Neighborhood ID not found');
                return;
            }

            try {
                const token = localStorage.getItem('token');
                const response = await axios.get(`http://localhost:5000/neighborhoods/${neighborhoodId}/residents`, {
                    headers: { Authorization: `Bearer ${token}` },
                });
                setResidents(response.data);
            } catch (error) {
                toast.error('Failed to fetch residents');
            }
        };

        fetchResidents();
    }, []);

    const handleDelete = async (id) => {
        if (window.confirm('Are you sure you want to delete this resident?')) {
            try {
                const token = localStorage.getItem('token');
                const url = `http://localhost:5000/residents/${id}`;
                console.log(`Sending DELETE request to: ${url}`);

                await axios.delete(url, {
                    headers: { Authorization: `Bearer ${token}` },
                });

                setResidents((prevResidents) =>
                    prevResidents.filter((resident) => resident.id !== id)
                );
                toast.success('Resident deleted successfully');
            } catch (error) {
                console.error('Delete error:', error.response ? error.response.data : error.message);
                toast.error('Failed to delete resident. Please try again.');
            }
        }
    };
    return (
        <div className="p-4">
            <h2 className="text-2xl mb-4">Residents List</h2>
            <button
                className="mb-4 bg-blue-600 text-white py-2 px-4 rounded"
                onClick={() => navigate('/add-resident')}
            >
                Add New Resident
            </button>
            <ul>
                {residents.length > 0 ? (
                    residents.map((resident) => (
                        <li key={resident.id} className="mb-4 border-b pb-2 flex justify-between items-center">
                            <span>{resident.name}</span>
                            <button
                                className="ml-4 text-red-600 hover:text-red-800"
                                onClick={() => handleDelete(resident.id)}
                            >
                                Delete
                            </button>
                        </li>
                    ))
                ) : (
                    <li>No residents found</li>
                )}
            </ul>
        </div>
    );
};

export default ResidentsList;
