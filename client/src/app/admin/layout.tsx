'use client'

import React from 'react'
import { AdminNavbar } from '@/components/layouts/AdminNavbar'
import { Toaster } from 'sonner'
import { ProtectedRoute } from '@/components/shared/ProtectedRoute'

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <ProtectedRoute allowedRoles={['ADMIN']}>
      <div className="min-h-screen bg-[#F8FAFC]">
        <AdminNavbar />
        <main className="pb-12">
          {children}
        </main>
        <Toaster position="top-center" />
      </div>
    </ProtectedRoute>
  )
}
