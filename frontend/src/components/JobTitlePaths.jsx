import React, { useState, useEffect } from "react";
import { api } from "../services/api";

export default function JobTitlePaths({ jobTitle }) {
  const [paths, setPaths] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!jobTitle) {
      setPaths(null);
      return;
    }
    setLoading(true);
    setError(null);
    api
      .getJobTitleClusters(jobTitle)
      .then((data) => setPaths(data))
      .catch((err) => {
        setError("Failed to load job paths.");
        setPaths(null);
      })
      .finally(() => setLoading(false));
  }, [jobTitle]);

  if (!jobTitle) return null;
  if (loading) return <div>Loading profile paths...</div>;
  if (error) return <div className="text-red-500">{error}</div>;
  if (!paths || Object.keys(paths).length === 0) return null;
  if (paths.error || paths.message) return <div>{paths.error || paths.message}</div>;

  return (
    <div className="mb-4 p-3 bg-yellow-50 rounded">
      <h2 className="text-lg font-semibold mb-2">Profile Paths for "{jobTitle}"</h2>
      <div className="space-y-3">
        {Object.entries(paths).map(([cluster, info]) => (
          <div key={cluster} className="p-2 border rounded bg-white">
            <div className="font-medium mb-1">{cluster} (Profiles: {info.Size})</div>
            <div>
              <strong>Top Skills:</strong> {info.TopSkills.join(", ") || "N/A"}
            </div>
            <div>
              <strong>Top Factors:</strong> {info.TopFactors.join(", ") || "N/A"}
            </div>
            <div>
              <strong>Example Titles:</strong>{" "}
              {(info.FilteredJobTitles || []).join(", ") || "N/A"}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}