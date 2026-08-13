'use client'

import React, { useEffect, useState } from 'react'
import { HerbService } from '@/services/api/herbs'
import { useApi } from '@/hooks/useApi'
import { LoadingState } from '@/components/shared/LoadingState'
import { ErrorState } from '@/components/shared/ErrorState'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Search, Leaf } from 'lucide-react'

export default function HerbCatalogPage() {
  const { data: herbs, isLoading, error, execute: fetchHerbs } = useApi(HerbService.getAllHerbs)
  const [searchTerm, setSearchTerm] = useState('')

  useEffect(() => {
    fetchHerbs()
  }, [fetchHerbs])

  if (isLoading && !herbs) {
    return <LoadingState message="Loading herb catalog..." />
  }

  if (error && !herbs) {
    return <ErrorState message={error} onRetry={() => fetchHerbs()} />
  }

  const filteredHerbs = (herbs || []).filter(herb => 
    herb.commonName.toLowerCase().includes(searchTerm.toLowerCase()) ||
    herb.botanicalName.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const glassCard = "bg-white/80 backdrop-blur-xl border border-white/60 shadow-[0_8px_40px_rgb(0,0,0,0.04)] rounded-[24px] hover:shadow-[0_12px_50px_rgb(0,0,0,0.08)] transition-all duration-300"
  const inputStyles = "pl-10 h-12 border-slate-200 bg-slate-50/50 hover:bg-slate-50 rounded-xl focus-visible:ring-[#184E48]/20 focus-visible:border-[#184E48] transition-all text-sm shadow-sm"

  return (
    <div className="max-w-[1400px] mx-auto p-6 md:p-10 space-y-8 relative">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 pb-4">
        <div>
          <h1 className="text-4xl md:text-5xl font-bold tracking-tight text-[#1e293b] font-serif mb-2">Herb Catalog</h1>
          <p className="text-[17px] text-slate-600 font-medium">Browse the list of herbs supported by the Dravya platform.</p>
        </div>
        <div className="relative w-full md:w-80">
          <Search className="absolute left-3.5 top-3.5 h-5 w-5 text-slate-400" />
          <Input
            type="search"
            placeholder="Search herbs..."
            className={inputStyles}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>

      {!isLoading && filteredHerbs.length === 0 ? (
        <div className="py-20 text-center flex flex-col items-center justify-center bg-white/50 backdrop-blur-sm rounded-[24px] border border-dashed border-slate-300 shadow-sm">
          <div className="w-20 h-20 rounded-full bg-white flex items-center justify-center shadow-md mb-6">
            <Leaf className="w-10 h-10 text-slate-300" />
          </div>
          <h3 className="text-2xl font-bold text-[#1e293b] font-serif mb-2">No herbs found</h3>
          <p className="text-slate-500 max-w-md text-[15px]">There are no herbs matching your search criteria. Please try a different search term.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          {filteredHerbs.map((herb) => (
            <Card key={herb.id} className={`${glassCard} flex flex-col h-full overflow-hidden group`}>
              <div className="h-2 w-full bg-[#184E48]/10 group-hover:bg-[#184E48] transition-colors duration-500" />
              <CardHeader className="pb-4">
                <div className="flex justify-between items-start gap-4">
                  <div>
                    <CardTitle className="text-xl font-bold text-[#1e293b] mb-1">{herb.commonName}</CardTitle>
                    <CardDescription className="italic text-slate-500">{herb.botanicalName}</CardDescription>
                  </div>
                  {herb.isActive ? (
                    <Badge className="bg-emerald-100 text-emerald-800 hover:bg-emerald-200 border-none px-3 py-1 font-semibold">Active</Badge>
                  ) : (
                    <Badge variant="secondary" className="bg-slate-100 text-slate-600 border-none px-3 py-1 font-semibold">Inactive</Badge>
                  )}
                </div>
              </CardHeader>
              <CardContent className="flex-1 space-y-5 bg-slate-50/50 pt-5 mt-auto border-t border-slate-100/50">
                {herb.localName && (
                  <div>
                    <span className="text-xs font-bold uppercase tracking-wider text-slate-400 block mb-1">Local Name</span>
                    <p className="text-[15px] font-medium text-slate-700">{herb.localName}</p>
                  </div>
                )}
                <div>
                  <span className="text-xs font-bold uppercase tracking-wider text-slate-400 block mb-1">Family</span>
                  <p className="text-[15px] font-medium text-slate-700">{herb.family}</p>
                </div>
                {herb.description && (
                  <div>
                    <span className="text-xs font-bold uppercase tracking-wider text-slate-400 block mb-1">Description</span>
                    <p className="text-sm text-slate-600 leading-relaxed line-clamp-3">{herb.description}</p>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}

