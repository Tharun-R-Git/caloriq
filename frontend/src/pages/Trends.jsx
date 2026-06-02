import { useState, useEffect } from 'react'
import { CalorieLineChart, MacroBarChart, ExerciseAreaChart } from '../components/Charts'
import { getTrends } from '../api/api'

const DAY_OPTIONS = [7, 14, 30]

export default function Trends() {
  const [data, setData] = useState([])
  const [days, setDays] = useState(14)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    setLoading(true)
    getTrends(days)
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [days])

  return (
    <div className="max-w-md mx-auto px-4 pt-6 space-y-4">
      <h1 className="text-xl font-bold text-gray-900">Trends</h1>

      <div className="flex gap-2">
        {DAY_OPTIONS.map((d) => (
          <button
            key={d}
            onClick={() => setDays(d)}
            className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-colors ${
              days === d ? 'bg-green-500 text-white' : 'bg-white text-gray-600 border border-gray-200'
            }`}
          >
            {d}d
          </button>
        ))}
      </div>

      {loading ? (
        <p className="text-center text-gray-400 text-sm py-8">Loading…</p>
      ) : (
        <div className="space-y-4">
          <div className="bg-white rounded-2xl shadow-sm p-4">
            <h2 className="text-sm font-semibold text-gray-700 mb-3">Calorie Trend</h2>
            <CalorieLineChart data={data} />
          </div>

          <div className="bg-white rounded-2xl shadow-sm p-4">
            <h2 className="text-sm font-semibold text-gray-700 mb-1">Macro Breakdown</h2>
            <p className="text-xs text-gray-400 mb-3">Last 7 days · grams</p>
            <MacroBarChart data={data} />
          </div>

          <div className="bg-white rounded-2xl shadow-sm p-4">
            <h2 className="text-sm font-semibold text-gray-700 mb-3">Exercise vs Food</h2>
            <ExerciseAreaChart data={data} />
          </div>
        </div>
      )}
    </div>
  )
}
