'use client'

import React, { useEffect, useState } from 'react'
import { BatchService } from '@/services/api/batches'
import { useApi } from '@/hooks/useApi'
import { LoadingState } from '@/components/shared/LoadingState'
import { ErrorState } from '@/components/shared/ErrorState'
import { BatchStatusBadge } from '@/components/shared/BatchStatusBadge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Plus, Search, Eye, Package } from 'lucide-react'
import Link from 'next/link'

export default function ProducerBatchesPage() {
  const [page, setPage] = useState(1)
  const [searchTerm, setSearchTerm] = useState('')
  const limit = 10

  const { data, isLoading, error, execute: fetchBatches } = useApi(BatchService.getBatches)

  useEffect(() => {
    fetchBatches({ page, limit })
  }, [fetchBatches, page])

  const batches = data?.batches || []
  const pagination = data?.pagination

  const filteredBatches = batches.filter(b => 
    b.batchNumber.toLowerCase().includes(searchTerm.toLowerCase()) ||
    b.herb?.commonName.toLowerCase().includes(searchTerm.toLowerCase())
  )

  if (isLoading && !data) {
    return <LoadingState message="Loading your batches..." />
  }

  if (error && !data) {
    return <ErrorState message={error} onRetry={() => fetchBatches({ page, limit })} />
  }

  const glassCard = "bg-white/80 backdrop-blur-xl border border-white/60 shadow-[0_8px_40px_rgb(0,0,0,0.04)] rounded-[24px]"
  const inputStyles = "pl-10 h-12 border-slate-200 bg-slate-50/50 hover:bg-slate-50 rounded-xl focus-visible:ring-[#184E48]/20 focus-visible:border-[#184E48] transition-all text-sm shadow-sm"

  return (
    <div className="max-w-[1400px] mx-auto p-6 md:p-10 space-y-8 relative">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 pb-4">
        <div>
          <h1 className="text-4xl md:text-5xl font-bold tracking-tight text-[#1e293b] font-serif mb-2">My Batches</h1>
          <p className="text-[17px] text-slate-600 font-medium">Manage your herb production batches.</p>
        </div>
        <div className="flex flex-col sm:flex-row items-center gap-4 w-full md:w-auto">
          <div className="relative w-full md:w-72">
            <Search className="absolute left-3.5 top-3.5 h-5 w-5 text-slate-400" />
            <Input
              type="search"
              placeholder="Search batches..."
              className={inputStyles}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <Link href="/producer/batches/create" className="w-full sm:w-auto">
            <Button className="w-full bg-[#184E48] hover:bg-[#184E48]/90 text-white rounded-xl px-6 py-6 text-[15px] font-semibold shadow-[0_8px_30px_rgb(24,78,72,0.2)] hover:shadow-[0_8px_30px_rgb(24,78,72,0.3)] hover:-translate-y-0.5 transition-all duration-300">
              <Plus className="w-5 h-5 mr-2" />
              New Batch
            </Button>
          </Link>
        </div>
      </div>

      {!isLoading && filteredBatches.length === 0 ? (
        <div className="py-20 text-center flex flex-col items-center justify-center bg-white/50 backdrop-blur-sm rounded-[24px] border border-dashed border-slate-300 shadow-sm">
          <div className="w-20 h-20 rounded-full bg-white flex items-center justify-center shadow-md mb-6">
            <Package className="w-10 h-10 text-slate-300" />
          </div>
          <h3 className="text-2xl font-bold text-[#1e293b] font-serif mb-2">No batches found</h3>
          <p className="text-slate-500 mb-8 max-w-md text-[15px]">You haven't created any batches yet, or none match your search criteria. Create a new batch to start tracking.</p>
          <Link href="/producer/batches/create">
            <Button className="bg-[#184E48] hover:bg-[#184E48]/90 text-white rounded-xl shadow-md px-8 py-6 text-[15px]">
              Create your first batch
            </Button>
          </Link>
        </div>
      ) : (
        <div className={`${glassCard} overflow-hidden`}>
          <Table>
            <TableHeader className="bg-slate-50/80">
              <TableRow className="border-b-slate-100 hover:bg-transparent">
                <TableHead className="font-bold text-slate-600 h-14 pl-6">Batch Number</TableHead>
                <TableHead className="font-bold text-slate-600 h-14">Herb</TableHead>
                <TableHead className="font-bold text-slate-600 h-14">Quantity</TableHead>
                <TableHead className="font-bold text-slate-600 h-14">Harvest Date</TableHead>
                <TableHead className="font-bold text-slate-600 h-14">Status</TableHead>
                <TableHead className="font-bold text-slate-600 h-14 text-right pr-6">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredBatches.map((batch) => (
                <TableRow key={batch.id} className="border-b-slate-50 hover:bg-slate-50/50 transition-colors">
                  <TableCell className="font-semibold text-[#1e293b] pl-6 py-4">{batch.batchNumber}</TableCell>
                  <TableCell className="font-medium text-slate-700">{batch.herb?.commonName}</TableCell>
                  <TableCell className="text-slate-600">{batch.quantity} <span className="text-slate-400 text-sm">{batch.unit}</span></TableCell>
                  <TableCell className="text-slate-600">{new Date(batch.harvestDate).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })}</TableCell>
                  <TableCell>
                    <BatchStatusBadge status={batch.status} />
                  </TableCell>
                  <TableCell className="text-right pr-6">
                    <Button variant="ghost" size="icon" asChild className="hover:bg-[#184E48]/10 hover:text-[#184E48] rounded-xl transition-colors">
                      <Link href={`/producer/batches/${batch.id}`}>
                        <Eye className="w-5 h-5" />
                        <span className="sr-only">View</span>
                      </Link>
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}

      {/* Advanced Pagination controls */}
      {pagination && pagination.totalPages > 1 && (
        <div className="flex justify-between items-center bg-white/50 backdrop-blur-sm p-4 rounded-[20px] border border-slate-100 shadow-sm">
          <p className="text-sm font-medium text-slate-500 ml-2">
            Page {page} of {pagination.totalPages}
          </p>
          <div className="flex space-x-2">
            <Button 
              variant="outline" 
              className="rounded-xl border-slate-200 hover:bg-slate-50 font-semibold text-slate-600"
              disabled={page === 1}
              onClick={() => setPage(p => p - 1)}
            >
              Previous
            </Button>
            <Button 
              variant="outline" 
              className="rounded-xl border-slate-200 hover:bg-slate-50 font-semibold text-slate-600"
              disabled={page === pagination.totalPages}
              onClick={() => setPage(p => p + 1)}
            >
              Next
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}

