'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/store/authStore'
import { LoadingState } from '@/components/shared/LoadingState'
import { DistributorNavbar } from '@/components/layouts/DistributorNavbar'

export default function DistributorLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const { user, isHydrated, role } = useAuthStore()
  const router = useRouter()
  const [isAuthorized, setIsAuthorized] = useState(false)

  useEffect(() => {
    if (isHydrated) {
      if (!user) {
        router.replace('/login')
      } else if (role !== 'DISTRIBUTOR') {
        router.replace('/unauthorized')
      } else {
        setIsAuthorized(true)
      }
    }
  }, [user, isHydrated, role, router])

  if (!isHydrated || !isAuthorized) {
    return <LoadingState message="Verifying access..." />
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <DistributorNavbar />
      <main className="pt-16 sm:pt-20 pb-20 sm:pb-8 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
        <div className="mt-6 sm:mt-8">
          {children}
        </div>
      </main>
    </div>
  )
}
