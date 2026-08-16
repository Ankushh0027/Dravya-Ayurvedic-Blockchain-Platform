'use client'

import React, { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { BatchService } from '@/services/api/batches'
import { HerbService } from '@/services/api/herbs'
import { useApi } from '@/hooks/useApi'
import { CreateBatchForm } from '@/features/batch/components/CreateBatchForm'
import { CreateBatchPayload } from '@/types/batch'
import { toast } from 'sonner'
import { ChevronLeft } from 'lucide-react'
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
    <div className="container mx-auto p-6 max-w-3xl space-y-6">
      <div className="flex items-center space-x-4 mb-6">
        <Button variant="outline" size="icon" asChild>
          <Link href="/producer/batches">
            <ChevronLeft className="h-4 w-4" />
          </Link>
        </Button>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Create New Batch</h1>
          <p className="text-muted-foreground">Register a new herb harvest into the system.</p>
        </div>
      </div>

      <div className="border rounded-lg p-6 bg-card">
        <CreateBatchForm 
          herbs={herbs || []} 
          onSubmit={handleSubmit} 
          isLoading={isCreating} 
        />
      </div>
    </div>
  )
}
