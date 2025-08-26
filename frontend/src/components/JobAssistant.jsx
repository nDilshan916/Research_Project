import React, { useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "../services/api";
import { marked } from "marked";
import DOMPurify from "dompurify";
import "../App.css";

function renderMarkdown(text) {
  // Parse markdown and sanitize HTML for security
  return DOMPurify.sanitize(marked(text, { breaks: true }));
}

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

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleAsk();
    }
  };

  return (
    <div className="main-container" style={{ maxWidth: 680 }}>
      <h2
        className="jobtitle"
        style={{ textAlign: "center", marginBottom: 24 }}
      >
        Ask AI about: {decodeURIComponent(jobTitle || "")}
      </h2>
      <textarea
        placeholder="Type your question about this job..."
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        onKeyDown={handleKeyDown}
        rows={3}
        style={{
          width: "100%",
          fontSize: "1.1rem",
          borderRadius: 10,
          border: "1.5px solid #e0e7ff",
          padding: 12,
          marginBottom: 14,
          background: "#f7faff",
        }}
        disabled={loading}
      />
      <button
        className="dashboard-btn"
        onClick={handleAsk}
        disabled={loading || !question.trim() || !jobTitle}
        style={{ marginBottom: 12 }}
      >
        {loading ? "Asking..." : "Ask AI"}
      </button>
      <div style={{ marginTop: 24, minHeight: 120, position: "relative" }}>
        {loading && (
          <div
            className="loading-overlay"
            style={{ position: "absolute", inset: 0, borderRadius: 16 }}
          >
            <div className="spinner"></div>
            <div className="loading-text">Thinking...</div>
          </div>
        )}
        {!loading && answer && (
          <div
            className="ai-response-box"
            dangerouslySetInnerHTML={{ __html: renderMarkdown(answer) }}
          />
        )}
      </div>
    </div>
  );
}
