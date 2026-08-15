'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { ShieldCheck, UserCheck, SearchCheck } from 'lucide-react'
import Link from 'next/link'
import { Button } from '@/components/ui/button'

export default function AdminDashboard() {
  const glassCard = "bg-white/80 backdrop-blur-xl border border-white/60 shadow-[0_8px_40px_rgb(0,0,0,0.04)] rounded-[24px] overflow-hidden relative group hover:shadow-[0_8px_40px_rgb(0,0,0,0.08)] transition-all duration-300"

  return (
    <div className="max-w-[1400px] mx-auto p-6 md:p-10 space-y-8">
      <div className="border-b border-slate-200/50 pb-6 flex justify-between items-end">
        <div>
          <h1 className="text-4xl md:text-5xl font-bold tracking-tight text-[#1e293b] font-serif mb-2">Admin Dashboard</h1>
          <p className="text-[17px] text-slate-600 font-medium">Platform management and administration.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 pt-4">
        {/* Verification Management Card */}
        <Link href="/admin/verifications" className="block">
          <Card className={glassCard}>
            <div className="absolute top-0 right-0 w-[200px] h-[200px] bg-blue-500/5 rounded-full blur-[40px] pointer-events-none group-hover:bg-blue-500/10 transition-colors duration-500" />
            <CardHeader>
              <div className="w-14 h-14 bg-blue-50 rounded-2xl flex items-center justify-center mb-4 ring-4 ring-white shadow-sm group-hover:scale-110 transition-transform duration-300">
                <ShieldCheck className="w-7 h-7 text-blue-500" />
              </div>
              <CardTitle className="text-xl font-bold text-[#1e293b]">Verifications</CardTitle>
              <CardDescription className="text-[15px] mt-1 text-slate-500 font-medium">
                Assign producer verification requests to authorities.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button variant="ghost" className="w-full justify-between mt-2 text-blue-600 hover:text-blue-700 hover:bg-blue-50 font-semibold group/btn">
                Manage Queue
                <span className="transform translate-x-0 group-hover/btn:translate-x-1 transition-transform duration-200">→</span>
              </Button>
            </CardContent>
          </Card>
        </Link>
        
        {/* Users Management Placeholder */}
        <Card className={`${glassCard} opacity-60 grayscale`}>
          <CardHeader>
            <div className="w-14 h-14 bg-slate-100 rounded-2xl flex items-center justify-center mb-4 ring-4 ring-white shadow-sm">
              <UserCheck className="w-7 h-7 text-slate-500" />
            </div>
            <CardTitle className="text-xl font-bold text-[#1e293b]">Users (Next Phase)</CardTitle>
            <CardDescription className="text-[15px] mt-1 text-slate-500 font-medium">
              Manage platform users and roles.
            </CardDescription>
          </CardHeader>
        </Card>

        {/* System Settings Placeholder */}
        <Card className={`${glassCard} opacity-60 grayscale`}>
          <CardHeader>
            <div className="w-14 h-14 bg-slate-100 rounded-2xl flex items-center justify-center mb-4 ring-4 ring-white shadow-sm">
              <SearchCheck className="w-7 h-7 text-slate-500" />
            </div>
            <CardTitle className="text-xl font-bold text-[#1e293b]">System (Next Phase)</CardTitle>
            <CardDescription className="text-[15px] mt-1 text-slate-500 font-medium">
              Configure platform wide settings.
            </CardDescription>
          </CardHeader>
        </Card>
      </div>
    </div>
  )
}
