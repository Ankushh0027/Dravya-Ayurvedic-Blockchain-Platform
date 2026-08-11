'use client'

import { useTranslation } from 'react-i18next'

export default function LabDashboardPage() {
  const { t } = useTranslation()

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold">{t('dashboard.labDashboardTitle')}</h1>
      <p>{t('dashboard.labDashboardWelcome')}</p>
    </div>
  )
}
