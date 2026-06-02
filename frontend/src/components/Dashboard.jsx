import { useCalories } from '../hooks/useCalories'

function Stat({ label, value, unit, color }) {
  return (
    <div className="text-center">
      <p className={`text-xl font-bold ${color}`}>{value ?? '—'}</p>
      <p className="text-xs text-gray-400">{unit}</p>
      <p className="text-xs text-gray-500 mt-0.5">{label}</p>
    </div>
  )
}

export default function Dashboard({ date }) {
  const { summary, loading, error } = useCalories(date)

  if (loading) return <div className="p-6 text-center text-gray-400 text-sm">Loading…</div>
  if (error) return <div className="p-4 text-red-500 text-sm">{error}</div>
  if (!summary) return null

  const { calories_consumed, calories_burned, goal } = summary
  const net = calories_consumed - calories_burned
  const remaining = goal - net
  const pct = Math.min(100, goal > 0 ? (net / goal) * 100 : 0)

  return (
    <div className="bg-white rounded-2xl shadow-sm p-4 space-y-4">
      <h2 className="font-semibold text-gray-800">Today</h2>
      <div className="grid grid-cols-3 gap-2">
        <Stat label="Consumed" value={calories_consumed} unit="kcal" color="text-orange-500" />
        <Stat label="Burned" value={calories_burned} unit="kcal" color="text-blue-500" />
        <Stat label="Remaining" value={remaining} unit="kcal" color={remaining >= 0 ? 'text-green-600' : 'text-red-500'} />
      </div>
      <div className="space-y-1">
        <div className="w-full bg-gray-100 rounded-full h-2">
          <div
            className="bg-green-500 h-2 rounded-full transition-all duration-300"
            style={{ width: `${pct}%` }}
          />
        </div>
        <p className="text-xs text-gray-400 text-right">{net} / {goal} kcal</p>
      </div>
    </div>
  )
}
