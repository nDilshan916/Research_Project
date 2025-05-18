import React, { useState, useEffect } from "react";

function App() {
  const [jobTitle, setJobTitle] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [jobTitles, setJobTitles] = useState([]);

  // Fetch job titles on mount
  useEffect(() => {
    fetch("http://127.0.0.1:5000/api/job_titles")
      .then((res) => res.json())
      .then((data) => setJobTitles(data));
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResults([]);
    const response = await fetch("http://127.0.0.1:5000/api/search", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ category: jobTitle }),
    });
    const data = await response.json();
    setResults(data);
    setLoading(false);
  };

  return (
    <div style={{ padding: 20 }}>
      <h1>Job Search</h1>
      <form onSubmit={handleSubmit}>
        <select
          value={jobTitle}
          onChange={(e) => setJobTitle(e.target.value)}
          required
        >
          <option value="">Select a job title</option>
          {jobTitles.map((title, idx) => (
            <option key={idx} value={title}>
              {title}
            </option>
          ))}
        </select>
        <button type="submit">Search</button>
      </form>
      {loading && <p>Loading...</p>}
      <h2>Results</h2>
      {results.length === 0 && !loading && <p>No results found.</p>}
      {results.length > 0 && (
        <table border="1">
          <thead>
            <tr>
              {Object.keys(results[0]).map((key) => (
                <th key={key}>{key}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {results.map((row, idx) => (
              <tr key={idx}>
                {Object.values(row).map((val, i) => (
                  <td key={i}>{val}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default App;
