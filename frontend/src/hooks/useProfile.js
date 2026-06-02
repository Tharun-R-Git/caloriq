import { useState, useEffect } from 'react'
import { getProfile, updateProfile } from '../api/api'

export function useProfile() {
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    setLoading(true)
    getProfile()
      .then(setProfile)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  const save = async (data) => {
    const updated = await updateProfile(data)
    setProfile(updated)
    return updated
  }

  return { profile, loading, error, save }
}
