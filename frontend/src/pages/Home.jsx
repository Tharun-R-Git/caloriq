import { useState, useEffect, useCallback } from 'react'
import { RadialBarChart, RadialBar, ResponsiveContainer } from 'recharts'
import { getDashboardSummary, logFood } from '../api/api'

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

export default function Home() {
  const [data, setData] = useState(EMPTY)
  const [loading, setLoading] = useState(true)
  const [quickAdding, setQuickAdding] = useState(null)

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
    </div>
  )
}
