'use client'

import React, { useEffect, useState } from 'react'
import { adminApi } from '@/services/api/admin'
import { useApi } from '@/hooks/useApi'
import { AdminVerification, VerificationAuthority } from '@/types/admin'
import { LoadingState } from '@/components/shared/LoadingState'
import { ErrorState } from '@/components/shared/ErrorState'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { toast } from 'sonner'
import { ShieldCheck, Calendar, MapPin, UserCheck, ArrowRight } from 'lucide-react'
import { format } from 'date-fns'

export default function AdminVerificationsPage() {
  const { data: verificationsData, isLoading, error, execute: fetchVerifications } = useApi(adminApi.getPendingVerifications)
  const { data: authoritiesData, execute: fetchAuthorities } = useApi(adminApi.getVerificationAuthorities)

  const [assigningId, setAssigningId] = useState<string | null>(null)
  const [selectedAuthorities, setSelectedAuthorities] = useState<Record<string, string>>({})

  useEffect(() => {
    fetchVerifications()
    fetchAuthorities()
  }, [fetchVerifications, fetchAuthorities])

  const verifications = verificationsData?.verifications || []
  const authorities = authoritiesData?.authorities || []

  const handleSelectAuthority = (verificationId: string, authorityId: string) => {
    setSelectedAuthorities(prev => ({
      ...prev,
      [verificationId]: authorityId
    }))
  }

  const handleAssign = async (verificationId: string) => {
    const authorityId = selectedAuthorities[verificationId]
    if (!authorityId) {
      toast.error('Please select an authority first.')
      return
    }

    try {
      setAssigningId(verificationId)
      await adminApi.assignVerificationAuthority(verificationId, { authorityId })
      toast.success('Authority assigned successfully.')
      fetchVerifications()
    } catch (err: any) {
      toast.error(err.response?.data?.message || 'Failed to assign authority.')
    } finally {
      setAssigningId(null)
    }
  }

  if (isLoading) return <LoadingState message="Loading verification requests..." />
  if (error) return <ErrorState message={error} onRetry={() => fetchVerifications()} />

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'PENDING': return 'bg-amber-100 text-amber-800 border-amber-200'
      case 'ASSIGNED': return 'bg-blue-100 text-blue-800 border-blue-200'
      case 'UNDER_REVIEW': return 'bg-purple-100 text-purple-800 border-purple-200'
      case 'COMPLETED': return 'bg-emerald-100 text-emerald-800 border-emerald-200'
      default: return 'bg-slate-100 text-slate-800 border-slate-200'
    }
  }

  return (
    <div className="max-w-[1400px] mx-auto p-6 md:p-10 space-y-8">
      {/* Hero Section */}
      <div className="relative rounded-[24px] overflow-hidden bg-gradient-to-br from-[#184E48] to-[#113834] p-8 md:p-10 shadow-xl border border-white/10">
        <div className="absolute top-0 right-0 w-[400px] h-[400px] bg-teal-500/10 rounded-full blur-[60px] pointer-events-none -translate-y-1/2 translate-x-1/3" />
        <div className="absolute inset-0 bg-[url('/noise.png')] opacity-20 mix-blend-overlay" />
        
        <div className="relative z-10 max-w-2xl">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-12 h-12 bg-white/10 rounded-xl flex items-center justify-center backdrop-blur-sm border border-white/20">
              <ShieldCheck className="w-6 h-6 text-emerald-300" />
            </div>
            <h1 className="text-3xl md:text-4xl font-bold tracking-tight text-white font-serif">Verification Queue</h1>
          </div>
          <p className="text-emerald-50/80 font-medium leading-relaxed">
            Review pending producer verifications and assign them to authorized government verifiers for field inspection and approval.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 pt-4">
        {verifications.length === 0 ? (
          <Card className="bg-white/80 backdrop-blur-xl border border-white/60 shadow-[0_8px_40px_rgb(0,0,0,0.04)] rounded-[24px] overflow-hidden">
            <div className="flex flex-col items-center justify-center p-16 text-center">
              <div className="w-20 h-20 bg-slate-50 rounded-full flex items-center justify-center mb-6">
                <ShieldCheck className="w-10 h-10 text-slate-400" />
              </div>
              <h3 className="text-xl font-bold text-slate-800 mb-2 font-serif">No Pending Requests</h3>
              <p className="text-slate-500 max-w-md">There are currently no producer verifications requiring assignment.</p>
            </div>
          </Card>
        ) : (
          verifications.map((verification) => (
            <Card key={verification.id} className="bg-white/80 backdrop-blur-xl border border-white/60 shadow-[0_8px_40px_rgb(0,0,0,0.04)] rounded-[24px] overflow-hidden hover:shadow-[0_8px_40px_rgb(0,0,0,0.08)] transition-all duration-300">
              <CardContent className="p-0">
                <div className="flex flex-col md:flex-row">
                  {/* Left Info Section */}
                  <div className="flex-1 p-6 md:p-8 md:border-r border-slate-100">
                    <div className="flex justify-between items-start mb-6">
                      <div>
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="text-2xl font-bold text-slate-800 font-serif">
                            {verification.producerProfile.farmName}
                          </h3>
                          <span className={`px-3 py-1 rounded-full text-xs font-bold border ${getStatusColor(verification.status)}`}>
                            {verification.status}
                          </span>
                        </div>
                        <div className="flex items-center gap-2 text-slate-500">
                          <UserCheck className="w-4 h-4" />
                          <span className="font-medium">{verification.producerProfile.user.name} ({verification.producerProfile.user.email})</span>
                        </div>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <div className="bg-slate-50 p-4 rounded-xl border border-slate-100">
                        <div className="flex items-center gap-2 text-slate-400 mb-1">
                          <MapPin className="w-4 h-4" />
                          <span className="text-xs font-bold uppercase tracking-wider">Location</span>
                        </div>
                        <p className="text-[15px] font-semibold text-slate-700">
                          {verification.producerProfile.district}, {verification.producerProfile.state}
                        </p>
                      </div>
                      <div className="bg-slate-50 p-4 rounded-xl border border-slate-100">
                        <div className="flex items-center gap-2 text-slate-400 mb-1">
                          <Calendar className="w-4 h-4" />
                          <span className="text-xs font-bold uppercase tracking-wider">Request Date</span>
                        </div>
                        <p className="text-[15px] font-semibold text-slate-700">
                          {format(new Date(verification.createdAt), 'MMM d, yyyy')}
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Right Action Section */}
                  <div className="w-full md:w-[350px] bg-slate-50/50 p-6 md:p-8 flex flex-col justify-center">
                    <h4 className="text-sm font-bold text-slate-800 mb-4 uppercase tracking-wider">Assignment</h4>
                    
                    {verification.authority ? (
                      <div className="mb-6 p-4 bg-white border border-blue-100 rounded-xl shadow-sm">
                        <p className="text-xs text-slate-500 font-medium mb-1">Currently Assigned To:</p>
                        <p className="font-bold text-blue-900">{verification.authority.name}</p>
                        <p className="text-sm text-slate-600">{verification.authority.email}</p>
                      </div>
                    ) : null}

                    <div className="space-y-4">
                      <select 
                        className="w-full flex h-12 items-center justify-between rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-[#184E48] focus:border-transparent font-medium shadow-sm appearance-none cursor-pointer"
                        value={selectedAuthorities[verification.id] || ''}
                        onChange={(e) => handleSelectAuthority(verification.id, e.target.value)}
                        disabled={assigningId === verification.id}
                      >
                        <option value="" disabled>Select Authority</option>
                        {authorities.map(auth => (
                          <option key={auth.id} value={auth.id}>
                            {auth.name} ({auth.organization || 'Independent'})
                          </option>
                        ))}
                      </select>

                      <Button 
                        onClick={() => handleAssign(verification.id)}
                        disabled={!selectedAuthorities[verification.id] || assigningId === verification.id}
                        className="w-full bg-[#184E48] hover:bg-[#184E48]/90 text-white rounded-xl shadow-md px-6 py-6 text-[15px] font-bold transition-all duration-300 flex justify-between items-center group disabled:opacity-100 disabled:cursor-not-allowed disabled:hover:bg-[#184E48] disabled:hover:translate-x-0"
                      >
                        {assigningId === verification.id ? 'Assigning...' : (verification.authority ? 'Reassign Authority' : 'Assign Authority')}
                        <ArrowRight className="w-5 h-5 transform group-hover:translate-x-1 transition-transform" />
                      </Button>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  )
}
