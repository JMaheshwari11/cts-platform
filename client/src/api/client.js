import axios from "axios"

// In production (Vercel) we set VITE_API_BASE to the Render backend URL.
// In dev it stays empty so Vite's proxy forwards /api to localhost:8000.
const API_BASE = import.meta.env.VITE_API_BASE || ""

export const apiClient = axios.create({
  baseURL: `${API_BASE}/api/v1`,
  headers: { "Content-Type": "application/json" },
  timeout: 30000,
})

apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error("API Error:", error.response?.data || error.message)
    return Promise.reject(error)
  }
)

export default apiClient
