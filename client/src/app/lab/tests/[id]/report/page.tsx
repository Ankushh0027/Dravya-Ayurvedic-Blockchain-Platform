'use client'

import React, { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { labApi } from '@/services/api/lab'
import { QualityTest, LabReport } from '@/types/lab'
import { LoadingState } from '@/components/shared/LoadingState'
import { ErrorState } from '@/components/shared/ErrorState'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { 
  ArrowLeft, 
  FileText, 
  Lock, 
  AlertCircle,
  ExternalLink,
  CheckCircle2,
  AlertTriangle
} from 'lucide-react'
import Link from 'next/link'
import { toast } from 'sonner'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'

const generateLabReportSchema = z.object({
  reportUrl: z.string().url('Must be a valid URL'),
  reportFileName: z.string().min(1, 'File name is required'),
  reportFileType: z.string().min(1, 'File type is required'),
})

type GenerateReportFormValues = z.infer<typeof generateLabReportSchema>

export default function LabTestReport() {
  const params = useParams()
  const router = useRouter()
  const [test, setTest] = useState<QualityTest | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isFinalizing, setIsFinalizing] = useState(false)

  const { register, handleSubmit, formState: { errors } } = useForm<GenerateReportFormValues>({
    resolver: zodResolver(generateLabReportSchema),
    defaultValues: {
      reportUrl: '',
      reportFileName: '',
      reportFileType: 'application/pdf'
    }
  })

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

  const onSubmitGenerate = async (data: GenerateReportFormValues) => {
    setIsSubmitting(true)
    try {
      await labApi.generateReport(test!.id, data)
      toast.success('Draft report generated successfully')
      await fetchTestDetails()
    } catch (err: any) {
      toast.error(err.response?.data?.message || 'Failed to generate report')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleFinalize = async (reportId: string) => {
    setIsFinalizing(true)
    try {
      await labApi.finalizeReport(reportId)
      toast.success('Report finalized successfully. Results are now anchored on blockchain.')
      await fetchTestDetails()
    } catch (err: any) {
      toast.error(err.response?.data?.message || 'Failed to finalize report')
    } finally {
      setIsFinalizing(false)
    }
  }

  if (isLoading && !test) return <LoadingState message="Loading test details..." />
  if (error && !test) return <ErrorState message={error} onRetry={fetchTestDetails} />
  if (!test) return <ErrorState message="Test not found" onRetry={fetchTestDetails} />

  const glassCard = "bg-white/70 backdrop-blur-xl border border-white/60 shadow-[0_8px_40px_rgb(0,0,0,0.04)] rounded-[24px]"
  
  if (test.status !== 'COMPLETED') {
    return (
      <div className="max-w-[800px] mx-auto p-6 md:p-10 space-y-8 w-full text-center">
        <div className="w-20 h-20 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-6">
          <AlertTriangle className="w-10 h-10 text-orange-600" />
        </div>
        <h1 className="text-3xl font-bold tracking-tight text-[#1e293b] font-serif mb-2">
          Test Not Completed
        </h1>
        <p className="text-[17px] text-slate-600 font-medium max-w-lg mx-auto">
          You must complete the testing phase before generating a report. Please return to the test details and finalize the results first.
        </p>
        <div className="pt-6">
          <Link href={`/lab/tests/${test.id}`}>
            <Button className="bg-[#184E48] hover:bg-[#184E48]/90 text-white font-bold rounded-xl py-6 px-8 shadow-md">
              <ArrowLeft className="w-5 h-5 mr-2" />
              Return to Test
            </Button>
          </Link>
        </div>
      </div>
    )
  }

  const activeReport = test.reports && test.reports.length > 0 ? test.reports[0] : null
  const isFinalized = activeReport?.status === 'FINALIZED'

  return (
    <div className="max-w-[1000px] mx-auto p-6 md:p-10 space-y-8 w-full">
      <Link href={`/lab/tests/${test.id}`} className="inline-flex items-center text-sm font-semibold text-slate-500 hover:text-[#184E48] transition-colors mb-2">
        <ArrowLeft className="w-4 h-4 mr-1" />
        Back to Test Details
      </Link>

      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
        <div>
          <h1 className="text-3xl md:text-4xl font-bold tracking-tight text-[#1e293b] font-serif mb-2 flex items-center gap-3">
            <FileText className="w-8 h-8 text-[#184E48]" />
            Lab Report
          </h1>
          <p className="text-[17px] text-slate-600 font-medium">Batch #{test.batch.batchNumber} • {test.batch.herb.commonName}</p>
        </div>

        {isFinalized && (
          <div className="px-4 py-2 rounded-xl text-sm font-bold tracking-wider bg-slate-100 text-slate-700 flex items-center gap-2 border border-slate-200 shadow-sm">
            <Lock className="w-4 h-4" />
            FINALIZED & ANCHORED
          </div>
        )}
      </div>

      {!activeReport && (
        <Card className={`${glassCard} overflow-hidden max-w-[800px] mx-auto`}>
          <CardHeader className="border-b border-slate-100/50 pb-6 bg-white/50">
            <CardTitle className="text-xl font-serif text-[#1e293b]">Generate Lab Report</CardTitle>
            <CardDescription className="text-slate-500 font-medium">Link an external lab report to this completed quality test.</CardDescription>
          </CardHeader>
          <CardContent className="p-8 space-y-6">
            <div className="flex items-start gap-3 p-4 rounded-xl bg-orange-50/50 border border-orange-100 mb-6">
              <AlertCircle className="w-5 h-5 text-orange-600 flex-shrink-0 mt-0.5" />
              <div className="text-sm text-orange-800">
                <strong>Limitation Notice:</strong> Direct file uploading is not currently supported by the backend architecture. Please provide a direct URL to the externally hosted PDF report instead of uploading a local file.
              </div>
            </div>

            <form onSubmit={handleSubmit(onSubmitGenerate)} className="space-y-6">
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-1.5">Report URL (External Hosting) *</label>
                <Input 
                  {...register('reportUrl')} 
                  placeholder="https://example.com/reports/batch-123.pdf"
                  className="bg-white/50 border-slate-200 focus:border-[#184E48] rounded-xl h-12"
                />
                {errors.reportUrl && <p className="text-red-500 text-xs mt-1">{errors.reportUrl.message}</p>}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-1.5">File Name *</label>
                  <Input 
                    {...register('reportFileName')} 
                    placeholder="batch-123-report.pdf"
                    className="bg-white/50 border-slate-200 focus:border-[#184E48] rounded-xl h-12"
                  />
                  {errors.reportFileName && <p className="text-red-500 text-xs mt-1">{errors.reportFileName.message}</p>}
                </div>
                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-1.5">File Type *</label>
                  <Input 
                    {...register('reportFileType')} 
                    placeholder="application/pdf"
                    className="bg-white/50 border-slate-200 focus:border-[#184E48] rounded-xl h-12"
                  />
                  {errors.reportFileType && <p className="text-red-500 text-xs mt-1">{errors.reportFileType.message}</p>}
                </div>
              </div>

              <Button 
                type="submit" 
                disabled={isSubmitting}
                className="w-full bg-[#1e293b] hover:bg-[#1e293b]/90 text-white font-bold rounded-xl py-6 mt-4"
              >
                <FileText className="w-5 h-5 mr-2" />
                {isSubmitting ? 'Generating...' : 'Generate Draft Report'}
              </Button>
            </form>
          </CardContent>
        </Card>
      )}

      {activeReport && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2">
            <Card className={`${glassCard} overflow-hidden h-full`}>
              <CardHeader className="border-b border-slate-100/50 pb-6 bg-white/50">
                <CardTitle className="text-xl font-serif text-[#1e293b]">Report Details</CardTitle>
                <CardDescription className="text-slate-500 font-medium">Information about the generated lab report.</CardDescription>
              </CardHeader>
              <CardContent className="p-6 md:p-8 space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                  <div>
                    <p className="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-1">Report Number</p>
                    <p className="font-bold text-[#1e293b] font-mono text-lg">{activeReport.reportNumber}</p>
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-1">Status</p>
                    <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg text-sm font-bold bg-slate-100 text-slate-700 border border-slate-200">
                      {isFinalized ? <Lock className="w-4 h-4" /> : <FileText className="w-4 h-4" />}
                      {activeReport.status}
                    </div>
                  </div>
                  <div className="md:col-span-2">
                    <p className="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-2">Report Document</p>
                    <div className="flex items-center gap-4 p-4 rounded-xl bg-slate-50 border border-slate-200">
                      <div className="w-12 h-12 rounded-lg bg-red-100 flex items-center justify-center flex-shrink-0">
                        <FileText className="w-6 h-6 text-red-600" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-bold text-[#1e293b] truncate">{activeReport.reportFileName}</p>
                        <p className="text-sm text-slate-500 truncate">{activeReport.reportFileType}</p>
                      </div>
                      <a 
                        href={activeReport.reportUrl} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="flex-shrink-0"
                      >
                        <Button variant="outline" size="sm" className="bg-white border-slate-200 hover:bg-slate-50">
                          <ExternalLink className="w-4 h-4 mr-2" />
                          View
                        </Button>
                      </a>
                    </div>
                  </div>
                  {activeReport.finalizedAt && (
                    <div className="md:col-span-2">
                      <p className="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-1">Finalized At</p>
                      <p className="font-medium text-[#1e293b]">
                        {new Date(activeReport.finalizedAt).toLocaleDateString()} {new Date(activeReport.finalizedAt).toLocaleTimeString()}
                      </p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="lg:col-span-1">
            {!isFinalized ? (
              <Card className={`${glassCard} p-6 border-[#184E48] bg-white/90`}>
                <h2 className="text-xl font-bold text-[#1e293b] font-serif mb-2">Finalize Report</h2>
                <p className="text-sm text-slate-600 font-medium mb-6">
                  Review the report carefully. Finalizing will lock the report and automatically anchor the results to the blockchain. This action cannot be undone.
                </p>
                
                <Button 
                  onClick={() => handleFinalize(activeReport.id)}
                  disabled={isFinalizing}
                  className="w-full bg-[#184E48] hover:bg-[#184E48]/90 text-white font-bold rounded-xl py-6 shadow-md"
                >
                  <Lock className="w-5 h-5 mr-2" />
                  {isFinalizing ? 'Finalizing...' : 'Finalize & Anchor'}
                </Button>
              </Card>
            ) : (
              <Card className={`${glassCard} p-6 bg-slate-50 border-slate-200`}>
                <div className="text-center py-4">
                  <div className="w-16 h-16 rounded-full bg-emerald-100 flex items-center justify-center mx-auto mb-4">
                    <CheckCircle2 className="w-8 h-8 text-emerald-600" />
                  </div>
                  <h3 className="text-lg font-bold text-[#1e293b] mb-2">Report Locked</h3>
                  <p className="text-sm text-slate-500 font-medium">
                    This report has been finalized and anchored to the blockchain. No further modifications can be made.
                  </p>
                </div>
              </Card>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
