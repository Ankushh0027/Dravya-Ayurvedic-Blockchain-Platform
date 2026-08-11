'use client'

import { ProducerStats } from '@/features/producer/components/ProducerStats'
import { BatchesTable } from '@/features/producer/components/BatchesTable'
import { useTranslation } from 'react-i18next'

export default function ProducerDashboardPage() {
  const { t } = useTranslation()

  return (
    <div className="flex-1 space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">{t('producer.dashboardTitle')}</h2>
        <p className="text-muted-foreground">{t('producer.dashboardSubtitle')}</p>
      </div>
      <ProducerStats />
      <div>
        <h3 className="text-lg font-semibold mb-3">{t('producer.myBatches')}</h3>
        <BatchesTable />
      </div>
    </div>
  )
}