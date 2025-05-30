import React, { useState } from 'react';
import { api } from '../services/api';

export default function ProfileForm({ job, onResult }) {
  const [skills, setSkills] = useState("");
  const [subjects, setSubjects] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    try {
      // Use the API service instead of direct fetch
      const data = await api.predictSkills(
        job, 
        skills.split(',').map(s => s.trim()).filter(Boolean),
        subjects.split(',').map(s => s.trim()).filter(Boolean)
      );
      onResult(data);
    } catch (err) {
      console.error("Error predicting skills:", err);
      setError("Failed to predict skill gaps. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="mb-4">
      <h2 className="font-semibold mb-2">Your Background</h2>
      <input 
        type="text" 
        className="border p-2 mr-2 w-full mb-2" 
        placeholder="Your skills (comma separated)" 
        value={skills} 
        onChange={e => setSkills(e.target.value)} 
      />
      <input 
        type="text" 
        className="border p-2 mr-2 w-full mb-2" 
        placeholder="Your subjects (comma separated)" 
        value={subjects} 
        onChange={e => setSubjects(e.target.value)} 
      />
      <button 
        className="bg-green-500 text-white px-4 py-2 disabled:bg-gray-400" 
        type="submit"
        disabled={loading}
      >
        {loading ? "Processing..." : "Predict Gaps"}
      </button>
      {error && <div className="mt-2 text-red-500">{error}</div>}
    </form>
  );
}