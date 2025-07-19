const API_BASE_URL = "http://localhost:5001";

/**
 * Generic API request function with error handling
 */
async function apiRequest(endpoint, options = {}) {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...(options.headers || {}),
      },
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`API request failed: ${endpoint}`, error);
    throw error;
  }
}

export const api = {
  getCategories: () => apiRequest("/categories"),
  getJobs: (category) => apiRequest(`/jobs/${encodeURIComponent(category)}`),
  getCategoryDetails: (category) =>
    apiRequest(`/category/${encodeURIComponent(category)}`),
  predictSkills: (jobTitle, skills, subjects) =>
    apiRequest("/predict", {
      method: "POST",
      body: JSON.stringify({ job_title: jobTitle, skills, subjects }),
    }),
  getJobDetails: (jobTitle) =>
    apiRequest(`/job_details/${encodeURIComponent(jobTitle)}`),
  getJobTitleClusters: (jobTitle, clusters = 5) =>
    apiRequest(
      `/job_title_clusters/${encodeURIComponent(jobTitle)}?clusters=${clusters}`
    ),
  askLLM: async (jobTitle, question) => {
    const response = await fetch(`${API_BASE_URL}/api/ai-assistant`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ jobTitle, question }),
    });
    if (!response.ok) throw new Error("AI API error");
    return await response.json();
  },
};
