'use client'

import React, { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { labApi } from '@/services/api/lab'
import { QualityTest } from '@/types/lab'
import { LoadingState } from '@/components/shared/LoadingState'
import { ErrorState } from '@/components/shared/ErrorState'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { 
  ArrowLeft, 
  TestTube2, 
  Plus, 
  CheckCircle2, 
  XCircle, 
  AlertCircle,
  FileText
} from 'lucide-react'
import Link from 'next/link'
import { toast } from 'sonner'
import { useForm, Controller } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'

const addTestResultSchema = z.object({
  parameter: z.string().min(1, 'Parameter is required'),
  value: z.number().optional().or(z.string().transform(val => val === '' ? undefined : Number(val))),
  unit: z.string().optional(),
  referenceRange: z.string().optional(),
  resultStatus: z.enum(['PASS', 'FAIL', 'NOT_APPLICABLE']),
  remarks: z.string().optional(),
})

type TestResultFormValues = z.infer<typeof addTestResultSchema>

export default function LabTestResults() {
  const params = useParams()
  const router = useRouter()
  const [test, setTest] = useState<QualityTest | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isCompleting, setIsCompleting] = useState(false)

  const { register, handleSubmit, control, reset, formState: { errors } } = useForm<TestResultFormValues>({
    resolver: zodResolver(addTestResultSchema) as any,
    defaultValues: {
      parameter: '',
      value: undefined,
      unit: '',
      referenceRange: '',
      resultStatus: 'PASS',
      remarks: ''
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

  const onSubmitResult = async (data: TestResultFormValues) => {
    setIsSubmitting(true)
    try {
      await labApi.addTestResult(test!.id, data)
      toast.success('Test result added successfully')
      reset()
      await fetchTestDetails() // Refresh to show new result
    } catch (err: any) {
      toast.error(err.response?.data?.message || 'Failed to add test result')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleCompleteTest = async () => {
    setIsCompleting(true)
    try {
      await labApi.completeTest(test!.id)
      toast.success('Test completed successfully')
      await fetchTestDetails()
    } catch (err: any) {
      toast.error(err.response?.data?.message || 'Failed to complete test')
    } finally {
      setIsCompleting(false)
    }
  }

  if (isLoading && !test) return <LoadingState message="Loading test details..." />
  if (error && !test) return <ErrorState message={error} onRetry={fetchTestDetails} />
  if (!test) return <ErrorState message="Test not found" onRetry={fetchTestDetails} />

  const glassCard = "bg-white/70 backdrop-blur-xl border border-white/60 shadow-[0_8px_40px_rgb(0,0,0,0.04)] rounded-[24px]"
  const isUnderTest = test.status === 'UNDER_TESTING'
  const isCompleted = test.status === 'COMPLETED'
  const canComplete = isUnderTest && test.results && test.results.length > 0

  return (
    <div className="max-w-[1200px] mx-auto p-6 md:p-10 space-y-8 w-full">
      <Link href={`/lab/tests/${test.id}`} className="inline-flex items-center text-sm font-semibold text-slate-500 hover:text-[#184E48] transition-colors mb-2">
        <ArrowLeft className="w-4 h-4 mr-1" />
        Back to Test Details
      </Link>

      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
        <div>
          <h1 className="text-3xl md:text-4xl font-bold tracking-tight text-[#1e293b] font-serif mb-2 flex items-center gap-3">
            <TestTube2 className="w-8 h-8 text-[#184E48]" />
            Test Results
          </h1>
          <p className="text-[17px] text-slate-600 font-medium">Batch #{test.batch.batchNumber} • {test.batch.herb.commonName}</p>
        </div>

        {isCompleted && test.overallResult && (
          <div className={`px-4 py-2 rounded-xl text-lg font-bold tracking-wider border-2 ${test.overallResult === 'PASS' ? 'bg-emerald-50 border-emerald-200 text-emerald-700' : 'bg-red-50 border-red-200 text-red-700'}`}>
            OVERALL: {test.overallResult}
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Results List */}
        <div className="lg:col-span-2 space-y-6">
          <Card className={`${glassCard} overflow-hidden`}>
            <CardHeader className="border-b border-slate-100/50 pb-6 bg-white/50">
              <CardTitle className="text-xl font-serif text-[#1e293b]">Recorded Parameters</CardTitle>
              <CardDescription className="text-slate-500 font-medium">All parameter results entered for this test.</CardDescription>
            </CardHeader>
            <CardContent className="p-0">
              {(!test.results || test.results.length === 0) ? (
                <div className="p-12 text-center flex flex-col items-center">
                  <div className="w-16 h-16 rounded-full bg-slate-100 flex items-center justify-center mb-4">
                    <AlertCircle className="w-8 h-8 text-slate-400" />
                  </div>
                  <h3 className="text-lg font-bold text-[#1e293b] mb-2">No results recorded</h3>
                  <p className="text-slate-500 font-medium">Add parameters using the form to build the test report.</p>
                </div>
              ) : (
                <div className="divide-y divide-slate-100/50">
                  {test.results.map((result) => (
                    <div key={result.id} className="p-6 hover:bg-slate-50/50 transition-colors flex flex-col md:flex-row justify-between gap-4">
                      <div>
                        <h4 className="font-bold text-[#1e293b] text-lg mb-1">{result.parameter}</h4>
                        <div className="flex flex-wrap items-center gap-x-4 gap-y-2 text-sm text-slate-600">
                          {result.value !== null && (
                            <span className="font-medium bg-white px-2 py-1 rounded-md border border-slate-200">
                              Value: {result.value} {result.unit}
                            </span>
                          )}
                          {result.referenceRange && (
                            <span className="text-slate-500">
                              Ref: {result.referenceRange}
                            </span>
                          )}
                        </div>
                        {result.remarks && (
                          <p className="mt-3 text-sm text-slate-500 italic bg-white/60 p-2 rounded-lg border border-slate-100 inline-block">
                            "{result.remarks}"
                          </p>
                        )}
                      </div>
                      <div className="flex-shrink-0 flex items-center md:items-start">
                        <div className={`px-3 py-1.5 rounded-lg text-sm font-bold flex items-center gap-1.5 ${
                          result.resultStatus === 'PASS' ? 'bg-emerald-100 text-emerald-800' :
                          result.resultStatus === 'FAIL' ? 'bg-red-100 text-red-800' :
                          'bg-slate-100 text-slate-700'
                        }`}>
                          {result.resultStatus === 'PASS' && <CheckCircle2 className="w-4 h-4" />}
                          {result.resultStatus === 'FAIL' && <XCircle className="w-4 h-4" />}
                          {result.resultStatus}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Action Panel (Add Result / Complete) */}
        <div className="lg:col-span-1 space-y-6">
          {isUnderTest && (
            <Card className={`${glassCard} p-6`}>
              <h2 className="text-xl font-bold text-[#1e293b] font-serif mb-6">Add Parameter Result</h2>
              <form onSubmit={handleSubmit(onSubmitResult)} className="space-y-4">
                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-1.5">Parameter Name *</label>
                  <Input 
                    {...register('parameter')} 
                    placeholder="e.g. Moisture Content"
                    className="bg-white/50 border-slate-200 focus:border-[#184E48] rounded-xl"
                  />
                  {errors.parameter && <p className="text-red-500 text-xs mt-1">{errors.parameter.message}</p>}
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-1.5">Value</label>
                    <Input 
                      type="number" 
                      step="any"
                      {...register('value')} 
                      placeholder="e.g. 12.5"
                      className="bg-white/50 border-slate-200 focus:border-[#184E48] rounded-xl"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-1.5">Unit</label>
                    <Input 
                      {...register('unit')} 
                      placeholder="e.g. %"
                      className="bg-white/50 border-slate-200 focus:border-[#184E48] rounded-xl"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-1.5">Reference Range</label>
                  <Input 
                    {...register('referenceRange')} 
                    placeholder="e.g. < 15%"
                    className="bg-white/50 border-slate-200 focus:border-[#184E48] rounded-xl"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-1.5">Result Status *</label>
                  <Controller
                    control={control}
                    name="resultStatus"
                    render={({ field }) => (
                      <Select onValueChange={(val) => field.onChange(val || 'PASS')} defaultValue={field.value}>
                        <SelectTrigger className="bg-white/50 border-slate-200 focus:border-[#184E48] rounded-xl">
                          <SelectValue placeholder="Select status" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="PASS">PASS</SelectItem>
                          <SelectItem value="FAIL">FAIL</SelectItem>
                          <SelectItem value="NOT_APPLICABLE">NOT APPLICABLE</SelectItem>
                        </SelectContent>
                      </Select>
                    )}
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-1.5">Remarks</label>
                  <Textarea 
                    {...register('remarks')} 
                    placeholder="Optional notes"
                    className="bg-white/50 border-slate-200 focus:border-[#184E48] rounded-xl min-h-[80px]"
                  />
                </div>

                <Button 
                  type="submit" 
                  disabled={isSubmitting}
                  className="w-full bg-[#1e293b] hover:bg-[#1e293b]/90 text-white font-bold rounded-xl py-6"
                >
                  <Plus className="w-5 h-5 mr-2" />
                  {isSubmitting ? 'Adding...' : 'Add Result'}
                </Button>
              </form>
            </Card>
          )}

          {isUnderTest && (
            <Card className={`${glassCard} p-6 border-emerald-100 bg-emerald-50/30`}>
              <h2 className="text-xl font-bold text-[#1e293b] font-serif mb-2">Complete Testing</h2>
              <p className="text-sm text-slate-600 font-medium mb-6">
                Finish testing and lock results. The overall batch result will be calculated automatically based on parameter results.
              </p>
              
              <Button 
                onClick={handleCompleteTest}
                disabled={!canComplete || isCompleting}
                className="w-full bg-[#184E48] hover:bg-[#184E48]/90 text-white font-bold rounded-xl py-6 shadow-md"
              >
                <CheckCircle2 className="w-5 h-5 mr-2" />
                {isCompleting ? 'Completing...' : 'Complete Test Workflow'}
              </Button>
              
              {!canComplete && (
                <p className="text-xs text-center text-orange-600 font-medium mt-3">
                  At least one result parameter must be added to complete testing.
                </p>
              )}
            </Card>
          )}

          {isCompleted && (
            <Card className={`${glassCard} p-6 border-[#184E48]/10 bg-[#184E48]/5`}>
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-full bg-white flex items-center justify-center shadow-sm">
                  <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                </div>
                <div>
                  <h2 className="text-lg font-bold text-[#1e293b]">Test Completed</h2>
                  <p className="text-xs text-slate-500 font-medium">Results are locked.</p>
                </div>
              </div>
              
              <Link href={`/lab/tests/${test.id}/report`} className="block w-full mt-6">
                <Button className="w-full bg-[#184E48] hover:bg-[#184E48]/90 text-white font-bold rounded-xl py-6 shadow-md">
                  <FileText className="w-5 h-5 mr-2" />
                  Manage Lab Report
                </Button>
              </Link>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}
