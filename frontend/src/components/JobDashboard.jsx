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
  PieChart,
  Pie,
  LineChart,
  Line,
} from "recharts";

function JobDashboard() {
  const [dashboardData, setDashboardData] = useState(null);
  const { jobTitle } = useParams();
  const decodedJobTitle = decodeURIComponent(jobTitle);

  useEffect(() => {
    if (decodedJobTitle) {
      const url = `http://localhost:5000/job_dashboard_data/${encodeURIComponent(
        decodedJobTitle
      )}`;
      fetch(url)
        .then((res) => res.json())
        .then((data) => setDashboardData(data))
        .catch((err) => {
          console.error("Error fetching dashboard data:", err);
        });
    }
  }, [decodedJobTitle]);

  if (!dashboardData) {
    return <p>Loading dashboard...</p>;
  }
  if (dashboardData.error) {
    return <p className="text-red-500 font-semibold">{dashboardData.error}</p>;
  }

  // Convert {key: value} to [{name, value}]
  const toChartData = (obj) =>
    obj && typeof obj === "object"
      ? Object.entries(obj).map(([key, value]) => ({ name: key, value }))
      : [];

  // Convert {year: count} to [{year, count}]
  const toLineChartData = (obj) =>
    obj && typeof obj === "object"
      ? Object.entries(obj).map(([year, count]) => ({ year, count }))
      : [];

  const totalDegreeCount = dashboardData.degree_counts
    ? Object.values(dashboardData.degree_counts).reduce(
        (acc, val) => acc + val,
        0
      )
    : 0;

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">
        Dashboard for: {decodedJobTitle}
      </h1>

      {!dashboardData ? (
        <p>Loading dashboard...</p>
      ) : dashboardData.error ? (
        <p className="text-red-500 font-semibold">{dashboardData.error}</p>
      ) : (
        <>
          <section className="mb-10">
            <h2 className="text-xl font-semibold mb-2">Sector Distribution</h2>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={toChartData(dashboardData.sector_counts)}>
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
            <h2 className="text-xl font-semibold mb-2">
              Department Distribution
            </h2>
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={toChartData(dashboardData.dept_counts)}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  fill="#2B6CB0"
                  label
                />
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </section>

          <section className="mb-10">
            <h2 className="text-xl font-semibold mb-2">Degree Distribution</h2>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={toChartData(dashboardData.degree_counts)}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis allowDecimals={false} domain={[0, totalDegreeCount]} />
                <Tooltip />
                <Legend />
                <Bar dataKey="value" fill="#805AD5" />
              </BarChart>
            </ResponsiveContainer>
          </section>

          <section className="mb-10">
            <h2 className="text-xl font-semibold mb-2">Growth Over Time</h2>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={toLineChartData(dashboardData.year_counts)}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="year" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="count" stroke="#2B6CB0" />
              </LineChart>
            </ResponsiveContainer>
          </section>
        </>
      )}
    </div>
  );
}

export default JobDashboard;
