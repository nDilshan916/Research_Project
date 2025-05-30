import React, { useState } from 'react';

export default function RecommendationForm({ setRecommendations }) {
  const [careerPath, setCareerPath] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    const res = await fetch('http://localhost:5000/recommend', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ careerPath }),
    });
    const data = await res.json();
    setRecommendations(data);
  };

  return (
    <form onSubmit={handleSubmit} className="mb-4">
      <input
        type="text"
        className="border p-2 mr-2"
        placeholder="Enter desired career path"
        value={careerPath}
        onChange={(e) => setCareerPath(e.target.value)}
      />
      <button className="bg-blue-500 text-white px-4 py-2" type="submit">
        Recommend
      </button>
    </form>
  );
}