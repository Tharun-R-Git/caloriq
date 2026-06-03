import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Register() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    if (password.length < 6) {
      setError('Password must be at least 6 characters.')
      return
    }
    setSubmitting(true)
    try {
      await register(email.trim(), password, name.trim())
      navigate('/')
    } catch (err) {
      let msg = 'Sign up failed. Please try again.'
      try { msg = JSON.parse(err.message)?.detail || msg } catch { /* keep default */ }
      setError(msg)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="max-w-md mx-auto px-4 pt-16 pb-24">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-green-600">CaloriQ</h1>
        <p className="text-sm text-gray-400 mt-1">Create an account to start tracking</p>
      </div>

      <form onSubmit={handleSubmit} className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5 space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-600 mb-1.5">Name</label>
          <input
            type="text"
            value={name}
            onChange={e => setName(e.target.value)}
            placeholder="e.g. Alex"
            autoComplete="name"
            className="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-green-400"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-600 mb-1.5">Email</label>
          <input
            type="email"
            value={email}
            onChange={e => setEmail(e.target.value)}
            placeholder="you@example.com"
            autoComplete="email"
            required
            className="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-green-400"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-600 mb-1.5">Password</label>
          <input
            type="password"
            value={password}
            onChange={e => setPassword(e.target.value)}
            placeholder="At least 6 characters"
            autoComplete="new-password"
            required
            className="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-green-400"
          />
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-xl px-4 py-3 text-sm text-red-600">
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={submitting}
          className="w-full py-3 rounded-xl bg-green-500 text-white text-sm font-medium disabled:opacity-40 transition-opacity"
        >
          {submitting ? 'Creating account…' : 'Sign Up'}
        </button>
      </form>

      <p className="text-center text-sm text-gray-400 mt-5">
        Already have an account?{' '}
        <Link to="/login" className="text-green-600 font-medium">Log in</Link>
      </p>
    </div>
  )
}
