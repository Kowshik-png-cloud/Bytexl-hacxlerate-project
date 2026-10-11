const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL ||
  "https://edupulse-api-7efl.onrender.com"
).replace(/\/+$/, "");

export async function apiRequest(endpoint, options = {}) {
  const path = endpoint.startsWith("/")
    ? endpoint
    : `/${endpoint}`;

  if (path.toLowerCase().endsWith(".csv")) {
    const response = await fetch("/data/student_analytics_1000.csv");

    if (!response.ok) {
      throw new Error(`CSV loading failed: ${response.status}`);
    }

    return response.text();
  }

  const response = await fetch(`${API_BASE_URL}${path}`, options);

  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
  }

  return response.json();
}

export { API_BASE_URL };
