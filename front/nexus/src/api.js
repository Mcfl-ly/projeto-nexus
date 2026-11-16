// Only this public URL is exposed to the browser. Secrets belong in the API.
export const API_BASE_URL = (import.meta.env.VITE_API_URL ?? (import.meta.env.DEV ? "http://localhost:8000" : "")).replace(/\/$/, "");
export const apiUrl = (path) => API_BASE_URL + path;
