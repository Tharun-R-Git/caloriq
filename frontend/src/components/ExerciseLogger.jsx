import { useState, useEffect, useCallback } from 'react'
import { logExercise, getTodayExercise, deleteExercise } from '../api/api'

const INTENSITIES = [
  { value: 'light',    label: 'Light',    color: 'text-green-600' },
  { value: 'moderate', label: 'Moderate', color: 'text-yellow-600' },
  { value: 'vigorous', label: 'Vigorous', color: 'text-red-600' },
]

const empty = { name: '', duration_minutes: '', intensity: 'moderate' }

function Spinner() {
  return (
    <span className="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
  )
}

function BurnBadge({ calories }) {
  return (
    <span className="text-xs font-semibold bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full">
      {calories} kcal burned
    </span>
  )
}

function TodayList({ entries, onDelete, totalBurned }) {
  if (entries.length === 0) return (
    <div className="bg-white rounded-2xl shadow-sm p-4">
      <p className="text-sm text-gray-400 text-center">No exercise logged today yet.</p>
    </div>
  )

  const intensityColor = { light: 'text-green-600', moderate: 'text-yellow-600', vigorous: 'text-red-600' }

  return (
    <div className="bg-white rounded-2xl shadow-sm p-4 space-y-1">
      <div className="flex justify-between items-center mb-2">
        <h3 className="font-semibold text-gray-800 text-sm">Today</h3>
        <span className="text-sm font-bold text-blue-500">{totalBurned} kcal burned</span>
      </div>
      <ul className="divide-y divide-gray-100">
        {entries.map((e) => (
          <li key={e.id} className="flex justify-between items-center py-2">
            <div className="min-w-0 flex-1">
              <p className="text-sm font-medium text-gray-700 truncate capitalize">{e.name}</p>
              <p className="text-xs text-gray-400">
                {e.duration_minutes} min
                <span className={`ml-1 capitalize font-medium ${intensityColor[e.intensity] || 'text-gray-400'}`}>
                  · {e.intensity}
                </span>
                <span className="ml-1 text-gray-300">· {e.calories_burned} kcal</span>
              </p>
            </div>
            <button
              onClick={() => onDelete(e.id)}
              className="ml-3 text-xs text-red-400 hover:text-red-600 font-medium shrink-0"
            >
              Remove
            </button>
          </li>
        ))}
      </ul>
    </div>
  )
}

export default function ExerciseLogger({ onAdd }) {
  const [form, setForm] = useState(empty)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [lastResult, setLastResult] = useState(null)
  const [todayEntries, setTodayEntries] = useState([])

  const loadToday = useCallback(async () => {
    try {
      const data = await getTodayExercise()
      setTodayEntries(data.entries)
    } catch {
      // silent — today list is non-critical
    }
  }, [])

  useEffect(() => { loadToday() }, [loadToday])

  const set = (k, v) => setForm((f) => ({ ...f, [k]: v }))

  const submit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setLastResult(null)
    try {
      const result = await logExercise({
        name: form.name.trim(),
        duration_minutes: Number(form.duration_minutes),
        intensity: form.intensity,
      })
      setLastResult(result)
      setForm(empty)
      await loadToday()
      onAdd?.()
    } catch (err) {
      setError(err.message || 'Failed to log exercise')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id) => {
    await deleteExercise(id)
    await loadToday()
    onAdd?.()
  }

  const totalBurned = Math.round(todayEntries.reduce((s, e) => s + (e.calories_burned || 0), 0))

  return (
    <div className="space-y-4">
      <form onSubmit={submit} className="bg-white rounded-2xl shadow-sm p-4 space-y-3">
        <h3 className="font-semibold text-gray-800">Log Exercise</h3>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-3 text-xs text-red-600">{error}</div>
        )}

        {lastResult && (
          <div className="bg-blue-50 border border-blue-200 rounded-xl p-3 flex items-center justify-between">
            <p className="text-xs text-blue-700 font-medium capitalize">{lastResult.name} logged!</p>
            <BurnBadge calories={lastResult.calories_burned} />
          </div>
        )}

        <input
          required
          className="input"
          placeholder="e.g. running, swimming, gym"
          value={form.name}
          onChange={(e) => { set('name', e.target.value); setLastResult(null) }}
        />

        <div className="grid grid-cols-2 gap-2">
          <input
            required
            type="number"
            min="1"
            className="input"
            placeholder="Duration (min)"
            value={form.duration_minutes}
            onChange={(e) => set('duration_minutes', e.target.value)}
          />
          <select
            className="input"
            value={form.intensity}
            onChange={(e) => set('intensity', e.target.value)}
          >
            {INTENSITIES.map(({ value, label }) => (
              <option key={value} value={value}>{label}</option>
            ))}
          </select>
        </div>

        <button
          type="submit"
          disabled={loading || !form.name.trim() || !form.duration_minutes}
          className="w-full bg-blue-500 text-white py-2 rounded-xl font-medium text-sm flex items-center justify-center gap-2 disabled:opacity-50 active:bg-blue-600"
        >
          {loading ? <><Spinner /> Logging…</> : 'Log Exercise'}
        </button>
      </form>

      <TodayList entries={todayEntries} onDelete={handleDelete} totalBurned={totalBurned} />
    </div>
  )
}
