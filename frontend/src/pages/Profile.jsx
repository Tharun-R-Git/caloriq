import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { getProfile, setupProfile } from '../api/api'

// ── Conversion helpers ────────────────────────────────────────────────────────

function cmToFtIn(cm) {
  const totalIn = cm / 2.54
  const ft = Math.floor(totalIn / 12)
  const inches = Math.round(totalIn % 12)
  return `${ft}'${inches}"`
}

function kgToLbs(kg) {
  return Math.round(kg * 2.20462)
}

// ── Local calorie calculation (mirrors CLAUDE.md formulas) ────────────────────

const ACTIVITY_MULTIPLIERS = {
  sedentary: 1.2, light: 1.375, moderate: 1.55, active: 1.725, very_active: 1.9,
}

function localCalcBMR(weight_kg, height_cm, age, gender) {
  if (gender === 'female') return 447.6 + (9.25 * weight_kg) + (3.1 * height_cm) - (4.3 * age)
  return 88.36 + (13.4 * weight_kg) + (5.0 * height_cm) - (5.7 * age)
}

function localCalcGoals(form) {
  const bmr = localCalcBMR(form.weight_kg, form.height_cm, form.age, form.gender)
  const tdee = bmr * (ACTIVITY_MULTIPLIERS[form.activity_level] || 1.55)
  const offsets = { lose: -500, maintain: 0, gain: 300 }
  const daily_goal = Math.round(tdee + (offsets[form.aim] || 0))
  return {
    bmr: Math.round(bmr),
    tdee: Math.round(tdee),
    daily_goal,
    protein_goal_g: Math.round((daily_goal * 0.30) / 4),
    carbs_goal_g: Math.round((daily_goal * 0.45) / 4),
    fat_goal_g: Math.round((daily_goal * 0.25) / 9),
  }
}

// ── Static data ───────────────────────────────────────────────────────────────

const ACTIVITY_OPTIONS = [
  { value: 'sedentary', icon: '🪑', label: 'Sedentary',   desc: 'Desk job, little exercise' },
  { value: 'light',     icon: '🚶', label: 'Light',        desc: 'Light exercise 1–3 days/week' },
  { value: 'moderate',  icon: '🚴', label: 'Moderate',     desc: 'Moderate exercise 3–5 days/week' },
  { value: 'active',    icon: '🏋️', label: 'Active',       desc: 'Hard exercise 6–7 days/week' },
  { value: 'very_active', icon: '⚡', label: 'Very Active', desc: 'Physical job + hard exercise' },
]

const AIM_OPTIONS = [
  { value: 'lose',     icon: '📉', label: 'Lose Weight',  desc: '−500 kcal/day',  ring: 'border-blue-400 bg-blue-50',   check: 'text-blue-500' },
  { value: 'maintain', icon: '⚖️', label: 'Maintain',     desc: 'Stay at TDEE',   ring: 'border-green-400 bg-green-50', check: 'text-green-500' },
  { value: 'gain',     icon: '📈', label: 'Gain Muscle',  desc: '+300 kcal/day',  ring: 'border-orange-400 bg-orange-50', check: 'text-orange-500' },
]

const DIETARY_OPTIONS = [
  { value: 'veg',        label: 'Vegetarian',    icon: '🥦' },
  { value: 'eggetarian', label: 'Eggetarian',    icon: '🥚' },
  { value: 'non_veg',   label: 'Non-Vegetarian', icon: '🍗' },
]

const CUISINE_OPTIONS = [
  { value: 'north_indian',  label: 'North Indian' },
  { value: 'south_indian',  label: 'South Indian' },
  { value: 'chinese',       label: 'Chinese' },
  { value: 'italian',       label: 'Italian' },
  { value: 'mediterranean', label: 'Mediterranean' },
  { value: 'continental',   label: 'Continental' },
  { value: 'mexican',       label: 'Mexican' },
  { value: 'thai',          label: 'Thai' },
  { value: 'japanese',      label: 'Japanese' },
  { value: 'street_food',   label: 'Street Food' },
]

const STEP_TITLES = ['Basic Info', 'Food Preferences', 'Body Metrics', 'Activity Level', 'Your Goal', 'Summary']

