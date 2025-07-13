import React, { useState, useEffect } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  useNavigate,
} from "react-router-dom";
import CategoryList from "./components/CategoryList";
import JobSelector from "./components/JobSelector";
import ProfileForm from "./components/ProfileForm";
import JobAssistant from "./components/JobAssistant";
import JobDashboard from "./components/JobDashboard";
import { api } from "./services/api";
import "./App.css";

function MainApp() {
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [selectedJob, setSelectedJob] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  // Reset job on category change
  useEffect(() => {
    setSelectedJob(null);
  }, [selectedCategory]);

  // Summary state
  const [summaryData, setSummaryData] = useState(null);

  // Discover click handler
  const handleDiscover = async () => {
    setLoading(true);
    setSummaryData(null);
    try {
      // Pre-fetch job details
      const jobDetails = await api.getJobDetails(selectedJob);

      // Summarize all 3 sections in parallel (with timeout)
      // const timeoutPromise = new Promise(
      //   (_, reject) =>
      //     setTimeout(() => reject(new Error("LLM timeout")), 120000) // 60s timeout 2min
      // );
      const summariesPromise = Promise.all([
        api.askLLM(
          jobDetails.JobTitle,
          `For the job title "${
            jobDetails.JobTitle
          }", respond in a direct and formal style. Do not start with words like 'Absolutely!', 'Certainly!', 'Sure!', or similar. Explain in detail what each of the following necessary skills means and why it is important for the job. List each skill separately, start with the skill name in bold, then give a short, practical explanation:\n${jobDetails.Skills?.map(
            (s) => `- ${s}`
          ).join("\n")}`
        ),
        api.askLLM(
          jobDetails.JobTitle,
          `For the job title "${
            jobDetails.JobTitle
          }", respond in a direct and formal style. Do not start with words like 'Absolutely!', 'Certainly!', 'Sure!', or similar. Here are important factors for success. Please list each factor in bold, then give a concise, practical explanation of how it helps someone succeed:\n${jobDetails.Factors?.map(
            (f) => `- ${f}`
          ).join("\n")}`
        ),
        api.askLLM(
          jobDetails.JobTitle,
          `For the job title "${
            jobDetails.JobTitle
          }", respond in a direct and formal style. Do not start with words like 'Absolutely!', 'Certainly!', 'Sure!', or similar. Explain step by step how someone can get this job. List each step or requirement in bold, then add a short explanation or tip:\n${jobDetails.HowToGet?.map(
            (h) => `- ${h}`
          ).join("\n")}`
        ),
      ]);
      const [skillsRes, factorsRes, howToGetRes] = await Promise.race([
        summariesPromise,
        // timeoutPromise,
      ]);
      setSummaryData({
        jobDetails,
        summaries: {
          skills: skillsRes?.answer || "No summary.",
          factors: factorsRes?.answer || "No summary.",
          howToGet: howToGetRes?.answer || "No summary.",
        },
      });

      // Navigate and pass pre-fetched data
      navigate(`/profile/${encodeURIComponent(selectedJob)}`, {
        state: {
          jobDetails,
          summaries: {
            skills: skillsRes?.answer || "No summary.",
            factors: factorsRes?.answer || "No summary.",
            howToGet: howToGetRes?.answer || "No summary.",
          },
        },
      });
    } catch (err) {
      alert("Failed to generate summary. Try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="main-container">
      <div className="header">
        <h1>Career Guide</h1>
        <p className="subtitle">Discover, Plan, and Track Your Path</p>
      </div>
      <div className="content-card">
        <CategoryList
          onSelect={setSelectedCategory}
          selected={selectedCategory}
        />
        {selectedCategory && (
          <JobSelector
            category={selectedCategory}
            onSelect={setSelectedJob}
            selectedJob={selectedJob}
          />
        )}

        {loading && (
          <div className="loading-overlay">
            <div className="spinner"></div>
            <div className="loading-text">Gathering Information...</div>
          </div>
        )}

        {selectedJob && (
          <button
            className="discover-btn"
            disabled={loading}
            onClick={handleDiscover}
          >
            {loading ? "Loading..." : "Discover"}
          </button>
        )}
      </div>
    </div>
  );
}

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<MainApp />} />
        <Route path="/profile/:jobTitle" element={<ProfileForm />} />
        <Route path="/dashboard/:jobTitle" element={<JobDashboard />} />
        <Route path="/AI/:jobTitle" element={<JobAssistant />} />
      </Routes>
    </Router>
  );
}
