import { deleteFoodEntry, deleteExerciseEntry } from '../api/api'

function timeLabel(entry) {
  const ts = entry.logged_at
  if (!ts) return null
  const d = new Date(ts)
  return d.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })
}

export default function HistoryList({ foodEntries = [], exerciseEntries = [], onDelete }) {
  const handleDeleteFood = async (id) => {
    await deleteFoodEntry(id)
    onDelete?.()
  }

  const handleDeleteExercise = async (id) => {
    await deleteExerciseEntry(id)
    onDelete?.()
  }

  // Merge and sort chronologically (most recent first)
  // Use logged_at when available; fall back to id as proxy
  const merged = [
    ...foodEntries.map(e => ({ ...e, _type: 'food' })),
    ...exerciseEntries.map(e => ({ ...e, _type: 'exercise' })),
  ].sort((a, b) => {
    if (a.logged_at && b.logged_at) return new Date(b.logged_at) - new Date(a.logged_at)
    if (a.logged_at) return -1
    if (b.logged_at) return 1
    return b.id - a.id
  })

  if (merged.length === 0) {
    return (
      <div className="bg-white rounded-2xl shadow-sm p-6 text-center">
        <p className="text-sm text-gray-400">Nothing logged for this day.</p>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-2xl shadow-sm divide-y divide-gray-100">
      {merged.map(entry => {
        const isFood = entry._type === 'food'
        const time = timeLabel(entry)

        if (isFood) {
          return (
            <div key={`food-${entry.id}`} className="flex items-center gap-3 px-4 py-3">
              <div className="w-2 h-2 rounded-full bg-orange-400 shrink-0 mt-0.5" />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-800 truncate">{entry.name}</p>
                <p className="text-xs text-gray-400">
                  {entry.calories} kcal
                  {entry.protein_g > 0 && <span className="ml-1 text-purple-500">· P {entry.protein_g}g</span>}
                  {time && <span className="ml-1 text-gray-300">· {time}</span>}
                </p>
              </div>
              <button
                onClick={() => handleDeleteFood(entry.id)}
                className="text-xs text-red-400 hover:text-red-600 font-medium shrink-0 px-1"
              >
                Remove
              </button>
            </div>
          )
        }

        return (
          <div key={`ex-${entry.id}`} className="flex items-center gap-3 px-4 py-3 bg-blue-50/40">
            <div className="w-2 h-2 rounded-full bg-blue-400 shrink-0 mt-0.5" />
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-800 truncate">{entry.name}</p>
              <p className="text-xs text-gray-400">
                {entry.calories_burned} kcal burned
                {entry.duration_minutes > 0 && <span className="ml-1">· {entry.duration_minutes} min</span>}
                {entry.exercise_type && <span className="ml-1 bg-blue-100 text-blue-600 px-1.5 py-0.5 rounded">{entry.exercise_type}</span>}
                {time && <span className="ml-1 text-gray-300">· {time}</span>}
              </p>
            </div>
            <button
              onClick={() => handleDeleteExercise(entry.id)}
              className="text-xs text-red-400 hover:text-red-600 font-medium shrink-0 px-1"
            >
              Remove
            </button>
          </div>
        )
      })}
    </div>
  )
}
