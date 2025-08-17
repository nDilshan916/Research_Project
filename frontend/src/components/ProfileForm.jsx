import React from "react";
import { useParams, useNavigate, useLocation } from "react-router-dom";

function renderMarkdown(text) {
  let html = text
    .replace(/^### (.*)$/gm, '<div class="ai-md-h3">$1</div>')
    .replace(/^---$/gm, "<hr/>")
    .replace(/\*\*(.*?)\*\*/g, "<b>$1</b>")
    .replace(/\*(.*?)\*/g, "<i>$1</i>")
    .replace(/^- (.*)$/gm, "<li>$1</li>")
    .replace(/(<li>[\s\S]*?<\/li>)/gm, "<ul>$1</ul>");
  html = html.replace(/(<ul>)+/g, "<ul>");
  html = html.replace(/(<\/ul>)+/g, "</ul>");
  return html;
}

export default function ProfileForm() {
  const { jobTitle } = useParams();
  const navigate = useNavigate();
  const location = useLocation();

  const jobDetails = location.state?.jobDetails;
  const summaries = location.state?.summaries;

  if (!jobTitle) return null;

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        height: "100vh", // full viewport height
      }}
    >
      {/* Scrollable content */}
      <div
        style={{
          flex: 1,
          overflowY: "auto",
          padding: "20px",
        }}
      >
        {jobDetails && (
          <h2
            style={{
              marginBottom: 22,
              textAlign: "center",
              fontWeight: 700,
              color: "#2f3a56",
            }}
          >
            {jobDetails.JobTitle}
          </h2>
        )}

        <div className="profile-columns">
          <div className="profile-col">
            <div className="ai-md-h3" style={{ marginTop: 0 }}>
              Skills
            </div>
            <div
              dangerouslySetInnerHTML={{
                __html: summaries?.skills
                  ? renderMarkdown(summaries.skills)
                  : `<span style="color:#8a98af">No summary.</span>`,
              }}
            />
          </div>
          <div className="profile-col">
            <div className="ai-md-h3" style={{ marginTop: 0 }}>
              Important Factors
            </div>
            <div
              dangerouslySetInnerHTML={{
                __html: summaries?.factors
                  ? renderMarkdown(summaries.factors)
                  : `<span style="color:#8a98af">No summary.</span>`,
              }}
            />
          </div>
          <div className="profile-col">
            <div className="ai-md-h3" style={{ marginTop: 0 }}>
              How to Get
            </div>
            <div
              dangerouslySetInnerHTML={{
                __html: summaries?.howToGet
                  ? renderMarkdown(summaries.howToGet)
                  : `<span style="color:#8a98af">No summary.</span>`,
              }}
            />
          </div>
        </div>
      </div>

      {/* Fixed footer buttons */}
      <div
        style={{
          padding: "2px 10px",
          borderTop: "5px solid #ddd",
          display: "flex",
          gap: 10,
          justifyContent: "center",
          backgroundColor: "white",
          position: "sticky",
          bottom: 15,
        }}
      >
        <button
          className="dashboard-btn"
          onClick={() => {
            navigate(`/AI/${encodeURIComponent(jobTitle)}`);
          }}
        >
          Ask More
        </button>
        <button
          className="dashboard-btn"
          onClick={() => {
            navigate(`/dashboard/${encodeURIComponent(jobTitle)}`);
          }}
        >
          View Dashboard
        </button>
      </div>
    </div>
  );
}
