'use client'

import { Button } from '@/components/ui/button'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/store/authStore'
import { getDashboardRoute } from '@/utils/routes'

export default function UnauthorizedPage() {
  const router = useRouter()
  const user = useAuthStore((state) => state.user)
  const logout = useAuthStore((state) => state.logout)

  const handleLogout = () => {
    logout()
  }

  const goHome = () => {
    if (user) {
      router.push(getDashboardRoute(user.role))
    } else {
      router.push('/login')
    }
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-slate-50">
      <div className="max-w-md w-full bg-white p-8 rounded-xl shadow-sm border border-slate-200 text-center">
        <h1 className="text-3xl font-bold text-red-600 mb-4">Unauthorized</h1>
        <p className="text-slate-600 mb-8">
          You don&apos;t have permission to access this page.
        </p>
        <div className="flex flex-col gap-3">
          <Button onClick={() => router.back()} variant="outline">Go Back</Button>
          <Button onClick={goHome} className="bg-[#184E48] hover:bg-[#184E48]/90">
            {user ? 'Go to Dashboard' : 'Go to Login'}
          </Button>
          {user && (
            <Button onClick={handleLogout} variant="ghost" className="text-slate-500">
              Logout
            </Button>
          )}
        </div>
      </div>
    </div>
  )
}
