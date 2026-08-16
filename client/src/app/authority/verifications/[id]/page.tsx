'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { authorityApi } from '@/services/api/authority'
import { ProducerVerification } from '@/types/authority'
import { LoadingState } from '@/components/shared/LoadingState'
import { ErrorState } from '@/components/shared/ErrorState'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Checkbox } from '@/components/ui/checkbox'
import { ShieldCheck, MapPin, Calendar, CheckCircle2, XCircle, FileText, ArrowLeft, Loader2 } from 'lucide-react'
import { toast } from 'sonner'
import Link from 'next/link'
import { format } from 'date-fns'

export default function AuthorityVerificationDetailsPage() {
  const params = useParams()
  const router = useRouter()
  const verificationId = params.id as string

  const [verification, setVerification] = useState<ProducerVerification | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  // Form states matching backend schema exactly
  const [identityVerified, setIdentityVerified] = useState(false)
  const [documentsVerified, setDocumentsVerified] = useState(false)
  const [landVerified, setLandVerified] = useState(false)
  const [locationVerified, setLocationVerified] = useState(false)
  const [cultivationVerified, setCultivationVerified] = useState(false)
  const [inspectionDate, setInspectionDate] = useState('')
  const [latitude, setLatitude] = useState<number | ''>('')
  const [longitude, setLongitude] = useState<number | ''>('')
  const [observations, setObservations] = useState('')
  
  // Rejection form
  const [isRejecting, setIsRejecting] = useState(false)
  const [rejectionReason, setRejectionReason] = useState('')

  useEffect(() => {
    fetchVerification()
  }, [verificationId])

  const fetchVerification = async () => {
    setIsLoading(true)
    setError(null)
    try {
      const response = await authorityApi.getVerificationDetails(verificationId)
      if (response.data?.success && response.data.data?.verification) {
        const v = response.data.data.verification
        setVerification(v)
        
        // Pre-fill existing data if completed
        if (v.status === 'COMPLETED') {
          setIdentityVerified(v.identityVerified || false)
          setDocumentsVerified(v.documentsVerified || false)
          setLandVerified(v.landVerified || false)
          setLocationVerified(v.locationVerified || false)
          setCultivationVerified(v.cultivationVerified || false)
          setInspectionDate(v.inspectionDate ? format(new Date(v.inspectionDate), 'yyyy-MM-dd') : '')
          setLatitude(v.latitude || '')
          setLongitude(v.longitude || '')
          setObservations(v.observations || '')
          if (v.rejectionReason) setRejectionReason(v.rejectionReason)
        } else {
          // Set current date as default for new inspections
          setInspectionDate(format(new Date(), 'yyyy-MM-dd'))
        }
      } else {
        setError('Failed to load verification details')
      }
    } catch (err: any) {
      console.error('Error fetching verification:', err)
      setError(err.response?.data?.message || 'Failed to load verification')
    } finally {
      setIsLoading(false)
    }
  }

  const handleApprove = async () => {
    if (!inspectionDate || latitude === '' || longitude === '') {
      toast.error('Please fill all required fields (Inspection Date, Latitude, Longitude)')
      return
    }

    setIsSubmitting(true)
    try {
      await authorityApi.approveVerification(verificationId, {
        identityVerified,
        documentsVerified,
        landVerified,
        locationVerified,
        cultivationVerified,
        inspectionDate: new Date(inspectionDate).toISOString(),
        latitude: Number(latitude),
        longitude: Number(longitude),
        observations: observations || undefined,
      })
      toast.success('Producer verification approved!')
      await fetchVerification()
    } catch (err: any) {
      console.error('Error approving verification:', err)
      toast.error(err.response?.data?.message || 'Failed to approve verification')
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
      await authorityApi.rejectVerification(verificationId, {
        rejectionReason,
      })
      toast.success('Producer verification rejected.')
      setIsRejecting(false)
      await fetchVerification()
    } catch (err: any) {
      console.error('Error rejecting verification:', err)
      toast.error(err.response?.data?.message || 'Failed to reject verification')
    } finally {
      setIsSubmitting(false)
    }
  }

  if (isLoading) {
    return <LoadingState message="Loading verification details..." />
  }

  if (error || !verification) {
    return <ErrorState message={error || 'Verification not found'} onRetry={fetchVerification} />
  }

  const glassCard = "bg-white/80 backdrop-blur-xl border border-white/60 shadow-xl rounded-[24px] transition-all duration-300 hover:shadow-2xl hover:border-white/80"
  const inputStyle = "bg-white/50 border-white/60 text-slate-900 placeholder:text-slate-400 focus:bg-white focus:ring-[#184E48]/20 focus:border-[#184E48]/30 backdrop-blur-sm transition-all duration-300 rounded-xl"
  const isCompleted = verification.status === 'COMPLETED'
  const isApproved = verification.decision === 'APPROVED'

  return (
    <div className="max-w-[1400px] mx-auto p-6 md:p-10 space-y-10 animate-in fade-in duration-500">
      <Link href="/authority/verifications" className="inline-flex items-center text-sm font-medium text-slate-500 hover:text-[#184E48] transition-colors">
        <ArrowLeft className="w-4 h-4 mr-1" />
        Back to Verifications
      </Link>

      {/* Hero Section */}
      <div className="relative rounded-[24px] overflow-hidden bg-gradient-to-br from-[#184E48] to-[#113834] p-8 md:p-10 shadow-xl border border-white/10 mt-4">
        <div className="absolute top-0 right-0 w-[400px] h-[400px] bg-teal-500/10 rounded-full blur-[60px] pointer-events-none -translate-y-1/2 translate-x-1/3" />
        <div className="absolute bottom-0 left-0 w-[300px] h-[300px] bg-emerald-500/10 rounded-full blur-[50px] pointer-events-none translate-y-1/3 -translate-x-1/4" />
        <div className="absolute inset-0 bg-[url('/noise.png')] opacity-20 mix-blend-overlay" />
        
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="max-w-2xl">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 bg-white/10 rounded-xl flex items-center justify-center backdrop-blur-sm border border-white/20">
                <ShieldCheck className="w-6 h-6 text-emerald-300" />
              </div>
              <h1 className="text-3xl md:text-4xl font-bold tracking-tight text-white font-serif">Verification Assessment</h1>
            </div>
            <p className="text-emerald-50/80 font-medium leading-relaxed">
              Review producer details and submit your official on-ground verification report.
            </p>
          </div>
          
          {isCompleted && (
            <div className={`px-6 py-3 rounded-2xl border flex items-center gap-3 font-bold shadow-lg backdrop-blur-md ${isApproved ? 'bg-emerald-500/20 text-emerald-100 border-emerald-500/30' : 'bg-red-500/20 text-red-100 border-red-500/30'}`}>
              {isApproved ? <CheckCircle2 className="w-6 h-6" /> : <XCircle className="w-6 h-6" />}
              {isApproved ? 'OFFICIALLY VERIFIED' : 'REJECTED'}
            </div>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Column: Producer Info */}
        <div className="lg:col-span-1 space-y-6">
          <Card className={`${glassCard} border-t-4 border-t-[#184E48] relative overflow-hidden`}>
            <div className="absolute top-0 right-0 w-32 h-32 bg-[#184E48]/5 rounded-bl-full pointer-events-none" />
            <CardHeader>
              <CardTitle className="text-2xl font-serif text-[#1e293b]">Producer Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4 text-sm">
              <div>
                <span className="block text-slate-500 mb-1 text-xs uppercase tracking-wider font-semibold">Name</span>
                <span className="font-semibold text-slate-900">{verification.producerProfile?.user?.name}</span>
              </div>
              <div>
                <span className="block text-slate-500 mb-1 text-xs uppercase tracking-wider font-semibold">Contact</span>
                <span className="text-slate-700">{verification.producerProfile?.user?.email}</span>
                <br />
                <span className="text-slate-700">{verification.producerProfile?.user?.phone || 'No phone provided'}</span>
              </div>
            </CardContent>
          </Card>

          <Card className={`${glassCard}`}>
            <CardHeader>
              <CardTitle className="text-xl font-serif flex items-center gap-2">
                <MapPin className="w-5 h-5 text-[#184E48]" />
                Farm Details
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4 text-sm">
              <div>
                <span className="block text-slate-500 mb-1 text-xs uppercase tracking-wider font-semibold">Farm Name</span>
                <span className="font-semibold text-slate-900">{verification.producerProfile?.farmName}</span>
              </div>
              <div>
                <span className="block text-slate-500 mb-1 text-xs uppercase tracking-wider font-semibold">Address</span>
                <span className="text-slate-700">{verification.producerProfile?.address}</span>
              </div>
              <div>
                <span className="block text-slate-500 mb-1 text-xs uppercase tracking-wider font-semibold">Location</span>
                <span className="text-slate-700">{verification.producerProfile?.village}, {verification.producerProfile?.tehsil}</span>
                <br />
                <span className="text-slate-700">{verification.producerProfile?.district}, {verification.producerProfile?.state} {verification.producerProfile?.pincode}</span>
              </div>
              <div>
                <span className="block text-slate-500 mb-1 text-xs uppercase tracking-wider font-semibold">Land Size</span>
                <span className="font-semibold text-slate-900">{verification.producerProfile?.landSize} {verification.producerProfile?.landSizeUnit}</span>
              </div>
              {verification.producerProfile?.latitude && (
                <div>
                  <span className="block text-slate-500 mb-1 text-xs uppercase tracking-wider font-semibold">Coordinates</span>
                  <span className="text-slate-700 font-mono text-xs">{verification.producerProfile?.latitude}, {verification.producerProfile?.longitude}</span>
                </div>
              )}
            </CardContent>
          </Card>

          {verification.producerProfile?.verificationDocuments && verification.producerProfile.verificationDocuments.length > 0 && (
            <Card className={`${glassCard}`}>
              <CardHeader>
                <CardTitle className="text-xl font-serif flex items-center gap-2">
                  <FileText className="w-5 h-5 text-[#184E48]" />
                  Documents
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {verification.producerProfile.verificationDocuments.map(doc => (
                    <a key={doc.id} href={doc.fileUrl} target="_blank" rel="noreferrer" className="flex items-center justify-between p-3 rounded-lg border border-slate-200 bg-slate-50 hover:bg-slate-100 transition-colors">
                      <div className="truncate pr-4 text-sm font-medium text-slate-700">{doc.fileName}</div>
                      <span className="text-[10px] uppercase font-bold text-slate-400">{doc.type}</span>
                    </a>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Right Column: Verification Checklist */}
        <div className="lg:col-span-2 space-y-6">
          <Card className={`${glassCard} relative overflow-hidden`}>
            <div className="absolute top-0 right-0 w-64 h-64 bg-orange-500/5 rounded-full blur-[60px] pointer-events-none" />
            <CardHeader className="border-b border-slate-100/50 pb-6">
              <CardTitle className="text-2xl font-serif text-[#1e293b]">On-Ground Verification Checklist</CardTitle>
              <CardDescription className="text-slate-500 font-medium">Verify the physical existence and accuracy of the producer's claims.</CardDescription>
            </CardHeader>
            <CardContent className="pt-6 space-y-8">
              
              <div className="space-y-4">
                <h3 className="text-sm font-bold text-slate-500 uppercase tracking-wider">Checklist Items</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {[
                    { id: 'identity', label: 'Identity Verified', state: identityVerified, setter: setIdentityVerified },
                    { id: 'docs', label: 'Documents Verified', state: documentsVerified, setter: setDocumentsVerified },
                    { id: 'land', label: 'Land Verified', state: landVerified, setter: setLandVerified },
                    { id: 'location', label: 'Location Verified', state: locationVerified, setter: setLocationVerified },
                    { id: 'cultivation', label: 'Cultivation Verified', state: cultivationVerified, setter: setCultivationVerified },
                  ].map(item => (
                    <div 
                      key={item.id} 
                      className={`flex items-center space-x-4 p-4 rounded-2xl border transition-all duration-300 ${
                        item.state 
                          ? 'bg-emerald-50/80 border-emerald-200/60 shadow-sm' 
                          : 'bg-white/60 border-slate-200 hover:bg-white/90 hover:shadow-md'
                      }`}
                    >
                      <div className={`flex-shrink-0 w-6 h-6 rounded-md flex items-center justify-center transition-colors duration-300 ${
                        item.state ? 'bg-emerald-500 text-white' : 'bg-slate-200 text-transparent'
                      }`}>
                        <CheckCircle2 className="w-4 h-4" />
                      </div>
                      <Checkbox 
                        id={item.id} 
                        checked={item.state} 
                        onCheckedChange={(c) => item.setter(c as boolean)} 
                        disabled={isCompleted}
                        className="hidden"
                      />
                      <label htmlFor={item.id} className={`text-[15px] font-bold cursor-pointer flex-1 transition-colors duration-300 ${
                        item.state ? 'text-emerald-900' : 'text-slate-600'
                      }`}>
                        {item.label}
                      </label>
                    </div>
                  ))}
                </div>
              </div>

              <div className="space-y-4">
                <h3 className="text-sm font-bold text-slate-500 uppercase tracking-wider">Inspection Details</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <label className="text-sm font-semibold text-slate-700">Inspection Date <span className="text-red-500">*</span></label>
                    <Input 
                      type="date" 
                      value={inspectionDate} 
                      onChange={e => setInspectionDate(e.target.value)} 
                      disabled={isCompleted}
                      className={inputStyle}
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
                      disabled={isCompleted}
                      className={inputStyle}
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
                      disabled={isCompleted}
                      className={inputStyle}
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
                  disabled={isCompleted}
                  className={`min-h-[120px] !border-black ${inputStyle}`}
                />
              </div>
              
              {isCompleted && !isApproved && verification.rejectionReason && (
                <div className="p-4 rounded-xl bg-red-50 border border-red-100 text-red-800 space-y-1">
                  <span className="font-bold text-sm block">Rejection Reason</span>
                  <p className="text-sm">{verification.rejectionReason}</p>
                </div>
              )}

              {!isCompleted && (
                <div className="flex flex-col sm:flex-row gap-3 pt-6 border-t border-slate-100">
                  {!isRejecting ? (
                    <>
                      <Button
                        onClick={handleApprove}
                        disabled={isSubmitting}
                        className="w-full sm:w-auto bg-[#184E48] hover:bg-[#184E48]/90 text-white rounded-xl shadow-md font-semibold px-8"
                      >
                        {isSubmitting ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <CheckCircle2 className="w-4 h-4 mr-2" />}
                        Approve Verification
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
                          placeholder="Why is this verification being rejected?"
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
