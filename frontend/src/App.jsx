import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom'
import Home from './pages/Home'
import Log from './pages/Log'
import HistoryPage from './pages/History'
import Trends from './pages/Trends'
import ProfilePage from './pages/Profile'

const NAV_ITEMS = [
  { to: '/', label: 'Home' },
  { to: '/log', label: 'Log' },
  { to: '/history', label: 'History' },
  { to: '/trends', label: 'Trends' },
  { to: '/profile', label: 'Profile' },
]

function NavBar() {
  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 flex max-w-md mx-auto left-1/2 -translate-x-1/2 w-full">
      {NAV_ITEMS.map(({ to, label }) => (
        <NavLink
          key={to}
          to={to}
          end={to === '/'}
          className={({ isActive }) =>
            `flex-1 text-center py-3 text-xs font-medium transition-colors ${
              isActive ? 'text-green-600' : 'text-gray-400'
            }`
          }
        >
          {label}
        </NavLink>
      ))}
    </nav>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50 pb-16">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/log" element={<Log />} />
          <Route path="/history" element={<HistoryPage />} />
          <Route path="/trends" element={<Trends />} />
          <Route path="/profile" element={<ProfilePage />} />
        </Routes>
        <NavBar />
      </div>
    </BrowserRouter>
  )
}
