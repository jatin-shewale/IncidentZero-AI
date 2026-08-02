import axios from "axios";

export const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: API_URL,
  timeout: 15000,
});

export function wsURL(path) {
  const base = API_URL.replace(/^http/, "ws");
  return `${base}${path}`;
}
