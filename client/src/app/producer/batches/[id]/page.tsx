'use client'

import React, { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import { BatchService } from '@/services/api/batches'
import { useApi } from '@/hooks/useApi'
import { LoadingState } from '@/components/shared/LoadingState'
import { ErrorState } from '@/components/shared/ErrorState'
import { BatchStatusBadge } from '@/components/shared/BatchStatusBadge'
import { SupplyChainTimeline } from '@/features/batch/components/SupplyChainTimeline'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { ChevronLeft, Edit, Send, ShieldCheck, MapPin, Calendar, Scale, Sprout, Clock } from 'lucide-react'
import Link from 'next/link'
import { toast } from 'sonner'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'

export default function BatchDetailsPage() {
  const params = useParams()
  const batchId = params.id as string

  const { data: batch, isLoading, error, execute: fetchBatch } = useApi(BatchService.getBatchById)
  const { data: timelineData, execute: fetchTimeline } = useApi(BatchService.getBatchSupplyChain)
  
  const { isLoading: isSubmitting, execute: submitBatch } = useApi(BatchService.submitBatch)
  const { isLoading: isRequesting, execute: requestInspection } = useApi(BatchService.requestInspection)

  const [submitDialogOpen, setSubmitDialogOpen] = useState(false)
  const [inspectionDialogOpen, setInspectionDialogOpen] = useState(false)

  useEffect(() => {
    if (batchId) {
      fetchBatch(batchId)
      fetchTimeline(batchId)
    }
  }, [batchId, fetchBatch, fetchTimeline])

  if (isLoading && !batch) return <LoadingState message="Loading batch details..." />
  if (error && !batch) return <ErrorState message={error} onRetry={() => fetchBatch(batchId)} />
  if (!batch) return null

  const handleSubmit = async () => {
    const result = await submitBatch(batch.id)
    if (result) {
      toast.success('Batch submitted for verification successfully.')
      setSubmitDialogOpen(false)
      fetchBatch(batch.id)
      fetchTimeline(batch.id)
    } else {
      toast.error('Failed to submit batch. Make sure your producer profile is VERIFIED.')
      setSubmitDialogOpen(false)
    }
  }

  const handleRequestInspection = async () => {
    const result = await requestInspection(batch.id)
    if (result) {
      toast.success('Lot inspection requested successfully.')
      setInspectionDialogOpen(false)
      fetchBatch(batch.id)
      fetchTimeline(batch.id)
    } else {
      toast.error('Failed to request lot inspection. The batch might not be in the correct state.')
      setInspectionDialogOpen(false)
    }
  }

  const canEdit = batch.status === 'DRAFT'
  const canSubmit = batch.status === 'DRAFT'
  const canRequestInspection = batch.status === 'PENDING_VERIFICATION'

  const glassCard = "bg-white/80 backdrop-blur-xl border border-white/60 shadow-[0_8px_40px_rgb(0,0,0,0.04)] rounded-[24px]"

  return (
    <div className="max-w-[1400px] mx-auto p-6 md:p-10 space-y-8 relative">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 border-b border-slate-200/50 pb-6">
        <div className="flex items-center gap-4">
          <Button variant="outline" size="icon" asChild className="rounded-xl border-slate-200 hover:bg-slate-50 w-12 h-12 shadow-sm shrink-0">
            <Link href="/producer/batches">
              <ChevronLeft className="h-5 w-5 text-slate-600" />
            </Link>
          </Button>
          <div>
            <div className="flex items-center gap-3 mb-1">
              <h1 className="text-3xl md:text-4xl font-bold tracking-tight text-[#1e293b] font-serif">{batch.batchNumber}</h1>
              <BatchStatusBadge status={batch.status} />
            </div>
            <p className="text-[16px] text-slate-500 font-medium">Herb: <span className="text-[#184E48] font-bold">{batch.herb?.commonName}</span></p>
          </div>
        </div>
        
        {/* Action Bar */}
        <div className="flex flex-wrap items-center gap-3">
          {canEdit && (
            <Button variant="outline" asChild className="rounded-xl border-[#184E48]/20 text-[#184E48] hover:bg-slate-50 font-bold px-6 py-6 shadow-sm">
              <Link href={`/producer/batches/${batch.id}/edit`}>
                <Edit className="w-4 h-4 mr-2" />
                Edit Batch
              </Link>
            </Button>
          )}
          
          {canSubmit && (
            <Button onClick={() => setSubmitDialogOpen(true)} className="bg-[#184E48] hover:bg-[#184E48]/90 text-white rounded-xl px-6 py-6 font-bold shadow-[0_8px_30px_rgb(24,78,72,0.2)] hover:shadow-[0_8px_30px_rgb(24,78,72,0.3)] hover:-translate-y-0.5 transition-all duration-300">
              <Send className="w-4 h-4 mr-2" />
              Submit Batch
            </Button>
          )}

          {canRequestInspection && (
            <Button onClick={() => setInspectionDialogOpen(true)} className="bg-amber-500 hover:bg-amber-600 text-white rounded-xl px-6 py-6 font-bold shadow-[0_8px_30px_rgb(245,158,11,0.2)] hover:shadow-[0_8px_30px_rgb(245,158,11,0.3)] hover:-translate-y-0.5 transition-all duration-300">
              <ShieldCheck className="w-4 h-4 mr-2" />
              Request Inspection
            </Button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Production Details */}
        <div className="lg:col-span-2 space-y-8">
          <Card className={`${glassCard}`}>
            <CardHeader className="border-b border-slate-100/50 pb-6 mb-4">
              <CardTitle className="text-2xl font-serif text-[#1e293b]">Production Details</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                <div className="flex items-start gap-4 p-4 rounded-2xl bg-slate-50/50 border border-slate-100">
                  <div className="w-12 h-12 rounded-full bg-blue-50 flex items-center justify-center shrink-0">
                    <Scale className="w-6 h-6 text-blue-600" />
                  </div>
                  <div>
                    <span className="text-xs font-bold uppercase tracking-wider text-slate-400 block mb-1">Quantity</span>
                    <p className="text-xl font-bold text-[#1e293b]">{batch.quantity} <span className="text-sm font-medium text-slate-500">{batch.unit}</span></p>
                  </div>
                </div>

                <div className="flex items-start gap-4 p-4 rounded-2xl bg-slate-50/50 border border-slate-100">
                  <div className="w-12 h-12 rounded-full bg-emerald-50 flex items-center justify-center shrink-0">
                    <Calendar className="w-6 h-6 text-emerald-600" />
                  </div>
                  <div>
                    <span className="text-xs font-bold uppercase tracking-wider text-slate-400 block mb-1">Harvest Date</span>
                    <p className="text-lg font-bold text-[#1e293b]">{new Date(batch.harvestDate).toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' })}</p>
                  </div>
                </div>

                <div className="flex items-start gap-4 p-4 rounded-2xl bg-slate-50/50 border border-slate-100">
                  <div className="w-12 h-12 rounded-full bg-purple-50 flex items-center justify-center shrink-0">
                    <Sprout className="w-6 h-6 text-purple-600" />
                  </div>
                  <div>
                    <span className="text-xs font-bold uppercase tracking-wider text-slate-400 block mb-1">Cultivation Method</span>
                    <p className="text-lg font-bold text-[#1e293b] capitalize">{batch.cultivationMethod.replace(/_/g, ' ').toLowerCase()}</p>
                  </div>
                </div>

                <div className="flex items-start gap-4 p-4 rounded-2xl bg-slate-50/50 border border-slate-100">
                  <div className="w-12 h-12 rounded-full bg-slate-100 flex items-center justify-center shrink-0">
                    <Clock className="w-6 h-6 text-slate-500" />
                  </div>
                  <div>
                    <span className="text-xs font-bold uppercase tracking-wider text-slate-400 block mb-1">Created At</span>
                    <p className="text-lg font-bold text-[#1e293b]">{new Date(batch.createdAt).toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' })}</p>
                  </div>
                </div>
              </div>
              
              <div className="p-5 rounded-2xl bg-amber-50/50 border border-amber-100/50">
                <span className="text-xs font-bold uppercase tracking-wider text-amber-800/60 block mb-3">Farm Location</span>
                <div className="flex items-start gap-3">
                  <MapPin className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
                  <div>
                    <p className="text-[16px] font-bold text-[#1e293b]">{batch.farmLocation}</p>
                    {(batch.latitude && batch.longitude) && (
                      <p className="text-sm font-medium text-amber-700/70 mt-1">Coordinates: {batch.latitude}, {batch.longitude}</p>
                    )}
                  </div>
                </div>
              </div>

              {batch.harvestDetails && (
                <div className="p-5 rounded-2xl bg-slate-50/50 border border-slate-100">
                  <span className="text-xs font-bold uppercase tracking-wider text-slate-400 block mb-2">Harvest Notes</span>
                  <p className="text-[15px] text-slate-700 leading-relaxed">{batch.harvestDetails}</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Timeline */}
        <div className="lg:col-span-1">
          <Card className={`${glassCard}`}>
            <CardHeader className="border-b border-slate-100/50 pb-6 mb-4">
              <CardTitle className="text-2xl font-serif text-[#1e293b]">Supply Chain</CardTitle>
              <CardDescription className="text-slate-500 font-medium">History of events for this batch</CardDescription>
            </CardHeader>
            <CardContent>
              {timelineData ? (
                <SupplyChainTimeline events={timelineData.events} />
              ) : (
                <LoadingState message="Loading timeline..." />
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Submit Dialog */}
      <Dialog open={submitDialogOpen} onOpenChange={setSubmitDialogOpen}>
        <DialogContent className="rounded-[24px]">
          <DialogHeader>
            <DialogTitle className="text-2xl font-serif">Submit Batch</DialogTitle>
            <DialogDescription className="text-base">
              Are you sure you want to submit this batch for verification? You will not be able to edit the details once submitted.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="mt-4">
            <Button variant="outline" className="rounded-xl font-semibold" onClick={() => setSubmitDialogOpen(false)}>Cancel</Button>
            <Button onClick={handleSubmit} disabled={isSubmitting} className="rounded-xl bg-[#184E48] hover:bg-[#184E48]/90 font-bold">
              {isSubmitting ? 'Submitting...' : 'Yes, Submit Batch'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Inspection Dialog */}
      <Dialog open={inspectionDialogOpen} onOpenChange={setInspectionDialogOpen}>
        <DialogContent className="rounded-[24px]">
          <DialogHeader>
            <DialogTitle className="text-2xl font-serif">Request Lot Inspection</DialogTitle>
            <DialogDescription className="text-base">
              Request an on-ground inspection for this batch by a Verification Authority.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="mt-4">
            <Button variant="outline" className="rounded-xl font-semibold" onClick={() => setInspectionDialogOpen(false)}>Cancel</Button>
            <Button onClick={handleRequestInspection} disabled={isRequesting} className="rounded-xl bg-amber-500 hover:bg-amber-600 font-bold">
              {isRequesting ? 'Requesting...' : 'Confirm Request'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
