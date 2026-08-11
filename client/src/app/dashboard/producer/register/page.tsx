'use client'

import { RegisterBatchForm } from '@/features/producer/components/RegisterBatchForm'
import { useTranslation } from 'react-i18next'

export default function RegisterBatchPage() {
  const { t } = useTranslation()

  return (
    <div className="flex-1 space-y-4 max-w-2xl">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">{t('producer.registerBatchTitle')}</h2>
        <p className="text-muted-foreground">{t('producer.registerBatchSubtitle')}</p>
      </div>
      <RegisterBatchForm />
    </div>
  )
}