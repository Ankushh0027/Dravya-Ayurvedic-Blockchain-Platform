'use client'

import React, { useEffect, useState } from 'react'
import { labApi } from '@/services/api/lab'
import { LabDashboardStats } from '@/types/lab'
import { LoadingState } from '@/components/shared/LoadingState'
import { ErrorState } from '@/components/shared/ErrorState'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { FlaskConical, TestTube2, CheckCircle2, XCircle, ClipboardCheck, ArrowRight, FileText } from 'lucide-react'
import { useAuthStore } from '@/store/authStore'
import Link from 'next/link'

export default function LabDashboard() {
  const user = useAuthStore(state => state.user)
  const [stats, setStats] = useState<LabDashboardStats | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchDashboard()
  }, [])

  const fetchDashboard = async () => {
    setIsLoading(true)
    setError(null)
    try {
      const data = await labApi.getDashboard()
      setStats(data)
    } catch (err: any) {
      console.error('Error fetching dashboard:', err)
      setError(err.response?.data?.message || 'Failed to load dashboard data')
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading && !stats) {
    return <LoadingState message="Loading lab dashboard..." />
  }

  if (error && !stats) {
    return <ErrorState message={error || 'Dashboard data unavailable'} onRetry={fetchDashboard} />
  }

  const glassCard = "bg-white/70 backdrop-blur-xl !border !border-black shadow-[0_8px_40px_rgb(0,0,0,0.04)] rounded-[24px] hover:shadow-[0_12px_50px_rgb(0,0,0,0.08)] transition-all duration-500 overflow-hidden relative"

  return (
    <div className="max-w-[1400px] mx-auto p-6 md:p-10 space-y-10">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
        <div>
          <h1 className="text-4xl md:text-5xl font-bold tracking-tight text-[#1e293b] font-serif mb-2">
            Welcome, <span className="text-[#184E48]">{user?.name}</span>
          </h1>
          <p className="text-[17px] text-slate-600 font-medium">Overview of your laboratory testing assignments.</p>
        </div>
        <div className="flex flex-wrap gap-4">
          <Link href="/lab/tests">
            <Button variant="outline" className="!border !border-black bg-white hover:bg-slate-50 text-[#184E48] rounded-xl px-6 py-6 text-[15px] font-bold shadow-sm transition-all duration-300">
              <FlaskConical className="w-4 h-4 mr-2" />
              Test Queue
            </Button>
          </Link>
          <Link href="/lab/tests?status=COMPLETED">
            <Button className="bg-[#184E48] hover:bg-[#184E48]/90 text-white rounded-xl px-6 py-6 text-[15px] font-semibold shadow-[0_8px_30px_rgb(24,78,72,0.2)] hover:shadow-[0_8px_30px_rgb(24,78,72,0.3)] hover:-translate-y-0.5 transition-all duration-300">
              <FileText className="w-5 h-5 mr-2" />
              Upload Reports
            </Button>
          </Link>
        </div>
      </div>

      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card className={`${glassCard} group`}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-bold text-slate-500 uppercase tracking-wider">Pending Assignment</CardTitle>
              <div className="w-12 h-12 rounded-2xl bg-orange-50 group-hover:bg-orange-100 flex items-center justify-center shadow-sm transition-colors duration-300">
                <ClipboardCheck className="h-6 w-6 text-orange-600" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-4xl font-bold text-[#1e293b] font-serif">{stats.dashboard.assignedTests}</div>
            </CardContent>
          </Card>

          <Card className={`${glassCard} group`}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-bold text-slate-500 uppercase tracking-wider">Sample Received</CardTitle>
              <div className="w-12 h-12 rounded-2xl bg-blue-50 group-hover:bg-blue-100 flex items-center justify-center shadow-sm transition-colors duration-300">
                <FlaskConical className="h-6 w-6 text-blue-600" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-4xl font-bold text-[#1e293b] font-serif">{stats.dashboard.samplesReceived}</div>
            </CardContent>
          </Card>

          <Card className={`${glassCard} group`}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-bold text-slate-500 uppercase tracking-wider">Under Testing</CardTitle>
              <div className="w-12 h-12 rounded-2xl bg-teal-50 group-hover:bg-teal-100 flex items-center justify-center shadow-sm transition-colors duration-300">
                <TestTube2 className="h-6 w-6 text-teal-600" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-4xl font-bold text-[#1e293b] font-serif">{stats.dashboard.underTesting}</div>
            </CardContent>
          </Card>

          <Card className={`${glassCard} group`}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-bold text-slate-500 uppercase tracking-wider">Completed Tests</CardTitle>
              <div className="w-12 h-12 rounded-2xl bg-[#184E48]/5 group-hover:bg-[#184E48]/10 flex items-center justify-center shadow-sm transition-colors duration-300">
                <CheckCircle2 className="h-6 w-6 text-[#184E48]" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="flex items-baseline gap-2">
                <div className="text-4xl font-bold text-[#1e293b] font-serif">{stats.dashboard.completedTests}</div>
                <div className="text-sm font-medium text-slate-500 flex items-center gap-1">
                  <span className="text-emerald-600">{stats.dashboard.passedTests} Pass</span>
                  <span>/</span>
                  <span className="text-red-500">{stats.dashboard.failedTests} Fail</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
        <Card className={`xl:col-span-2 ${glassCard}`}>
          <CardHeader className="border-b border-slate-100/50 pb-6 mb-4 flex flex-row items-center justify-between">
            <div>
              <CardTitle className="text-2xl font-serif text-[#1e293b]">Recent Assignments</CardTitle>
              <CardDescription className="text-slate-500 font-medium">Recently assigned tests that need your attention.</CardDescription>
            </div>
            <Link href="/lab/tests" className="text-[#184E48] hover:text-[#184E48]/80 text-sm font-semibold flex items-center gap-1 bg-[#184E48]/5 hover:bg-[#184E48]/10 px-4 py-2 rounded-lg transition-colors">
              View all <ArrowRight className="w-4 h-4 ml-1" />
            </Link>
          </CardHeader>
          <CardContent>
            {stats?.recentAssigned.length === 0 ? (
              <div className="py-12 text-center flex flex-col items-center justify-center bg-slate-50/50 rounded-[20px] border border-dashed border-slate-200">
                <div className="w-16 h-16 rounded-full bg-white flex items-center justify-center shadow-sm mb-4">
                  <ClipboardCheck className="w-8 h-8 text-slate-300" />
                </div>
                <h3 className="text-lg font-bold text-[#1e293b] mb-1">No recent assignments found</h3>
                <p className="text-slate-500 mb-6 max-w-sm">When the Verification Authority assigns a batch for lab testing, it will appear here.</p>
                <Link href="/lab/tests">
                  <Button className="bg-[#184E48] hover:bg-[#184E48]/90 text-white rounded-xl shadow-md">
                    View All Tests
                  </Button>
                </Link>
              </div>
            ) : (
              <div className="space-y-3">
                {stats?.recentAssigned.map((test) => (
                  <Link href={`/lab/tests/${test.id}`} key={test.id} className="block">
                    <div className="group flex items-center justify-between p-4 bg-white/50 hover:bg-white rounded-2xl border border-slate-100 shadow-sm hover:shadow-md transition-all duration-300 cursor-pointer">
                      <div className="flex flex-col">
                        <span className="text-lg font-bold text-[#1e293b] group-hover:text-[#184E48] transition-colors">
                          Batch #{test.batch.batchNumber}
                        </span>
                        <div className="text-sm font-medium text-slate-500 flex items-center gap-1.5 mt-1">
                          <div className="w-5 h-5 rounded-full bg-[#184E48]/10 flex items-center justify-center">
                            <FlaskConical className="w-3 h-3 text-[#184E48]" />
                          </div>
                          {test.batch.herb.commonName}
                        </div>
                      </div>
                      <div className="flex items-center gap-4">
                        <span className="px-3 py-1 bg-orange-100 text-orange-800 rounded-full text-xs font-bold tracking-wide">
                          {test.status.replace('_', ' ')}
                        </span>
                        <ArrowRight className="w-5 h-5 text-slate-300 group-hover:text-[#184E48] transition-colors group-hover:translate-x-1 duration-300" />
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <Card className={`xl:col-span-1 ${glassCard}`}>
          <CardHeader className="border-b border-slate-100/50 pb-6 mb-4">
            <CardTitle className="text-2xl font-serif text-[#1e293b]">Quick Actions</CardTitle>
            <CardDescription className="text-slate-500 font-medium">Common laboratory tasks</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <Link href="/lab/tests" className="block">
              <div className="flex items-center gap-4 p-4 rounded-2xl hover:bg-white !border !border-black hover:shadow-md transition-all duration-300 group cursor-pointer">
                <div className="w-12 h-12 rounded-2xl bg-blue-50 group-hover:bg-blue-100 flex items-center justify-center transition-colors">
                  <FlaskConical className="w-6 h-6 text-blue-600" />
                </div>
                <div>
                  <h4 className="font-bold text-[#1e293b] group-hover:text-[#184E48] transition-colors">Test Queue</h4>
                  <p className="text-sm text-slate-500">View all assigned tests</p>
                </div>
              </div>
            </Link>
            
            <Link href="/lab/tests?status=COMPLETED" className="block">
              <div className="flex items-center gap-4 p-4 rounded-2xl hover:bg-white border border-transparent hover:border-slate-100 hover:shadow-md transition-all duration-300 group cursor-pointer">
                <div className="w-12 h-12 rounded-2xl bg-emerald-50 group-hover:bg-emerald-100 flex items-center justify-center transition-colors">
                  <FileText className="w-6 h-6 text-emerald-600" />
                </div>
                <div>
                  <h4 className="font-bold text-[#1e293b] group-hover:text-[#184E48] transition-colors">Upload Reports</h4>
                  <p className="text-sm text-slate-500">Upload reports for completed tests</p>
                </div>
              </div>
            </Link>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
