import {
  LineChart, Line,
  BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from 'recharts'

export function CalorieLineChart({ data = [] }) {
  return (
    <ResponsiveContainer width="100%" height={200}>
      <LineChart data={data} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis dataKey="date" tick={{ fontSize: 9 }} tickFormatter={(v) => v.slice(5)} />
        <YAxis tick={{ fontSize: 9 }} />
        <Tooltip labelFormatter={(v) => v} formatter={(v, n) => [`${v} kcal`, n]} />
        <Legend wrapperStyle={{ fontSize: 11 }} />
        <Line type="monotone" dataKey="calories_consumed" stroke="#f97316" name="Consumed" dot={false} strokeWidth={2} />
        <Line type="monotone" dataKey="calories_burned" stroke="#3b82f6" name="Burned" dot={false} strokeWidth={2} />
        <Line type="monotone" dataKey="goal" stroke="#22c55e" name="Goal" dot={false} strokeDasharray="5 5" strokeWidth={1.5} />
      </LineChart>
    </ResponsiveContainer>
  )
}

export function MacroBarChart({ data = [] }) {
  return (
    <ResponsiveContainer width="100%" height={200}>
      <BarChart data={data} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis dataKey="date" tick={{ fontSize: 9 }} tickFormatter={(v) => v.slice(5)} />
        <YAxis tick={{ fontSize: 9 }} />
        <Tooltip formatter={(v, n) => [`${v} g`, n]} />
        <Legend wrapperStyle={{ fontSize: 11 }} />
        <Bar dataKey="protein" fill="#a855f7" name="Protein" />
        <Bar dataKey="carbs" fill="#f59e0b" name="Carbs" />
        <Bar dataKey="fat" fill="#ef4444" name="Fat" />
      </BarChart>
    </ResponsiveContainer>
  )
}
