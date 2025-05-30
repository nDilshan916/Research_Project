import React, { useState, useEffect } from 'react';
import { api } from '../services/api';

export default function CategoryList({ onSelect }) {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        setLoading(true);
        const data = await api.getCategories();
        setCategories(data || []);
        setError(null);
      } catch (err) {
        setError('Failed to load categories. Please check if the server is running.');
        console.error('Error fetching categories:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchCategories();
  }, []);

  if (loading) return <div className="p-4">Loading categories...</div>;
  if (error) return <div className="p-4 text-red-500">{error}</div>;
  if (categories.length === 0) return <div className="p-4">No categories found.</div>;

  return (
    <div className="mb-4">
      <h2 className="text-lg font-semibold mb-2">Select a Job Category</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
        {categories.map(category => (
          <button
            key={category}
            className="p-2 border rounded hover:bg-gray-100"
            onClick={() => onSelect(category)}
          >
            {category}
          </button>
        ))}
      </div>
    </div>
  );
}