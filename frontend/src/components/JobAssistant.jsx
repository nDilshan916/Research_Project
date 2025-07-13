import React, { useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "../services/api";
import "../App.css";

function renderMarkdown(text) {
  // Basic markdown for bold, italics, lists, headers
  let html = text
    .replace(/^### (.*)$/gm, '<div class="ai-md-h3">$1</div>')
    .replace(/^---$/gm, '<hr class="ai-md-hr"/>')
    .replace(/\*\*(.*?)\*\*/g, '<b>$1</b>')
    .replace(/\*(.*?)\*/g, '<i>$1</i>')
    .replace(/^-\s(.*)$/gm, '<li>$1</li>')
    .replace(/<li>([\s\S]*?)<\/li>/gm, '<ul class="ai-md-list"><li>$1</li></ul>')
    .replace(/\n{2,}/g, '<br/>')
    .replace(/\n/g, ' ');

  // Remove duplicate <ul> from multiple lines
  html = html.replace(/(<ul class="ai-md-list">)+/g, '<ul class="ai-md-list">');
  html = html.replace(/(<\/ul>)+/g, '</ul>');
  return html;
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
      <h2 className="jobtitle" style={{ textAlign: "center", marginBottom: 24 }}>
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
            style={{
              background: "linear-gradient(120deg, #f6f8fd 85%, #edf9fc 100%)",
              borderRadius: 16,
              padding: "24px 26px",
              color: "#212b3c",
              boxShadow: "0 2px 16px 0 rgba(80, 112, 255, 0.09)",
              fontSize: "1.13rem",
              marginBottom: 20,
              border: "1.5px solid #e8edfa",
              lineHeight: 1.7,
            }}
            dangerouslySetInnerHTML={{ __html: renderMarkdown(answer) }}
          />
        )}
      </div>
    </div>
  );
}