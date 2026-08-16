'use client'

import { useState, useRef, useEffect } from 'react'
import { Footer } from '@/features/landing/components/Footer'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { ShieldCheck, ScanLine, Search, X } from 'lucide-react'
import { Smartphone, ArrowLeft } from 'lucide-react'
import Link from 'next/link'
import { LeafSprig } from '@/features/landing/components/LeafSprig'
import { FloatingLeaf } from '@/features/landing/components/FloatingLeaf'
import jsQR from 'jsqr'
import { useTranslation } from 'react-i18next'
import { LanguageSelector } from '@/components/shared/LanguageSelector'
import { publicApi, PublicVerificationResponse } from '@/services/api/public'
import { toast } from 'sonner'
import { Loader2 } from 'lucide-react'

export default function VerifyPage() {
  const { t } = useTranslation()
  const [scanning, setScanning] = useState(false)
  const [batchId, setBatchId] = useState('')
  const [isVerifying, setIsVerifying] = useState(false)
  const [verificationResult, setVerificationResult] = useState<PublicVerificationResponse | null>(null)
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const rafRef = useRef<number | null>(null)

  const handleVerify = async (codeToVerify: string = batchId) => {
    if (!codeToVerify.trim()) {
      toast.error('Please enter a verification code')
      return
    }

    try {
      setIsVerifying(true)
      setVerificationResult(null)
      const data = await publicApi.verifyQR(codeToVerify)
      setVerificationResult(data)
      if (data.verified) {
        toast.success('Product verified successfully')
      } else {
        toast.error(data.message || 'Verification failed')
      }
    } catch (error: any) {
      console.error('Verification error:', error)
      toast.error(error.response?.data?.message || 'Failed to verify product')
    } finally {
      setIsVerifying(false)
    }
  }

  const startScan = async () => {
    setScanning(true)
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment' },
      })
      streamRef.current = stream
      if (videoRef.current) {
        videoRef.current.srcObject = stream
        await videoRef.current.play()
        tick()
      }
    } catch {
      setScanning(false)
      alert(t('verify.cameraAlert'))
    }
  }

  const stopScan = () => {
    if (rafRef.current) cancelAnimationFrame(rafRef.current)
    streamRef.current?.getTracks().forEach((t) => t.stop())
    streamRef.current = null
    setScanning(false)
  }

  const tick = () => {
    const video = videoRef.current
    const canvas = canvasRef.current
    if (video && canvas && video.readyState === video.HAVE_ENOUGH_DATA) {
      canvas.width = video.videoWidth
      canvas.height = video.videoHeight
      const ctx = canvas.getContext('2d')
      if (ctx) {
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height)
        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height)
        const code = jsQR(imageData.data, imageData.width, imageData.height)
        if (code) {
          setBatchId(code.data)
          stopScan()
          handleVerify(code.data)
          return
        }
      }
    }
    rafRef.current = requestAnimationFrame(tick)
  }

  useEffect(() => {
    return () => stopScan()
  }, [])

  return (
    <div className="min-h-screen bg-[#F8F9FA] relative font-sans overflow-x-hidden">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_50%_0%,rgba(24,78,72,0.08),transparent_60%)] z-0" />

      <div className="absolute top-[12%] left-0 w-[200px] md:w-[300px] lg:w-[400px] pointer-events-none z-0 opacity-75 mix-blend-multiply transform -translate-x-[15%]">
        <LeafSprig className="w-full h-auto text-primary" />
      </div>

      <div className="absolute top-[25%] right-0 w-[200px] md:w-[300px] lg:w-[400px] pointer-events-none z-0 opacity-75 mix-blend-multiply transform translate-x-[15%]">
        <LeafSprig className="w-full h-auto text-primary" flip={true} />
      </div>

      <div className="absolute top-[45%] left-[17%] w-[110px] md:w-[122px] lg:w-[130px] pointer-events-none z-0 opacity-50 mix-blend-multiply">
        <FloatingLeaf className="w-full h-auto text-primary" rotate={-70} />
      </div>

      <div className="absolute top-[18%] right-[17%] w-[90px] md:w-[100px] lg:w-[120px] pointer-events-none z-0 opacity-45 mix-blend-multiply">
        <FloatingLeaf className="w-full h-auto text-primary" rotate={70} />
      </div>

      <div className="w-full bg-[#184E48] backdrop-blur-xl border-b border-white/10 shadow-[0_4px_20px_rgb(0,0,0,0.1)] transition-all duration-300">
        <nav className="flex items-center justify-between px-6 py-2.5 max-w-7xl mx-auto w-full">
          <div className="flex items-center gap-3">
            <div className="w-[66px] h-[66px] rounded-full overflow-hidden flex-shrink-0">
              <img
                src="/logo-out.png"
                alt="Dravya"
                className="w-full h-full object-cover object-center"
              />
            </div>

            <div className="flex flex-col justify-center">
              <div className="flex items-center gap-2.5">
                <h1 className="text-xl md:text-2xl font-bold leading-none text-white tracking-tight font-serif">
                  Dravya
                </h1>
                <div className="w-[1.5px] h-4 bg-white/30 rounded-full" />
                <span className="text-lg font-medium text-[var(--accent)] leading-none mt-0.5">
                  द्रव्य
                </span>
              </div>

              <p className="text-[10px] text-slate-300 font-bold tracking-[0.15em] uppercase mt-1">
                {t('landing.tagline')}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <Link
              href="/"
              className="flex items-center gap-2 text-sm font-bold text-white bg-teal-800 hover:bg-teal-700 transition-colors rounded-lg py-2 px-4"
            >
              <ArrowLeft className="w-4 h-4" />
              {t('nav.backToHome')}
            </Link>

            <Button
              variant="outline"
              className="hidden lg:flex items-center gap-2 rounded-lg border-white/20 bg-white/5 text-white hover:bg-white/10 hover:text-white px-5"
            >
              <Smartphone className="w-4 h-4 text-teal-200" />
              {t('nav.downloadApp')}
            </Button>

            <LanguageSelector variant="navbar" />
          </div>
        </nav>
      </div>

      <div className="flex flex-col items-center justify-center px-6 py-24 relative z-10 max-w-2xl mx-auto text-center">
        <h1 className="text-4xl md:text-5xl lg:text-6xl font-extrabold tracking-tight text-[#184E48] leading-[1.1] mb-4 font-serif">
          {t('verify.title')}
        </h1>
        <p className="text-base md:text-lg text-gray-600 mb-10 max-w-md mx-auto">
          {t('verify.subtitle')}
        </p>

        <div className="w-full bg-white/70 backdrop-blur-xl border border-white/40 shadow-[0_8px_40px_rgb(0,0,0,0.08)] rounded-[24px] p-6 md:p-8">
          <div className="flex flex-col gap-4">
            <div className="flex flex-col sm:flex-row gap-3">
              <Input
                value={batchId}
                onChange={(e) => setBatchId(e.target.value)}
                placeholder={t('verify.inputPlaceholder')}
                className="bg-white/80 !border !border-black text-slate-900 placeholder:text-slate-400 h-12 rounded-xl shadow-sm focus-visible:ring-[#184E48]/20 focus-visible:border-[#184E48] text-base"
              />
              <Button 
                onClick={() => handleVerify()}
                disabled={isVerifying}
                className="h-12 px-8 bg-[#184E48] hover:bg-[#184E48]/90 text-white rounded-xl shadow-md transition-all active:scale-[0.98] font-semibold text-base shrink-0"
              >
                {isVerifying ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Search className="h-4 w-4 mr-2" />}
                {t('verify.verifyBtn')}
              </Button>
            </div>

            <div className="flex items-center gap-4 my-2">
              <div className="flex-1 h-px bg-slate-200" />
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">{t('verify.or')}</span>
              <div className="flex-1 h-px bg-slate-200" />
            </div>

            <Button
              onClick={startScan}
              variant="outline"
              className="h-12 w-full rounded-xl !border !border-black bg-white hover:bg-slate-50 text-slate-700 shadow-sm transition-all active:scale-[0.98] font-semibold text-base"
            >
              <ScanLine className="h-5 w-5 mr-2 text-[#184E48]" />
              {t('verify.scanQr')}
            </Button>
          </div>
        </div>

        {verificationResult ? (
          <div className="w-full mt-10 text-left bg-white rounded-2xl shadow-xl border border-slate-200 overflow-hidden">
            <div className={`p-6 border-b ${verificationResult.verified ? 'bg-green-50 border-green-100' : 'bg-red-50 border-red-100'}`}>
              <div className="flex items-center gap-4">
                <div className={`h-12 w-12 rounded-full flex items-center justify-center shrink-0 ${verificationResult.verified ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'}`}>
                  {verificationResult.verified ? <ShieldCheck className="h-6 w-6" /> : <X className="h-6 w-6" />}
                </div>
                <div>
                  <h2 className={`text-xl font-bold ${verificationResult.verified ? 'text-green-800' : 'text-red-800'}`}>
                    {verificationResult.verified ? 'Verified Authentic' : 'Verification Failed'}
                  </h2>
                  <p className={`text-sm mt-1 ${verificationResult.verified ? 'text-green-600' : 'text-red-600'}`}>
                    {verificationResult.message || (verificationResult.verified ? 'This product is authentic and fully traceable.' : 'This product could not be verified.')}
                  </p>
                </div>
              </div>
            </div>
            
            {verificationResult.verified && verificationResult.product && (
              <div className="p-6">
                <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-4">Product Details</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-xs text-slate-500 font-medium">Herb</p>
                    <p className="text-sm font-semibold text-slate-900">{verificationResult.product.herb}</p>
                    <p className="text-xs text-slate-500 italic">{verificationResult.product.botanicalName}</p>
                  </div>
                  <div>
                    <p className="text-xs text-slate-500 font-medium">Batch Number</p>
                    <p className="text-sm font-semibold text-slate-900">{verificationResult.product.batchNumber}</p>
                  </div>
                  <div>
                    <p className="text-xs text-slate-500 font-medium">Harvest Date</p>
                    <p className="text-sm font-semibold text-slate-900">{verificationResult.product.harvestDate}</p>
                  </div>
                  <div>
                    <p className="text-xs text-slate-500 font-medium">Producer</p>
                    <p className="text-sm font-semibold text-slate-900">{verificationResult.producer?.name}</p>
                    <p className="text-xs text-slate-500">{verificationResult.producer?.district}, {verificationResult.producer?.state}</p>
                  </div>
                </div>

                {verificationResult.timeline && verificationResult.timeline.length > 0 && (
                  <>
                    <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider mt-8 mb-4">Traceability Timeline</h3>
                    <div className="space-y-4 relative before:absolute before:inset-0 before:ml-2 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-slate-200 before:to-transparent">
                      {verificationResult.timeline.map((item, idx) => (
                        <div key={idx} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
                          <div className="flex items-center justify-center w-5 h-5 rounded-full border border-white bg-green-500 shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 shadow" />
                          <div className="w-[calc(100%-2.5rem)] md:w-[calc(50%-1.5rem)] p-3 rounded-xl border border-slate-200 bg-white shadow-sm">
                            <div className="flex items-center justify-between mb-1">
                              <span className="font-bold text-slate-800 text-sm">{item.label}</span>
                              <span className="text-xs font-medium text-green-600 bg-green-50 px-2 py-0.5 rounded-full">{item.status}</span>
                            </div>
                            <div className="text-xs text-slate-500">{item.date}</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </>
                )}
                
                {verificationResult.blockchain && (
                  <div className="mt-8 p-4 bg-slate-50 rounded-xl border border-slate-200 text-center">
                    <div className="flex items-center justify-center gap-2 mb-2">
                      <ShieldCheck className="h-5 w-5 text-[#184E48]" />
                      <span className="font-bold text-slate-800">Blockchain Secured</span>
                    </div>
                    <p className="text-xs text-slate-500">
                      This product's lifecycle data has been irreversibly anchored to {verificationResult.blockchain.details?.network || 'the blockchain'}. Data integrity verified.
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>
        ) : (
          <div className="w-full mt-10 p-6 bg-[#184E48] rounded-2xl text-left flex gap-4 shadow-xl border border-white/10">
            <div className="h-10 w-10 shrink-0 bg-white/10 rounded-full flex items-center justify-center">
              <ShieldCheck className="h-5 w-5 text-teal-200" />
            </div>
            <div>
              <h3 className="font-bold text-white text-sm mb-1">{t('verify.howItWorksTitle')}</h3>
              <p className="text-sm text-slate-200 leading-relaxed">
                {t('verify.howItWorksDesc')}
              </p>
            </div>
          </div>
        )}
      </div>
      {scanning && (
        <div className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-black/80 px-6">
          <div className="relative rounded-2xl overflow-hidden w-[90vw] max-w-sm aspect-square bg-black shadow-2xl">
            <video
              ref={videoRef}
              className="w-full h-full object-cover"
              muted
              playsInline
              autoPlay
            />
            <canvas ref={canvasRef} className="hidden" />

            <div className="pointer-events-none absolute inset-8 rounded-xl">
              <span className="absolute top-0 left-0 w-8 h-8 border-t-4 border-l-4 border-teal-400 rounded-tl-lg" />
              <span className="absolute top-0 right-0 w-8 h-8 border-t-4 border-r-4 border-teal-400 rounded-tr-lg" />
              <span className="absolute bottom-0 left-0 w-8 h-8 border-b-4 border-l-4 border-teal-400 rounded-bl-lg" />
              <span className="absolute bottom-0 right-0 w-8 h-8 border-b-4 border-r-4 border-teal-400 rounded-br-lg" />
            </div>

            <button
              onClick={stopScan}
              aria-label="Close scanner"
              className="absolute top-3 right-3 bg-black/60 hover:bg-black/80 text-white p-1.5 rounded-full transition-colors"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
          <p className="mt-4 text-white text-sm">{t('verify.pointCamera')}</p>
        </div>
      )}

      <Footer />
    </div>
  )
}
