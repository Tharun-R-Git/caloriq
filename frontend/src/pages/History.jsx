import { useState } from 'react'
import HistoryList from '../components/History'
import { useCalories } from '../hooks/useCalories'

export default function HistoryPage() {
  const [date, setDate] = useState(new Date().toISOString().split('T')[0])
  const { foodEntries, exerciseEntries, loading, refresh } = useCalories(date)

  return (
    <div className="max-w-md mx-auto px-4 pt-6 space-y-4">
      <h1 className="text-xl font-bold text-gray-900">History</h1>
      <input
        type="date"
        className="input"
        value={date}
        onChange={(e) => setDate(e.target.value)}
      />
      {loading
        ? <p className="text-center text-gray-400 text-sm">Loading…</p>
        : <HistoryList foodEntries={foodEntries} exerciseEntries={exerciseEntries} onDelete={refresh} />
      }
    </div>
  )
}