// ── Step sub-components ───────────────────────────────────────────────────────

function Step1({ form, set }) {
  return (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-600 mb-1.5">Your name</label>
        <input
          type="text"
          value={form.name}
          onChange={e => set('name', e.target.value)}
          placeholder="e.g. Alex"
          className="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-green-400"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-600 mb-1.5">Age</label>
        <input
          type="number"
          value={form.age}
          onChange={e => set('age', Math.max(10, Math.min(100, parseInt(e.target.value) || 10)))}
          min="10"
          max="100"
          className="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-green-400"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-600 mb-1.5">Gender</label>
        <div className="grid grid-cols-3 gap-2">
          {['male', 'female', 'other'].map(g => (
            <button
              key={g}
              type="button"
              onClick={() => set('gender', g)}
              className={`py-2.5 rounded-xl text-sm font-medium transition-colors capitalize ${
                form.gender === g
                  ? 'bg-green-500 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {g}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}

function Step2({ form, set }) {
  const toggleCuisine = (val) => {
    const current = form.cuisine_preferences || []
    const updated = current.includes(val) ? current.filter(c => c !== val) : [...current, val]
    set('cuisine_preferences', updated)
  }
  return (
    <div className="space-y-5">
      <div>
        <label className="block text-sm font-medium text-gray-600 mb-2">Dietary Preference</label>
        <div className="grid grid-cols-3 gap-2">
          {DIETARY_OPTIONS.map(opt => (
            <button key={opt.value} type="button" onClick={() => set('dietary_preference', opt.value)}
              className={`flex flex-col items-center gap-1 py-3 rounded-xl text-xs font-medium transition-colors ${
                form.dietary_preference === opt.value ? 'bg-green-500 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}>
              <span className="text-xl">{opt.icon}</span>
              {opt.label}
            </button>
          ))}
        </div>
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-600 mb-2">Cuisine Preferences <span className="text-gray-400 font-normal">(pick any)</span></label>
        <div className="flex flex-wrap gap-2">
          {CUISINE_OPTIONS.map(opt => {
            const selected = (form.cuisine_preferences || []).includes(opt.value)
            return (
              <button key={opt.value} type="button" onClick={() => toggleCuisine(opt.value)}
                className={`px-3 py-1.5 rounded-full text-xs font-medium border transition-colors ${
                  selected ? 'bg-green-500 text-white border-green-500' : 'bg-white text-gray-600 border-gray-200 hover:border-green-300'
                }`}>
                {opt.label}
              </button>
            )
          })}
        </div>
        {(form.cuisine_preferences || []).length === 0 && (
          <p className="text-xs text-gray-400 mt-1">Skip to get general recommendations</p>
        )}
      </div>
    </div>
  )
}

function Step3({ form, set }) {
  return (
    <div className="space-y-7">
      <div>
        <div className="flex justify-between items-end mb-2">
          <label className="text-sm font-medium text-gray-600">Height</label>
          <div className="text-right">
            <span className="text-2xl font-bold text-gray-900">{form.height_cm}</span>
            <span className="text-sm text-gray-400 ml-1">cm</span>
            <span className="text-xs text-gray-400 ml-2">({cmToFtIn(form.height_cm)})</span>
          </div>
        </div>
        <input
          type="range"
          min="140"
          max="220"
          value={form.height_cm}
          onChange={e => set('height_cm', parseInt(e.target.value))}
          className="w-full accent-green-500"
        />
        <div className="flex justify-between text-xs text-gray-300 mt-1">
          <span>140 cm</span>
          <span>220 cm</span>
        </div>
      </div>
      <div>
        <div className="flex justify-between items-end mb-2">
          <label className="text-sm font-medium text-gray-600">Weight</label>
          <div className="text-right">
            <span className="text-2xl font-bold text-gray-900">{form.weight_kg}</span>
            <span className="text-sm text-gray-400 ml-1">kg</span>
            <span className="text-xs text-gray-400 ml-2">({kgToLbs(form.weight_kg)} lbs)</span>
          </div>
        </div>
        <input
          type="range"
          min="30"
          max="200"
          value={form.weight_kg}
          onChange={e => set('weight_kg', parseInt(e.target.value))}
          className="w-full accent-green-500"
        />
        <div className="flex justify-between text-xs text-gray-300 mt-1">
          <span>30 kg</span>
          <span>200 kg</span>
        </div>
      </div>
    </div>
  )
}

function Step4({ form, set }) {
  return (
    <div className="space-y-2">
      {ACTIVITY_OPTIONS.map(opt => (
        <button
          key={opt.value}
          type="button"
          onClick={() => set('activity_level', opt.value)}
          className={`w-full flex items-center gap-3 p-3.5 rounded-xl border transition-colors text-left ${
            form.activity_level === opt.value
              ? 'border-green-400 bg-green-50'
              : 'border-gray-200 bg-white hover:border-gray-300'
          }`}
        >
          <span className="text-2xl w-8 text-center">{opt.icon}</span>
          <div className="flex-1 min-w-0">
            <p className="font-medium text-sm text-gray-900">{opt.label}</p>
            <p className="text-xs text-gray-400 truncate">{opt.desc}</p>
          </div>
          {form.activity_level === opt.value && (
            <span className="text-green-500 font-bold text-sm">✓</span>
          )}
        </button>
      ))}
    </div>
  )
}

function Step5({ form, set }) {
  return (
    <div className="space-y-3">
      {AIM_OPTIONS.map(opt => (
        <button
          key={opt.value}
          type="button"
          onClick={() => set('aim', opt.value)}
          className={`w-full p-4 rounded-2xl border-2 transition-all text-left ${
            form.aim === opt.value ? opt.ring : 'border-gray-200 bg-white hover:border-gray-300'
          }`}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="text-3xl">{opt.icon}</span>
              <div>
                <p className="font-semibold text-gray-900">{opt.label}</p>
                <p className="text-sm text-gray-400">{opt.desc}</p>
              </div>
            </div>
            {form.aim === opt.value && (
              <span className={`text-xl font-bold ${opt.check}`}>✓</span>
            )}
          </div>
        </button>
      ))}
    </div>
  )
}

function Step6({ form }) {
  const goals = localCalcGoals(form)
  return (
    <div className="space-y-4">
      <div className="bg-green-50 rounded-2xl p-5 text-center">
        <p className="text-sm font-medium text-green-600 mb-1">Daily Calorie Goal</p>
        <p className="text-5xl font-bold text-green-600">{goals.daily_goal.toLocaleString()}</p>
        <p className="text-xs text-green-500 mt-1">kcal / day</p>
      </div>
      <div className="grid grid-cols-2 gap-3">
        <div className="bg-white border border-gray-100 rounded-xl p-3 text-center shadow-sm">
          <p className="text-xs text-gray-400 uppercase tracking-wide">BMR</p>
          <p className="text-xl font-bold text-gray-800 mt-0.5">{goals.bmr.toLocaleString()}</p>
          <p className="text-xs text-gray-400">kcal base</p>
        </div>
        <div className="bg-white border border-gray-100 rounded-xl p-3 text-center shadow-sm">
          <p className="text-xs text-gray-400 uppercase tracking-wide">TDEE</p>
          <p className="text-xl font-bold text-gray-800 mt-0.5">{goals.tdee.toLocaleString()}</p>
          <p className="text-xs text-gray-400">kcal active</p>
        </div>
      </div>
      <div className="bg-white border border-gray-100 rounded-xl p-4 shadow-sm">
        <p className="text-sm font-medium text-gray-600 mb-3">Daily Macro Targets</p>
        <div className="grid grid-cols-3 gap-2 text-center">
          <div>
            <p className="text-xl font-bold text-blue-500">{goals.protein_goal_g}g</p>
            <p className="text-xs text-gray-400">Protein</p>
          </div>
          <div>
            <p className="text-xl font-bold text-amber-500">{goals.carbs_goal_g}g</p>
            <p className="text-xs text-gray-400">Carbs</p>
          </div>
          <div>
            <p className="text-xl font-bold text-rose-400">{goals.fat_goal_g}g</p>
            <p className="text-xs text-gray-400">Fat</p>
          </div>
        </div>
      </div>
    </div>
  )
}

// ── Profile view (after onboarding) ──────────────────────────────────────────

function StatCard({ label, value, sub }) {
  return (
    <div className="bg-white border border-gray-100 rounded-xl p-3 shadow-sm">
      <p className="text-xs text-gray-400 uppercase tracking-wide mb-1">{label}</p>
      <p className="font-semibold text-gray-800 text-sm">{value}</p>
      {sub && <p className="text-xs text-gray-400 mt-0.5 truncate">{sub}</p>}
    </div>
  )
}

function ProfileView({ profile, onEdit }) {
  const goals = profile.goals
  const actOpt = ACTIVITY_OPTIONS.find(a => a.value === profile.activity_level)
  const aimOpt = AIM_OPTIONS.find(a => a.value === profile.aim)

  return (
    <div className="max-w-md mx-auto px-4 pt-6 pb-24 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">{profile.name || 'Profile'}</h1>
          <p className="text-sm text-gray-400 mt-0.5 capitalize">
            {profile.gender} · {profile.age} yrs · {aimOpt?.label || profile.aim}
            {profile.dietary_preference && ` · ${profile.dietary_preference.replace('_', '-')}`}
          </p>
        </div>
        <button
          onClick={onEdit}
          className="px-3 py-1.5 rounded-lg border border-gray-200 text-gray-600 text-sm hover:bg-gray-50"
        >
          Edit
        </button>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <StatCard
          label="Height"
          value={`${profile.height_cm} cm`}
          sub={cmToFtIn(profile.height_cm)}
        />
        <StatCard
          label="Weight"
          value={`${profile.weight_kg} kg`}
          sub={`${kgToLbs(profile.weight_kg)} lbs`}
        />
        <StatCard
          label="Activity"
          value={actOpt?.label || profile.activity_level}
          sub={actOpt?.desc}
        />
        <StatCard
          label="Goal"
          value={aimOpt?.label || profile.aim}
          sub={aimOpt?.desc}
        />
      </div>

      {goals && (
        <>
          <div className="bg-green-50 rounded-2xl p-4 text-center">
            <p className="text-sm font-medium text-green-600 mb-1">Daily Calorie Goal</p>
            <p className="text-4xl font-bold text-green-600">{goals.daily_goal.toLocaleString()}</p>
            <p className="text-xs text-green-500 mt-0.5">kcal / day</p>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="bg-white border border-gray-100 rounded-xl p-3 text-center shadow-sm">
              <p className="text-xs text-gray-400 uppercase tracking-wide">BMR</p>
              <p className="text-xl font-bold text-gray-800 mt-0.5">{Math.round(goals.bmr).toLocaleString()}</p>
              <p className="text-xs text-gray-400">kcal base</p>
            </div>
            <div className="bg-white border border-gray-100 rounded-xl p-3 text-center shadow-sm">
              <p className="text-xs text-gray-400 uppercase tracking-wide">TDEE</p>
              <p className="text-xl font-bold text-gray-800 mt-0.5">{Math.round(goals.tdee).toLocaleString()}</p>
              <p className="text-xs text-gray-400">kcal active</p>
            </div>
          </div>

          <div className="bg-white border border-gray-100 rounded-xl p-4 shadow-sm">
            <p className="text-sm font-medium text-gray-600 mb-3">Daily Macro Targets</p>
            <div className="grid grid-cols-3 gap-2 text-center">
              <div>
                <p className="text-xl font-bold text-blue-500">{Math.round(goals.protein_goal_g)}g</p>
                <p className="text-xs text-gray-400">Protein</p>
              </div>
              <div>
                <p className="text-xl font-bold text-amber-500">{Math.round(goals.carbs_goal_g)}g</p>
                <p className="text-xs text-gray-400">Carbs</p>
              </div>
              <div>
                <p className="text-xl font-bold text-rose-400">{Math.round(goals.fat_goal_g)}g</p>
                <p className="text-xs text-gray-400">Fat</p>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  )
}

// ── Main page ─────────────────────────────────────────────────────────────────

export default function ProfilePage() {
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(true)
  const [step, setStep] = useState(1)
  const [form, setForm] = useState({
    name: '',
    email: '',
    age: 25,
    gender: 'male',
    height_cm: 170,
    weight_kg: 70,
    activity_level: 'moderate',
    aim: 'maintain',
    dietary_preference: null,
    cuisine_preferences: [],
  })
  const [saving, setSaving] = useState(false)
  const [editing, setEditing] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    getProfile()
      .then(p => {
        setProfile(p)
        if (p.is_setup) {
          setForm({
            name: p.name || '',
            email: p.email || '',
            age: p.age ?? 25,
            gender: p.gender || 'male',
            height_cm: p.height_cm ?? 170,
            weight_kg: p.weight_kg ?? 70,
            activity_level: p.activity_level || 'moderate',
            aim: p.aim || 'maintain',
            dietary_preference: p.dietary_preference || null,
            cuisine_preferences: p.cuisine_preferences || [],
          })
        }
      })
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }))

  const canNext = () => {
    if (step === 1) return form.name.trim().length > 0 && Number(form.age) >= 10
    return true
  }

  const handleSave = async () => {
    setSaving(true)
    try {
      const payload = {
        name: form.name,
        email: form.email || null,
        age: Number(form.age),
        gender: form.gender,
        height_cm: Number(form.height_cm),
        weight_kg: Number(form.weight_kg),
        activity_level: form.activity_level,
        aim: form.aim,
        dietary_preference: form.dietary_preference || null,
        cuisine_preferences: form.cuisine_preferences || [],
      }
      const updated = await setupProfile(payload)
      setProfile(updated)
      setEditing(false)
      navigate('/')
    } catch (e) {
      console.error(e)
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <div className="max-w-md mx-auto px-4 pt-6">
        <div className="text-center text-gray-400 text-sm py-12">Loading…</div>
      </div>
    )
  }

  if (profile?.is_setup && !editing) {
    return (
      <ProfileView
        profile={profile}
        onEdit={() => { setStep(1); setEditing(true) }}
      />
    )
  }

  const progressPct = (step / 6) * 100

  return (
    <div className="max-w-md mx-auto px-4 pt-6 pb-24 space-y-5">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold text-gray-900">
          {editing ? 'Edit Profile' : 'Set Up Your Profile'}
        </h1>
        <p className="text-sm text-gray-400 mt-0.5">
          Step {step} of 6 — {STEP_TITLES[step - 1]}
        </p>
      </div>

      {/* Progress bar */}
      <div className="w-full h-1.5 bg-gray-100 rounded-full overflow-hidden">
        <div
          className="h-full bg-green-400 rounded-full transition-all duration-300"
          style={{ width: `${progressPct}%` }}
        />
      </div>

      {/* Step card */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5">
        <h2 className="font-semibold text-gray-800 mb-4">{STEP_TITLES[step - 1]}</h2>
        {step === 1 && <Step1 form={form} set={set} />}
        {step === 2 && <Step2 form={form} set={set} />}
        {step === 3 && <Step3 form={form} set={set} />}
        {step === 4 && <Step4 form={form} set={set} />}
        {step === 5 && <Step5 form={form} set={set} />}
        {step === 6 && <Step6 form={form} />}
      </div>

      {/* Navigation */}
      <div className="flex gap-3">
        {step > 1 && (
          <button
            onClick={() => setStep(s => s - 1)}
            className="flex-1 py-3 rounded-xl border border-gray-200 text-gray-600 text-sm font-medium hover:bg-gray-50"
          >
            Back
          </button>
        )}
        {step < 6 ? (
          <button
            onClick={() => setStep(s => s + 1)}
            disabled={!canNext()}
            className="flex-1 py-3 rounded-xl bg-green-500 text-white text-sm font-medium disabled:opacity-40 transition-opacity"
          >
            Next
          </button>
        ) : (
          <button
            onClick={handleSave}
            disabled={saving}
            className="flex-1 py-3 rounded-xl bg-green-500 text-white text-sm font-medium disabled:opacity-40 transition-opacity"
          >
            {saving ? 'Saving…' : 'Start Tracking'}
          </button>
        )}
      </div>
    </div>
  )
}
