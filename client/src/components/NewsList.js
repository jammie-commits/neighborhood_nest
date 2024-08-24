// src/components/NewsList.js
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';

const NewsList = () => {
    const [news, setNews] = useState([]);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchNews = async () => {
            try {
                const token = localStorage.getItem('token');
                const neighborhoodId = localStorage.getItem('neighborhood_id'); // Retrieve neighborhood ID from local storage

                if (!neighborhoodId) {
                    throw new Error('Neighborhood ID not found');
                }

                const response = await axios.get(`http://localhost:5000/neighborhoods/${neighborhoodId}/news`, {
                    headers: { Authorization: `Bearer ${token}` },
                });

                setNews(response.data);
            } catch (error) {
                toast.error('Failed to fetch news');
                console.error('Error fetching news:', error); // Log the error for debugging
            }
        };

        fetchNews();
    }, []);

    const handleDelete = async (id) => {
        try {
            const token = localStorage.getItem('token');
            await axios.delete(`http://localhost:5000/news/${id}`, {
                headers: { Authorization: `Bearer ${token}` },
            });
            setNews(news.filter((item) => item.id !== id));
            toast.success('News deleted successfully');
        } catch (error) {
            toast.error('Failed to delete news');
            console.error('Error deleting news:', error); // Log the error for debugging
        }
    };

    return (
        <div className="p-4">
            <h2 className="text-2xl mb-4">News List</h2>
            <button
                className="mb-4 bg-blue-600 text-white py-2 px-4 rounded"
                onClick={() => navigate('/add-news')}
            >
                Add News
            </button>
            <ul>
                {news.map((item) => (
                    <li key={item.id} className="mb-4 border-b pb-2">
                        <h3>{item.title}</h3>
                        <p>{item.content}</p>
                        <button
                            className="ml-4 text-red-600"
                            onClick={() => handleDelete(item.id)}
                        >
                            Delete
                        </button>
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default NewsList;
