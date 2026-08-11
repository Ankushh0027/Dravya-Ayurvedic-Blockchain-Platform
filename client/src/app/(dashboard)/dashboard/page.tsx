'use client'

import { DashboardStats } from '@/features/dashboard/components/DashboardStats'
import { DashboardCharts } from '@/features/dashboard/components/DashboardCharts'
import { useTranslation } from 'react-i18next'

export default function DashboardPage() {
  const { t } = useTranslation()

  return (
    <div className="flex-1 space-y-4">
      <div className="flex items-center justify-between space-y-2">
        <h2 className="text-3xl font-bold tracking-tight">{t('dashboard.title')}</h2>
      </div>
      <DashboardStats />
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7 mt-4">
        <DashboardCharts />
      </div>
    </div>
  )
}
