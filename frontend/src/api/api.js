const BASE = (import.meta.env.VITE_API_URL || '') + '/api'

const TOKEN_KEY = 'caloriq_token'

export const getToken = () => localStorage.getItem(TOKEN_KEY)
export const setToken = (t) => localStorage.setItem(TOKEN_KEY, t)
export const clearToken = () => localStorage.removeItem(TOKEN_KEY)

async function request(path, options = {}) {
  const token = getToken()
  const res = await fetch(`${BASE}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
    ...options,
  })
  // Expired/invalid token: drop it and bounce to login (unless we're already
  // on an auth screen, e.g. a failed login attempt).
  if (res.status === 401) {
    clearToken()
    const current = window.location.pathname
    if (current !== '/login' && current !== '/register') {
      window.location.href = '/login'
    }
    throw new Error(await res.text())
  }
  if (!res.ok) throw new Error(await res.text())
  if (res.status === 204) return null
  return res.json()
}

// Auth
export const register = (email, password, name) =>
  request('/auth/register', { method: 'POST', body: JSON.stringify({ email, password, name }) })
export const login = (email, password) =>
  request('/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) })
export const getMe = () => request('/auth/me')

// Food — Gemini analysis
export const analyzeFood = (name, description) =>
  request('/food/analyze', { method: 'POST', body: JSON.stringify({ name, description }) })

export const analyzeFoodPhoto = (imageBase64, mimeType) =>
  request('/food/analyze-photo', { method: 'POST', body: JSON.stringify({ image_base64: imageBase64, mime_type: mimeType }) })

// Food — logging
export const logFood = (entry) =>
  request('/food/log', { method: 'POST', body: JSON.stringify(entry) })

// Food — queries
export const getTodayFood = () => request('/food/today')
export const getFoodHistory = () => request('/food/history')
export const deleteFood = (id) => request(`/food/${id}`, { method: 'DELETE' })

// Food — legacy (used by History page)
export const getFoodEntries = (date) => request(`/food?date=${date}`)
export const addFoodEntry = (data) => request('/food/log', { method: 'POST', body: JSON.stringify(data) })
export const deleteFoodEntry = (id) => request(`/food/${id}`, { method: 'DELETE' })

// Exercise entries
export const getExerciseEntries = (date) => request(`/exercise?date=${date}`)
export const addExerciseEntry = (data) => request('/exercise', { method: 'POST', body: JSON.stringify(data) })
export const deleteExerciseEntry = (id) => request(`/exercise/${id}`, { method: 'DELETE' })

// Exercise — new routes
export const analyzeExercise = (description, duration_minutes) =>
  request('/exercise/analyze', { method: 'POST', body: JSON.stringify({ description, duration_minutes }) })
export const logExercise = (data) => request('/exercise/log', { method: 'POST', body: JSON.stringify(data) })
export const getTodayExercise = () => request('/exercise/today')
export const deleteExercise = (id) => request(`/exercise/${id}`, { method: 'DELETE' })

// Profile
export const getProfile = () => request('/profile')
export const setupProfile = (data) => request('/profile/setup', { method: 'POST', body: JSON.stringify(data) })
export const updateProfile = (data) => request('/profile', { method: 'PUT', body: JSON.stringify(data) })
export const getProfileGoals = () => request('/profile/goals')

// Analytics
export const getDailySummary = (date) => request(`/analytics/daily?date=${date}`)
export const getDashboardSummary = () => request('/analytics/daily-summary')
export const getWeeklySummary = () => request('/analytics/weekly')
export const getTrends = (days = 30) => request(`/analytics/trends?days=${days}`)

// AI suggestions
export const getAISuggestions = () => request('/ai/suggestions')

// AI meal recommendations
export const getRecommendations = (meal_source = 'home') =>
  request(`/ai/recommendations?meal_source=${meal_source}`)
