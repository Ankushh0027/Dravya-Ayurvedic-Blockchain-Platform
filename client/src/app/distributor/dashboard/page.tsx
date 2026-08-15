'use client'

import React, { useEffect, useState } from 'react'
import { distributorApi } from '@/services/api/distributor'
import { DistributorDashboardStats, DistributorAssignment } from '@/types/distributor'
import { LoadingState } from '@/components/shared/LoadingState'
import { ErrorState } from '@/components/shared/ErrorState'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { useAuthStore } from '@/store/authStore'
import Link from 'next/link'
import { Truck, ArrowRight, ClipboardList, CheckCircle2, PackageCheck, Send, Package, Clock } from 'lucide-react'

export default function DistributorDashboard() {
  const { user } = useAuthStore()
  const [stats, setStats] = useState<DistributorDashboardStats | null>(null)
  const [assignments, setAssignments] = useState<DistributorAssignment[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    setIsLoading(true)
    setError(null)
    try {
      const [statsData, batchesData] = await Promise.all([
        distributorApi.getDashboard(),
        distributorApi.getAssignedBatches()
      ])
      setStats(statsData)
      setAssignments(batchesData.assignments)
    } catch (err: any) {
      console.error('Error fetching distributor dashboard:', err)
      setError(err.response?.data?.message || 'Failed to load dashboard data')
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) return <LoadingState message="Loading your dashboard..." />
  if (error) return <ErrorState message={error} onRetry={fetchDashboardData} />

  // Get up to 5 most recent assignments
  const recentAssignments = [...assignments]
    .sort((a, b) => new Date(b.assignedAt).getTime() - new Date(a.assignedAt).getTime())
    .slice(0, 5)

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
        <div>
          <h1 className="text-4xl md:text-5xl font-bold tracking-tight text-[#1e293b] font-serif mb-2">
            Welcome, <span className="text-[#184E48]">{user?.name}</span>
          </h1>
          <p className="text-[17px] text-slate-600 font-medium">Manage your logistics and supply chain assignments.</p>
        </div>
        <div className="flex flex-wrap gap-4">
          <Link href="/distributor/batches">
            <Button className="bg-[#184E48] hover:bg-[#184E48]/90 text-white rounded-xl px-6 py-6 text-[15px] font-semibold shadow-[0_8px_30px_rgb(24,78,72,0.2)] hover:shadow-[0_8px_30px_rgb(24,78,72,0.3)] hover:-translate-y-0.5 transition-all duration-300">
              <Truck className="w-5 h-5 mr-2" />
              View Assigned Batches
            </Button>
          </Link>
        </div>
      </div>

      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card className="bg-white/70 backdrop-blur-xl !border !border-black shadow-[0_8px_30px_rgb(0,0,0,0.04)] hover:shadow-[0_8px_30px_rgb(0,0,0,0.08)] transition-all duration-300 rounded-[24px]">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-bold text-slate-500 uppercase tracking-wider">Awaiting Receipt</CardTitle>
              <div className="w-10 h-10 rounded-full bg-orange-50 flex items-center justify-center">
                <Clock className="w-5 h-5 text-orange-600" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-4xl font-extrabold text-[#1e293b]">{stats.awaitingAcceptance}</div>
              <p className="text-xs font-semibold text-orange-600 mt-1">Ready to receive</p>
            </CardContent>
          </Card>

          <Card className="bg-white/70 backdrop-blur-xl !border !border-black shadow-[0_8px_30px_rgb(0,0,0,0.04)] hover:shadow-[0_8px_30px_rgb(0,0,0,0.08)] transition-all duration-300 rounded-[24px]">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-bold text-slate-500 uppercase tracking-wider">Received / In Hub</CardTitle>
              <div className="w-10 h-10 rounded-full bg-blue-50 flex items-center justify-center">
                <Package className="w-5 h-5 text-blue-600" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-4xl font-extrabold text-[#1e293b]">{stats.accepted}</div>
              <p className="text-xs font-semibold text-blue-600 mt-1">Waiting for dispatch</p>
            </CardContent>
          </Card>

          <Card className="bg-white/70 backdrop-blur-xl !border !border-black shadow-[0_8px_30px_rgb(0,0,0,0.04)] hover:shadow-[0_8px_30px_rgb(0,0,0,0.08)] transition-all duration-300 rounded-[24px]">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-bold text-slate-500 uppercase tracking-wider">In Transit</CardTitle>
              <div className="w-10 h-10 rounded-full bg-indigo-50 flex items-center justify-center">
                <Send className="w-5 h-5 text-indigo-600" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-4xl font-extrabold text-[#1e293b]">{stats.inTransit}</div>
              <p className="text-xs font-semibold text-indigo-600 mt-1">Currently moving</p>
            </CardContent>
          </Card>

          <Card className="bg-white/70 backdrop-blur-xl !border !border-black shadow-[0_8px_30px_rgb(0,0,0,0.04)] hover:shadow-[0_8px_30px_rgb(0,0,0,0.08)] transition-all duration-300 rounded-[24px]">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-bold text-slate-500 uppercase tracking-wider">Delivered</CardTitle>
              <div className="w-10 h-10 rounded-full bg-emerald-50 flex items-center justify-center">
                <PackageCheck className="w-5 h-5 text-emerald-600" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-4xl font-extrabold text-[#1e293b]">{stats.delivered}</div>
              <p className="text-xs font-semibold text-emerald-600 mt-1">Successfully completed</p>
            </CardContent>
          </Card>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
          <Card className="bg-white/70 backdrop-blur-xl !border !border-black shadow-[0_8px_30px_rgb(0,0,0,0.04)] rounded-[24px] overflow-hidden">
            <CardHeader className="border-b border-slate-100 bg-white/50 pb-4">
              <div className="flex justify-between items-center">
                <div>
                  <CardTitle className="text-xl font-bold text-[#1e293b] font-serif flex items-center gap-2">
                    <ClipboardList className="w-5 h-5 text-[#184E48]" />
                    Recent Assignments
                  </CardTitle>
                  <CardDescription className="text-sm font-medium mt-1">Latest batches assigned to you</CardDescription>
                </div>
                <Link href="/distributor/batches">
                  <Button variant="ghost" className="text-[#184E48] hover:bg-[#184E48]/10 font-semibold rounded-xl">
                    View All
                  </Button>
                </Link>
              </div>
            </CardHeader>
            <CardContent className="p-0">
              {recentAssignments.length === 0 ? (
                <div className="p-12 text-center flex flex-col items-center justify-center">
                  <div className="w-20 h-20 bg-slate-50 rounded-full flex items-center justify-center mb-4">
                    <Truck className="w-10 h-10 text-slate-300" />
                  </div>
                  <h3 className="text-lg font-bold text-slate-700 mb-2">No Assignments Yet</h3>
                  <p className="text-slate-500 max-w-sm mx-auto">
                    When an admin assigns a verified batch to you, it will appear here.
                  </p>
                </div>
              ) : (
                <div className="divide-y divide-slate-100">
                  {recentAssignments.map((assignment) => (
                    <div key={assignment.id} className="p-5 hover:bg-slate-50/80 transition-colors group">
                      <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-4">
                        <div>
                          <div className="flex items-center gap-2 mb-1">
                            <h4 className="font-bold text-[#1e293b] text-lg">{assignment.batch?.herb?.commonName || 'Unknown Herb'}</h4>
                            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-slate-100 text-slate-600">
                              {assignment.batch?.batchNumber}
                            </span>
                          </div>
                          <div className="flex items-center gap-3 text-sm text-slate-500 font-medium">
                            <span className="flex items-center gap-1.5">
                              <Package className="w-4 h-4 text-slate-400" />
                              {assignment.batch?.quantity} {assignment.batch?.unit}
                            </span>
                            <span className="w-1 h-1 rounded-full bg-slate-300" />
                            <span className="flex items-center gap-1.5">
                              <Clock className="w-4 h-4 text-slate-400" />
                              Assigned {new Date(assignment.assignedAt).toLocaleDateString()}
                            </span>
                          </div>
                        </div>
                        <Link href={`/distributor/batches/${assignment.batchId}`}>
                          <Button variant="outline" className="w-full sm:w-auto rounded-xl !border !border-black text-[#184E48] hover:bg-[#184E48] hover:text-white transition-all duration-300 group-hover:shadow-md">
                            Manage Logistics
                            <ArrowRight className="w-4 h-4 ml-2" />
                          </Button>
                        </Link>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        <div className="space-y-6">
          <Card className="bg-[#184E48] text-white border-none shadow-[0_8px_30px_rgb(24,78,72,0.2)] rounded-[24px] overflow-hidden relative">
            <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full blur-2xl -mr-10 -mt-10 pointer-events-none" />
            <CardHeader>
              <CardTitle className="text-xl font-bold font-serif">Quick Guide</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex gap-3">
                <div className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center shrink-0">
                  <span className="font-bold text-sm">1</span>
                </div>
                <div>
                  <h4 className="font-semibold text-white/90">Receive Batch</h4>
                  <p className="text-sm text-white/70 mt-1">Verify physical quantity and accept custody from producer.</p>
                </div>
              </div>
              <div className="flex gap-3">
                <div className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center shrink-0">
                  <span className="font-bold text-sm">2</span>
                </div>
                <div>
                  <h4 className="font-semibold text-white/90">Dispatch Batch</h4>
                  <p className="text-sm text-white/70 mt-1">Record tracking information when batch leaves your facility.</p>
                </div>
              </div>
              <div className="flex gap-3">
                <div className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center shrink-0">
                  <span className="font-bold text-sm">3</span>
                </div>
                <div>
                  <h4 className="font-semibold text-white/90">Deliver Batch</h4>
                  <p className="text-sm text-white/70 mt-1">Confirm final hand-off quantity and location.</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
