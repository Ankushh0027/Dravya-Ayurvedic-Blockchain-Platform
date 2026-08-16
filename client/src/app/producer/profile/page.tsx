'use client'

import React, { useEffect } from 'react'
import { ProducerService } from '@/services/api/producer'
import { useApi } from '@/hooks/useApi'
import { ProducerProfileForm } from '@/features/producer/components/ProducerProfileForm'
import { LoadingState } from '@/components/shared/LoadingState'
import { ErrorState } from '@/components/shared/ErrorState'
import { toast } from 'sonner'
import { ProducerProfile } from '@/types/producer'
import { Badge } from '@/components/ui/badge'

export default function ProducerProfilePage() {
  const { 
    data: profile, 
    isLoading: isFetching, 
    error: fetchError, 
    execute: fetchProfile 
  } = useApi(ProducerService.getProfile)

  const { 
    isLoading: isSaving, 
    execute: updateProfile 
  } = useApi(ProducerService.updateProfile)

  useEffect(() => {
    fetchProfile()
  }, [fetchProfile])

  const handleSubmit = async (values: Partial<ProducerProfile>) => {
    const result = await updateProfile(values)
    if (result) {
      toast.success('Profile saved successfully.')
      fetchProfile() // Refresh after API success
    } else {
      toast.error('Failed to save profile.')
    }
  }

  return (
    <div className="container mx-auto p-6 max-w-4xl space-y-6">
      <div className="flex justify-between items-center border-b pb-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Producer Profile</h1>
          <p className="text-muted-foreground">Manage your farm and organizational details.</p>
        </div>
        {profile && (
          <Badge variant={profile.verificationStatus === 'VERIFIED' ? 'default' : 'secondary'}>
            {profile.verificationStatus}
          </Badge>
        )}
      </div>

      {isFetching && !profile ? (
        <LoadingState message="Loading profile..." />
      ) : fetchError && !profile ? (
        // The API returns 404 if profile doesn't exist, which is an expected state for new users
        fetchError.includes('not found') ? (
          <ProducerProfileForm initialData={null} onSubmit={handleSubmit} isLoading={isSaving} />
        ) : (
          <ErrorState message={fetchError} onRetry={() => fetchProfile()} />
        )
      ) : (
        <ProducerProfileForm initialData={profile} onSubmit={handleSubmit} isLoading={isSaving} />
      )}
    </div>
  )
}
