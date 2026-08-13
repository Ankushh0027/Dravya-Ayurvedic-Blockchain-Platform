'use client'

import React, { useEffect, useState } from 'react'
import { authorityApi } from '@/services/api/authority'
import { AuthorityDashboardStats } from '@/types/authority'
import { LoadingState } from '@/components/shared/LoadingState'
import { ErrorState } from '@/components/shared/ErrorState'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { ShieldCheck, SearchCheck, CheckCircle2, XCircle, CalendarClock } from 'lucide-react'
import { useAuthStore } from '@/store/authStore'
import Link from 'next/link'

export default function AuthorityDashboard() {
  const user = useAuthStore(state => state.user)
  const [stats, setStats] = useState<AuthorityDashboardStats | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchDashboard()
  }, [])

  const fetchDashboard = async () => {
    setIsLoading(true)
    setError(null)
    try {
      const response = await authorityApi.getDashboard()
      if (response.data?.success && response.data.data?.dashboard) {
        setStats(response.data.data.dashboard)
      } else {
        setError('Failed to load dashboard statistics')
      }
    } catch (err: any) {
      console.error('Error fetching dashboard:', err)
      setError(err.response?.data?.message || 'Failed to load dashboard data')
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading && !stats) {
    return <LoadingState message="Loading authority dashboard..." />
  }

  if (error && !stats) {
    return <ErrorState message={error || 'Dashboard data unavailable'} onRetry={fetchDashboard} />
  }

  const glassCard = "bg-white/70 backdrop-blur-xl border border-white/60 shadow-[0_8px_40px_rgb(0,0,0,0.04)] rounded-[24px] hover:shadow-[0_12px_50px_rgb(0,0,0,0.08)] transition-all duration-500 overflow-hidden relative"

  return (
    <div className="max-w-[1400px] mx-auto p-6 md:p-10 space-y-10">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
        <div>
          <h1 className="text-4xl md:text-5xl font-bold tracking-tight text-[#1e293b] font-serif mb-2">
            Welcome, <span className="text-[#184E48]">{user?.name}</span>
          </h1>
          <p className="text-[17px] text-slate-600 font-medium">Overview of your assigned verification and inspection tasks.</p>
        </div>
        <div className="flex flex-wrap gap-4">
          <Link href="/authority/verifications">
            <Button variant="outline" className="border-[#184E48]/20 bg-white hover:bg-slate-50 text-[#184E48] rounded-xl px-6 py-6 text-[15px] font-bold shadow-sm transition-all duration-300">
              <ShieldCheck className="w-4 h-4 mr-2" />
              Producer Queue
            </Button>
          </Link>
          <Link href="/authority/inspections">
            <Button className="bg-[#184E48] hover:bg-[#184E48]/90 text-white rounded-xl px-6 py-6 text-[15px] font-semibold shadow-[0_8px_30px_rgb(24,78,72,0.2)] hover:shadow-[0_8px_30px_rgb(24,78,72,0.3)] hover:-translate-y-0.5 transition-all duration-300">
              <SearchCheck className="w-5 h-5 mr-2" />
              Inspection Queue
            </Button>
          </Link>
        </div>
      </div>

      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6">
          <Card className={`${glassCard} group`}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-bold text-slate-500 uppercase tracking-wider">Pending Verif.</CardTitle>
              <div className="w-12 h-12 rounded-2xl bg-orange-50 group-hover:bg-orange-100 flex items-center justify-center shadow-sm transition-colors duration-300">
                <ShieldCheck className="h-6 w-6 text-orange-600" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-4xl font-bold text-[#1e293b] font-serif">{stats.pendingProducerVerifications}</div>
            </CardContent>
          </Card>

          <Card className={`${glassCard} group`}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-bold text-slate-500 uppercase tracking-wider">Pending Inspections</CardTitle>
              <div className="w-12 h-12 rounded-2xl bg-blue-50 group-hover:bg-blue-100 flex items-center justify-center shadow-sm transition-colors duration-300">
                <SearchCheck className="h-6 w-6 text-blue-600" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-4xl font-bold text-[#1e293b] font-serif">{stats.pendingLotInspections}</div>
            </CardContent>
          </Card>

          <Card className={`${glassCard} group`}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-bold text-slate-500 uppercase tracking-wider">This Month</CardTitle>
              <div className="w-12 h-12 rounded-2xl bg-teal-50 group-hover:bg-teal-100 flex items-center justify-center shadow-sm transition-colors duration-300">
                <CalendarClock className="h-6 w-6 text-teal-600" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-4xl font-bold text-[#1e293b] font-serif">{stats.inspectionsThisMonth}</div>
            </CardContent>
          </Card>

          <Card className={`${glassCard} group`}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-bold text-slate-500 uppercase tracking-wider">Approved Prod.</CardTitle>
              <div className="w-12 h-12 rounded-2xl bg-emerald-50 group-hover:bg-emerald-100 flex items-center justify-center shadow-sm transition-colors duration-300">
                <CheckCircle2 className="h-6 w-6 text-emerald-600" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-4xl font-bold text-[#1e293b] font-serif">{stats.approvedProducers}</div>
            </CardContent>
          </Card>

          <Card className={`${glassCard} group`}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-bold text-slate-500 uppercase tracking-wider">Rejected Prod.</CardTitle>
              <div className="w-12 h-12 rounded-2xl bg-red-50 group-hover:bg-red-100 flex items-center justify-center shadow-sm transition-colors duration-300">
                <XCircle className="h-6 w-6 text-red-600" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-4xl font-bold text-[#1e293b] font-serif">{stats.rejectedProducers}</div>
            </CardContent>
          </Card>
        </div>
      )}

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
        <Card className={`xl:col-span-2 ${glassCard}`}>
          <CardHeader className="border-b border-slate-100/50 pb-6 mb-4">
            <CardTitle className="text-2xl font-serif text-[#1e293b]">Verification Guidelines</CardTitle>
            <CardDescription className="text-slate-500 font-medium">Standard operating procedures for field authorities.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-start gap-4 p-4 rounded-2xl bg-slate-50 border border-slate-100">
                <div className="w-10 h-10 rounded-xl bg-orange-100 flex items-center justify-center flex-shrink-0 mt-1">
                  <ShieldCheck className="w-5 h-5 text-orange-600" />
                </div>
                <div>
                  <h4 className="font-bold text-[#1e293b] mb-1">Producer Verifications</h4>
                  <p className="text-sm text-slate-600">Ensure the physical location matches the submitted coordinates. Verify the identity documents, land ownership, and stated land size before approval.</p>
                </div>
              </div>
              
              <div className="flex items-start gap-4 p-4 rounded-2xl bg-slate-50 border border-slate-100">
                <div className="w-10 h-10 rounded-xl bg-blue-100 flex items-center justify-center flex-shrink-0 mt-1">
                  <SearchCheck className="w-5 h-5 text-blue-600" />
                </div>
                <div>
                  <h4 className="font-bold text-[#1e293b] mb-1">Lot Inspections</h4>
                  <p className="text-sm text-slate-600">During lot inspection, the declared quantity must be strictly verified against the physically inspected quantity. Ensure packaging prevents contamination.</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className={`xl:col-span-1 ${glassCard}`}>
          <CardHeader className="border-b border-slate-100/50 pb-6 mb-4">
            <CardTitle className="text-2xl font-serif text-[#1e293b]">Quick Actions</CardTitle>
            <CardDescription className="text-slate-500 font-medium">Common tasks</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <Link href="/authority/verifications" className="block">
              <div className="flex items-center gap-4 p-4 rounded-2xl hover:bg-white border border-transparent hover:border-slate-100 hover:shadow-md transition-all duration-300 group cursor-pointer">
                <div className="w-12 h-12 rounded-2xl bg-orange-50 group-hover:bg-orange-100 flex items-center justify-center transition-colors">
                  <ShieldCheck className="w-6 h-6 text-orange-600" />
                </div>
                <div>
                  <h4 className="font-bold text-[#1e293b] group-hover:text-[#184E48] transition-colors">Producer Queue</h4>
                  <p className="text-sm text-slate-500">View pending profiles</p>
                </div>
              </div>
            </Link>
            
            <Link href="/authority/inspections" className="block">
              <div className="flex items-center gap-4 p-4 rounded-2xl hover:bg-white border border-transparent hover:border-slate-100 hover:shadow-md transition-all duration-300 group cursor-pointer">
                <div className="w-12 h-12 rounded-2xl bg-blue-50 group-hover:bg-blue-100 flex items-center justify-center transition-colors">
                  <SearchCheck className="w-6 h-6 text-blue-600" />
                </div>
                <div>
                  <h4 className="font-bold text-[#1e293b] group-hover:text-[#184E48] transition-colors">Inspection Queue</h4>
                  <p className="text-sm text-slate-500">View pending batches</p>
                </div>
              </div>
            </Link>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
