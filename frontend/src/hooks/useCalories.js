import { useState, useEffect, useCallback } from 'react'
import { getFoodEntries, getExerciseEntries, getDailySummary } from '../api/api'

export function useCalories(date) {
  const [foodEntries, setFoodEntries] = useState([])
  const [exerciseEntries, setExerciseEntries] = useState([])
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const load = useCallback(async () => {
    if (!date) return
    setLoading(true)
    setError(null)
    try {
      const [food, exercise, daily] = await Promise.all([
        getFoodEntries(date),
        getExerciseEntries(date),
        getDailySummary(date),
      ])
      setFoodEntries(food)
      setExerciseEntries(exercise)
      setSummary(daily)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }, [date])

  useEffect(() => {
    load()
  }, [load])

  return { foodEntries, exerciseEntries, summary, loading, error, refresh: load }
}
