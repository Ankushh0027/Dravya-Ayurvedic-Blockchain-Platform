'use client'

import React, { useEffect, useState, Suspense } from 'react'
import { useSearchParams } from 'next/navigation'
import { labApi } from '@/services/api/lab'
import { QualityTest } from '@/types/lab'
import { LoadingState } from '@/components/shared/LoadingState'
import { ErrorState } from '@/components/shared/ErrorState'
import { EmptyState } from '@/components/shared/EmptyState'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Search, FlaskConical, ArrowRight, Filter, Clock } from 'lucide-react'
import Link from 'next/link'
import { Card } from '@/components/ui/card'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'

function LabTestsQueueContent() {
  const searchParams = useSearchParams()
  const initialStatus = searchParams.get('status') || 'ALL'
  
  const [tests, setTests] = useState<QualityTest[]>([])
  const [filteredTests, setFilteredTests] = useState<QualityTest[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState(initialStatus)

  useEffect(() => {
    fetchTests()
  }, [])

  useEffect(() => {
    filterTests()
  }, [searchTerm, statusFilter, tests])

  const fetchTests = async () => {
    setIsLoading(true)
    setError(null)
    try {
      const data = await labApi.getAssignedTests()
      setTests(data)
    } catch (err: any) {
      console.error('Error fetching lab tests:', err)
      setError(err.response?.data?.message || 'Failed to load tests')
    } finally {
      setIsLoading(false)
    }
  }

  const filterTests = () => {
    let result = [...tests]

    if (statusFilter !== 'ALL') {
      result = result.filter(test => test.status === statusFilter)
    }

    if (searchTerm) {
      const term = searchTerm.toLowerCase()
      result = result.filter(test => 
        test.batch.batchNumber.toLowerCase().includes(term) ||
        test.batch.herb.commonName.toLowerCase().includes(term) ||
        (test.sampleId && test.sampleId.toLowerCase().includes(term))
      )
    }

    setFilteredTests(result)
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'PENDING_ASSIGNMENT':
        return <span className="px-3 py-1 bg-slate-100 text-slate-800 rounded-full text-xs font-bold tracking-wide">PENDING</span>
      case 'ASSIGNED':
        return <span className="px-3 py-1 bg-orange-100 text-orange-800 rounded-full text-xs font-bold tracking-wide">ASSIGNED</span>
      case 'SAMPLE_RECEIVED':
        return <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-bold tracking-wide">SAMPLE RECEIVED</span>
      case 'UNDER_TESTING':
        return <span className="px-3 py-1 bg-teal-100 text-teal-800 rounded-full text-xs font-bold tracking-wide">UNDER TESTING</span>
      case 'COMPLETED':
        return <span className="px-3 py-1 bg-emerald-100 text-emerald-800 rounded-full text-xs font-bold tracking-wide">COMPLETED</span>
      default:
        return <span className="px-3 py-1 bg-slate-100 text-slate-800 rounded-full text-xs font-bold tracking-wide">{status}</span>
    }
  }

  if (isLoading && tests.length === 0) {
    return <LoadingState message="Loading assigned tests..." />
  }

  if (error && tests.length === 0) {
    return <ErrorState message={error} onRetry={fetchTests} />
  }

  const glassCard = "bg-white/70 backdrop-blur-xl border border-white/60 shadow-[0_8px_40px_rgb(0,0,0,0.04)] rounded-[24px]"

  return (
    <div className="max-w-[1200px] mx-auto p-6 md:p-10 space-y-8 w-full">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
        <div>
          <h1 className="text-4xl font-bold tracking-tight text-[#1e293b] font-serif mb-2">
            Test Queue
          </h1>
          <p className="text-[17px] text-slate-600 font-medium">Manage and track your assigned laboratory tests.</p>
        </div>
      </div>

      <Card className={`${glassCard} p-4`}>
        <div className="flex flex-col md:flex-row gap-4 items-center">
          <div className="relative flex-1 w-full">
            <Search className="absolute left-3.5 top-3 h-5 w-5 text-slate-400" />
            <Input 
              placeholder="Search by Batch #, Herb, or Sample ID..." 
              className="pl-11 h-12 bg-white/50 border-slate-200 rounded-xl w-full text-base focus-visible:ring-[#184E48]/20 focus-visible:border-[#184E48] transition-all"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <div className="flex items-center gap-3 w-full md:w-auto">
            <div className="bg-white/50 border border-slate-200 rounded-xl flex items-center h-12 px-3 text-slate-500 flex-shrink-0">
              <Filter className="w-5 h-5" />
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-full md:w-[200px] h-12 bg-white/50 border-slate-200 rounded-xl font-medium focus:ring-[#184E48]/20 focus:border-[#184E48]">
                <SelectValue placeholder="All Statuses" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="ALL">All Statuses</SelectItem>
                <SelectItem value="ASSIGNED">Assigned</SelectItem>
                <SelectItem value="SAMPLE_RECEIVED">Sample Received</SelectItem>
                <SelectItem value="UNDER_TESTING">Under Testing</SelectItem>
                <SelectItem value="COMPLETED">Completed</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </Card>

      <div className="space-y-4">
        {filteredTests.length === 0 ? (
          <EmptyState 
            icon={<FlaskConical className="w-12 h-12 text-slate-300" />}
            title="No tests found"
            description="There are no tests matching your current filters."
          />
        ) : (
          <div className="grid gap-4">
            {filteredTests.map((test) => (
              <Card key={test.id} className="bg-white/80 backdrop-blur-md border border-white/60 shadow-sm hover:shadow-md transition-all duration-300 rounded-[20px] overflow-hidden group">
                <div className="flex flex-col md:flex-row p-6 gap-6 md:items-center">
                  {/* Icon & Primary Info */}
                  <div className="flex items-start gap-4 flex-1">
                    <div className="w-12 h-12 rounded-2xl bg-teal-50 group-hover:bg-teal-100 flex items-center justify-center flex-shrink-0 transition-colors border border-teal-100/50 mt-1">
                      <FlaskConical className="w-6 h-6 text-teal-600" />
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-[#1e293b] mb-1 group-hover:text-[#184E48] transition-colors">
                        Batch #{test.batch.batchNumber}
                      </h3>
                      <div className="flex flex-wrap items-center gap-y-2 gap-x-4 text-sm text-slate-500 font-medium">
                        <span className="flex items-center gap-1.5">
                          <span className="w-1.5 h-1.5 rounded-full bg-slate-300" />
                          {test.batch.herb.commonName}
                        </span>
                        <span className="flex items-center gap-1.5">
                          <span className="w-1.5 h-1.5 rounded-full bg-slate-300" />
                          Qty: {test.batch.quantity} kg
                        </span>
                        {test.sampleId && (
                          <span className="flex items-center gap-1.5">
                            <span className="w-1.5 h-1.5 rounded-full bg-slate-300" />
                            Sample ID: {test.sampleId}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Status & Date */}
                  <div className="flex flex-row md:flex-col items-center md:items-end justify-between md:justify-center gap-3 md:w-[200px] flex-shrink-0 border-t md:border-t-0 md:border-l border-slate-100 pt-4 md:pt-0 md:pl-6">
                    {getStatusBadge(test.status)}
                    <div className="flex items-center gap-1.5 text-xs text-slate-400 font-medium">
                      <Clock className="w-3.5 h-3.5" />
                      {new Date(test.createdAt).toLocaleDateString()}
                    </div>
                  </div>

                  {/* Action */}
                  <div className="flex items-center justify-end w-full md:w-auto">
                    <Link href={`/lab/tests/${test.id}`} className="w-full md:w-auto">
                      <Button className="w-full md:w-auto bg-white hover:bg-slate-50 text-[#184E48] border border-slate-200 shadow-sm rounded-xl font-semibold transition-all group-hover:border-[#184E48]/30">
                        View Details
                        <ArrowRight className="w-4 h-4 ml-2 opacity-50 group-hover:opacity-100 group-hover:translate-x-1 transition-all" />
                      </Button>
                    </Link>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default function LabTestsQueue() {
  return (
    <Suspense fallback={<LoadingState message="Loading assigned tests..." />}>
      <LabTestsQueueContent />
    </Suspense>
  )
}
