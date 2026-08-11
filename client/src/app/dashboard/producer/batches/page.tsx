'use client'

import { BatchesTable } from '@/features/producer/components/BatchesTable'
import { useTranslation } from 'react-i18next'

export default function MyBatchesPage() {
  const { t } = useTranslation()

  return (
    <div className="flex-1 space-y-4">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">{t('producer.myBatches')}</h2>
        <p className="text-muted-foreground">{t('producer.allBatchesSubtitle')}</p>
      </div>
      <BatchesTable />
    </div>
  )
}