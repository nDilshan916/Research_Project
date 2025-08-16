// JobDashboard.jsx
import React from "react";
import { useParams } from "react-router-dom";

function JobDashboard() {
  const { jobTitle } = useParams();
  const decodedJobTitle = decodeURIComponent(jobTitle);

  // Pass jobTitle as query param to Dash app
  const dashUrl = `/dash/?jobTitle=${encodeURIComponent(decodedJobTitle)}`;

  return (
    <div style={{ width: "100%", height: "90vh" }}>
      <iframe
        title="AI Career Dashboard"
        src={dashUrl}
        style={{ width: "100%", height: "100%", border: "none" }}
      />
    </div>
  );
}

export default JobDashboard;