import React, { useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "../services/api"; // Or replace with your fetch logic

export default function JobAIAssistant() {
  const { jobTitle } = useParams();
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);

  const handleAsk = async () => {
    setLoading(true);
    setAnswer("");
    try {
      // You should implement this endpoint in your backend to connect to an LLM (like OpenAI, etc.)
      const res = await api.askLLM(jobTitle, question);
      setAnswer(res.answer);
    } catch (e) {
      setAnswer("Sorry, failed to get a response from AI.");
    }
    setLoading(false);
  };

  return (
    <div>
      <h2>Ask AI about: {decodeURIComponent(jobTitle)}</h2>
      <textarea
        placeholder="Type your question about this job..."
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        rows={3}
        style={{ width: "100%" }}
      />
      <button onClick={handleAsk} disabled={loading || !question.trim()}>
        {loading ? "Asking..." : "Ask AI"}
      </button>
      <div style={{ marginTop: 16 }}>
        {answer && (
          <div>
            <strong>AI says:</strong>
            <div style={{ whiteSpace: "pre-wrap", marginTop: 8 }}>{answer}</div>
          </div>
        )}
      </div>
    </div>
  );
}
