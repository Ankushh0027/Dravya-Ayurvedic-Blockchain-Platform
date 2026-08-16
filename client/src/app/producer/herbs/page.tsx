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

  const getHerbImages = (name: string): string[] => {
    const n = name.toLowerCase()
    if (n.includes('aloe')) return ['/assets/herbs/Alovera.jpeg']
    if (n.includes('ashwa')) return ['/assets/herbs/Ashwagandha.jpeg']
    if (n.includes('brahmi')) return ['/assets/herbs/Brahmi.jpeg']
    if (n.includes('ginger')) return ['/assets/herbs/Ginger.jpeg', '/assets/herbs/Ginger-1.jpg']
    if (n.includes('neem')) return ['/assets/herbs/Neem.jpeg']
    if (n.includes('turmeric')) return ['/assets/herbs/Turmeric.jpeg', '/assets/herbs/Turmeric-1.webp']
    if (n.includes('tulsi')) return ['/assets/herbs/tulsi.jpeg']
    if (n.includes('haritaki')) return ['/assets/herbs/Haritaki.webp']
    if (n.includes('mulethi')) return ['/assets/herbs/mulethi.jpeg']
    if (n.includes('shatavari')) return ['/assets/herbs/shatavari.webp']
    if (n.includes('amla') || n.includes('gooseberry')) return ['/assets/herbs/amla.webp']
    if (n.includes('giloy')) return ['/assets/herbs/giloy.png']
    return []
  }

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
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 lg:gap-8">
          {filteredHerbs.map((herb, index) => {
            const images = getHerbImages(herb.commonName)

            return (
              <Card key={herb.id} className={`${glassCard} flex flex-col h-full overflow-hidden group`}>
                
                {/* Images Section */}
                {images.length > 0 && (
                  <div className="w-full h-48 flex overflow-hidden bg-slate-100 rounded-t-[23px] relative z-0">
                    {images.length === 1 ? (
                      <img 
                        src={images[0]} 
                        alt={herb.commonName} 
                        className="w-full h-full object-cover hover:scale-105 transition-transform duration-500" 
                      />
                    ) : (
                      <>
                        <div className="w-1/2 h-full overflow-hidden border-r border-white/20">
                          <img 
                            src={images[0]} 
                            alt={`${herb.commonName} 1`} 
                            className="w-full h-full object-cover hover:scale-110 transition-transform duration-500" 
                          />
                        </div>
                        <div className="w-1/2 h-full overflow-hidden">
                          <img 
                            src={images[1]} 
                            alt={`${herb.commonName} 2`} 
                            className="w-full h-full object-cover hover:scale-110 transition-transform duration-500" 
                          />
                        </div>
                      </>
                    )}
                  </div>
                )}

                {/* Header Section */}
                <div className="relative p-6 pb-5 w-full bg-[#184E48]/5 border-b border-[#184E48]/10">
                  <div className="flex justify-between items-start gap-4">
                    <div>
                      <h2 className="text-xl md:text-2xl font-bold text-[#1e293b] leading-tight font-serif mb-1">
                        {herb.commonName}
                      </h2>
                      <div className="flex items-center gap-1.5 text-slate-500">
                        <Leaf className="w-3.5 h-3.5 text-[#184E48]" />
                        <span className="italic text-[13px] font-medium">{herb.botanicalName}</span>
                      </div>
                    </div>
                    {herb.isActive ? (
                      <Badge className="bg-emerald-100 text-emerald-800 hover:bg-emerald-200 border-none px-2.5 py-0.5 font-bold shadow-sm">Active</Badge>
                    ) : (
                      <Badge variant="secondary" className="bg-slate-100 text-slate-600 border-none px-2.5 py-0.5 font-bold shadow-sm">Inactive</Badge>
                    )}
                  </div>
                </div>

                {/* Content Section */}
                <CardContent className="flex-1 p-5 md:p-6 space-y-5 pt-6 bg-[#184E48] rounded-b-[23px]">
                  
                  <div className="grid grid-cols-2 gap-4">
                    {herb.localName && (
                      <div>
                        <span className="text-[11px] font-bold uppercase tracking-wider block mb-1 text-white/50">Local Name</span>
                        <p className="text-[14px] font-semibold truncate text-white">{herb.localName}</p>
                      </div>
                    )}
                    <div>
                      <span className="text-[11px] font-bold uppercase tracking-wider block mb-1 text-white/50">Family</span>
                      <p className="text-[14px] font-semibold truncate text-white">{herb.family}</p>
                    </div>
                  </div>
                  
                  {herb.description && (
                    <div className="pt-2 border-t border-white/10">
                      <span className="text-[11px] font-bold uppercase tracking-wider block mb-2 mt-2 text-white/50">Description</span>
                      <p className="text-sm leading-relaxed line-clamp-3 text-white/80">{herb.description}</p>
                    </div>
                  )}
                  
                </CardContent>
              </Card>
            )
          })}
        </div>
      )}
    </div>
  )
}

