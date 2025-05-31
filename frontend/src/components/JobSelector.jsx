import React, { useState, useEffect } from "react";
import { api } from "../services/api";

export default function JobSelector({ category, onSelect, selectedJob }) {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [categoryDetails, setCategoryDetails] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);

        // Fetch jobs and category details in parallel
        const [jobsData, detailsData] = await Promise.all([
          api.getJobs(category),
          api.getCategoryDetails(category),
        ]);

        setJobs(jobsData || []);
        setCategoryDetails(detailsData);
        setError(null);
      } catch (err) {
        setError("Failed to load jobs. Please check your connection.");
        console.error("Error fetching jobs:", err);
      } finally {
        setLoading(false);
      }
    };

    if (category) {
      fetchData();
    }
  }, [category]);

  if (!category) return null;
  if (loading) return <div className="p-4">Loading jobs...</div>;
  if (error) return <div className="p-4 text-red-500">{error}</div>;
  if (jobs.length === 0)
    return <div className="p-4">No jobs found for this category.</div>;

  return (
    <div className="mb-4">
      <h2 className="text-lg font-semibold mb-2">Select a Job Title</h2>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
        {jobs.map((job) => (
          <button
            key={job}
            className={`p-2 border rounded hover:bg-gray-100 ${
              selectedJob === job ? "bg-blue-200 border-blue-500 font-bold" : ""
            }`}
            onClick={() => onSelect(job)}
          >
            {job}
          </button>
        ))}
      </div>
    </div>
  );
}
