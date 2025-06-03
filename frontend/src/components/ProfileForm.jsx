import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom"; // <-- import this!
import { api } from "../services/api";

export default function ProfileForm() {
  const { jobTitle } = useParams(); // <-- get jobTitle from URL params!
  const navigate = useNavigate();
  const [jobDetails, setJobDetails] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!jobTitle) {
      setJobDetails(null);
      return;
    }
    setLoading(true);
    setError(null);
    api
      .getJobDetails(jobTitle)
      .then((data) => setJobDetails(data))
      .catch((err) => setError("Failed to load job details."))
      .finally(() => setLoading(false));
  }, [jobTitle]);

  if (!jobTitle) return null;

  return (
    <div>
      {loading && <div>Loading job details...</div>}
      {error && <div style={{ color: "red" }}>{error}</div>}
      {jobDetails && (
        <div className="job-details">
          <h2>{jobDetails.JobTitle}</h2>
          <div>
            <strong>Necessary Skills:</strong>{" "}
            {jobDetails.Skills?.join(", ") || "N/A"}
          </div>
          <div>
            <strong>Important Factors:</strong>{" "}
            {jobDetails.Factors?.join(", ") || "N/A"}
          </div>
          <div>
            <strong>How to Get:</strong>{" "}
            {jobDetails.HowToGet?.join(", ") || "N/A"}
          </div>
        </div>
      )}
      {
        <button
          className="dashboard-btn"
          onClick={() => {
            navigate(`/dashboard/${encodeURIComponent(jobTitle)}`);
          }}
        >
          View Dashboard
        </button>
      }
    </div>
  );
}
