'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { ShieldCheck, UserCheck, SearchCheck, Activity, Database, Server, Network } from 'lucide-react'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { useAuthStore } from '@/store/authStore'

export default function AdminDashboard() {
  const user = useAuthStore(state => state.user)
  
  const glassCard = "bg-white/80 backdrop-blur-xl border border-white/60 shadow-[0_8px_40px_rgb(0,0,0,0.04)] rounded-[24px] overflow-hidden relative group hover:shadow-[0_8px_40px_rgb(0,0,0,0.08)] transition-all duration-500"

  return (
    <div className="max-w-[1400px] mx-auto p-4 md:p-6 space-y-6 h-[calc(100vh-80px)] flex flex-col justify-center">
      
      {/* Hero Section */}
      <div className="relative rounded-[24px] overflow-hidden bg-gradient-to-br from-[#184E48] to-[#113834] p-6 md:p-8 shadow-xl border border-white/10">
        {/* Decorative elements */}
        <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-emerald-500/10 rounded-full blur-[80px] pointer-events-none -translate-y-1/2 translate-x-1/3" />
        <div className="absolute bottom-0 left-0 w-[400px] h-[400px] bg-teal-500/10 rounded-full blur-[60px] pointer-events-none translate-y-1/3 -translate-x-1/4" />
        <div className="absolute inset-0 bg-[url('/noise.png')] opacity-20 mix-blend-overlay" />
        
        <div className="relative z-10 max-w-2xl">
          <h1 className="text-3xl md:text-4xl font-bold tracking-tight text-white font-serif mb-2">
            Welcome back, {user?.name?.split(' ')[0] || 'Admin'}
          </h1>
          <p className="text-base text-emerald-50/80 font-medium leading-relaxed max-w-xl">
            You have full administrative control over the Dravya Ayurvedic Supply Chain platform. Monitor verifications, manage users, and oversee system health.
          </p>
        </div>
      </div>

      <div>
        <h2 className="text-xl font-bold text-slate-800 font-serif mb-4 px-2">Core Modules</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {/* Verification Management Card */}
          <Link href="/admin/verifications" className="block h-full">
            <Card className={`${glassCard} h-full border-[#184E48]/20 bg-gradient-to-b from-white to-teal-50/30`}>
              <div className="absolute top-0 right-0 w-[200px] h-[200px] bg-teal-500/10 rounded-full blur-[40px] pointer-events-none group-hover:bg-teal-500/20 transition-colors duration-500" />
              <CardHeader className="pb-3">
                <div className="w-12 h-12 bg-[#184E48]/10 rounded-2xl flex items-center justify-center mb-4 ring-4 ring-white shadow-sm group-hover:scale-110 group-hover:bg-[#184E48] transition-all duration-300">
                  <ShieldCheck className="w-6 h-6 text-[#184E48] group-hover:text-white transition-colors duration-300" />
                </div>
                <CardTitle className="text-xl font-bold text-[#1e293b] font-serif">Verifications</CardTitle>
                <CardDescription className="text-sm mt-1 text-slate-500 font-medium leading-relaxed">
                  Review and assign pending producer verification requests to authorized government verifiers.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button variant="ghost" className="w-full justify-between mt-2 text-[#184E48] hover:text-white hover:bg-[#184E48] font-bold text-sm rounded-xl py-4 group/btn transition-all duration-300 shadow-sm border border-[#184E48]/10">
                  Manage Queue
                  <span className="transform translate-x-0 group-hover/btn:translate-x-1 transition-transform duration-200">→</span>
                </Button>
              </CardContent>
            </Card>
          </Link>
          
          {/* Users Management */}
          <Card className={`${glassCard} h-full bg-white/40`}>
            <div className="absolute inset-0 bg-slate-50/50 backdrop-blur-[2px] z-20 flex flex-col items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-[24px]">
              <span className="bg-slate-800 text-white px-4 py-2 rounded-full text-sm font-bold shadow-xl">Deploying in Phase 2</span>
            </div>
            <CardHeader className="pb-3">
              <div className="w-12 h-12 bg-slate-100 rounded-2xl flex items-center justify-center mb-4 ring-4 ring-white shadow-sm">
                <UserCheck className="w-6 h-6 text-slate-500" />
              </div>
              <CardTitle className="text-xl font-bold text-slate-700 font-serif">User Control</CardTitle>
              <CardDescription className="text-sm mt-1 text-slate-500 font-medium leading-relaxed">
                Manage platform users, update role-based access control, and suspend accounts.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button disabled variant="outline" className="w-full justify-between mt-2 rounded-xl py-4 border-slate-200 text-slate-400 text-sm">
                Module Locked
                <span>🔒</span>
              </Button>
            </CardContent>
          </Card>

          {/* System Settings */}
          <Card className={`${glassCard} h-full bg-white/40`}>
            <div className="absolute inset-0 bg-slate-50/50 backdrop-blur-[2px] z-20 flex flex-col items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-[24px]">
              <span className="bg-slate-800 text-white px-4 py-2 rounded-full text-sm font-bold shadow-xl">Deploying in Phase 2</span>
            </div>
            <CardHeader className="pb-3">
              <div className="w-12 h-12 bg-slate-100 rounded-2xl flex items-center justify-center mb-4 ring-4 ring-white shadow-sm">
                <SearchCheck className="w-6 h-6 text-slate-500" />
              </div>
              <CardTitle className="text-xl font-bold text-slate-700 font-serif">System Config</CardTitle>
              <CardDescription className="text-sm mt-1 text-slate-500 font-medium leading-relaxed">
                Configure platform-wide settings, notification templates, and blockchain smart contract parameters.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button disabled variant="outline" className="w-full justify-between mt-2 rounded-xl py-4 border-slate-200 text-slate-400 text-sm">
                Module Locked
                <span>🔒</span>
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* System Health Section */}
      <div className="pt-2">
        <h2 className="text-xl font-bold text-slate-800 font-serif mb-4 px-2">System Health</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Card className="bg-white/90 border-slate-100 shadow-sm rounded-2xl">
            <CardContent className="p-4 flex flex-col md:flex-row items-start md:items-center gap-3 md:gap-4">
              <div className="w-10 h-10 rounded-full bg-emerald-50 flex items-center justify-center shrink-0">
                <Server className="w-5 h-5 text-emerald-600" />
              </div>
              <div>
                <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Main API</p>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                  <p className="font-bold text-slate-700">Online</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-white/90 border-slate-100 shadow-sm rounded-2xl">
            <CardContent className="p-4 flex flex-col md:flex-row items-start md:items-center gap-3 md:gap-4">
              <div className="w-10 h-10 rounded-full bg-blue-50 flex items-center justify-center shrink-0">
                <Database className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Database</p>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-emerald-500" />
                  <p className="font-bold text-slate-700">Connected</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-white/90 border-slate-100 shadow-sm rounded-2xl">
            <CardContent className="p-4 flex flex-col md:flex-row items-start md:items-center gap-3 md:gap-4">
              <div className="w-10 h-10 rounded-full bg-purple-50 flex items-center justify-center shrink-0">
                <Network className="w-5 h-5 text-purple-600" />
              </div>
              <div>
                <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Hyperledger</p>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                  <p className="font-bold text-slate-700">Synced</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-white/90 border-slate-100 shadow-sm rounded-2xl">
            <CardContent className="p-4 flex flex-col md:flex-row items-start md:items-center gap-3 md:gap-4">
              <div className="w-10 h-10 rounded-full bg-amber-50 flex items-center justify-center shrink-0">
                <Activity className="w-5 h-5 text-amber-600" />
              </div>
              <div>
                <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Audit Log</p>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-amber-500" />
                  <p className="font-bold text-slate-700">Recording</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
