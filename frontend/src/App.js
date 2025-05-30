import React, { useState } from 'react';
import CategoryList from './components/CategoryList';
import JobSelector from './components/JobSelector';
import ProfileForm from './components/ProfileForm';
import PredictionResult from './components/PredictionResult';

export default function App() {
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [selectedJob, setSelectedJob] = useState(null);
  const [result, setResult] = useState(null);

  return (
    <div className="p-4">
      <h1 className="text-xl font-bold mb-4">AI Career Guide</h1>
      <CategoryList onSelect={setSelectedCategory} />
      {selectedCategory && <JobSelector category={selectedCategory} onSelect={setSelectedJob} />}
      {selectedJob && <ProfileForm job={selectedJob} onResult={setResult} />}
      {result && <PredictionResult result={result} />}
    </div>
  );
}
