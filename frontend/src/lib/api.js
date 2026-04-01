import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
})

// Response interceptor for error handling
client.interceptors.response.use(
  response => response,
  error => {
    console.error('API Error:', error.message)
    return Promise.reject(error)
  }
)

export const fetchRivers = async () => {
  try {
    const response = await client.get('/api/rivers')
    return response.data
  } catch (error) {
    console.error('Failed to fetch rivers:', error)
    throw error
  }
}

export const fetchRiverDetail = async (riverId) => {
  try {
    const response = await client.get(`/api/rivers/${riverId}`)
    return response.data
  } catch (error) {
    console.error(`Failed to fetch river ${riverId}:`, error)
    throw error
  }
}

export const fetchRiverHistory = async (riverId, days = 7) => {
  try {
    const response = await client.get(`/api/rivers/${riverId}/history`, {
      params: { days }
    })
    return response.data
  } catch (error) {
    console.error(`Failed to fetch history for river ${riverId}:`, error)
    throw error
  }
}

export const fetchHealth = async () => {
  try {
    const response = await client.get('/api/health')
    return response.data
  } catch (error) {
    console.error('Failed to fetch API health:', error)
    throw error
  }
}

export default client
