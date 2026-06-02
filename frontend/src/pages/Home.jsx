import { useState, useEffect, useCallback } from 'react'
import { RadialBarChart, RadialBar, ResponsiveContainer } from 'recharts'
import { getDashboardSummary, logFood, getRecommendations } from '../api/api'

const EMPTY = {
  calories_in: 0,
  calories_burned: 0,
  net_calories: 0,
  daily_goal: 2000,
  remaining: 2000,
  protein_g: 0,
  carbs_g: 0,
  fat_g: 0,
  recent_foods: [],
}

function ringColor(net, goal) {
  if (net > goal) return '#ef4444'
  if (net >= goal - 100) return '#f59e0b'
  return '#22c55e'
}

function StatCard({ label, value, unit, colorClass }) {
  return (
    <div className="bg-white rounded-2xl p-4 shadow-sm border border-gray-100">
      <p className="text-xs text-gray-400 font-medium uppercase tracking-wide">{label}</p>
      <p className={`text-2xl font-bold mt-1 ${colorClass}`}>
        {value.toLocaleString()}
      </p>
      <p className="text-xs text-gray-400">{unit}</p>
    </div>
  )
}

function MacroPill({ label, value, color }) {
  return (
    <span className={`inline-flex items-center gap-0.5 px-2 py-0.5 rounded-full text-xs font-medium ${color}`}>
      {label} {value}g
    </span>
  )
}

