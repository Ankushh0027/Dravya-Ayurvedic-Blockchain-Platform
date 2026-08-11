'use client'

import { StatCard } from '@/components/shared/StatCard'
import { Package, Clock, CheckCircle2, XCircle } from 'lucide-react'
import { mockBatches } from '../data/batches'
import { useTranslation } from 'react-i18next'

export function ProducerStats() {
  const { t } = useTranslation()
  const total = mockBatches.length
  const pending = mockBatches.filter((b) => b.status === 'pending').length
  const verified = mockBatches.filter((b) => b.status === 'verified').length
  const rejected = mockBatches.filter((b) => b.status === 'rejected').length

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <StatCard title={t('producer.statTotalBatches')} value={String(total)} description={t('producer.statTotalDesc')} icon={Package} />
      <StatCard title={t('producer.statPendingReview')} value={String(pending)} description={t('producer.statPendingDesc')} icon={Clock} />
      <StatCard title={t('producer.statVerified')} value={String(verified)} description={t('producer.statVerifiedDesc')} icon={CheckCircle2} />
      <StatCard title={t('producer.statRejected')} value={String(rejected)} description={t('producer.statRejectedDesc')} icon={XCircle} />
    </div>
  )
}