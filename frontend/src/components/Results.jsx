import React from "react";

export default function Results({ recommendations }) {
  if (!recommendations.length) return null;

  return (
    <div>
      <h2 className="font-bold mt-4 mb-2">Recommendations:</h2>
      <ul>
        {recommendations.map((rec, idx) => (
          <li key={idx} className="mb-2">
            <strong>{rec.JobTitle}</strong>
            <br />
            Skills: {rec.RecommendedSkills}
            <br />
            Subjects: {rec.RecommendedSubjects}
          </li>
        ))}
      </ul>
    </div>
  );
}
