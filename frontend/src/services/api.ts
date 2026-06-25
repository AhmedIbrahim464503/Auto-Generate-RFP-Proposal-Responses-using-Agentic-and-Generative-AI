const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export async function fetchFromAPI(endpoint: string, options: RequestInit = {}) {
  const headers = {
    "Content-Type": "application/json",
    ...options.headers,
  };

  const response = await fetch(`${BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    throw new Error(errorBody.message || `API error: ${response.status}`);
  }

  return response.json();
}

export const apiService = {
  getHealth: () => fetchFromAPI("/health"),
  getReadiness: () => fetchFromAPI("/readiness"),
  getVersion: () => fetchFromAPI("/version"),
};
