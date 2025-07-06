import React, { useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "../services/api";
import "../App.css"; // Make sure App.css contains spinner/loading styles

export default function JobAIAssistant() {
  const { jobTitle } = useParams();
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);

  const handleAsk = async () => {
    if (!jobTitle || !question.trim()) return;
    setLoading(true);
    setAnswer("");
    try {
      const res = await api.askLLM(jobTitle, question);
      setAnswer(res.answer || "No answer received.");
    } catch (e) {
      setAnswer("Sorry, failed to get a response from AI.");
    }
    setLoading(false);
  };

  return (
    <div className="main-container" style={{ maxWidth: 600 }}>
      <h2 className="jobtitle">
        Ask AI about: {decodeURIComponent(jobTitle || "")}
      </h2>
      <textarea
        placeholder="Type your question about this job..."
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        rows={3}
        style={{
          width: "100%",
          fontSize: "1.1rem",
          borderRadius: 10,
          border: "1.5px solid #e0e7ff",
          padding: 12,
          marginBottom: 14,
        }}
        disabled={loading}
      />
      <button
        className="dashboard-btn"
        onClick={handleAsk}
        disabled={loading || !question.trim() || !jobTitle}
      >
        {loading ? "Asking..." : "Ask AI"}
      </button>
      <div style={{ marginTop: 32, minHeight: 120, position: "relative" }}>
        {loading && (
          <div
            className="loading-overlay"
            style={{ position: "absolute", inset: 0 }}
          >
            <div className="spinner"></div>
            <div className="loading-text">AI is thinking...</div>
          </div>
        )}
        {!loading && answer && (
          <div
            style={{
              background: "#f3f6fd",
              borderRadius: 12,
              padding: "18px 20px",
              color: "#212b3c",
              boxShadow: "0 2px 8px 0 rgba(80, 112, 255, 0.08)",
              fontSize: "1.13rem",
            }}
          >
            <strong style={{ color: "#4666ff" }}>AI says:</strong>
            <div style={{ whiteSpace: "pre-wrap", marginTop: 8 }}>{answer}</div>
          </div>
        )}
      </div>
    </div>
  );
}
