'use client'

import React, { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { distributorApi } from '@/services/api/distributor'
import { DistributorAssignment, DistributorBatch, SupplyChainEvent } from '@/types/distributor'
import { LoadingState } from '@/components/shared/LoadingState'
import { ErrorState } from '@/components/shared/ErrorState'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { ArrowLeft, Package, MapPin, ClipboardList, CheckCircle2, Truck, Navigation, CalendarClock, Map, Send, FileText, Clock } from 'lucide-react'
import Link from 'next/link'
import { format } from 'date-fns'
import { useAuthStore } from '@/store/authStore'
import { toast } from 'sonner'
import { BatchStatusBadge } from '@/components/shared/BatchStatusBadge'

export default function DistributorBatchDetails() {
  const params = useParams()
  const router = useRouter()
  const { user } = useAuthStore()
  
  const [assignment, setAssignment] = useState<DistributorAssignment | null>(null)
  const [batch, setBatch] = useState<DistributorBatch | null>(null)
  const [events, setEvents] = useState<SupplyChainEvent[]>([])
  
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  // Form State
  const [formData, setFormData] = useState({
    quantity: '',
    unit: 'KG',
    location: '',
    referenceNumber: '',
    notes: ''
  })
  const [showConfirmation, setShowConfirmation] = useState(false)
  const [pendingAction, setPendingAction] = useState<'RECEIVE' | 'DISPATCH' | 'DELIVER' | null>(null)

  useEffect(() => {
    fetchBatchDetails()
  }, [params.id])

  const fetchBatchDetails = async () => {
    setIsLoading(true)
    setError(null)
    try {
      const data = await distributorApi.getAssignedBatches()
      const foundAssignment = data.assignments.find(a => a.batchId === params.id)
      
      if (!foundAssignment || !foundAssignment.batch) {
        throw new Error('Batch not found or not assigned to you')
      }
      
      setAssignment(foundAssignment)
      setBatch(foundAssignment.batch)
      
      // Sort events chronologically
      const sortedEvents = [...(foundAssignment.batch.supplyChainEvents || [])].sort(
        (a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
      )
      setEvents(sortedEvents)
      
      // Pre-fill quantity based on action context
      if (foundAssignment.status === 'ASSIGNED') {
        setFormData(prev => ({ ...prev, quantity: foundAssignment.batch!.quantity.toString(), unit: foundAssignment.batch!.unit }))
      } else if (foundAssignment.status === 'ACCEPTED' && foundAssignment.batch.status === 'QUALITY_APPROVED') {
        // Find received event to prefill dispatch
        const rxEvent = sortedEvents.find(e => e.action === 'BATCH_RECEIVED')
        if (rxEvent && rxEvent.quantity) {
          setFormData(prev => ({ ...prev, quantity: rxEvent.quantity!.toString(), unit: rxEvent.unit || 'KG' }))
        }
      } else if (foundAssignment.status === 'ACCEPTED' && foundAssignment.batch.status === 'IN_TRANSIT') {
        // Find dispatched event to prefill delivery
        const txEvent = sortedEvents.find(e => e.action === 'BATCH_DISPATCHED')
        if (txEvent && txEvent.quantity) {
          setFormData(prev => ({ ...prev, quantity: txEvent.quantity!.toString(), unit: txEvent.unit || 'KG' }))
        }
      }
      
    } catch (err: any) {
      console.error('Error fetching batch details:', err)
      setError(err.message || 'Failed to load batch details')
    } finally {
      setIsLoading(false)
    }
  }

  const handleAction = async () => {
    if (!batch || !pendingAction) return
    
    setIsSubmitting(true)
    try {
      const payload = {
        quantity: parseFloat(formData.quantity),
        unit: formData.unit,
        notes: formData.notes || undefined,
        referenceNumber: formData.referenceNumber || undefined,
        ...(pendingAction === 'RECEIVE' ? { location: formData.location } : { destination: formData.location })
      }

      if (pendingAction === 'RECEIVE') {
        await distributorApi.receiveBatch(batch.id, payload)
        toast.success('Batch received successfully')
      } else if (pendingAction === 'DISPATCH') {
        await distributorApi.dispatchBatch(batch.id, payload)
        toast.success('Batch dispatched successfully')
      } else if (pendingAction === 'DELIVER') {
        await distributorApi.deliverBatch(batch.id, payload)
        toast.success('Batch delivered successfully')
      }

      setShowConfirmation(false)
      setPendingAction(null)
      fetchBatchDetails() // Refresh data
    } catch (err: any) {
      toast.error(err.response?.data?.message || err.message || `Failed to ${pendingAction.toLowerCase()} batch`)
    } finally {
      setIsSubmitting(false)
    }
  }

  const prepareConfirmation = (action: 'RECEIVE' | 'DISPATCH' | 'DELIVER') => {
    if (!formData.quantity || isNaN(parseFloat(formData.quantity))) {
      toast.error('Please enter a valid quantity')
      return
    }
    setPendingAction(action)
    setShowConfirmation(true)
  }

  if (isLoading) return <LoadingState message="Loading batch logistics..." />
  if (error || !batch || !assignment) return <ErrorState message={error || 'Batch not found'} />

  // Determine current context and allowable actions
  const isAssigned = assignment.status === 'ASSIGNED'
  const isAccepted = assignment.status === 'ACCEPTED'
  const isCompleted = assignment.status === 'COMPLETED'
  
  const canReceive = isAssigned
  const canDispatch = isAccepted && batch.status === 'QUALITY_APPROVED'
  const canDeliver = isAccepted && batch.status === 'IN_TRANSIT'

  const receivedEvent = events.find(e => e.action === 'BATCH_RECEIVED')
  const dispatchedEvent = events.find(e => e.action === 'BATCH_DISPATCHED')
  const deliveredEvent = events.find(e => e.action === 'BATCH_DELIVERED')
  
  const declaredQuantity = batch.quantity
  const receivedQuantity = receivedEvent?.quantity
  const dispatchedQuantity = dispatchedEvent?.quantity
  const deliveredQuantity = deliveredEvent?.quantity

  const discrepancy = receivedQuantity ? (receivedQuantity - declaredQuantity) : null

  return (
    <div className="space-y-6 pb-20 animate-in fade-in duration-500">
      <div className="flex items-center gap-4 mb-6">
        <Link href="/distributor/batches">
          <Button variant="ghost" size="icon" className="h-10 w-10 rounded-full hover:bg-slate-200">
            <ArrowLeft className="h-5 w-5 text-slate-600" />
          </Button>
        </Link>
        <div>
          <div className="flex items-center gap-3 mb-1">
            <h1 className="text-3xl font-bold font-serif text-[#1e293b]">Logistics View</h1>
            <BatchStatusBadge status={batch.status} />
          </div>
          <p className="text-slate-500 font-medium">{batch.batchNumber}</p>
        </div>
      </div>

      {showConfirmation && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-sm p-4">
          <Card className="w-full max-w-md animate-in zoom-in-95 duration-200">
            <CardHeader>
              <CardTitle>Confirm {pendingAction}</CardTitle>
              <CardDescription>Please review the quantity details before confirming.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="p-4 bg-slate-50 rounded-xl space-y-3">
                <div className="flex justify-between text-sm">
                  <span className="text-slate-500">Batch:</span>
                  <span className="font-mono font-bold">{batch.batchNumber}</span>
                </div>
                {pendingAction === 'RECEIVE' && (
                  <>
                    <div className="flex justify-between text-sm">
                      <span className="text-slate-500">Declared Quantity:</span>
                      <span className="font-bold">{declaredQuantity} {batch.unit}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-slate-500">Received Quantity:</span>
                      <span className="font-bold text-[#184E48]">{formData.quantity} {formData.unit}</span>
                    </div>
                    {parseFloat(formData.quantity) !== declaredQuantity && (
                      <div className="flex justify-between text-sm pt-2 border-t border-slate-200">
                        <span className="text-slate-500">Discrepancy:</span>
                        <span className={`font-bold ${parseFloat(formData.quantity) < declaredQuantity ? 'text-red-500' : 'text-orange-500'}`}>
                          {parseFloat(formData.quantity) - declaredQuantity} {formData.unit}
                        </span>
                      </div>
                    )}
                  </>
                )}
                {pendingAction === 'DISPATCH' && (
                  <>
                    <div className="flex justify-between text-sm">
                      <span className="text-slate-500">Available (Received):</span>
                      <span className="font-bold">{receivedQuantity} {batch.unit}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-slate-500">Dispatch Quantity:</span>
                      <span className="font-bold text-blue-600">{formData.quantity} {formData.unit}</span>
                    </div>
                  </>
                )}
                {pendingAction === 'DELIVER' && (
                  <>
                    <div className="flex justify-between text-sm">
                      <span className="text-slate-500">Dispatched:</span>
                      <span className="font-bold">{dispatchedQuantity} {batch.unit}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-slate-500">Deliver Quantity:</span>
                      <span className="font-bold text-emerald-600">{formData.quantity} {formData.unit}</span>
                    </div>
                  </>
                )}
              </div>
              <div className="flex gap-3 pt-4">
                <Button variant="outline" className="flex-1" onClick={() => setShowConfirmation(false)}>Cancel</Button>
                <Button className="flex-1 bg-[#184E48] hover:bg-[#184E48]/90 text-white" onClick={handleAction} disabled={isSubmitting}>
                  {isSubmitting ? 'Processing...' : 'Confirm'}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Actions & Details */}
        <div className="lg:col-span-2 space-y-6">
          
          {/* Action Card based on state */}
          {!isCompleted && (
            <Card className="border-[#184E48]/20 shadow-md overflow-hidden relative">
              <div className="absolute top-0 left-0 w-2 h-full bg-[#184E48]" />
              <CardHeader className="bg-slate-50/50">
                <CardTitle className="flex items-center gap-2 text-xl font-serif text-[#184E48]">
                  {canReceive && <><Package className="w-5 h-5" /> Receive Batch</>}
                  {canDispatch && <><Send className="w-5 h-5" /> Dispatch Batch</>}
                  {canDeliver && <><CheckCircle2 className="w-5 h-5" /> Deliver Batch</>}
                </CardTitle>
                <CardDescription>
                  {canReceive && 'Record physical receipt of the batch and note any quantity discrepancies.'}
                  {canDispatch && 'Record dispatch details as the batch leaves your facility.'}
                  {canDeliver && 'Confirm final delivery to the retailer or destination.'}
                </CardDescription>
              </CardHeader>
              <CardContent className="p-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <div>
                      <label className="text-sm font-semibold text-slate-700 mb-1.5 block">Quantity ({formData.unit}) <span className="text-red-500">*</span></label>
                      <Input
                        type="number"
                        step="0.01"
                        value={formData.quantity}
                        onChange={(e) => setFormData(prev => ({ ...prev, quantity: e.target.value }))}
                        className="bg-white text-lg h-12"
                        placeholder="e.g. 240"
                      />
                      {canReceive && parseFloat(formData.quantity) !== declaredQuantity && !isNaN(parseFloat(formData.quantity)) && (
                        <p className={`text-xs mt-2 font-medium ${parseFloat(formData.quantity) < declaredQuantity ? 'text-red-600' : 'text-orange-600'}`}>
                          Notice: This differs from the declared {declaredQuantity} {batch.unit}. The discrepancy will be recorded.
                        </p>
                      )}
                    </div>
                    <div>
                      <label className="text-sm font-semibold text-slate-700 mb-1.5 block">
                        {canReceive ? 'Storage Location' : 'Destination'}
                      </label>
                      <Input
                        value={formData.location}
                        onChange={(e) => setFormData(prev => ({ ...prev, location: e.target.value }))}
                        className="bg-white"
                        placeholder={canReceive ? 'Warehouse A, Rack 3' : 'Retailer XYZ, Mumbai'}
                      />
                    </div>
                  </div>
                  <div className="space-y-4">
                    <div>
                      <label className="text-sm font-semibold text-slate-700 mb-1.5 block">Reference Number (Optional)</label>
                      <Input
                        value={formData.referenceNumber}
                        onChange={(e) => setFormData(prev => ({ ...prev, referenceNumber: e.target.value }))}
                        className="bg-white"
                        placeholder="Waybill, Receipt #..."
                      />
                    </div>
                    <div>
                      <label className="text-sm font-semibold text-slate-700 mb-1.5 block">Notes (Optional)</label>
                      <Textarea
                        value={formData.notes}
                        onChange={(e) => setFormData(prev => ({ ...prev, notes: e.target.value }))}
                        className="bg-white resize-none h-20"
                        placeholder="Any physical observations..."
                      />
                    </div>
                  </div>
                </div>
                <div className="mt-6 flex justify-end">
                  <Button 
                    className="bg-[#184E48] hover:bg-[#184E48]/90 text-white rounded-xl px-8 h-12 text-base font-semibold shadow-md"
                    onClick={() => {
                      if (canReceive) prepareConfirmation('RECEIVE')
                      else if (canDispatch) prepareConfirmation('DISPATCH')
                      else if (canDeliver) prepareConfirmation('DELIVER')
                    }}
                  >
                    {canReceive && 'Confirm Receipt'}
                    {canDispatch && 'Confirm Dispatch'}
                    {canDeliver && 'Confirm Delivery'}
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Batch Information Details */}
          <Card className="bg-white shadow-sm border-slate-200">
            <CardHeader className="border-b border-slate-100 pb-4">
              <CardTitle className="text-lg font-bold text-slate-800 flex items-center gap-2">
                <FileText className="w-5 h-5 text-slate-400" />
                Batch Details
              </CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <div className="grid grid-cols-1 sm:grid-cols-2 divide-y sm:divide-y-0 sm:divide-x divide-slate-100">
                <div className="p-6 space-y-4">
                  <div>
                    <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Herb Information</div>
                    <div className="font-bold text-slate-800 text-lg">{batch.herb?.commonName}</div>
                    <div className="text-sm text-slate-500 italic">{batch.herb?.botanicalName}</div>
                  </div>
                  <div>
                    <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Producer</div>
                    <div className="font-medium text-slate-800">{batch.producerProfile?.farmName}</div>
                    <div className="text-sm text-slate-500 flex items-center gap-1 mt-0.5">
                      <MapPin className="w-3.5 h-3.5" />
                      {batch.farmLocation}
                    </div>
                  </div>
                </div>
                <div className="p-6 space-y-4 bg-slate-50/50">
                  <div>
                    <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Harvest Data</div>
                    <div className="font-medium text-slate-800 flex items-center gap-2">
                      <CalendarClock className="w-4 h-4 text-slate-400" />
                      {format(new Date(batch.harvestDate), 'MMMM d, yyyy')}
                    </div>
                    <div className="text-sm text-slate-600 mt-1 capitalize">{batch.cultivationMethod.replace('_', ' ').toLowerCase()}</div>
                  </div>
                  <div>
                    <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Assignment</div>
                    <div className="font-medium text-slate-800 flex items-center gap-2">
                      <ClipboardList className="w-4 h-4 text-slate-400" />
                      {assignment.status}
                    </div>
                    <div className="text-sm text-slate-500 mt-1">
                      Assigned: {format(new Date(assignment.assignedAt), 'MMM d, yyyy HH:mm')}
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Right Column: Timeline & Quantities */}
        <div className="space-y-6">
          
          {/* Quantity Tracker Component */}
          <Card className="bg-[#184E48] text-white border-none shadow-lg overflow-hidden">
            <CardHeader className="bg-black/10 pb-4 border-b border-white/10">
              <CardTitle className="text-base font-bold text-white/90 uppercase tracking-widest text-center flex items-center justify-center gap-2">
                <Package className="w-4 h-4 text-teal-300" />
                Quantity Tracking
              </CardTitle>
            </CardHeader>
            <CardContent className="p-6 space-y-5">
              <div className="flex justify-between items-end border-b border-white/20 pb-3">
                <span className="text-white/70 font-medium text-sm">Original Declared</span>
                <span className="text-xl font-bold">{declaredQuantity} <span className="text-sm text-white/70">{batch.unit}</span></span>
              </div>
              
              <div className="flex justify-between items-end pb-1">
                <span className="text-white/90 font-medium">Received by you</span>
                <span className="text-xl font-bold">{receivedQuantity !== undefined ? receivedQuantity : '--'} <span className="text-sm text-white/70">{batch.unit}</span></span>
              </div>
              
              {discrepancy !== null && discrepancy !== 0 && (
                <div className="flex justify-between items-center py-2 px-3 bg-red-500/20 rounded-lg border border-red-500/30">
                  <span className="text-red-200 font-bold text-xs uppercase tracking-wider">Discrepancy</span>
                  <span className="text-red-300 font-bold text-sm">
                    {discrepancy > 0 ? '+' : ''}{discrepancy} {batch.unit}
                  </span>
                </div>
              )}

              <div className="flex justify-between items-end pt-2">
                <span className="text-white/90 font-medium">Dispatched</span>
                <span className="text-xl font-bold text-blue-200">{dispatchedQuantity !== undefined ? dispatchedQuantity : '--'} <span className="text-sm text-white/70">{batch.unit}</span></span>
              </div>

              <div className="flex justify-between items-end pt-2 border-t border-white/20 mt-2">
                <span className="text-white font-bold">Delivered</span>
                <span className="text-2xl font-bold text-emerald-300">{deliveredQuantity !== undefined ? deliveredQuantity : '--'} <span className="text-sm text-white/70">{batch.unit}</span></span>
              </div>
            </CardContent>
          </Card>

          {/* Supply Chain Timeline */}
          <Card className="bg-white border-slate-200 shadow-sm">
            <CardHeader className="border-b border-slate-100 pb-4">
              <CardTitle className="text-lg font-bold text-slate-800 flex items-center gap-2">
                <Navigation className="w-5 h-5 text-indigo-500" />
                Supply Chain Timeline
              </CardTitle>
            </CardHeader>
            <CardContent className="p-6">
              {events.length === 0 ? (
                <div className="text-center py-6 text-slate-500 text-sm">
                  No logistics events recorded yet.
                </div>
              ) : (
                <div className="relative border-l-2 border-slate-100 ml-3 space-y-6">
                  {events.map((event, index) => (
                    <div key={event.id} className="relative pl-6">
                      <div className="absolute -left-[9px] top-1 w-4 h-4 rounded-full bg-white border-2 border-indigo-500" />
                      <div className="text-sm font-bold text-[#1e293b]">
                        {event.action.replace('BATCH_', '').replace('_', ' ')}
                      </div>
                      <div className="text-xs text-slate-500 mt-1 flex flex-col gap-0.5">
                        <span className="flex items-center gap-1.5"><Clock className="w-3 h-3" /> {format(new Date(event.timestamp), 'MMM d, yyyy HH:mm')}</span>
                        {event.quantity && (
                          <span className="flex items-center gap-1.5 text-slate-700 font-medium">
                            <Package className="w-3 h-3 text-slate-400" /> {event.quantity} {event.unit}
                          </span>
                        )}
                        {event.location && (
                          <span className="flex items-center gap-1.5 text-slate-600">
                            <MapPin className="w-3 h-3 text-slate-400" /> {event.location}
                          </span>
                        )}
                        {event.referenceNumber && (
                          <span className="font-mono text-[10px] bg-slate-100 px-1.5 py-0.5 rounded mt-1 w-fit">Ref: {event.referenceNumber}</span>
                        )}
                      </div>
                    </div>
                  ))}
                  {/* Future Expected Event if not completed */}
                  {!isCompleted && (
                    <div className="relative pl-6 opacity-40">
                      <div className="absolute -left-[9px] top-1 w-4 h-4 rounded-full bg-slate-100 border-2 border-slate-300" />
                      <div className="text-sm font-bold text-slate-500 italic">
                        {canReceive ? 'Awaiting Receipt' : canDispatch ? 'Awaiting Dispatch' : 'Awaiting Delivery'}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
