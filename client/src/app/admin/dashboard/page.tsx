'use client'

import { useAuthStore } from '@/store/authStore'
import { Button } from '@/components/ui/button'
import { useRouter } from 'next/navigation'

export default function AdminDashboard() {
  const logout = useAuthStore((state) => state.logout)
  const user = useAuthStore((state) => state.user)
  const router = useRouter()

  const handleLogout = () => {
    document.cookie = 'auth_token=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT;'
    localStorage.removeItem('token')
    logout()
    router.push('/login')
  }

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">Admin Dashboard</h1>
      <p className="mb-4">Welcome, {user?.name || 'Admin'}!</p>
      <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-md text-yellow-800 mb-6 inline-block">
        Dashboard coming in next phase
      </div>
      <div>
        <Button onClick={handleLogout} variant="destructive">Logout</Button>
      </div>
    </div>
  )
}
