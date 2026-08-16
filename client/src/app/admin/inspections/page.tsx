'use client'

import { useCallback, useEffect, useState } from 'react'
import { AxiosError } from 'axios'
import { ClipboardCheck, Loader2, MapPin, RefreshCw, UserCheck } from 'lucide-react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { adminApi } from '@/services/api/admin'
import type { AdminLotInspection, VerificationAuthority } from '@/types/admin'

function getErrorMessage(error: unknown, fallback: string): string {
  if (error instanceof AxiosError) {
    const response = error.response?.data
    if (typeof response === 'object' && response !== null && 'message' in response && typeof response.message === 'string') {
      return response.message
    }
  }
  return error instanceof Error ? error.message : fallback
}

export default function AdminInspectionsPage() {
  const [inspections, setInspections] = useState<AdminLotInspection[]>([])
  const [authorities, setAuthorities] = useState<VerificationAuthority[]>([])
  const [selectedAuthorities, setSelectedAuthorities] = useState<Record<string, string>>({})
  const [isLoading, setIsLoading] = useState(true)
  const [assigningId, setAssigningId] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const loadData = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      const [inspectionsData, authoritiesData] = await Promise.all([
        adminApi.getPendingLotInspections(),
        adminApi.getVerificationAuthorities(),
      ])
      setInspections(inspectionsData.inspections)
      setAuthorities(authoritiesData.authorities)
    } catch (loadError) {
      setError(getErrorMessage(loadError, 'Unable to load lot inspections.'))
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    const timer = window.setTimeout(() => void loadData(), 0)
    return () => window.clearTimeout(timer)
  }, [loadData])

  const handleAssign = async (inspection: AdminLotInspection) => {
    const authorityId = selectedAuthorities[inspection.id] ?? inspection.authorityId
    if (!authorityId) {
      toast.error('Select a verification authority first.')
      return
    }
    setAssigningId(inspection.id)
    try {
      await adminApi.assignLotInspection(inspection.id, { authorityId })
      toast.success('Verification authority assigned to the lot inspection.')
      await loadData()
    } catch (assignError) {
      toast.error(getErrorMessage(assignError, 'Unable to assign the lot inspection.'))
    } finally {
      setAssigningId(null)
    }
  }

  return (
    <div className="max-w-[1400px] mx-auto p-6 md:p-10 space-y-8">
      <div className="rounded-[24px] bg-gradient-to-br from-[#184E48] to-[#113834] p-8 md:p-10 shadow-xl text-white">
        <div className="flex items-center gap-3 mb-4"><div className="w-12 h-12 bg-white/10 border border-white/20 rounded-xl flex items-center justify-center"><ClipboardCheck className="w-6 h-6 text-emerald-300" /></div><h1 className="text-3xl md:text-4xl font-bold font-serif">Lot Inspections</h1></div>
        <p className="text-emerald-50/80 font-medium">Assign pending batch inspections to a verification authority for on-ground review.</p>
      </div>

      <div className="flex justify-end"><Button variant="outline" onClick={() => void loadData()} disabled={isLoading} className="border-[#B8D5CD] bg-white text-[#184E48] hover:bg-[#EEF7F4]"><RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />Refresh</Button></div>

      {isLoading ? <div className="flex justify-center py-16 text-slate-500"><Loader2 className="w-5 h-5 animate-spin mr-2" />Loading lot inspections…</div> : error ? <Card className="!bg-red-50 border-red-200 rounded-2xl"><CardContent className="p-6 text-red-800">{error}</CardContent></Card> : inspections.length === 0 ? <Card className="!bg-white border border-[#D7E7E2] rounded-2xl"><CardContent className="p-12 text-center text-slate-500">There are no pending lot inspections to assign.</CardContent></Card> : <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {inspections.map(inspection => <Card key={inspection.id} className="!bg-white border border-[#D7E7E2] rounded-[24px] shadow-sm"><CardContent className="p-6 space-y-5">
          <div className="flex items-start justify-between gap-3"><div><h2 className="text-xl font-bold text-slate-800">{inspection.batch.batchNumber}</h2><p className="text-sm text-[#184E48] font-medium mt-1">{inspection.batch.herb.commonName} · {inspection.declaredQuantity} {inspection.batch.unit}</p></div><span className="rounded-full bg-amber-50 border border-amber-200 px-3 py-1 text-xs font-bold text-amber-800">{inspection.status.replaceAll('_', ' ')}</span></div>
          <div className="flex gap-4 text-sm text-slate-600"><span className="flex items-center gap-1.5"><MapPin className="w-4 h-4 text-slate-400" />{inspection.batch.producerProfile.farmName}</span><span className="flex items-center gap-1.5"><UserCheck className="w-4 h-4 text-slate-400" />{inspection.authority?.name ?? 'Unassigned'}</span></div>
          <div className="grid sm:grid-cols-[1fr_auto] gap-3"><select aria-label={`Authority for ${inspection.batch.batchNumber}`} value={selectedAuthorities[inspection.id] ?? inspection.authorityId ?? ''} onChange={event => setSelectedAuthorities(current => ({ ...current, [inspection.id]: event.target.value }))} className="h-11 rounded-xl border border-[#B8D5CD] bg-[#F8FCFB] px-3 text-sm font-medium text-slate-800 focus:outline-none focus:ring-2 focus:ring-[#184E48]"><option value="" disabled>Select verification authority</option>{authorities.map(authority => <option key={authority.id} value={authority.id}>{authority.name} ({authority.organization ?? authority.email})</option>)}</select><Button onClick={() => void handleAssign(inspection)} disabled={assigningId === inspection.id || !(selectedAuthorities[inspection.id] ?? inspection.authorityId)} className="bg-[#184E48] hover:bg-[#113834] text-white rounded-xl">{assigningId === inspection.id ? <Loader2 className="w-4 h-4 animate-spin" /> : inspection.authorityId ? 'Reassign' : 'Assign'}</Button></div>
        </CardContent></Card>)}
      </div>}
    </div>
  )
}
