'use client'

import { useTranslation } from 'react-i18next'
import { ChevronDown, Globe } from 'lucide-react'
import { useEffect, useState } from 'react'
import '@/i18n/i18n'

interface LanguageSelectorProps {
  variant?: 'navbar' | 'dashboard' | 'default'
  className?: string
}

export function LanguageSelector({ variant = 'navbar', className = '' }: LanguageSelectorProps) {
  const { i18n } = useTranslation()
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  const currentLanguage = i18n.language?.startsWith('hi') ? 'hi' : 'en'

  const handleLanguageChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newLang = e.target.value
    i18n.changeLanguage(newLang)
    if (typeof window !== 'undefined') {
      localStorage.setItem('dravya-language', newLang)
    }
  }

  const baseStyles =
    'relative inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm font-semibold transition-colors duration-200 cursor-pointer focus:outline-none focus:ring-2 focus:ring-teal-400'

  const variantStyles =
    variant === 'dashboard'
      ? 'border border-slate-200 dark:border-slate-800 bg-background text-foreground hover:bg-slate-100 dark:hover:bg-slate-800'
      : 'border border-white/20 bg-white/5 text-white hover:bg-white/10'

  return (
    <div className={`relative inline-flex items-center ${className}`}>
      <div className={`${baseStyles} ${variantStyles}`}>
        <Globe className="w-4 h-4 text-teal-200 shrink-0" />
        <select
          value={mounted ? currentLanguage : 'en'}
          onChange={handleLanguageChange}
          aria-label="Select Language / भाषा चुनें"
          className="appearance-none bg-transparent pr-5 font-semibold text-inherit cursor-pointer focus:outline-none"
        >
          <option value="en" className="bg-[#184E48] text-white">
            English
          </option>
          <option value="hi" className="bg-[#184E48] text-white">
            हिन्दी
          </option>
        </select>
        <ChevronDown className="w-4 h-4 text-slate-300 pointer-events-none absolute right-2.5 shrink-0" />
      </div>
    </div>
  )
}
