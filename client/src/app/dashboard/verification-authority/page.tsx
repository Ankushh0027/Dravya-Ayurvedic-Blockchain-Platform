'use client'

import { useTranslation } from 'react-i18next'

export default function VerificationAuthorityPage() {
  const { t } = useTranslation()

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold">{t('dashboard.verificationAuthorityTitle')}</h1>
      <p>{t('dashboard.verificationAuthorityWelcome')}</p>
    </div>
  )
}
