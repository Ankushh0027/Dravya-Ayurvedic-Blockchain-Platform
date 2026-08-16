'use client'

import React, { useEffect } from 'react'
import { useAuthStore } from '@/store/authStore'
import { ProducerService } from '@/services/api/producer'
import { useApi } from '@/hooks/useApi'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { LoadingState } from '@/components/shared/LoadingState'
import { ErrorState } from '@/components/shared/ErrorState'
import { BatchStatusBadge } from '@/components/shared/BatchStatusBadge'
import { Activity, Leaf, AlertCircle, FileText, CheckCircle2, FlaskConical, Navigation, ShieldCheck, Plus, Package } from 'lucide-react'
import Link from 'next/link'

export default function ProducerDashboard() {
  const user = useAuthStore(state => state.user)
  const { data: stats, isLoading, error, execute: fetchDashboard } = useApi(ProducerService.getDashboard)

  useEffect(() => {
    fetchDashboard()
  }, [fetchDashboard])

  if (isLoading && !stats) return <LoadingState message="Loading dashboard statistics..." />
  if (error && !stats) return <ErrorState message={error} onRetry={() => fetchDashboard()} />

  const db = stats?.dashboard
  const recent = stats?.recentBatches || []

  const hasNoActivity = db && Object.values(db).every(v => v === 0)

  // Reusable card class
  const glassCard = "bg-white/80 backdrop-blur-xl border border-white/60 shadow-[0_8px_40px_rgb(0,0,0,0.04)] rounded-[24px] hover:shadow-[0_12px_50px_rgb(0,0,0,0.08)] transition-all duration-500 overflow-hidden relative"

  return (
    <div className="max-w-[1400px] mx-auto p-6 md:p-10 space-y-10">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
        <div>
          <h1 className="text-4xl md:text-5xl font-bold tracking-tight text-[#1e293b] font-serif mb-2">
            Welcome, <span className="text-[#184E48]">{user?.name}</span>
          </h1>
          <p className="text-[17px] text-slate-600 font-medium">Here is your producer dashboard overview.</p>
        </div>
        <div className="flex flex-wrap gap-4">
          <Link href="/producer/profile">
            <Button variant="outline" className="border-white/60 bg-white/50 hover:bg-white text-[#184E48] rounded-xl px-6 py-6 text-[15px] font-bold shadow-sm transition-all duration-300 backdrop-blur-sm">
              <Navigation className="w-4 h-4 mr-2" />
              My Profile
            </Button>
          </Link>
          <Link href="/producer/batches/create">
            <Button className="bg-[#184E48] hover:bg-[#184E48]/90 text-white rounded-xl px-6 py-6 text-[15px] font-semibold shadow-[0_8px_30px_rgb(24,78,72,0.2)] hover:shadow-[0_8px_30px_rgb(24,78,72,0.3)] hover:-translate-y-0.5 transition-all duration-300">
              <Plus className="w-5 h-5 mr-2" />
              Create Batch
            </Button>
          </Link>
        </div>
      </div>

      {hasNoActivity && (
        <Card className={`${glassCard} bg-gradient-to-br from-white/90 to-[#184E48]/5`}>
          <div className="absolute top-0 left-0 w-full h-1 bg-[#184E48]" />
          <CardHeader>
            <CardTitle className="text-2xl font-serif text-[#1e293b]">Welcome to Dravya</CardTitle>
            <CardDescription className="text-base text-slate-600">Get started by completing your profile and creating your first batch.</CardDescription>
          </CardHeader>
          <CardContent className="flex gap-4">
            <Link href="/producer/profile">
              <Button className="bg-[#184E48] hover:bg-[#184E48]/90 text-white rounded-xl shadow-md transition-all">
                Complete Profile
              </Button>
            </Link>
          </CardContent>
        </Card>
      )}

      {db && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card className={`${glassCard} group`}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-bold text-slate-500 uppercase tracking-wider">Total Batches</CardTitle>
              <div className="w-12 h-12 rounded-2xl bg-[#184E48]/5 group-hover:bg-[#184E48]/10 flex items-center justify-center shadow-sm transition-colors duration-300">
                <Activity className="h-6 w-6 text-[#184E48]" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-4xl font-bold text-[#1e293b] font-serif">{db.totalBatches}</div>
            </CardContent>
          </Card>

          <Card className={`${glassCard} group`}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-bold text-slate-500 uppercase tracking-wider">Draft Batches</CardTitle>
              <div className="w-12 h-12 rounded-2xl bg-slate-100 group-hover:bg-slate-200 flex items-center justify-center shadow-sm transition-colors duration-300">
                <FileText className="h-6 w-6 text-slate-600" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-4xl font-bold text-[#1e293b] font-serif">{db.draftBatches}</div>
            </CardContent>
          </Card>

          <Card className={`${glassCard} group`}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-bold text-slate-500 uppercase tracking-wider">Pending Verif.</CardTitle>
              <div className="w-12 h-12 rounded-2xl bg-amber-100 group-hover:bg-amber-200 flex items-center justify-center shadow-sm transition-colors duration-300">
                <AlertCircle className="h-6 w-6 text-amber-600" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-4xl font-bold text-[#1e293b] font-serif">{db.pendingVerification}</div>
            </CardContent>
          </Card>

          <Card className={`${glassCard} group`}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-bold text-slate-500 uppercase tracking-wider">Verified Batches</CardTitle>
              <div className="w-12 h-12 rounded-2xl bg-emerald-100 group-hover:bg-emerald-200 flex items-center justify-center shadow-sm transition-colors duration-300">
                <CheckCircle2 className="h-6 w-6 text-emerald-600" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-4xl font-bold text-[#1e293b] font-serif">{db.verifiedBatches}</div>
            </CardContent>
          </Card>
        </div>
      )}

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
        <Card className={`xl:col-span-2 ${glassCard}`}>
          <CardHeader className="border-b border-slate-100/50 pb-6 mb-4">
            <CardTitle className="text-2xl font-serif text-[#1e293b]">Recent Batches</CardTitle>
            <CardDescription className="text-slate-500 font-medium">Your most recently created or updated batches.</CardDescription>
          </CardHeader>
          <CardContent>
            {recent.length === 0 ? (
              <div className="py-12 text-center flex flex-col items-center justify-center bg-slate-50/50 rounded-[20px] border border-dashed border-slate-200">
                <div className="w-16 h-16 rounded-full bg-white flex items-center justify-center shadow-sm mb-4">
                  <Package className="w-8 h-8 text-slate-300" />
                </div>
                <h3 className="text-lg font-bold text-[#1e293b] mb-1">No batches found</h3>
                <p className="text-slate-500 mb-6 max-w-sm">You haven't created any batches yet. Start tracking your herbs by creating a new batch.</p>
                <Link href="/producer/batches/create">
                  <Button className="bg-[#184E48] hover:bg-[#184E48]/90 text-white rounded-xl shadow-md">
                    Create First Batch
                  </Button>
                </Link>
              </div>
            ) : (
              <div className="space-y-3">
                {recent.map(batch => (
                  <div key={batch.id} className="group flex items-center justify-between p-4 bg-white/50 hover:bg-white rounded-2xl border border-slate-100 shadow-sm hover:shadow-md transition-all duration-300 cursor-pointer">
                    <div className="flex flex-col">
                      <Link href={`/producer/batches/${batch.id}`} className="text-lg font-bold text-[#1e293b] group-hover:text-[#184E48] transition-colors">
                        {batch.batchNumber}
                      </Link>
                      <div className="text-sm font-medium text-slate-500 flex items-center gap-1.5 mt-1">
                        <div className="w-5 h-5 rounded-full bg-[#184E48]/10 flex items-center justify-center">
                          <Leaf className="w-3 h-3 text-[#184E48]" />
                        </div>
                        {batch.herb?.commonName}
                      </div>
                    </div>
                    <div>
                      <BatchStatusBadge status={batch.status} />
                    </div>
                  </div>
                ))}
                <div className="pt-4">
                  <Link href="/producer/batches" className="w-full inline-block">
                    <Button variant="outline" className="w-full bg-white/50 hover:bg-white text-[#1e293b] border-white/60 rounded-xl font-bold py-6 backdrop-blur-sm shadow-sm transition-all">
                      View All Batches
                    </Button>
                  </Link>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        <Card className={`xl:col-span-1 ${glassCard}`}>
          <CardHeader className="border-b border-slate-100/50 pb-6 mb-4">
            <CardTitle className="text-2xl font-serif text-[#1e293b]">Quick Actions</CardTitle>
            <CardDescription className="text-slate-500 font-medium">Common tasks</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <Link href="/producer/herbs" className="block">
              <div className="flex items-center gap-4 p-4 rounded-2xl hover:bg-white border border-transparent hover:border-slate-100 hover:shadow-md transition-all duration-300 group cursor-pointer">
                <div className="w-12 h-12 rounded-2xl bg-emerald-50 group-hover:bg-emerald-100 flex items-center justify-center transition-colors">
                  <Leaf className="w-6 h-6 text-emerald-600" />
                </div>
                <div>
                  <h4 className="font-bold text-[#1e293b] group-hover:text-[#184E48] transition-colors">Herb Catalog</h4>
                  <p className="text-sm text-slate-500">View supported herbs</p>
                </div>
              </div>
            </Link>
            
            <Link href="/producer/verification" className="block">
              <div className="flex items-center gap-4 p-4 rounded-2xl bg-white/30 hover:bg-white border border-transparent hover:border-white/60 hover:shadow-md transition-all duration-300 group cursor-pointer">
                <div className="w-12 h-12 rounded-2xl bg-blue-50 group-hover:bg-blue-100 flex items-center justify-center transition-colors">
                  <ShieldCheck className="w-6 h-6 text-blue-600" />
                </div>
                <div>
                  <h4 className="font-bold text-[#1e293b] group-hover:text-[#184E48] transition-colors">Verification Status</h4>
                  <p className="text-sm text-slate-500">Check profile verification</p>
                </div>
              </div>
            </Link>

            <Link href="/producer/profile" className="block">
              <div className="flex items-center gap-4 p-4 rounded-2xl bg-white/30 hover:bg-white border border-transparent hover:border-white/60 hover:shadow-md transition-all duration-300 group cursor-pointer">
                <div className="w-12 h-12 rounded-2xl bg-purple-50 group-hover:bg-purple-100 flex items-center justify-center transition-colors">
                  <Navigation className="w-6 h-6 text-purple-600" />
                </div>
                <div>
                  <h4 className="font-bold text-[#1e293b] group-hover:text-[#184E48] transition-colors">Update Profile</h4>
                  <p className="text-sm text-slate-500">Manage farm details</p>
                </div>
              </div>
            </Link>

            <Link href="/producer/batches/create" className="block">
              <div className="flex items-center gap-4 p-4 rounded-2xl bg-white/30 hover:bg-white border border-transparent hover:border-white/60 hover:shadow-md transition-all duration-300 group cursor-pointer">
                <div className="w-12 h-12 rounded-2xl bg-[#184E48]/5 group-hover:bg-[#184E48]/10 flex items-center justify-center transition-colors">
                  <FlaskConical className="w-6 h-6 text-[#184E48]" />
                </div>
                <div>
                  <h4 className="font-bold text-[#1e293b] group-hover:text-[#184E48] transition-colors">Create Batch</h4>
                  <p className="text-sm text-slate-500">Record a new harvest</p>
                </div>
              </div>
            </Link>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
