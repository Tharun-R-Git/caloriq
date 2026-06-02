import { useState, useEffect } from 'react'
import { useProfile } from '../hooks/useProfile'

const ACTIVITY_LEVELS = ['sedentary', 'light', 'moderate', 'active', 'very_active']

export default function ProfileForm() {
  const { profile, loading, save } = useProfile()
  const [form, setForm] = useState({
    name: '', age: '', weight_kg: '', height_cm: '', goal_calories: 2000, activity_level: 'moderate',
  })
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    if (profile) setForm(profile)
  }, [profile])

  const set = (k, v) => setForm((f) => ({ ...f, [k]: v }))

  const submit = async (e) => {
    e.preventDefault()
    setSaving(true)
    try {
      await save(form)
      setSaved(true)
      setTimeout(() => setSaved(false), 2000)
    } finally {
      setSaving(false)
    }
  }

  if (loading) return <div className="p-6 text-center text-gray-400 text-sm">Loading…</div>

  return (
    <form onSubmit={submit} className="bg-white rounded-2xl shadow-sm p-4 space-y-3">
      <h3 className="font-semibold text-gray-800">Profile</h3>
      <input className="input" placeholder="Name" value={form.name || ''} onChange={(e) => set('name', e.target.value)} />
      <div className="grid grid-cols-2 gap-2">
        <input type="number" className="input" placeholder="Age" value={form.age || ''} onChange={(e) => set('age', e.target.value)} />
        <select className="input" value={form.activity_level || 'moderate'} onChange={(e) => set('activity_level', e.target.value)}>
          {ACTIVITY_LEVELS.map((l) => <option key={l} value={l}>{l.replace('_', ' ')}</option>)}
        </select>
      </div>
      <div className="grid grid-cols-2 gap-2">
        <input type="number" className="input" placeholder="Weight (kg)" value={form.weight_kg || ''} onChange={(e) => set('weight_kg', e.target.value)} />
        <input type="number" className="input" placeholder="Height (cm)" value={form.height_cm || ''} onChange={(e) => set('height_cm', e.target.value)} />
      </div>
      <input type="number" className="input" placeholder="Daily calorie goal" value={form.goal_calories || ''} onChange={(e) => set('goal_calories', e.target.value)} />
      <button
        type="submit"
        disabled={saving}
        className="w-full bg-green-500 text-white py-2 rounded-xl font-medium text-sm disabled:opacity-50"
      >
        {saving ? 'Saving…' : saved ? 'Saved!' : 'Save Profile'}
      </button>
    </form>
  )
}
