import React, { useState, useEffect } from "react";
import { api } from "../services/api";

export default function ProfileForm({ selectedJobTitle }) {
  const [jobDetails, setJobDetails] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!selectedJobTitle) {
      setJobDetails(null);
      return;
    }
    setLoading(true);
    setError(null);
    api
      .getJobDetails(selectedJobTitle)
      .then((data) => setJobDetails(data))
      .catch((err) => setError("Failed to load job details."))
      .finally(() => setLoading(false));
  }, [selectedJobTitle]);

  if (!selectedJobTitle) return null;

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
    </div>
  );
}