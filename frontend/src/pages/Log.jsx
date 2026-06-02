import { useState } from 'react'
import FoodLogger from '../components/FoodLogger'
import ExerciseLogger from '../components/ExerciseLogger'

const TABS = ['food', 'exercise']

export default function Log() {
  const [tab, setTab] = useState('food')

  return (
    <div className="max-w-md mx-auto px-4 pt-6 space-y-4">
      <h1 className="text-xl font-bold text-gray-900">Log</h1>
      <div className="flex rounded-xl overflow-hidden border border-gray-200">
        {TABS.map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`flex-1 py-2 text-sm font-medium capitalize transition-colors ${
              tab === t ? 'bg-green-500 text-white' : 'bg-white text-gray-500'
            }`}
          >
            {t}
          </button>
        ))}
      </div>
      {tab === 'food' ? <FoodLogger /> : <ExerciseLogger />}
    </div>
  )
}
