import { useState, useEffect, useCallback } from 'react'
import { analyzeExercise, logExercise, getTodayExercise, deleteExercise } from '../api/api'

function Spinner() {
  return <span className="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
}

function ConfidenceBadge({ value }) {
  const pct = Math.round(value * 100)
  const color = value >= 0.8 ? 'bg-green-100 text-green-700' : value >= 0.5 ? 'bg-yellow-100 text-yellow-700' : 'bg-red-100 text-red-700'
  return <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${color}`}>{pct}% confidence</span>
}

function AnalysisCard({ result, description, duration, onLog, logging }) {
  return (
    <div className="border border-blue-200 bg-blue-50 rounded-2xl p-4 space-y-3">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-semibold text-gray-800 capitalize">{description}</p>
          <p className="text-xs text-gray-500">{duration} min · <span className="capitalize">{result.intensity}</span> · {result.exercise_type}</p>
        </div>
        <ConfidenceBadge value={result.confidence} />
      </div>
      <div className="text-center py-1">
        <p className="text-3xl font-bold text-blue-600">{result.calories_burned}</p>
        <p className="text-xs text-gray-400">kcal burned</p>
      </div>
      <button
        onClick={onLog}
        disabled={logging}
        className="w-full bg-blue-500 text-white py-2 rounded-xl font-medium text-sm flex items-center justify-center gap-2 disabled:opacity-60"
      >
        {logging ? <><Spinner /> Logging…</> : 'Log it'}
      </button>
    </div>
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
                <span className={`ml-1 capitalize font-medium ${intensityColor[e.intensity] || 'text-gray-400'}`}>· {e.intensity}</span>
                <span className="ml-1 text-gray-300">· {e.calories_burned} kcal</span>
              </p>
            </div>
            <button onClick={() => onDelete(e.id)} className="ml-3 text-xs text-red-400 hover:text-red-600 font-medium shrink-0">
              Remove
            </button>
          </li>
        ))}
      </ul>
    </div>
  )
}

export default function ExerciseLogger({ onAdd }) {
  const [description, setDescription] = useState('')
  const [duration, setDuration] = useState('')
  const [analyzing, setAnalyzing] = useState(false)
  const [logging, setLogging] = useState(false)
  const [error, setError] = useState(null)
  const [analysisResult, setAnalysisResult] = useState(null)
  const [todayEntries, setTodayEntries] = useState([])

  const loadToday = useCallback(async () => {
    try {
      const data = await getTodayExercise()
      setTodayEntries(data.entries)
    } catch { /* silent */ }
  }, [])

  useEffect(() => { loadToday() }, [loadToday])

  const handleAnalyze = async (e) => {
    e.preventDefault()
    if (!description.trim() || !duration) return
    setAnalyzing(true)
    setError(null)
    setAnalysisResult(null)
    try {
      const result = await analyzeExercise(description.trim(), Number(duration))
      setAnalysisResult(result)
    } catch (err) {
      setError(err.message || 'AI analysis failed')
    } finally {
      setAnalyzing(false)
    }
  }

  const handleLog = async () => {
    if (!analysisResult) return
    setLogging(true)
    try {
      await logExercise({
        name: description.trim(),
        duration_minutes: Number(duration),
        intensity: analysisResult.intensity,
        calories_burned_override: analysisResult.calories_burned,
      })
      setDescription('')
      setDuration('')
      setAnalysisResult(null)
      await loadToday()
      onAdd?.()
    } catch (err) {
      setError(err.message || 'Failed to log exercise')
    } finally {
      setLogging(false)
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
      <form onSubmit={handleAnalyze} className="bg-white rounded-2xl shadow-sm p-4 space-y-3">
        <h3 className="font-semibold text-gray-800">Log Exercise</h3>

        {error && <div className="bg-red-50 border border-red-200 rounded-xl p-3 text-xs text-red-600">{error}</div>}

        <textarea
          required
          className="input resize-none"
          rows={2}
          placeholder="Describe your exercise — e.g. ran 5km on treadmill with 2% incline"
          value={description}
          onChange={(e) => { setDescription(e.target.value); setAnalysisResult(null) }}
        />

        <input
          required
          type="number"
          min="1"
          className="input"
          placeholder="Duration (minutes)"
          value={duration}
          onChange={(e) => { setDuration(e.target.value); setAnalysisResult(null) }}
        />

        <button
          type="submit"
          disabled={analyzing || !description.trim() || !duration}
          className="w-full bg-blue-500 text-white py-2 rounded-xl font-medium text-sm flex items-center justify-center gap-2 disabled:opacity-50 active:bg-blue-600"
        >
          {analyzing ? <><Spinner /> Analyzing…</> : '✨ Estimate with AI'}
        </button>
      </form>

      {analysisResult && (
        <AnalysisCard
          result={analysisResult}
          description={description}
          duration={duration}
          onLog={handleLog}
          logging={logging}
        />
      )}

      <TodayList entries={todayEntries} onDelete={handleDelete} totalBurned={totalBurned} />
    </div>
  )
}
