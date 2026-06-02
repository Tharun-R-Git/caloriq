import ProfileForm from '../components/Profile'

export default function ProfilePage() {
  return (
    <div className="max-w-md mx-auto px-4 pt-6 space-y-4">
      <h1 className="text-xl font-bold text-gray-900">Profile</h1>
      <ProfileForm />
    </div>
  )
}
