'use client'

import { useCallback, useEffect, useState } from 'react'
import { AxiosError } from 'axios'
import { FlaskConical, Loader2, MapPin, RefreshCw, UserCheck } from 'lucide-react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { adminApi } from '@/services/api/admin'
import type { Laboratory, PendingLabAssignment } from '@/types/admin'

function getErrorMessage(error: unknown, fallback: string): string {
  if (error instanceof AxiosError) {
    const response = error.response?.data
    if (typeof response === 'object' && response !== null && 'message' in response && typeof response.message === 'string') {
      return response.message
    }
  }
  return error instanceof Error ? error.message : fallback
}

export default function AdminLabTestsPage() {
  const [batches, setBatches] = useState<PendingLabAssignment[]>([])
  const [laboratories, setLaboratories] = useState<Laboratory[]>([])
  const [selectedLaboratories, setSelectedLaboratories] = useState<Record<string, string>>({})
  const [isLoading, setIsLoading] = useState(true)
  const [assigningId, setAssigningId] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const loadData = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      const [assignmentsData, laboratoriesData] = await Promise.all([
        adminApi.getPendingLabAssignments(),
        adminApi.getLaboratories(),
      ])
      setBatches(assignmentsData.batches)
      setLaboratories(laboratoriesData.laboratories)
    } catch (loadError) {
      setError(getErrorMessage(loadError, 'Unable to load laboratory assignments.'))
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    const timer = window.setTimeout(() => void loadData(), 0)
    return () => window.clearTimeout(timer)
  }, [loadData])

  const handleAssign = async (batch: PendingLabAssignment) => {
    const labId = selectedLaboratories[batch.id]
    if (!labId) {
      toast.error('Select a laboratory first.')
      return
    }

    setAssigningId(batch.id)
    try {
      await adminApi.assignLabTest(batch.id, { labId })
      toast.success(`Test assigned for batch ${batch.batchNumber}.`)
      await loadData()
    } catch (assignError) {
      toast.error(getErrorMessage(assignError, 'Unable to assign the laboratory test.'))
    } finally {
      setAssigningId(null)
    }
  }

  return (
    <div className="max-w-[1400px] mx-auto p-6 md:p-10 space-y-8">
      <div className="rounded-[24px] bg-gradient-to-br from-[#184E48] to-[#113834] p-8 md:p-10 shadow-xl text-white">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-12 h-12 bg-white/10 border border-white/20 rounded-xl flex items-center justify-center">
            <FlaskConical className="w-6 h-6 text-emerald-300" />
          </div>
          <h1 className="text-3xl md:text-4xl font-bold font-serif">Laboratory Test Queue</h1>
        </div>
        <p className="text-emerald-50/80 font-medium">Assign an active laboratory after a batch&apos;s lot inspection has been approved.</p>
      </div>

      <div className="flex justify-end">
        <Button variant="outline" onClick={() => void loadData()} disabled={isLoading} className="border-[#B8D5CD] bg-white text-[#184E48] hover:bg-[#EEF7F4]">
          <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />Refresh
        </Button>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-16 text-slate-500"><Loader2 className="w-5 h-5 animate-spin mr-2" />Loading laboratory assignments…</div>
      ) : error ? (
        <Card className="!bg-red-50 border-red-200 rounded-2xl"><CardContent className="p-6 text-red-800">{error}</CardContent></Card>
      ) : batches.length === 0 ? (
        <Card className="!bg-white border border-[#D7E7E2] rounded-2xl"><CardContent className="p-12 text-center text-slate-500">There are no approved batches awaiting laboratory assignment.</CardContent></Card>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {batches.map(batch => (
            <Card key={batch.id} className="!bg-white border border-[#D7E7E2] rounded-[24px] shadow-sm">
              <CardContent className="p-6 space-y-5">
                <div className="flex items-start justify-between gap-3">
                  <div><h2 className="text-xl font-bold text-slate-800">{batch.batchNumber}</h2><p className="text-sm text-[#184E48] font-medium mt-1">{batch.herb.commonName} · {batch.quantity} {batch.unit}</p></div>
                  <span className="rounded-full bg-amber-50 border border-amber-200 px-3 py-1 text-xs font-bold text-amber-800">Ready for lab</span>
                </div>
                <div className="flex gap-4 text-sm text-slate-600"><span className="flex items-center gap-1.5"><MapPin className="w-4 h-4 text-slate-400" />{batch.producerProfile.farmName}</span><span className="flex items-center gap-1.5"><UserCheck className="w-4 h-4 text-slate-400" />Awaiting assignment</span></div>
                <div className="grid sm:grid-cols-[1fr_auto] gap-3">
                  <select aria-label={`Laboratory for ${batch.batchNumber}`} value={selectedLaboratories[batch.id] ?? ''} onChange={event => setSelectedLaboratories(current => ({ ...current, [batch.id]: event.target.value }))} className="h-11 rounded-xl border border-[#B8D5CD] bg-[#F8FCFB] px-3 text-sm font-medium text-slate-800 focus:outline-none focus:ring-2 focus:ring-[#184E48]">
                    <option value="" disabled>Select laboratory</option>
                    {laboratories.map(laboratory => <option key={laboratory.id} value={laboratory.id}>{laboratory.name} ({laboratory.organization ?? laboratory.email})</option>)}
                  </select>
                  <Button onClick={() => void handleAssign(batch)} disabled={assigningId === batch.id || !selectedLaboratories[batch.id]} className="bg-[#184E48] hover:bg-[#113834] text-white rounded-xl">{assigningId === batch.id ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Assign'}</Button>
                </div>
                {laboratories.length === 0 && <p className="text-sm text-amber-700">No active LAB users are available to receive this assignment.</p>}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
