import { useState, useEffect, useCallback, useRef } from 'react'
import { analyzeFood, analyzeFoodPhoto, logFood, getTodayFood, deleteFood } from '../api/api'

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
        <p className="text-sm font-semibold text-gray-800">
          {result.food_name ? result.food_name : result.serving_size}
        </p>
        <ConfidenceBadge value={result.confidence} />
      </div>
      {result.food_name && (
        <p className="text-xs text-gray-500">{result.serving_size}</p>
      )}
      {result.items_detected && result.items_detected.length > 0 && (
        <p className="text-xs text-gray-500">
          Detected: {result.items_detected.join(', ')}
        </p>
      )}
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

function TextTab({ onResult }) {
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [analyzing, setAnalyzing] = useState(false)
  const [error, setError] = useState(null)

  const handleAnalyze = async (e) => {
    e.preventDefault()
    if (!name.trim()) return
    setAnalyzing(true)
    setError(null)
    try {
      const data = await analyzeFood(name.trim(), description.trim() || undefined)
      onResult({ data, logName: name.trim(), logDescription: description.trim() || null })
    } catch (err) {
      const msg = err.message || 'Gemini analysis failed'
      try { setError(JSON.parse(msg).detail || msg) } catch { setError(msg) }
    } finally {
      setAnalyzing(false)
    }
  }

  return (
    <form onSubmit={handleAnalyze} className="space-y-3">
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-3 text-xs text-red-600">{error}</div>
      )}
      <input
        required
        className="input"
        placeholder="e.g. chicken biryani 1 plate"
        value={name}
        onChange={(e) => { setName(e.target.value) }}
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
  )
}

function PhotoTab({ onResult }) {
  const [preview, setPreview] = useState(null)
  const [imageBase64, setImageBase64] = useState(null)
  const [mimeType, setMimeType] = useState(null)
  const [analyzing, setAnalyzing] = useState(false)
  const [error, setError] = useState(null)
  const [dragging, setDragging] = useState(false)
  const fileInputRef = useRef(null)

  const processFile = (file) => {
    if (!file || !file.type.startsWith('image/')) {
      setError('Please select a JPEG or PNG image.')
      return
    }
    if (file.type !== 'image/jpeg' && file.type !== 'image/png') {
      setError('Only JPEG and PNG images are supported.')
      return
    }
    setError(null)
    const reader = new FileReader()
    reader.onload = (e) => {
      const dataUrl = e.target.result
      const base64 = dataUrl.split(',')[1]
      setPreview(dataUrl)
      setImageBase64(base64)
      setMimeType(file.type)
    }
    reader.readAsDataURL(file)
  }

  const handleFileChange = (e) => {
    const file = e.target.files[0]
    if (file) processFile(file)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setDragging(false)
    const file = e.dataTransfer.files[0]
    if (file) processFile(file)
  }

  const handleAnalyze = async () => {
    if (!imageBase64 || !mimeType) return
    setAnalyzing(true)
    setError(null)
    try {
      const data = await analyzeFoodPhoto(imageBase64, mimeType)
      onResult({ data, logName: data.food_name || 'Photo meal', logDescription: null })
    } catch (err) {
      const msg = err.message || 'Photo analysis failed'
      try { setError(JSON.parse(msg).detail || msg) } catch { setError(msg) }
    } finally {
      setAnalyzing(false)
    }
  }

  return (
    <div className="space-y-3">
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-3 text-xs text-red-600">{error}</div>
      )}

      <div
        onClick={() => fileInputRef.current?.click()}
        onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        className={`relative border-2 border-dashed rounded-2xl p-6 flex flex-col items-center justify-center cursor-pointer transition-colors ${
          dragging ? 'border-indigo-400 bg-indigo-50' : 'border-gray-300 bg-gray-50 hover:border-indigo-300'
        }`}
      >
        {preview ? (
          <img src={preview} alt="Food preview" className="max-h-48 rounded-xl object-cover" />
        ) : (
          <>
            <svg className="w-10 h-10 text-gray-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            <p className="text-sm text-gray-500 font-medium">Tap to take photo or upload</p>
            <p className="text-xs text-gray-400 mt-1">JPEG or PNG</p>
          </>
        )}
        <input
          ref={fileInputRef}
          type="file"
          accept="image/jpeg,image/png"
          capture="environment"
          className="hidden"
          onChange={handleFileChange}
        />
      </div>

      {preview && (
        <button
          type="button"
          onClick={() => { setPreview(null); setImageBase64(null); setMimeType(null) }}
          className="text-xs text-gray-400 hover:text-gray-600 underline w-full text-center"
        >
          Remove photo
        </button>
      )}

      <button
        type="button"
        disabled={analyzing || !imageBase64}
        onClick={handleAnalyze}
        className="w-full bg-indigo-500 text-white py-2 rounded-xl font-medium text-sm flex items-center justify-center gap-2 disabled:opacity-50 active:bg-indigo-600"
      >
        {analyzing ? <><Spinner /> Analyzing…</> : '📷 Analyze photo'}
      </button>
    </div>
  )
}

export default function FoodLogger() {
  const [tab, setTab] = useState('text')
  const [result, setResult] = useState(null)
  const [pendingLog, setPendingLog] = useState(null)
  const [logging, setLogging] = useState(false)
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

  const handleResult = ({ data, logName, logDescription }) => {
    setResult(data)
    setPendingLog({ name: logName, description: logDescription })
  }

  const handleLog = async () => {
    if (!result || !pendingLog) return
    setLogging(true)
    try {
      await logFood({
        name: pendingLog.name,
        description: pendingLog.description,
        calories: result.calories,
        protein_g: result.protein_g,
        carbs_g: result.carbs_g,
        fat_g: result.fat_g,
        serving_size: result.serving_size,
      })
      setResult(null)
      setPendingLog(null)
      await loadToday()
    } catch (err) {
      console.error(err)
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
      <div className="bg-white rounded-2xl shadow-sm p-4 space-y-4">
        <h3 className="font-semibold text-gray-800">What did you eat?</h3>

        {/* Tabs */}
        <div className="flex rounded-xl bg-gray-100 p-1 gap-1">
          <button
            type="button"
            onClick={() => { setTab('text'); setResult(null) }}
            className={`flex-1 py-1.5 rounded-lg text-sm font-medium transition-colors ${
              tab === 'text' ? 'bg-white text-gray-800 shadow-sm' : 'text-gray-500'
            }`}
          >
            Text
          </button>
          <button
            type="button"
            onClick={() => { setTab('photo'); setResult(null) }}
            className={`flex-1 py-1.5 rounded-lg text-sm font-medium transition-colors ${
              tab === 'photo' ? 'bg-white text-gray-800 shadow-sm' : 'text-gray-500'
            }`}
          >
            Photo
          </button>
        </div>

        {tab === 'text' ? (
          <TextTab onResult={handleResult} />
        ) : (
          <PhotoTab onResult={handleResult} />
        )}
      </div>

      {result && (
        <AnalysisCard result={result} onLog={handleLog} logging={logging} />
      )}

      <TodayList entries={todayEntries} onDelete={handleDelete} total={totalCalories} />
    </div>
  )
}
