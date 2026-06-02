import { useState, useEffect, useCallback } from 'react'
import { analyzeFood, logFood, getTodayFood, deleteFood } from '../api/api'

function Spinner() {
  return (
    <span className="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
  )
}

function ConfidenceBadge({ value }) {
  const pct = Math.round(value * 100)
  const color = value >= 0.8 ? 'bg-green-100 text-green-700' : value >= 0.5 ? 'bg-yellow-100 text-yellow-700' : 'bg-red-100 text-red-700'
  return <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${color}`}>{pct}% confidence</span>
}

function MacroChip({ label, value, unit = 'g', color }) {
  return (
    <div className="text-center">
      <p className={`text-base font-bold ${color}`}>{value}</p>
      <p className="text-xs text-gray-400">{unit}</p>
      <p className="text-xs text-gray-500">{label}</p>
    </div>
  )
}

function AnalysisCard({ result, onLog, logging }) {
  return (
    <div className="border border-green-200 bg-green-50 rounded-2xl p-4 space-y-3">
      <div className="flex items-center justify-between">
        <p className="text-sm font-semibold text-gray-800">{result.serving_size}</p>
        <ConfidenceBadge value={result.confidence} />
      </div>
      <div className="flex justify-around">
        <MacroChip label="Calories" value={result.calories} unit="kcal" color="text-orange-500" />
        <MacroChip label="Protein" value={result.protein_g} color="text-purple-600" />
        <MacroChip label="Carbs" value={result.carbs_g} color="text-amber-500" />
        <MacroChip label="Fat" value={result.fat_g} color="text-red-500" />
      </div>
      <button
        onClick={onLog}
        disabled={logging}
        className="w-full bg-green-500 text-white py-2 rounded-xl font-medium text-sm flex items-center justify-center gap-2 disabled:opacity-60"
      >
        {logging ? <><Spinner /> Logging…</> : 'Log it'}
      </button>
    </div>
  )
}

function TodayList({ entries, onDelete, total }) {
  if (entries.length === 0) return (
    <div className="bg-white rounded-2xl shadow-sm p-4">
      <p className="text-sm text-gray-400 text-center">Nothing logged today yet.</p>
    </div>
  )
  return (
    <div className="bg-white rounded-2xl shadow-sm p-4 space-y-1">
      <div className="flex justify-between items-center mb-2">
        <h3 className="font-semibold text-gray-800 text-sm">Today</h3>
        <span className="text-sm font-bold text-orange-500">{total} kcal</span>
      </div>
      <ul className="divide-y divide-gray-100">
        {entries.map((e) => (
          <li key={e.id} className="flex justify-between items-center py-2">
            <div className="min-w-0 flex-1">
              <p className="text-sm font-medium text-gray-700 truncate">{e.name}</p>
              <p className="text-xs text-gray-400">
                {e.calories} kcal
                {e.serving_size && <span className="ml-1 text-gray-300">· {e.serving_size}</span>}
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

export default function FoodLogger() {
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [analyzing, setAnalyzing] = useState(false)
  const [result, setResult] = useState(null)
  const [logging, setLogging] = useState(false)
  const [error, setError] = useState(null)
  const [todayEntries, setTodayEntries] = useState([])

  const loadToday = useCallback(async () => {
    try {
      const entries = await getTodayFood()
      setTodayEntries(entries)
    } catch {
      // silent — today list is non-critical
    }
  }, [])

  useEffect(() => { loadToday() }, [loadToday])

  const handleAnalyze = async (e) => {
    e.preventDefault()
    if (!name.trim()) return
    setAnalyzing(true)
    setError(null)
    setResult(null)
    try {
      const data = await analyzeFood(name.trim(), description.trim() || undefined)
      setResult(data)
    } catch (err) {
      const msg = err.message || 'Gemini analysis failed'
      try {
        setError(JSON.parse(msg).detail || msg)
      } catch {
        setError(msg)
      }
    } finally {
      setAnalyzing(false)
    }
  }

  const handleLog = async () => {
    if (!result) return
    setLogging(true)
    try {
      await logFood({
        name: name.trim(),
        description: description.trim() || null,
        calories: result.calories,
        protein_g: result.protein_g,
        carbs_g: result.carbs_g,
        fat_g: result.fat_g,
        serving_size: result.serving_size,
      })
      setName('')
      setDescription('')
      setResult(null)
      await loadToday()
    } catch (err) {
      setError(err.message)
    } finally {
      setLogging(false)
    }
  }

  const handleDelete = async (id) => {
    await deleteFood(id)
    await loadToday()
  }

  const totalCalories = Math.round(todayEntries.reduce((s, e) => s + e.calories, 0))

  return (
    <div className="space-y-4">
      <form onSubmit={handleAnalyze} className="bg-white rounded-2xl shadow-sm p-4 space-y-3">
        <h3 className="font-semibold text-gray-800">What did you eat?</h3>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-3 text-xs text-red-600">{error}</div>
        )}

        <input
          required
          className="input"
          placeholder="e.g. chicken biryani 1 plate"
          value={name}
          onChange={(e) => { setName(e.target.value); setResult(null) }}
        />

        <textarea
          className="input resize-none"
          rows={2}
          placeholder="Optional: add details (e.g. homemade, extra oil)"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />

        <button
          type="submit"
          disabled={analyzing || !name.trim()}
          className="w-full bg-indigo-500 text-white py-2 rounded-xl font-medium text-sm flex items-center justify-center gap-2 disabled:opacity-50 active:bg-indigo-600"
        >
          {analyzing ? <><Spinner /> Analyzing…</> : '✨ Analyze with Gemini'}
        </button>
      </form>

      {result && (
        <AnalysisCard result={result} onLog={handleLog} logging={logging} />
      )}

      <TodayList entries={todayEntries} onDelete={handleDelete} total={totalCalories} />
    </div>
  )
}
