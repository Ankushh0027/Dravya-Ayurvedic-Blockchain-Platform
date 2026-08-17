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
  const { user } = useAuthStore()
  const router = useRouter()
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  useEffect(() => {
    if (mounted && user && user.role !== 'DISTRIBUTOR') {
      router.replace('/unauthorized')
    }
  }, [user, mounted, router])

  if (!mounted) {
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
