// import React from 'react';

// export default function PredictionResult({ result }) {
//   if (!result || (result.MissingSkills?.length === 0 && result.MissingSubjects?.length === 0)) {
//     return null;
//   }

//   if (result.error) {
//     return <div className="p-4 mt-4 bg-red-100 rounded text-red-700">{result.error}</div>
//   }

//   return (
//     <div className="mt-4">
//       <h2 className="text-lg font-semibold mb-2">Recommendation Results</h2>
      
//       {result.JobMatches && result.JobMatches.length > 0 && (
//         <div className="mb-4">
//           <h3 className="font-medium">Matching Jobs:</h3>
//           <div className="flex flex-wrap gap-1 mt-1">
//             {result.JobMatches.map(job => (
//               <span key={job} className="px-2 py-1 bg-gray-100 text-sm rounded">
//                 {job}
//               </span>
//             ))}
//           </div>
//         </div>
//       )}
      
//       <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
//         <div className="p-3 bg-blue-50 rounded">
//           <h3 className="font-medium mb-2">Recommended Skills</h3>
//           {result.MissingSkills?.length > 0 ? (
//             <ul>
//               {result.MissingSkills.map(skill => (
//                 <li key={skill.name} className="mb-1 flex justify-between">
//                   <span>{skill.name}</span>
//                   <span className="text-blue-700">{Math.round(skill.relevance * 100)}%</span>
//                 </li>
//               ))}
//             </ul>
//           ) : (
//             <p>No skill gaps identified!</p>
//           )}
//         </div>
        
//         <div className="p-3 bg-green-50 rounded">
//           <h3 className="font-medium mb-2">Recommended Subjects</h3>
//           {result.MissingSubjects?.length > 0 ? (
//             <ul>
//               {result.MissingSubjects.map(subject => (
//                 <li key={subject.name} className="mb-1 flex justify-between">
//                   <span>{subject.name}</span>
//                   <span className="text-green-700">{Math.round(subject.relevance * 100)}%</span>
//                 </li>
//               ))}
//             </ul>
//           ) : (
//             <p>No subject gaps identified!</p>
//           )}
//         </div>
//       </div>
      
//       <div className="mt-4 text-sm text-gray-600">
//         Based on {result.JobMatchCount} similar job profiles
//       </div>
//     </div>
//   );
// }