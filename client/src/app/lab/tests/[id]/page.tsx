'use client'

import React, { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { labApi } from '@/services/api/lab'
import { QualityTest } from '@/types/lab'
import { LoadingState } from '@/components/shared/LoadingState'
import { ErrorState } from '@/components/shared/ErrorState'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { 
  FlaskConical, 
  ArrowLeft, 
  ClipboardCheck, 
  TestTube2, 
  CheckCircle2,
  FileText,
  AlertCircle
} from 'lucide-react'
import Link from 'next/link'
import { toast } from 'sonner'
import { cn } from '@/lib/utils'

export default function LabTestDetails() {
  const params = useParams()
  const router = useRouter()
  const [test, setTest] = useState<QualityTest | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isActionLoading, setIsActionLoading] = useState(false)

  useEffect(() => {
    fetchTestDetails()
  }, [params.id])

  const fetchTestDetails = async () => {
    setIsLoading(true)
    setError(null)
    try {
      const data = await labApi.getTestDetails(params.id as string)
      setTest(data)
    } catch (err: any) {
      console.error('Error fetching test details:', err)
      setError(err.response?.data?.message || 'Failed to load test details')
    } finally {
      setIsLoading(false)
    }
  }

  const handleReceiveSample = async () => {
    setIsActionLoading(true)
    try {
      await labApi.receiveSample(test!.id)
      toast.success('Sample marked as received.')
      await fetchTestDetails()
    } catch (err: any) {
      toast.error(err.response?.data?.message || 'Failed to receive sample')
    } finally {
      setIsActionLoading(false)
    }
  }

  const handleStartTest = async () => {
    setIsActionLoading(true)
    try {
      await labApi.startTest(test!.id)
      toast.success('Testing started.')
      await fetchTestDetails()
    } catch (err: any) {
      toast.error(err.response?.data?.message || 'Failed to start testing')
    } finally {
      setIsActionLoading(false)
    }
  }

  if (isLoading && !test) return <LoadingState message="Loading test details..." />
  if (error && !test) return <ErrorState message={error} onRetry={fetchTestDetails} />
  if (!test) return <ErrorState message="Test not found" onRetry={fetchTestDetails} />

  const glassCard = "bg-white/70 backdrop-blur-xl border border-white/60 shadow-[0_8px_40px_rgb(0,0,0,0.04)] rounded-[24px]"

  // Workflow steps
  const steps = [
    { key: 'ASSIGNED', title: 'Assigned', icon: ClipboardCheck, date: test.assignedAt },
    { key: 'SAMPLE_RECEIVED', title: 'Sample Received', icon: FlaskConical, date: test.receivedAt },
    { key: 'UNDER_TESTING', title: 'Under Testing', icon: TestTube2, date: test.testingStartedAt },
    { key: 'COMPLETED', title: 'Completed', icon: CheckCircle2, date: test.testingCompletedAt }
  ]

  const currentStepIndex = steps.findIndex(s => s.key === test.status)
  // If COMPLETED, index is 3. If ASSIGNED, index is 0.

  return (
    <div className="max-w-[1200px] mx-auto p-6 md:p-10 space-y-8 w-full">
      <Link href="/lab/tests" className="inline-flex items-center text-sm font-semibold text-slate-500 hover:text-[#184E48] transition-colors mb-2">
        <ArrowLeft className="w-4 h-4 mr-1" />
        Back to Test Queue
      </Link>

      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
        <div>
          <h1 className="text-3xl md:text-4xl font-bold tracking-tight text-[#1e293b] font-serif mb-2">
            Quality Test
          </h1>
          <p className="text-[17px] text-slate-600 font-medium">Batch #{test.batch.batchNumber}</p>
        </div>

        {/* Status Badge */}
        <div className={cn(
          "px-4 py-2 rounded-xl text-sm font-bold tracking-wider",
          test.status === 'COMPLETED' ? "bg-emerald-100 text-emerald-800" :
          test.status === 'UNDER_TESTING' ? "bg-teal-100 text-teal-800" :
          test.status === 'SAMPLE_RECEIVED' ? "bg-blue-100 text-blue-800" :
          "bg-orange-100 text-orange-800"
        )}>
          {test.status.replace('_', ' ')}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        <div className="lg:col-span-2 space-y-8">
          {/* Main Info */}
          <Card className={`${glassCard} overflow-hidden`}>
            <div className="grid grid-cols-1 md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-slate-100">
              <div className="p-6 md:p-8 space-y-6">
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-10 h-10 rounded-xl bg-teal-50 flex items-center justify-center">
                    <FlaskConical className="w-5 h-5 text-teal-600" />
                  </div>
                  <h2 className="text-xl font-bold text-[#1e293b] font-serif">Batch Details</h2>
                </div>
                
                <div className="space-y-4">
                  <div>
                    <p className="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-1">Herb</p>
                    <p className="font-medium text-[#1e293b]">{test.batch.herb.commonName} <span className="text-slate-400 text-sm">({test.batch.herb.scientificName})</span></p>
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-1">Quantity</p>
                    <p className="font-medium text-[#1e293b]">{test.batch.quantity} kg</p>
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-1">Producer</p>
                    <p className="font-medium text-[#1e293b]">{test.batch.producerProfile?.farmName || 'Unknown'}</p>
                  </div>
                </div>
              </div>

              <div className="p-6 md:p-8 space-y-6 bg-slate-50/50">
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-10 h-10 rounded-xl bg-blue-50 flex items-center justify-center">
                    <TestTube2 className="w-5 h-5 text-blue-600" />
                  </div>
                  <h2 className="text-xl font-bold text-[#1e293b] font-serif">Sample Info</h2>
                </div>

                <div className="space-y-4">
                  <div>
                    <p className="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-1">Sample ID</p>
                    {test.sampleId ? (
                      <p className="font-bold text-[#1e293b] font-mono bg-white px-3 py-1.5 rounded-lg border border-slate-200 inline-block">
                        {test.sampleId}
                      </p>
                    ) : (
                      <p className="text-slate-400 italic">Not yet assigned</p>
                    )}
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-1">Overall Result</p>
                    {test.overallResult ? (
                      <p className={cn("font-bold text-lg", test.overallResult === 'PASS' ? "text-emerald-600" : "text-red-600")}>
                        {test.overallResult}
                      </p>
                    ) : (
                      <p className="text-slate-400 italic">Pending tests</p>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </Card>

          {/* Action Area */}
          <Card className={`${glassCard} p-6 md:p-8`}>
            <h2 className="text-xl font-bold text-[#1e293b] font-serif mb-6">Available Actions</h2>
            
            <div className="flex flex-col sm:flex-row gap-4">
              {test.status === 'ASSIGNED' && (
                <Button 
                  onClick={handleReceiveSample}
                  disabled={isActionLoading}
                  className="w-full sm:w-auto bg-[#184E48] hover:bg-[#184E48]/90 text-white rounded-xl py-6 px-8 font-bold shadow-md hover:shadow-lg transition-all"
                >
                  {isActionLoading ? 'Processing...' : 'Receive Sample'}
                </Button>
              )}
              
              {test.status === 'SAMPLE_RECEIVED' && (
                <Button 
                  onClick={handleStartTest}
                  disabled={isActionLoading}
                  className="w-full sm:w-auto bg-[#184E48] hover:bg-[#184E48]/90 text-white rounded-xl py-6 px-8 font-bold shadow-md hover:shadow-lg transition-all"
                >
                  {isActionLoading ? 'Starting...' : 'Start Testing'}
                </Button>
              )}

              {test.status === 'UNDER_TESTING' && (
                <Link href={`/lab/tests/${test.id}/results`} className="w-full sm:w-auto">
                  <Button 
                    className="w-full sm:w-auto bg-[#184E48] hover:bg-[#184E48]/90 text-white rounded-xl py-6 px-8 font-bold shadow-md hover:shadow-lg transition-all"
                  >
                    Enter Test Results
                  </Button>
                </Link>
              )}

              {test.status === 'COMPLETED' && (
                <>
                  <Link href={`/lab/tests/${test.id}/results`} className="w-full sm:w-auto">
                    <Button 
                      variant="outline"
                      className="w-full sm:w-auto border-slate-200 text-slate-700 hover:bg-slate-50 rounded-xl py-6 px-8 font-bold transition-all"
                    >
                      View Results
                    </Button>
                  </Link>
                  <Link href={`/lab/tests/${test.id}/report`} className="w-full sm:w-auto">
                    <Button 
                      className="w-full sm:w-auto bg-[#184E48] hover:bg-[#184E48]/90 text-white rounded-xl py-6 px-8 font-bold shadow-md hover:shadow-lg transition-all"
                    >
                      <FileText className="w-4 h-4 mr-2" />
                      Manage Report
                    </Button>
                  </Link>
                </>
              )}
            </div>

            {test.status === 'ASSIGNED' && (
              <div className="mt-6 flex items-start gap-3 p-4 rounded-xl bg-orange-50/50 border border-orange-100">
                <AlertCircle className="w-5 h-5 text-orange-600 flex-shrink-0 mt-0.5" />
                <p className="text-sm text-orange-800">You must physically receive and verify the sample before you can start testing.</p>
              </div>
            )}
          </Card>
        </div>

        {/* Timeline */}
        <div className="lg:col-span-1">
          <Card className={`${glassCard} p-6 md:p-8 h-full`}>
            <h2 className="text-xl font-bold text-[#1e293b] font-serif mb-8">Test Lifecycle</h2>
            
            <div className="space-y-8 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-slate-200 before:to-transparent">
              {steps.map((step, index) => {
                const isCompleted = currentStepIndex >= index;
                const isCurrent = currentStepIndex === index;
                
                return (
                  <div key={step.key} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
                    {/* Icon */}
                    <div className={cn(
                      "flex items-center justify-center w-10 h-10 rounded-full border-4 shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2",
                      isCompleted ? "bg-[#184E48] border-white text-white" : "bg-white border-slate-100 text-slate-400",
                      isCurrent && "ring-4 ring-[#184E48]/20"
                    )}>
                      <step.icon className="w-4 h-4" />
                    </div>
                    {/* Card */}
                    <div className={cn(
                      "w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] p-4 rounded-2xl border transition-colors",
                      isCompleted ? "bg-white border-slate-200 shadow-sm" : "bg-slate-50 border-slate-100/50 opacity-60"
                    )}>
                      <div className="flex items-center justify-between space-x-2 mb-1">
                        <div className={cn("font-bold text-sm", isCompleted ? "text-[#1e293b]" : "text-slate-500")}>
                          {step.title}
                        </div>
                      </div>
                      {step.date && (
                        <div className="text-xs font-medium text-slate-400">
                          {new Date(step.date).toLocaleDateString()} {new Date(step.date).toLocaleTimeString()}
                        </div>
                      )}
                    </div>
                  </div>
                )
              })}
            </div>
          </Card>
        </div>

      </div>
    </div>
  )
}
