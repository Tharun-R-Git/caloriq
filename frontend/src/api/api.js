const BASE = '/api'

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  })
  if (!res.ok) throw new Error(await res.text())
  if (res.status === 204) return null
  return res.json()
}

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
