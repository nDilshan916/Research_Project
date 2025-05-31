import React, { useState, useEffect } from "react";
import CategoryList from "./components/CategoryList";
import JobSelector from "./components/JobSelector";
import ProfileForm from "./components/ProfileForm";
import PredictionResult from "./components/PredictionResult";
import JobTitlePaths from "./components/JobTitlePaths";

export default function App() {
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [selectedJob, setSelectedJob] = useState(null);
  const [result, setResult] = useState(null);

  // Reset job and result on category change
  useEffect(() => {
    setSelectedJob(null);
    setResult(null);
  }, [selectedCategory]);

  // Reset result on job change
  useEffect(() => {
    setResult(null);
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
    </div>
  );
}