'use client'

import { useCallback, useEffect, useState } from 'react'
import { AxiosError } from 'axios'
import QRCode from 'qrcode'
import { Download, Loader2, Package, Printer, QrCode, RefreshCw, TriangleAlert } from 'lucide-react'
import { toast } from 'sonner'
import { adminApi } from '@/services/api/admin'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import type { Batch } from '@/types/batch'
import type { GeneratedQRCode } from '@/types/admin'

function getApiErrorMessage(error: unknown, fallback: string): string {
  if (error instanceof AxiosError) {
    const response = error.response?.data
    if (typeof response === 'object' && response !== null && 'message' in response && typeof response.message === 'string') {
      return response.message
    }
  }
  return error instanceof Error ? error.message : fallback
}

function formatStatus(status: string): string {
  return status.replaceAll('_', ' ').toLowerCase().replace(/\b\w/g, letter => letter.toUpperCase())
}

export default function AdminQRPage() {
  const [batches, setBatches] = useState<Batch[]>([])
  const [selectedBatchId, setSelectedBatchId] = useState('')
  const [generatedQR, setGeneratedQR] = useState<GeneratedQRCode | null>(null)
  const [qrAsset, setQrAsset] = useState<string | null>(null)
  const [isLoadingBatches, setIsLoadingBatches] = useState(true)
  const [isGenerating, setIsGenerating] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const loadBatches = useCallback(async () => {
    setIsLoadingBatches(true)
    setError(null)
    try {
      setBatches(await adminApi.getQRCompatibleBatches())
    } catch {
      setError('Unable to load eligible batches.')
    } finally {
      setIsLoadingBatches(false)
    }
  }, [])

  useEffect(() => {
    const timer = window.setTimeout(() => {
      void loadBatches()
    }, 0)
    return () => window.clearTimeout(timer)
  }, [loadBatches])

  const selectedBatch = batches.find(batch => batch.id === selectedBatchId) ?? null

  const handleGenerate = async () => {
    if (!selectedBatch) {
      toast.error('Select a batch before generating its QR code.')
      return
    }

    setIsGenerating(true)
    setError(null)
    setGeneratedQR(null)
    setQrAsset(null)
    try {
      const qr = await adminApi.generateQRCode(selectedBatch.id)
      const asset = await QRCode.toDataURL(qr.verificationUrl, {
        errorCorrectionLevel: 'M',
        margin: 2,
        width: 640,
      })
      setGeneratedQR(qr)
      setQrAsset(asset)
      toast.success('QR code generated successfully.')
    } catch (generationError) {
      const message = getApiErrorMessage(generationError, 'Unable to generate the QR code. Please try again.')
      setError(message)
      toast.error(message)
    } finally {
      setIsGenerating(false)
    }
  }

  const handleDownload = () => {
    if (!qrAsset || !selectedBatch) return
    const link = document.createElement('a')
    link.href = qrAsset
    link.download = `${selectedBatch.batchNumber}-verification-qr.png`
    link.click()
  }

  const handlePrint = () => {
    if (!qrAsset || !generatedQR || !selectedBatch) return
    const printWindow = window.open('', '_blank')
    if (!printWindow) {
      toast.error('Please allow pop-ups to print the QR code.')
      return
    }
    printWindow.document.write(`<!doctype html><html><head><title>${selectedBatch.batchNumber} QR code</title><style>body{font-family:Arial,sans-serif;margin:32px;color:#183c38}.card{max-width:440px;text-align:center;border:1px solid #d7e2e0;border-radius:16px;padding:24px}img{width:320px;height:320px;image-rendering:pixelated}h1{font-size:22px;margin:0 0 8px}p{margin:7px 0}.code{font-family:monospace;font-size:18px;font-weight:700;letter-spacing:1px}</style></head><body><section class="card"><h1>${selectedBatch.batchNumber}</h1><p>${selectedBatch.herb?.commonName ?? 'Herb product'} · ${selectedBatch.quantity} ${selectedBatch.unit}</p><img src="${qrAsset}" alt="Verification QR code" /><p class="code">${generatedQR.code}</p></section><script>window.onload=()=>{window.print();window.close()}</script></body></html>`)
    printWindow.document.close()
  }

  return (
    <div className="max-w-[1100px] mx-auto p-6 md:p-10 space-y-8">
      <div className="rounded-[24px] bg-gradient-to-br from-[#184E48] to-[#113834] p-8 md:p-10 shadow-xl text-white">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-12 h-12 rounded-xl bg-white/10 border border-white/20 flex items-center justify-center"><QrCode className="w-6 h-6 text-emerald-300" /></div>
          <h1 className="text-3xl md:text-4xl font-bold font-serif">QR Management</h1>
        </div>
        <p className="max-w-2xl text-emerald-50/80 font-medium">Generate a public verification QR code for a batch that has completed the required quality workflow.</p>
      </div>

      <Card className="rounded-[24px] !bg-white border border-[#D7E7E2] shadow-[0_10px_30px_rgba(24,78,72,0.08)] overflow-hidden">
        <CardContent className="p-6 md:p-8 space-y-6">
          <div className="flex items-start justify-between gap-4">
            <div><h2 className="text-xl font-bold text-slate-800">Select batch</h2><p className="text-sm text-slate-500 mt-1">Only batches in a QR-ready status are listed. The server validates all eligibility requirements before generation.</p></div>
            <Button variant="outline" size="sm" onClick={() => void loadBatches()} disabled={isLoadingBatches} className="border-[#B8D5CD] bg-white text-[#184E48] hover:bg-[#EEF7F4] hover:text-[#113834]"><RefreshCw className={`w-4 h-4 mr-2 ${isLoadingBatches ? 'animate-spin' : ''}`} />Refresh</Button>
          </div>

          {isLoadingBatches ? <div className="flex items-center justify-center py-12 text-slate-500"><Loader2 className="w-5 h-5 animate-spin mr-2 text-[#184E48]" />Loading batches…</div> : (
            <select value={selectedBatchId} onChange={event => { setSelectedBatchId(event.target.value); setGeneratedQR(null); setQrAsset(null); setError(null) }} className="w-full h-12 rounded-xl border border-[#B8D5CD] bg-[#F8FCFB] px-4 text-sm font-medium text-slate-800 shadow-sm focus:outline-none focus:ring-2 focus:ring-[#184E48] focus:bg-white" aria-label="Eligible batch">
              <option value="">Select an eligible batch</option>
              {batches.map(batch => <option key={batch.id} value={batch.id}>{batch.batchNumber} — {batch.herb?.commonName ?? 'Herb'} ({batch.quantity} {batch.unit})</option>)}
            </select>
          )}

          {!isLoadingBatches && batches.length === 0 && <p className="rounded-xl border border-[#D7E7E2] bg-[#F2F8F6] p-4 text-sm text-[#42635C]">No batches are currently eligible for QR generation.</p>}

          {selectedBatch && <div className="grid grid-cols-1 sm:grid-cols-5 gap-3 rounded-2xl bg-[#F2F8F6] border border-[#D7E7E2] p-4">
            <div><p className="text-xs font-bold uppercase tracking-wide text-slate-400">Batch</p><p className="mt-1 font-semibold text-slate-800">{selectedBatch.batchNumber}</p></div>
            <div><p className="text-xs font-bold uppercase tracking-wide text-slate-400">Product</p><p className="mt-1 font-semibold text-slate-800">{selectedBatch.herb?.commonName ?? '—'}</p></div>
            <div><p className="text-xs font-bold uppercase tracking-wide text-slate-400">Quantity</p><p className="mt-1 font-semibold text-slate-800">{selectedBatch.quantity} {selectedBatch.unit}</p></div>
            <div><p className="text-xs font-bold uppercase tracking-wide text-slate-400">Status</p><p className="mt-1 font-semibold text-slate-800">{formatStatus(selectedBatch.status)}</p></div>
            <div><p className="text-xs font-bold uppercase tracking-wide text-slate-400">Harvest date</p><p className="mt-1 font-semibold text-slate-800">{new Date(selectedBatch.harvestDate).toLocaleDateString()}</p></div>
          </div>}

          <Button onClick={() => void handleGenerate()} disabled={!selectedBatch || isLoadingBatches || isGenerating} className="w-full sm:w-auto bg-[#184E48] hover:bg-[#113834] text-white rounded-xl px-6">
            {isGenerating ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Package className="w-4 h-4 mr-2" />}{isGenerating ? 'Generating QR…' : 'Generate QR'}
          </Button>
        </CardContent>
      </Card>

      {error && <div role="alert" className="flex gap-3 rounded-2xl border border-red-200 bg-red-50 p-4 text-sm text-red-800"><TriangleAlert className="w-5 h-5 shrink-0" /><p>{error}</p></div>}

      {generatedQR && qrAsset && selectedBatch && <Card className="rounded-[24px] border-emerald-100 shadow-sm overflow-hidden">
        <CardContent className="p-6 md:p-8">
          <div className="grid md:grid-cols-[minmax(0,1fr)_340px] gap-8 items-center">
            <div className="space-y-4"><div><p className="text-sm font-bold text-emerald-700 uppercase tracking-wide">QR generated</p><h2 className="text-2xl font-bold text-slate-800 mt-1">{selectedBatch.batchNumber}</h2><p className="text-slate-600 mt-1">{selectedBatch.herb?.commonName ?? 'Herb product'} · {selectedBatch.quantity} {selectedBatch.unit}</p></div><div><p className="text-xs font-bold uppercase tracking-wide text-slate-400">Verification code</p><p className="mt-1 font-mono text-lg font-bold text-slate-800">{generatedQR.code}</p></div><p className="text-sm text-slate-500 break-all">{generatedQR.verificationUrl}</p><div className="flex flex-wrap gap-3"><Button onClick={handleDownload} className="bg-[#184E48] hover:bg-[#113834] rounded-xl"><Download className="w-4 h-4 mr-2" />Download QR</Button><Button variant="outline" onClick={handlePrint} className="rounded-xl"><Printer className="w-4 h-4 mr-2" />Print QR</Button></div></div>
            <div className="rounded-2xl border border-slate-200 bg-white p-4"><img src={qrAsset} alt={`Verification QR code for batch ${selectedBatch.batchNumber}`} className="w-full h-auto" /></div>
          </div>
        </CardContent>
      </Card>}
    </div>
  )
}
