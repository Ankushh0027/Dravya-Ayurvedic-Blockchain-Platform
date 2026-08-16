'use client'

import { StatCard } from '@/components/shared/StatCard'
import { Package, Users, Truck, CheckCircle } from 'lucide-react'
import { useTranslation } from 'react-i18next'

export function DashboardStats() {
  const { t } = useTranslation()

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <StatCard
        title={t('dashboard.statTotalBatches')}
        value="1,245"
        description={t('dashboard.statBatchesDesc')}
        icon={Package}
      />
      <StatCard title={t('dashboard.statActiveFarmers')} value="850" description={t('dashboard.statFarmersDesc')} icon={Users} />
      <StatCard
        title={t('dashboard.statPendingVerification')}
        value="32"
        description={t('dashboard.statPendingDesc')}
        icon={CheckCircle}
      />
      <StatCard title={t('dashboard.statShipments')} value="124" description={t('dashboard.statShipmentsDesc')} icon={Truck} />
    </div>
  )
}
