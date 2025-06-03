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
// import PredictionResult from "./components/PredictionResult";
import JobDashboard from "./components/JobDashboard";
import "./App.css"; // Import the new CSS for better styles

function MainApp() {
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [selectedJob, setSelectedJob] = useState(null);
  // const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  // Reset job and result on category change
  useEffect(() => {
    setSelectedJob(null);
    // setResult(null);
  }, [selectedCategory]);

  // Reset result on job change
  useEffect(() => {
    // setResult(null);
  }, [selectedJob]);

  useEffect(() => {
    if (selectedJob) {
      console.log("Selected job:", selectedJob);
    }
  }, [selectedJob]);

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
            <div className="loading-text">Loading...</div>
          </div>
        )}

        {selectedJob && (
          <button
            className="discover-btn"
            disabled={loading}
            onClick={() => {
              setLoading(true);
              setTimeout(() => {
                navigate(`/profile/${encodeURIComponent(selectedJob)}`);
                setLoading(false);
              }, 2000);
            }}
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
      </Routes>
    </Router>
  );
}
