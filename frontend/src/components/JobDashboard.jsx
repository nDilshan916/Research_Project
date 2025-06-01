import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
  Legend,
} from "recharts";

function JobDashboard() {
  const [jobData, setJobData] = useState(null);

  const { jobTitle } = useParams();
  console.log("Raw jobTitle param from URL:", jobTitle);

  const decodedJobTitle = decodeURIComponent(jobTitle);
  console.log("Decoded jobTitle:", decodedJobTitle);

  useEffect(() => {
    if (decodedJobTitle) {
      const url = `http://localhost:5000/job_details/${encodeURIComponent(
        decodedJobTitle
      )}`;
      console.log("Fetching job details from:", url);
      fetch(url)
        .then((res) => {
          if (!res.ok) {
            console.error("Fetch failed:", res.statusText);
            return null;
          }
          return res.json();
        })
        .then((data) => {
          console.log("Received data:", data);
          setJobData(data);
        })
        .catch((err) => {
          console.error("Error fetching job detail:", err);
        });
    }
  }, [decodedJobTitle]);

  // Helper: convert object to array of { name, value }
  const toChartData = (obj) =>
    obj && typeof obj === "object"
      ? Object.entries(obj).map(([key, value]) => ({ name: key, value }))
      : [];

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">
        Dashboard for: {decodedJobTitle}
      </h1>

      {jobData ? (
        <>
          <section className="mb-10">
            <h2 className="text-xl font-semibold mb-2">Cluster Distribution</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={toChartData(jobData.cluster_counts)}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Legend />
                <Bar dataKey="value" fill="#3182CE" />
              </BarChart>
            </ResponsiveContainer>
          </section>

          <section className="mb-10">
            <h2 className="text-xl font-semibold mb-2">Top Skills</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={toChartData(jobData.top_skills)}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Legend />
                <Bar dataKey="value" fill="#2B6CB0" />
              </BarChart>
            </ResponsiveContainer>
          </section>

          <section>
            <h2 className="text-xl font-semibold mb-2">Top Factors</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={toChartData(jobData.top_factors)}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Legend />
                <Bar dataKey="value" fill="#805AD5" />
              </BarChart>
            </ResponsiveContainer>
          </section>
        </>
      ) : (
        <p>Loading dashboard...</p>
      )}
    </div>
  );
}

export default JobDashboard;
