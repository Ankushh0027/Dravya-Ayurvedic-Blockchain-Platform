'use client'

import React, { useEffect, useState, Suspense } from 'react'
import { useSearchParams } from 'next/navigation'
import { distributorApi } from '@/services/api/distributor'
import { DistributorAssignment } from '@/types/distributor'
import { LoadingState } from '@/components/shared/LoadingState'
import { ErrorState } from '@/components/shared/ErrorState'
import { EmptyState } from '@/components/shared/EmptyState'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Search, Truck, ArrowRight, Filter, Clock, Package } from 'lucide-react'
import Link from 'next/link'
import { Card } from '@/components/ui/card'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'

function DistributorBatchesContent() {
  const searchParams = useSearchParams()
  const initialStatus = searchParams.get('status') || 'ALL'
  
  const [assignments, setAssignments] = useState<DistributorAssignment[]>([])
  const [filteredAssignments, setFilteredAssignments] = useState<DistributorAssignment[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState(initialStatus)

  useEffect(() => {
    fetchAssignments()
  }, [])

  useEffect(() => {
    filterAssignments()
  }, [searchTerm, statusFilter, assignments])

  const fetchAssignments = async () => {
    setIsLoading(true)
    setError(null)
    try {
      const data = await distributorApi.getAssignedBatches()
      setAssignments(data.assignments)
    } catch (err: any) {
      console.error('Error fetching assigned batches:', err)
      setError(err.response?.data?.message || 'Failed to load assigned batches')
    } finally {
      setIsLoading(false)
    }
  }

  const filterAssignments = () => {
    let filtered = [...assignments]

    if (statusFilter !== 'ALL') {
      filtered = filtered.filter(a => a.status === statusFilter)
    }

    if (searchTerm) {
      const term = searchTerm.toLowerCase()
      filtered = filtered.filter(a => 
        a.batch?.batchNumber.toLowerCase().includes(term) ||
        a.batch?.herb?.commonName.toLowerCase().includes(term) ||
        a.batch?.producerProfile?.farmName.toLowerCase().includes(term)
      )
    }

    setFilteredAssignments(filtered)
  }

  if (isLoading) return <LoadingState message="Loading assigned batches..." />
  if (error) return <ErrorState message={error} onRetry={fetchAssignments} />

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'ASSIGNED':
        return <span className="px-3 py-1 bg-orange-100 text-orange-700 rounded-full text-xs font-bold uppercase tracking-wider">Awaiting Receipt</span>
      case 'ACCEPTED':
        return <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-bold uppercase tracking-wider">Received / In Hub</span>
      case 'COMPLETED':
        return <span className="px-3 py-1 bg-emerald-100 text-emerald-700 rounded-full text-xs font-bold uppercase tracking-wider">Completed</span>
      case 'CANCELLED':
        return <span className="px-3 py-1 bg-red-100 text-red-700 rounded-full text-xs font-bold uppercase tracking-wider">Cancelled</span>
      default:
        return <span className="px-3 py-1 bg-slate-100 text-slate-700 rounded-full text-xs font-bold uppercase tracking-wider">{status}</span>
    }
  }

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
        <div>
          <h1 className="text-4xl md:text-5xl font-bold tracking-tight text-[#1e293b] font-serif mb-2">
            Assigned <span className="text-[#184E48]">Batches</span>
          </h1>
          <p className="text-[17px] text-slate-600 font-medium">Manage and track your assigned supply chain batches.</p>
        </div>
      </div>

      <Card className="bg-white/70 backdrop-blur-xl border-white/40 shadow-[0_8px_30px_rgb(0,0,0,0.04)] rounded-[24px] p-2">
        <div className="flex flex-col md:flex-row gap-4 p-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400" />
            <Input
              placeholder="Search by batch number, herb, or farm..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 h-12 bg-white border-slate-200 rounded-xl focus-visible:ring-[#184E48] text-base"
            />
          </div>
          <div className="w-full md:w-64">
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="h-12 bg-white border-slate-200 rounded-xl focus:ring-[#184E48]">
                <div className="flex items-center gap-2">
                  <Filter className="w-4 h-4 text-slate-500" />
                  <SelectValue placeholder="Filter by status" />
                </div>
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="ALL">All Assignments</SelectItem>
                <SelectItem value="ASSIGNED">Awaiting Receipt</SelectItem>
                <SelectItem value="ACCEPTED">Received / In Hub</SelectItem>
                <SelectItem value="COMPLETED">Completed</SelectItem>
                <SelectItem value="CANCELLED">Cancelled</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </Card>

      {filteredAssignments.length === 0 ? (
        <EmptyState
          icon={Truck}
          title="No assignments found"
          description={
            searchTerm || statusFilter !== 'ALL'
              ? 'No assignments match your current search filters.'
              : 'You have no batches assigned for distribution yet.'
          }
          actionLabel={searchTerm || statusFilter !== 'ALL' ? 'Clear Filters' : undefined}
          onAction={
            searchTerm || statusFilter !== 'ALL'
              ? () => {
                  setSearchTerm('')
                  setStatusFilter('ALL')
                }
              : undefined
          }
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredAssignments.map((assignment) => (
            <Card key={assignment.id} className="group bg-white hover:bg-slate-50/50 border-slate-200 shadow-sm hover:shadow-xl transition-all duration-300 rounded-[24px] overflow-hidden flex flex-col cursor-pointer" onClick={() => window.location.href = `/distributor/batches/${assignment.batchId}`}>
              <CardContent className="p-6 flex flex-col h-full">
                <div className="flex justify-between items-start mb-4">
                  <div className="px-3 py-1.5 bg-slate-100 text-slate-700 rounded-lg text-xs font-bold font-mono tracking-widest border border-slate-200/60">
                    {assignment.batch?.batchNumber}
                  </div>
                  {getStatusBadge(assignment.status)}
                </div>

                <div className="mb-6">
                  <h3 className="text-2xl font-bold text-[#1e293b] font-serif leading-tight">
                    {assignment.batch?.herb?.commonName || 'Unknown Herb'}
                  </h3>
                  <p className="text-slate-500 text-sm mt-1">{assignment.batch?.producerProfile?.farmName || 'Unknown Farm'}</p>
                </div>

                <div className="grid grid-cols-2 gap-4 mb-6">
                  <div className="bg-white p-3 rounded-xl border border-slate-100 shadow-sm">
                    <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-1">Declared Quantity</div>
                    <div className="font-semibold text-[#1e293b] flex items-center gap-1.5">
                      <Package className="w-4 h-4 text-emerald-600" />
                      {assignment.batch?.quantity} {assignment.batch?.unit}
                    </div>
                  </div>
                  <div className="bg-white p-3 rounded-xl border border-slate-100 shadow-sm">
                    <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-1">Assigned Date</div>
                    <div className="font-semibold text-[#1e293b] flex items-center gap-1.5">
                      <Clock className="w-4 h-4 text-blue-600" />
                      {new Date(assignment.assignedAt).toLocaleDateString()}
                    </div>
                  </div>
                </div>

                <div className="mt-auto pt-4 border-t border-slate-100">
                  <Button variant="ghost" className="w-full justify-between text-[#184E48] hover:text-[#184E48] hover:bg-[#184E48]/10 font-bold group-hover:px-6 transition-all duration-300">
                    Manage Logistics
                    <ArrowRight className="w-5 h-5 transition-transform group-hover:translate-x-1" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}

export default function DistributorBatches() {
  return (
    <Suspense fallback={<LoadingState message="Loading batches..." />}>
      <DistributorBatchesContent />
    </Suspense>
  )
}
