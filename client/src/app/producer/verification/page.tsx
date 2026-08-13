'use client'

import React, { useEffect } from 'react'
import { ProducerService } from '@/services/api/producer'
import { useApi } from '@/hooks/useApi'
import { LoadingState } from '@/components/shared/LoadingState'
import { ErrorState } from '@/components/shared/ErrorState'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from '@/components/ui/card'
import { toast } from 'sonner'
import { CheckCircle2, AlertCircle, Clock, FileWarning, ShieldCheck } from 'lucide-react'
import Link from 'next/link'

export default function ProducerVerificationPage() {
  const { data: statusData, isLoading, error, execute: fetchStatus } = useApi(ProducerService.getVerificationStatus)
  const { data: profile, execute: fetchProfile } = useApi(ProducerService.getProfile)
  const { isLoading: isRequesting, execute: requestVerification } = useApi(ProducerService.requestVerification)

  useEffect(() => {
    fetchStatus()
    fetchProfile()
  }, [fetchStatus, fetchProfile])

  const handleRequestVerification = async () => {
    const result = await requestVerification()
    if (result) {
      toast.success('Verification requested successfully.')
      fetchStatus() // Refresh state
    } else {
      toast.error('Failed to request verification. Make sure your profile is complete.')
    }
  }

  const glassCard = "bg-white/80 backdrop-blur-xl border border-white/60 shadow-[0_8px_40px_rgb(0,0,0,0.04)] rounded-[24px] overflow-hidden relative"

  if (isLoading && !statusData) {
    return <LoadingState message="Loading verification status..." />
  }

  if (error && !statusData) {
    if (error.includes('not found')) {
      return (
        <div className="max-w-[1400px] mx-auto p-6 md:p-10">
          <Card className={`${glassCard} max-w-3xl mx-auto`}>
            <div className="absolute top-0 right-0 w-[300px] h-[300px] bg-amber-500/5 rounded-full blur-[60px] pointer-events-none" />
            <CardHeader className="text-center pb-2 pt-10">
              <div className="w-20 h-20 bg-amber-50 rounded-full flex items-center justify-center mx-auto mb-6">
                <FileWarning className="w-10 h-10 text-amber-500" />
              </div>
              <CardTitle className="text-3xl font-serif text-[#1e293b]">Profile Required</CardTitle>
              <CardDescription className="text-base text-slate-500 max-w-md mx-auto mt-2">
                You must complete your producer profile before you can request official verification.
              </CardDescription>
            </CardHeader>
            <CardFooter className="flex justify-center pb-10 pt-6">
              <Link href="/producer/profile">
                <Button className="bg-[#184E48] hover:bg-[#184E48]/90 text-white rounded-xl shadow-md px-8 py-6 text-[15px] font-semibold">
                  Go to Profile
                </Button>
              </Link>
            </CardFooter>
          </Card>
        </div>
      )
    }
    return <ErrorState message={error} onRetry={() => fetchStatus()} />
  }

  const status = statusData?.status || 'PENDING'

  const getStatusDisplay = () => {
    switch (status) {
      case 'VERIFIED':
        return {
          icon: <CheckCircle2 className="w-14 h-14 text-emerald-500" />,
          iconBg: 'bg-emerald-50',
          title: 'Verified Producer',
          description: 'Your farm and organization have been officially verified. You have full access to submit batches to the supply chain.',
          glow: 'bg-emerald-500/10'
        }
      case 'UNDER_REVIEW':
        return {
          icon: <Clock className="w-14 h-14 text-blue-500" />,
          iconBg: 'bg-blue-50',
          title: 'Verification Under Review',
          description: 'Your request is currently being reviewed by a verification authority. We will notify you once a decision is made.',
          glow: 'bg-blue-500/10'
        }
      case 'REJECTED':
        return {
          icon: <AlertCircle className="w-14 h-14 text-red-500" />,
          iconBg: 'bg-red-50',
          title: 'Verification Rejected',
          description: 'Your verification request was rejected. Please review your profile details, update any inaccurate information, and try again.',
          glow: 'bg-red-500/10'
        }
      case 'PENDING':
      default:
        return {
          icon: <ShieldCheck className="w-14 h-14 text-amber-500" />,
          iconBg: 'bg-amber-50',
          title: 'Verification Pending',
          description: 'You have not submitted a verification request yet. Submit a request to begin the verification process and unlock batch creation.',
          glow: 'bg-amber-500/10'
        }
    }
  }

  const display = getStatusDisplay()
  const canRequest = status === 'PENDING' || status === 'REJECTED'

  return (
    <div className="max-w-[1400px] mx-auto p-6 md:p-10 space-y-8 relative">
      <div className="border-b border-slate-200/50 pb-6">
        <h1 className="text-4xl md:text-5xl font-bold tracking-tight text-[#1e293b] font-serif mb-2">Verification</h1>
        <p className="text-[17px] text-slate-600 font-medium">Manage your official verification status required for batch submission.</p>
      </div>

      <div className="max-w-3xl mx-auto pt-4">
        <Card className={`${glassCard}`}>
          {/* Decorative Glow */}
          <div className={`absolute top-0 right-0 w-[400px] h-[400px] ${display.glow} rounded-full blur-[80px] pointer-events-none`} />
          
          <CardContent className="flex flex-col items-center justify-center p-12 md:p-16 text-center relative z-10">
            <div className={`w-28 h-28 ${display.iconBg} rounded-full flex items-center justify-center mb-8 shadow-sm`}>
              {display.icon}
            </div>
            
            <h2 className="text-3xl font-bold font-serif text-[#1e293b] mb-4">{display.title}</h2>
            <p className="text-[16px] text-slate-600 max-w-md mx-auto leading-relaxed">{display.description}</p>
            
            {canRequest && (
              <Button 
                onClick={handleRequestVerification}
                disabled={isRequesting}
                className="mt-10 bg-[#184E48] hover:bg-[#184E48]/90 text-white rounded-xl shadow-[0_8px_30px_rgb(24,78,72,0.2)] hover:shadow-[0_8px_30px_rgb(24,78,72,0.3)] hover:-translate-y-0.5 transition-all duration-300 px-8 py-6 text-[16px] font-bold min-w-[240px]"
              >
                {isRequesting ? 'Requesting...' : 'Request Verification'}
              </Button>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

