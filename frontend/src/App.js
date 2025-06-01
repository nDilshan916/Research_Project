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
import PredictionResult from "./components/PredictionResult";
import JobTitlePaths from "./components/JobTitlePaths";
import JobDashboard from "./components/JobDashboard";

function MainApp() {
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [selectedJob, setSelectedJob] = useState(null);
  const [result, setResult] = useState(null);
  const navigate = useNavigate();

  // Reset job and result on category change
  useEffect(() => {
    setSelectedJob(null);
    setResult(null);
  }, [selectedCategory]);

  // Reset result on job change
  useEffect(() => {
    setResult(null);
  }, [selectedJob]);

  useEffect(() => {
    if (selectedJob) {
      console.log("Selected job:", selectedJob);
    }
  }, [selectedJob]);

  return (
    <div className="p-4">
      <h1 className="text-xl font-bold mb-4">AI Career Guide</h1>
      <CategoryList onSelect={setSelectedCategory} />
      {selectedCategory && (
        <JobSelector
          category={selectedCategory}
          onSelect={setSelectedJob}
          selectedJob={selectedJob}
        />
      )}
      {selectedJob && (
        <>
          <JobTitlePaths jobTitle={selectedJob} />
          <ProfileForm selectedJobTitle={selectedJob} />
        </>
      )}
      {result && <PredictionResult result={result} />}

      {selectedJob && (
        <button
          className="mt-4 bg-blue-500 text-white px-4 py-2 rounded"
          onClick={() => {
            if (selectedJob) {
              console.log("Navigating to dashboard for job:", selectedJob);
              navigate(`/dashboard/${encodeURIComponent(selectedJob)}`);
            } else {
              alert("Please select a job first.");
            }
          }}
        >
          View Dashboard
        </button>
      )}
    </div>
  );
}

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<MainApp />} />
        <Route path="/dashboard/:jobTitle" element={<JobDashboard />} />
      </Routes>
    </Router>
  );
}
