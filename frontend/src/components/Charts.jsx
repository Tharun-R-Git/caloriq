import {
  LineChart, Line,
  BarChart, Bar,
  AreaChart, Area,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from 'recharts'

const fmt = (v) => v.slice(5) // "2025-06-01" → "06-01"

export function CalorieLineChart({ data = [] }) {
  return (
    <ResponsiveContainer width="100%" height={200}>
      <LineChart data={data} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis dataKey="date" tick={{ fontSize: 9 }} tickFormatter={fmt} />
        <YAxis tick={{ fontSize: 9 }} />
        <Tooltip
          labelFormatter={(v) => v}
          formatter={(v, n) => [`${v} kcal`, n]}
        />
        <Legend wrapperStyle={{ fontSize: 11 }} />
        <Line
          type="monotone"
          dataKey="calories_in"
          stroke="#f87171"
          name="Calories in"
          dot={false}
          strokeWidth={2}
        />
        <Line
          type="monotone"
          dataKey="goal"
          stroke="#9ca3af"
          name="Daily goal"
          dot={false}
          strokeDasharray="5 5"
          strokeWidth={1.5}
        />
      </LineChart>
    </ResponsiveContainer>
  )
}

export function MacroBarChart({ data = [] }) {
  // Show only the last 7 entries regardless of the selected range
  const slice = data.slice(-7)
  return (
    <ResponsiveContainer width="100%" height={200}>
      <BarChart data={slice} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis dataKey="date" tick={{ fontSize: 9 }} tickFormatter={fmt} />
        <YAxis tick={{ fontSize: 9 }} />
        <Tooltip formatter={(v, n) => [`${v} g`, n]} />
        <Legend wrapperStyle={{ fontSize: 11 }} />
        <Bar dataKey="protein_g" stackId="macros" fill="#60a5fa" name="Protein" />
        <Bar dataKey="carbs_g"   stackId="macros" fill="#fbbf24" name="Carbs" />
        <Bar dataKey="fat_g"     stackId="macros" fill="#f87171" name="Fat" />
      </BarChart>
    </ResponsiveContainer>
  )
}

export function ExerciseAreaChart({ data = [] }) {
  return (
    <ResponsiveContainer width="100%" height={220}>
      <AreaChart data={data} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
        <defs>
          <linearGradient id="colorFood" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%"  stopColor="#f87171" stopOpacity={0.6} />
            <stop offset="95%" stopColor="#f87171" stopOpacity={0.05} />
          </linearGradient>
          <linearGradient id="colorExercise" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%"  stopColor="#2dd4bf" stopOpacity={0.6} />
            <stop offset="95%" stopColor="#2dd4bf" stopOpacity={0.05} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis dataKey="date" tick={{ fontSize: 9 }} tickFormatter={fmt} />
        <YAxis tick={{ fontSize: 9 }} />
        <Tooltip
          labelFormatter={(v) => v}
          formatter={(v, n) => [`${v} kcal`, n]}
        />
        <Legend wrapperStyle={{ fontSize: 11 }} />
        <Area
          type="monotone"
          dataKey="calories_in"
          stroke="#f87171"
          fill="url(#colorFood)"
          name="Food in"
          strokeWidth={2}
        />
        <Area
          type="monotone"
          dataKey="calories_burned"
          stroke="#2dd4bf"
          fill="url(#colorExercise)"
          name="Exercise burn"
          strokeWidth={2}
        />
        <Line
          type="monotone"
          dataKey="net"
          stroke="#6366f1"
          name="Net"
          dot={false}
          strokeWidth={2}
        />
      </AreaChart>
    </ResponsiveContainer>
  )
}
