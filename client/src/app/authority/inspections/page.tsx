'use client'

import { useEffect, useState } from 'react'
import { authorityApi } from '@/services/api/authority'
import { BatchInspection } from '@/types/authority'
import { LoadingState } from '@/components/shared/LoadingState'
import { ErrorState } from '@/components/shared/ErrorState'
import { format } from 'date-fns'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Search, MapPin, Calendar, CheckSquare, ChevronRight, SearchCheck, Info, Leaf, Scale } from 'lucide-react'
import { Card } from '@/components/ui/card'

export default function AuthorityInspectionsPage() {
  const [inspections, setInspections] = useState<BatchInspection[]>([])
  const [filteredInspections, setFilteredInspections] = useState<BatchInspection[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')

  useEffect(() => {
    fetchInspections()
  }, [])

  useEffect(() => {
    if (searchQuery.trim() === '') {
      setFilteredInspections(inspections)
    } else {
      const lowerQuery = searchQuery.toLowerCase()
      setFilteredInspections(inspections.filter(i => {
        const batchNumber = i.batch?.batchNumber?.toLowerCase() || ''
        const herbName = i.batch?.herb?.commonName?.toLowerCase() || ''
        const producerName = i.batch?.producerProfile?.farmName?.toLowerCase() || ''
        return batchNumber.includes(lowerQuery) || herbName.includes(lowerQuery) || producerName.includes(lowerQuery)
      }))
    }
  }, [searchQuery, inspections])

  const fetchInspections = async () => {
    setIsLoading(true)
    setError(null)
    try {
      const response = await authorityApi.getAssignedInspections()
      if (response.data?.success && response.data.data?.inspections) {
        setInspections(response.data.data.inspections)
        setFilteredInspections(response.data.data.inspections)
      } else {
        setError('Failed to load inspections')
      }
    } catch (err: any) {
      console.error('Error fetching inspections:', err)
      setError(err.response?.data?.message || 'Failed to load inspections')
    } finally {
      setIsLoading(false)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'PENDING': return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'UNDER_INSPECTION': return 'bg-blue-100 text-blue-800 border-blue-200'
      case 'APPROVED': return 'bg-green-100 text-green-800 border-green-200'
      case 'REJECTED': return 'bg-red-100 text-red-800 border-red-200'
      default: return 'bg-slate-100 text-slate-800 border-slate-200'
    }
  }

  if (isLoading) {
    return <LoadingState message="Loading assigned lot inspections..." />
  }

  if (error) {
    return <ErrorState message={error} onRetry={fetchInspections} />
  }

  const glassCard = "bg-white/70 backdrop-blur-xl border border-white/60 shadow-[0_8px_40px_rgb(0,0,0,0.04)] rounded-[24px] hover:shadow-[0_12px_50px_rgb(0,0,0,0.08)] transition-all duration-500 overflow-hidden relative"

  return (
    <div className="max-w-[1400px] mx-auto p-6 md:p-10 space-y-10 animate-in fade-in duration-500">
      
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 tracking-tight font-serif flex items-center gap-3">
            <SearchCheck className="w-8 h-8 text-[#184E48]" />
            Lot Inspections
          </h1>
          <p className="text-slate-500 mt-1">Review and conduct on-ground batch inspections.</p>
        </div>
      </div>

      <div className="flex flex-col sm:flex-row gap-4 justify-between items-center bg-white/70 backdrop-blur-xl p-4 rounded-[24px] border border-white/60 shadow-[0_8px_40px_rgb(0,0,0,0.04)]">
        <div className="relative w-full sm:w-96">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <Input
            placeholder="Search by batch, herb, or farm..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10 bg-white border-slate-200 rounded-xl w-full focus-visible:ring-[#184E48]/20 focus-visible:border-[#184E48]"
          />
        </div>
      </div>

      {filteredInspections.length === 0 ? (
        <Card className={`${glassCard} flex flex-col items-center justify-center py-16 text-center`}>
          <div className="w-16 h-16 bg-slate-50 rounded-2xl flex items-center justify-center shadow-inner border border-slate-100 mb-4">
            <Info className="w-8 h-8 text-slate-300" />
          </div>
          <h3 className="text-xl font-bold text-slate-900 font-serif mb-2">No inspections found</h3>
          <p className="text-slate-500 max-w-sm">
            {searchQuery ? 'Try adjusting your search terms.' : 'You have no assigned lot inspections at the moment.'}
          </p>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          {filteredInspections.map((inspection) => (
            <Card key={inspection.id} className={`${glassCard} flex flex-col overflow-hidden hover:shadow-[0_8px_30px_rgb(0,0,0,0.08)] transition-all duration-300`}>
              <div className="p-6 flex-1">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-lg font-bold text-slate-900 line-clamp-1">{inspection.batch?.batchNumber || 'Unknown Batch'}</h3>
                    <p className="text-sm font-medium text-[#184E48] flex items-center gap-1.5 mt-0.5">
                      <Leaf className="w-3.5 h-3.5" />
                      {inspection.batch?.herb?.commonName || 'Unknown Herb'}
                    </p>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-[11px] font-bold tracking-wider uppercase border shadow-sm ${getStatusColor(inspection.status)}`}>
                    {inspection.status}
                  </span>
                </div>

                <div className="space-y-3 mt-6">
                  <div className="flex items-center gap-3 text-sm text-slate-600">
                    <div className="w-8 h-8 rounded-full bg-slate-50 flex items-center justify-center border border-slate-100">
                      <MapPin className="w-4 h-4 text-slate-400" />
                    </div>
                    <div>
                      <p className="text-xs text-slate-400 font-medium uppercase tracking-wider">Farm</p>
                      <p className="font-medium text-slate-700 line-clamp-1">{inspection.batch?.producerProfile?.farmName || 'Unknown Farm'}</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-3 text-sm text-slate-600">
                    <div className="w-8 h-8 rounded-full bg-slate-50 flex items-center justify-center border border-slate-100">
                      <Scale className="w-4 h-4 text-slate-400" />
                    </div>
                    <div>
                      <p className="text-xs text-slate-400 font-medium uppercase tracking-wider">Declared Qty</p>
                      <p className="font-medium text-slate-700">{inspection.declaredQuantity} {inspection.batch?.unit || 'kg'}</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-3 text-sm text-slate-600">
                    <div className="w-8 h-8 rounded-full bg-slate-50 flex items-center justify-center border border-slate-100">
                      <Calendar className="w-4 h-4 text-slate-400" />
                    </div>
                    <div>
                      <p className="text-xs text-slate-400 font-medium uppercase tracking-wider">Assigned</p>
                      <p className="font-medium text-slate-700">{inspection.assignedAt ? format(new Date(inspection.assignedAt), 'MMM d, yyyy') : 'N/A'}</p>
                    </div>
                  </div>
                </div>
              </div>

              <div className="p-4 border-t border-slate-100/50 bg-slate-50/30 mt-auto">
                <Link href={`/authority/inspections/${inspection.id}`} className="block">
                  <Button className="w-full bg-white hover:bg-slate-50 text-[#184E48] border border-slate-200 hover:border-[#184E48]/30 shadow-sm rounded-xl font-bold transition-all py-6">
                    Review Details
                    <ChevronRight className="w-5 h-5 ml-2" />
                  </Button>
                </Link>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
