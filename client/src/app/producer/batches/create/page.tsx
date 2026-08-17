'use client'

import React, { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { BatchService } from '@/services/api/batches'
import { HerbService } from '@/services/api/herbs'
import { useApi } from '@/hooks/useApi'
import { CreateBatchForm } from '@/features/batch/components/CreateBatchForm'
import { CreateBatchPayload } from '@/types/batch'
import { toast } from 'sonner'
import { ChevronLeft, PackagePlus } from 'lucide-react'
import Link from 'next/link'
import { Button } from '@/components/ui/button'

export default function CreateBatchPage() {
  const router = useRouter()
  const { data: herbs, execute: fetchHerbs } = useApi(HerbService.getAllHerbs)
  const { isLoading: isCreating, execute: createBatch } = useApi(BatchService.createBatch)

  useEffect(() => {
    fetchHerbs()
  }, [fetchHerbs])

  const handleSubmit = async (values: CreateBatchPayload) => {
    const result = await createBatch(values)
    if (result) {
      toast.success(`Batch ${result.batchNumber} created successfully.`)
      router.push(`/producer/batches/${result.id}`)
    } else {
      toast.error('Failed to create batch.')
    }
  }

  return (
  <div className="max-w-5xl mx-auto p-4 md:p-6 lg:p-10 space-y-8">
    <section className="relative overflow-hidden rounded-[24px] bg-gradient-to-br from-[#184E48] to-[#113834] p-6 md:p-8 shadow-xl border border-white/10 text-white">
      <div className="absolute -right-20 -top-28 h-80 w-80 rounded-full bg-emerald-400/10 blur-3xl pointer-events-none" />

      <div className="relative flex items-center gap-4">
        <Button
          variant="outline"
          size="icon"
          asChild
          className="shrink-0 rounded-xl border-white/20 bg-white/10 text-white hover:bg-white/20 hover:text-white"
        >
          <Link href="/producer/batches">
            <ChevronLeft className="h-4 w-4" />
          </Link>
        </Button>

        <div className="flex min-w-0 items-center gap-4">
          <div className="hidden sm:flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl border border-white/20 bg-white/10">
            <PackagePlus className="h-6 w-6 text-emerald-200" />
          </div>

          <div>
            <p className="text-sm font-bold uppercase tracking-[0.16em] text-emerald-200">
              Producer workspace
            </p>
            <h1 className="mt-1 text-3xl md:text-4xl font-bold tracking-tight font-serif">
              Create New Batch
            </h1>
            <p className="mt-2 text-emerald-50/80 font-medium">
              Register a new herb harvest for traceable quality verification.
            </p>
          </div>
        </div>
      </div>
    </section>

    <section>
      <CreateBatchForm
        herbs={herbs || []}
        onSubmit={handleSubmit}
        isLoading={isCreating}
      />
    </section>
  </div>
)
}
