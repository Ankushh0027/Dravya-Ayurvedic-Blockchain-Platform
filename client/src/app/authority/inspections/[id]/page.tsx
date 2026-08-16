'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { authorityApi } from '@/services/api/authority'
import { BatchInspection } from '@/types/authority'
import { LoadingState } from '@/components/shared/LoadingState'
import { ErrorState } from '@/components/shared/ErrorState'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Checkbox } from '@/components/ui/checkbox'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { SearchCheck, MapPin, CheckCircle2, XCircle, ArrowLeft, Loader2, Play, Leaf, Scale } from 'lucide-react'
import { toast } from 'sonner'
import Link from 'next/link'
import { format } from 'date-fns'

export default function AuthorityInspectionDetailsPage() {
  const params = useParams()
  const router = useRouter()
  const inspectionId = params.id as string

  const [inspection, setInspection] = useState<BatchInspection | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isStarting, setIsStarting] = useState(false)

  // Form states matching backend schema exactly
  const [inspectedQuantity, setInspectedQuantity] = useState<number | ''>('')
  const [herbIdentityVerified, setHerbIdentityVerified] = useState(false)
  const [physicalQualityStatus, setPhysicalQualityStatus] = useState('')
  const [packagingStatus, setPackagingStatus] = useState('')
  const [documentsVerified, setDocumentsVerified] = useState(false)
  const [inspectionDate, setInspectionDate] = useState('')
  const [latitude, setLatitude] = useState<number | ''>('')
  const [longitude, setLongitude] = useState<number | ''>('')
  const [observations, setObservations] = useState('')
  
  // Rejection form
  const [isRejecting, setIsRejecting] = useState(false)
  const [rejectionReason, setRejectionReason] = useState('')

  useEffect(() => {
    fetchInspection()
  }, [inspectionId])

  const fetchInspection = async () => {
    setIsLoading(true)
    setError(null)
    try {
      const response = await authorityApi.getInspectionDetails(inspectionId)
      if (response.data?.success && response.data.data?.inspection) {
        const i = response.data.data.inspection
        setInspection(i)
        
        // Pre-fill existing data if finalized
        if (i.status === 'APPROVED' || i.status === 'REJECTED') {
          setInspectedQuantity(i.inspectedQuantity || i.declaredQuantity)
          setHerbIdentityVerified(i.herbIdentityVerified || false)
          setPhysicalQualityStatus(i.physicalQualityStatus || '')
          setPackagingStatus(i.packagingStatus || '')
          setDocumentsVerified(i.documentsVerified || false)
          setInspectionDate(i.inspectionDate ? format(new Date(i.inspectionDate), 'yyyy-MM-dd') : '')
          setLatitude(i.latitude || '')
          setLongitude(i.longitude || '')
          setObservations(i.observations || '')
          if (i.rejectionReason) setRejectionReason(i.rejectionReason)
        } else {
          // Defaults for new inspection
          setInspectionDate(format(new Date(), 'yyyy-MM-dd'))
          setInspectedQuantity(i.declaredQuantity) // Default to declared
        }
      } else {
        setError('Failed to load inspection details')
      }
    } catch (err: any) {
      console.error('Error fetching inspection:', err)
      setError(err.response?.data?.message || 'Failed to load inspection')
    } finally {
      setIsLoading(false)
    }
  }

  const handleStartInspection = async () => {
    setIsStarting(true)
    try {
      await authorityApi.startInspection(inspectionId)
      toast.success('Inspection started!')
      await fetchInspection()
    } catch (err: any) {
      console.error('Error starting inspection:', err)
      toast.error(err.response?.data?.message || 'Failed to start inspection')
    } finally {
      setIsStarting(false)
    }
  }

  const handleApprove = async () => {
    if (inspectedQuantity === '' || !physicalQualityStatus || !packagingStatus || !inspectionDate || latitude === '' || longitude === '') {
      toast.error('Please fill all required fields.')
      return
    }

    setIsSubmitting(true)
    try {
      await authorityApi.approveLotInspection(inspectionId, {
        inspectedQuantity: Number(inspectedQuantity),
        herbIdentityVerified,
        physicalQualityStatus,
        packagingStatus,
        documentsVerified,
        inspectionDate: new Date(inspectionDate).toISOString(),
        latitude: Number(latitude),
        longitude: Number(longitude),
        observations: observations || undefined,
      })
      toast.success('Lot inspection approved!')
      await fetchInspection()
    } catch (err: any) {
      console.error('Error approving inspection:', err)
      toast.error(err.response?.data?.message || 'Failed to approve inspection')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleReject = async () => {
    if (!rejectionReason.trim()) {
      toast.error('Rejection reason is required')
      return
    }

    setIsSubmitting(true)
    try {
      await authorityApi.rejectLotInspection(inspectionId, {
        rejectionReason,
      })
      toast.success('Lot inspection rejected.')
      setIsRejecting(false)
      await fetchInspection()
    } catch (err: any) {
      console.error('Error rejecting inspection:', err)
      toast.error(err.response?.data?.message || 'Failed to reject inspection')
    } finally {
      setIsSubmitting(false)
    }
  }

  if (isLoading) {
    return <LoadingState message="Loading inspection details..." />
  }

  if (error || !inspection) {
    return <ErrorState message={error || 'Inspection not found'} onRetry={fetchInspection} />
  }

  const glassCard = "bg-white/70 backdrop-blur-xl border border-white/60 shadow-[0_8px_40px_rgb(0,0,0,0.04)] rounded-[24px]"
  const isFinalized = inspection.status === 'APPROVED' || inspection.status === 'REJECTED'
  const isApproved = inspection.decision === 'APPROVED'
  
  // Calculate quantity difference if not finalized and actively inspecting
  const currentDiff = typeof inspectedQuantity === 'number' ? inspectedQuantity - inspection.declaredQuantity : 0

  return (
    <div className="max-w-[1400px] mx-auto p-6 md:p-10 space-y-10 animate-in fade-in duration-500">
      <Link href="/authority/inspections" className="inline-flex items-center text-sm font-medium text-slate-500 hover:text-[#184E48] transition-colors">
        <ArrowLeft className="w-4 h-4 mr-1" />
        Back to Inspections
      </Link>

      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <h1 className="text-4xl font-bold tracking-tight text-[#1e293b] font-serif flex items-center gap-3 mb-2">
            <SearchCheck className="w-10 h-10 text-[#184E48]" />
            Lot Inspection Details
          </h1>
          <p className="text-[17px] text-slate-600 font-medium">Conduct physical quality inspection and verify batch details.</p>
        </div>
        
        {isFinalized && (
          <div className={`px-4 py-2 rounded-xl border flex items-center gap-2 font-semibold ${isApproved ? 'bg-green-50 text-green-700 border-green-200' : 'bg-red-50 text-red-700 border-red-200'}`}>
            {isApproved ? <CheckCircle2 className="w-5 h-5" /> : <XCircle className="w-5 h-5" />}
            {isApproved ? 'APPROVED' : 'REJECTED'}
          </div>
        )}

        {inspection.status === 'PENDING' && (
          <Button
            onClick={handleStartInspection}
            disabled={isStarting}
            className="bg-blue-600 hover:bg-blue-700 text-white rounded-xl shadow-md font-semibold px-6"
          >
            {isStarting ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Play className="w-4 h-4 mr-2" />}
            Start Inspection
          </Button>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Column: Batch Info & Quantities */}
        <div className="lg:col-span-1 space-y-6">
          <Card className={`${glassCard} border-t-4 border-t-[#184E48] relative overflow-hidden`}>
            <div className="absolute top-0 right-0 w-32 h-32 bg-[#184E48]/5 rounded-bl-full pointer-events-none" />
            <CardHeader>
              <CardTitle className="text-2xl font-serif text-[#1e293b] flex items-center gap-2">
                <Leaf className="w-6 h-6 text-[#184E48]" />
                Batch Details
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4 text-sm">
              <div>
                <span className="block text-slate-500 mb-1 text-xs uppercase tracking-wider font-semibold">Batch Number</span>
                <span className="font-bold text-slate-900 font-mono bg-slate-100 px-2 py-1 rounded">{inspection.batch?.batchNumber}</span>
              </div>
              <div>
                <span className="block text-slate-500 mb-1 text-xs uppercase tracking-wider font-semibold">Herb</span>
                <span className="text-slate-700">{inspection.batch?.herb?.commonName} ({inspection.batch?.herb?.botanicalName})</span>
              </div>
              <div>
                <span className="block text-slate-500 mb-1 text-xs uppercase tracking-wider font-semibold">Cultivation Method</span>
                <span className="text-slate-700">{inspection.batch?.cultivationMethod}</span>
              </div>
              <div>
                <span className="block text-slate-500 mb-1 text-xs uppercase tracking-wider font-semibold">Producer & Farm</span>
                <span className="text-slate-700 font-medium">{inspection.batch?.producerProfile?.user?.name}</span>
                <br />
                <span className="text-slate-500">{inspection.batch?.producerProfile?.farmName}</span>
              </div>
              <div>
                <span className="block text-slate-500 mb-1 text-xs uppercase tracking-wider font-semibold">Harvest Date</span>
                <span className="text-slate-700">{inspection.batch?.harvestDate ? format(new Date(inspection.batch.harvestDate), 'MMM d, yyyy') : 'Unknown'}</span>
              </div>
            </CardContent>
          </Card>

          <Card className={`${glassCard} ${inspection.status === 'UNDER_INSPECTION' && currentDiff !== 0 ? 'border-orange-200 bg-orange-50/30' : ''}`}>
            <CardHeader>
              <CardTitle className="text-2xl font-serif text-[#1e293b] flex items-center gap-2">
                <Scale className="w-6 h-6 text-[#184E48]" />
                Quantity Verification
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4 text-sm">
              <div className="flex justify-between items-center p-3 rounded-lg bg-slate-50 border border-slate-100">
                <span className="text-slate-600 font-semibold">Declared</span>
                <span className="font-bold text-slate-900 text-lg">{inspection.declaredQuantity} {inspection.batch?.unit || 'kg'}</span>
              </div>
              
              <div className="space-y-2">
                <label className="text-sm font-semibold text-slate-700">Inspected Quantity <span className="text-red-500">*</span></label>
                <div className="flex items-center gap-2">
                  <Input 
                    type="number" 
                    step="any"
                    min={0}
                    value={inspectedQuantity} 
                    onChange={e => setInspectedQuantity(e.target.value === '' ? '' : Number(e.target.value))} 
                    disabled={isFinalized || inspection.status === 'PENDING'}
                    className={`bg-white font-bold text-lg ${currentDiff !== 0 ? 'text-orange-600' : 'text-slate-900'}`}
                  />
                  <span className="text-slate-500 font-semibold">{inspection.batch?.unit || 'kg'}</span>
                </div>
                {inspection.status === 'UNDER_INSPECTION' && currentDiff !== 0 && (
                  <p className="text-xs font-bold text-orange-600">
                    Difference: {currentDiff > 0 ? '+' : ''}{currentDiff} {inspection.batch?.unit || 'kg'}
                  </p>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Right Column: Inspection Checklist */}
        <div className="lg:col-span-2 space-y-6">
          <Card className={`${glassCard} relative overflow-hidden ${inspection.status === 'PENDING' ? 'opacity-60 pointer-events-none' : ''}`}>
            <div className="absolute top-0 right-0 w-64 h-64 bg-blue-500/5 rounded-full blur-[60px] pointer-events-none" />
            <CardHeader className="border-b border-slate-100/50 pb-6 flex flex-row items-center justify-between">
              <div>
                <CardTitle className="text-2xl font-serif text-[#1e293b]">Quality Inspection</CardTitle>
                <CardDescription className="text-slate-500 font-medium">Verify the physical quality and packaging of the lot.</CardDescription>
              </div>
              {inspection.status === 'PENDING' && (
                <div className="px-3 py-1 bg-slate-100 text-slate-500 text-xs font-bold uppercase rounded-full">
                  Start Inspection to Unlock
                </div>
              )}
            </CardHeader>
            <CardContent className="pt-6 space-y-8">
              
              <div className="space-y-4">
                <h3 className="text-sm font-bold text-slate-500 uppercase tracking-wider">Verifications</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="flex items-center space-x-3 p-3 rounded-xl border border-slate-100 bg-slate-50 hover:bg-slate-100/80 transition-colors">
                    <Checkbox 
                      id="herbIdentity" 
                      checked={herbIdentityVerified} 
                      onCheckedChange={(c) => setHerbIdentityVerified(c as boolean)} 
                      disabled={isFinalized}
                    />
                    <label htmlFor="herbIdentity" className="text-sm font-semibold text-slate-700 cursor-pointer flex-1">
                      Herb Identity Verified
                    </label>
                  </div>
                  <div className="flex items-center space-x-3 p-3 rounded-xl border border-slate-100 bg-slate-50 hover:bg-slate-100/80 transition-colors">
                    <Checkbox 
                      id="documentsVerified" 
                      checked={documentsVerified} 
                      onCheckedChange={(c) => setDocumentsVerified(c as boolean)} 
                      disabled={isFinalized}
                    />
                    <label htmlFor="documentsVerified" className="text-sm font-semibold text-slate-700 cursor-pointer flex-1">
                      Documents Verified
                    </label>
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <h3 className="text-sm font-bold text-slate-500 uppercase tracking-wider">Quality Assessments</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="text-sm font-semibold text-slate-700">Physical Quality <span className="text-red-500">*</span></label>
                    <Select value={physicalQualityStatus} onValueChange={(val: any) => setPhysicalQualityStatus(val)} disabled={isFinalized}>
                      <SelectTrigger className="bg-white">
                        <SelectValue placeholder="Select quality status" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="EXCELLENT">Excellent</SelectItem>
                        <SelectItem value="GOOD">Good / Standard</SelectItem>
                        <SelectItem value="FAIR">Fair / Passable</SelectItem>
                        <SelectItem value="POOR">Poor / Rejectable</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-semibold text-slate-700">Packaging Status <span className="text-red-500">*</span></label>
                    <Select value={packagingStatus} onValueChange={(val: any) => setPackagingStatus(val)} disabled={isFinalized}>
                      <SelectTrigger className="bg-white">
                        <SelectValue placeholder="Select packaging status" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="INTACT">Intact & Sealed</SelectItem>
                        <SelectItem value="ADEQUATE">Adequate</SelectItem>
                        <SelectItem value="DAMAGED">Damaged / Tampered</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <h3 className="text-sm font-bold text-slate-500 uppercase tracking-wider">Inspection Details</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <label className="text-sm font-semibold text-slate-700">Date <span className="text-red-500">*</span></label>
                    <Input 
                      type="date" 
                      value={inspectionDate} 
                      onChange={e => setInspectionDate(e.target.value)} 
                      disabled={isFinalized}
                      className="bg-white"
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-semibold text-slate-700">Latitude <span className="text-red-500">*</span></label>
                    <Input 
                      type="number" 
                      step="any"
                      min={-90}
                      max={90}
                      placeholder="e.g. 28.6139" 
                      value={latitude} 
                      onChange={e => setLatitude(e.target.value === '' ? '' : Number(e.target.value))} 
                      disabled={isFinalized}
                      className="bg-white"
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-semibold text-slate-700">Longitude <span className="text-red-500">*</span></label>
                    <Input 
                      type="number" 
                      step="any"
                      min={-180}
                      max={180}
                      placeholder="e.g. 77.2090" 
                      value={longitude} 
                      onChange={e => setLongitude(e.target.value === '' ? '' : Number(e.target.value))} 
                      disabled={isFinalized}
                      className="bg-white"
                    />
                  </div>
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-semibold text-slate-700">Observations (Optional)</label>
                <Textarea 
                  placeholder="Record any additional on-ground observations..."
                  value={observations}
                  onChange={e => setObservations(e.target.value)}
                  disabled={isFinalized}
                  className="min-h-[100px] bg-white"
                />
              </div>
              
              {isFinalized && !isApproved && inspection.rejectionReason && (
                <div className="p-4 rounded-xl bg-red-50 border border-red-100 text-red-800 space-y-1">
                  <span className="font-bold text-sm block">Rejection Reason</span>
                  <p className="text-sm">{inspection.rejectionReason}</p>
                </div>
              )}

              {inspection.status === 'UNDER_INSPECTION' && (
                <div className="flex flex-col sm:flex-row gap-3 pt-6 border-t border-slate-100">
                  {!isRejecting ? (
                    <>
                      <Button
                        onClick={handleApprove}
                        disabled={isSubmitting}
                        className="w-full sm:w-auto bg-[#184E48] hover:bg-[#184E48]/90 text-white rounded-xl shadow-md font-semibold px-8"
                      >
                        {isSubmitting ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <CheckCircle2 className="w-4 h-4 mr-2" />}
                        Approve Inspection
                      </Button>
                      <Button
                        onClick={() => setIsRejecting(true)}
                        disabled={isSubmitting}
                        variant="outline"
                        className="w-full sm:w-auto rounded-xl text-red-600 border-red-200 hover:bg-red-50 hover:border-red-300 font-semibold px-8"
                      >
                        Reject...
                      </Button>
                    </>
                  ) : (
                    <div className="w-full space-y-4 p-4 rounded-xl border border-red-200 bg-red-50/50">
                      <div className="space-y-2">
                        <label className="text-sm font-bold text-red-900">Provide Rejection Reason <span className="text-red-500">*</span></label>
                        <Textarea 
                          placeholder="Why is this lot inspection being rejected?"
                          value={rejectionReason}
                          onChange={e => setRejectionReason(e.target.value)}
                          className="bg-white border-red-200 focus-visible:ring-red-500/20"
                        />
                      </div>
                      <div className="flex gap-2">
                        <Button
                          onClick={handleReject}
                          disabled={isSubmitting}
                          className="bg-red-600 hover:bg-red-700 text-white rounded-xl font-semibold"
                        >
                          {isSubmitting ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <XCircle className="w-4 h-4 mr-2" />}
                          Confirm Rejection
                        </Button>
                        <Button
                          onClick={() => setIsRejecting(false)}
                          disabled={isSubmitting}
                          variant="ghost"
                          className="rounded-xl text-slate-600"
                        >
                          Cancel
                        </Button>
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
