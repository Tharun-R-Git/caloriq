import { deleteFoodEntry, deleteExerciseEntry } from '../api/api'

function Section({ title, entries, onDelete, labelKey, valueKey, valueUnit, badgeKey }) {
  return (
    <div className="bg-white rounded-2xl shadow-sm p-4">
      <h3 className="font-semibold text-gray-800 mb-3">{title}</h3>
      {entries.length === 0 ? (
        <p className="text-sm text-gray-400">No entries yet.</p>
      ) : (
        <ul className="divide-y divide-gray-100">
          {entries.map((e) => (
            <li key={e.id} className="flex justify-between items-center py-2.5">
              <div>
                <p className="text-sm font-medium text-gray-700">{e[labelKey]}</p>
                <p className="text-xs text-gray-400">
                  {e[valueKey]} {valueUnit}
                  {badgeKey && e[badgeKey] && (
                    <span className="ml-2 bg-gray-100 text-gray-500 px-1.5 py-0.5 rounded-md text-xs">{e[badgeKey]}</span>
                  )}
                </p>
              </div>
              <button
                onClick={() => onDelete(e.id)}
                className="text-red-400 text-xs font-medium hover:text-red-600 px-2 py-1"
              >
                Remove
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
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

  return (
    <div className="space-y-4">
      <Section
        title="Food"
        entries={foodEntries}
        onDelete={handleDeleteFood}
        labelKey="name"
        valueKey="calories"
        valueUnit="kcal"
        badgeKey="meal_type"
      />
      <Section
        title="Exercise"
        entries={exerciseEntries}
        onDelete={handleDeleteExercise}
        labelKey="name"
        valueKey="calories_burned"
        valueUnit="kcal burned"
        badgeKey="exercise_type"
      />
    </div>
  )
}
