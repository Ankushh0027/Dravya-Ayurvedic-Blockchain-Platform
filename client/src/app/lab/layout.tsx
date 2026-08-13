'use client'

import { LabNavbar } from '@/components/layouts/LabNavbar'
import { Footer } from '@/features/landing/components/Footer'
import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/store/authStore'
import { LoadingState } from '@/components/shared/LoadingState'

export default function LabLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const router = useRouter()
  const user = useAuthStore(state => state.user)
  const [isAuthorized, setIsAuthorized] = useState(false)

  useEffect(() => {
    // Basic frontend check. Middleware is the real security layer.
    if (!user) {
      router.push('/login')
    } else if (user.role !== 'LAB' && user.role !== 'ADMIN') {
      router.push('/unauthorized')
    } else {
      setIsAuthorized(true)
    }
  }, [user, router])

  if (!isAuthorized) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#F8F9FA]">
        <LoadingState message="Verifying access..." />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[#F8F9FA] flex flex-col font-sans relative overflow-x-hidden">
      {/* Background patterns */}
      <div className="fixed inset-0 pointer-events-none opacity-[0.03] mix-blend-multiply z-0">
        <div className="absolute inset-0 bg-[url('/pattern.svg')] bg-repeat opacity-50" />
      </div>

      <LabNavbar />
      
      <main className="flex-1 w-full max-w-[1600px] mx-auto px-4 sm:px-6 py-6 md:py-8 relative z-10 flex flex-col">
        {children}
      </main>

      <Footer />
    </div>
  )
}