export default function Home() {
  const [data, setData] = useState(EMPTY)
  const [loading, setLoading] = useState(true)
  const [quickAdding, setQuickAdding] = useState(null)
  const [recs, setRecs] = useState(null)
  const [recsLoading, setRecsLoading] = useState(false)
  const [loggingRec, setLoggingRec] = useState(null)

  const today = new Date().toLocaleDateString('en-GB', {
    weekday: 'long', day: 'numeric', month: 'long',
  })

  const load = useCallback(async () => {
    try {
      const summary = await getDashboardSummary()
      setData(summary)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { load() }, [load])

  const quickAdd = async (food) => {
    setQuickAdding(food.name)
    try {
      await logFood({
        name: food.name,
        calories: food.calories,
        protein_g: food.protein_g,
        carbs_g: food.carbs_g,
        fat_g: food.fat_g,
      })
      await load()
    } catch (e) {
      console.error(e)
    } finally {
      setQuickAdding(null)
    }
  }

  const fetchRecs = useCallback(async () => {
    setRecsLoading(true)
    try {
      const result = await getRecommendations()
      setRecs(result)
    } catch (e) {
      console.error(e)
    } finally {
      setRecsLoading(false)
    }
  }, [])

  const logRec = async (rec) => {
    setLoggingRec(rec.name)
    try {
      await logFood({
        name: rec.name,
        calories: rec.calories,
        protein_g: rec.protein_g,
        carbs_g: rec.carbs_g,
        fat_g: rec.fat_g,
        serving_size: rec.portion_size,
      })
      await load()
    } catch (e) {
      console.error(e)
    } finally {
      setLoggingRec(null)
    }
  }

  const pct = data.daily_goal > 0
    ? Math.min((data.net_calories / data.daily_goal) * 100, 100)
    : 0
  const fill = ringColor(data.net_calories, data.daily_goal)
  const ringData = [{ name: 'net', value: pct }]

  const remainColorClass =
    data.remaining < 0 ? 'text-red-500'
    : data.remaining < 100 ? 'text-amber-500'
    : 'text-green-600'

  return (
    <div className="max-w-md mx-auto px-4 pt-6 space-y-5">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">CaloriQ</h1>
        <p className="text-sm text-gray-400 mt-0.5">{today}</p>
      </div>

      {/* Net calorie ring */}
      <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 flex flex-col items-center">
        <p className="text-sm font-medium text-gray-500 mb-3">Daily Progress</p>
        <div className="relative w-48 h-48">
          <ResponsiveContainer width="100%" height="100%">
            <RadialBarChart
              innerRadius="62%"
              outerRadius="100%"
              data={ringData}
              startAngle={90}
              endAngle={-270}
              barSize={20}
            >
              <RadialBar
                dataKey="value"
                fill={fill}
                background={{ fill: '#f3f4f6' }}
                cornerRadius={10}
              />
            </RadialBarChart>
          </ResponsiveContainer>
          {/* Center overlay */}
          <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
            {loading ? (
              <span className="text-gray-300 text-lg">—</span>
            ) : (
              <>
                <span className="text-xl font-bold text-gray-900 leading-tight">
                  {data.net_calories.toLocaleString()}
                </span>
                <span className="text-xs text-gray-400">
                  / {data.daily_goal.toLocaleString()} kcal
                </span>
              </>
            )}
          </div>
        </div>
      </div>

      {/* 2×2 summary cards */}
      <div className="grid grid-cols-2 gap-3">
        <StatCard
          label="Consumed"
          value={data.calories_in}
          unit="kcal in"
          colorClass="text-orange-500"
        />
        <StatCard
          label="Burned"
          value={data.calories_burned}
          unit="kcal out"
          colorClass="text-blue-500"
        />
        <StatCard
          label="Net"
          value={data.net_calories}
          unit="kcal net"
          colorClass="text-gray-700"
        />
        <StatCard
          label="Remaining"
          value={data.remaining}
          unit="kcal left"
          colorClass={remainColorClass}
        />
      </div>

      {/* Quick-add shortcuts */}
      {data.recent_foods.length > 0 && (
        <div className="bg-white rounded-2xl p-4 shadow-sm border border-gray-100">
          <p className="text-sm font-medium text-gray-500 mb-3">Quick Add</p>
          <div className="space-y-2">
            {data.recent_foods.map((food) => (
              <button
                key={food.name}
                onClick={() => quickAdd(food)}
                disabled={quickAdding === food.name}
                className="w-full flex items-center justify-between px-4 py-2.5 rounded-xl bg-gray-50 hover:bg-gray-100 active:bg-gray-200 transition-colors text-left disabled:opacity-50"
              >
                <span className="text-sm font-medium text-gray-700 truncate">
                  {food.name}
                </span>
                <span className="text-xs text-gray-400 ml-2 shrink-0">
                  {food.calories} kcal
                </span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* AI Meal Recommendations */}
      <div className="bg-white rounded-2xl p-4 shadow-sm border border-gray-100 pb-6">
        <div className="flex items-center justify-between mb-3">
          <p className="text-sm font-medium text-gray-500">What should I eat next?</p>
          {recs && (
            <button
              onClick={fetchRecs}
              disabled={recsLoading}
              className="text-xs text-indigo-500 hover:text-indigo-700 font-medium disabled:opacity-40"
            >
              {recsLoading ? 'Refreshing…' : 'Refresh'}
            </button>
          )}
        </div>

        {!recs && (
          <button
            onClick={fetchRecs}
            disabled={recsLoading}
            className="w-full py-3 rounded-xl bg-indigo-50 hover:bg-indigo-100 active:bg-indigo-200 transition-colors text-indigo-700 text-sm font-semibold disabled:opacity-50"
          >
            {recsLoading ? (
              <span className="flex items-center justify-center gap-2">
                <svg className="animate-spin h-4 w-4 text-indigo-500" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
                </svg>
                Asking AI…
              </span>
            ) : 'Ask AI for suggestions'}
          </button>
        )}

        {recsLoading && recs && (
          <div className="flex items-center justify-center py-6 gap-2 text-sm text-gray-400">
            <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
            </svg>
            Getting new suggestions…
          </div>
        )}

        {recs && !recsLoading && (
          <>
            {recs.message && (
              <p className="text-xs text-gray-400 mb-3">{recs.message}</p>
            )}
            <div className="space-y-3">
              {recs.recommendations.map((rec) => (
                <div
                  key={rec.name}
                  className="rounded-xl border border-gray-100 bg-gray-50 p-3"
                >
                  {/* Header */}
                  <div className="flex items-start justify-between gap-2 mb-2">
                    <div>
                      <p className="text-sm font-semibold text-gray-800 leading-snug">{rec.name}</p>
                      <p className="text-xs text-gray-400 mt-0.5">{rec.portion_size}</p>
                    </div>
                    <span className="shrink-0 text-sm font-bold text-orange-500">
                      {rec.calories} kcal
                    </span>
                  </div>

                  {/* Macro pills */}
                  <div className="flex flex-wrap gap-1.5 mb-2">
                    <MacroPill label="P" value={rec.protein_g} color="bg-blue-100 text-blue-700" />
                    <MacroPill label="C" value={rec.carbs_g} color="bg-amber-100 text-amber-700" />
                    <MacroPill label="F" value={rec.fat_g} color="bg-rose-100 text-rose-700" />
                  </div>

                  {/* Reason */}
                  {rec.reason && (
                    <p className="text-xs text-gray-400 mb-3 leading-snug">{rec.reason}</p>
                  )}

                  {/* Log button */}
                  <button
                    onClick={() => logRec(rec)}
                    disabled={loggingRec === rec.name}
                    className="w-full py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 active:bg-indigo-800 text-white text-xs font-semibold transition-colors disabled:opacity-50"
                  >
                    {loggingRec === rec.name ? 'Logging…' : 'Log this'}
                  </button>
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  )
}
