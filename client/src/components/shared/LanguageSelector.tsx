'use client'

import { useTranslation } from 'react-i18next'
import { Globe } from 'lucide-react'
import { useEffect, useState } from 'react'
import '@/i18n/i18n'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

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

  const handleLanguageChange = (newLang: string | null) => {
    if (!newLang) return
    i18n.changeLanguage(newLang)
    if (typeof window !== 'undefined') {
      localStorage.setItem('dravya-language', newLang)
    }
  }

  const triggerStyles =
    variant === 'dashboard'
      ? 'h-9 min-w-[130px] rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 px-3 py-1.5 text-sm font-semibold text-slate-800 dark:text-slate-100 hover:bg-slate-50 dark:hover:bg-slate-800 shadow-sm focus:ring-2 focus:ring-[#184E48]/30'
      : 'h-9 min-w-[132px] justify-between gap-2 rounded-full border border-white/25 bg-white/10 px-3.5 py-1.5 text-sm font-semibold text-white backdrop-blur-md shadow-sm hover:bg-white/15 hover:border-white/40 focus:ring-2 focus:ring-emerald-300/40 transition-all duration-200 cursor-pointer'

  return (
    <div className={className}>
      <Select
        value={mounted ? currentLanguage : 'en'}
        onValueChange={handleLanguageChange}
      >
        <SelectTrigger className={triggerStyles}>
          <Globe className="h-3.5 w-3.5 shrink-0 text-emerald-200" strokeWidth={2.2} />
          <SelectValue placeholder="Language" />
        </SelectTrigger>
        <SelectContent
          side="bottom"
          align="end"
          sideOffset={8}
          alignItemWithTrigger={false}
          className="z-[100] min-w-[150px] rounded-2xl border border-[#184E48]/20 bg-white p-1.5 shadow-[0_12px_30px_-4px_rgba(24,78,72,0.25),0_4px_12px_-2px_rgba(0,0,0,0.08)]"
        >
          <SelectItem
            value="en"
            className="rounded-xl px-3 py-2 text-sm font-semibold text-slate-700 hover:text-white hover:bg-[#184E48] focus:bg-[#184E48] focus:text-white data-[highlighted]:bg-[#184E48] data-[highlighted]:text-white data-[highlighted]:*:text-white cursor-pointer transition-all duration-150 data-[state=checked]:bg-[#184E48]/10 data-[state=checked]:text-[#184E48] data-[state=checked]:font-bold"
          >
            🇬🇧 English
          </SelectItem>
          <SelectItem
            value="hi"
            className="rounded-xl px-3 py-2 text-sm font-semibold text-slate-700 hover:text-white hover:bg-[#184E48] focus:bg-[#184E48] focus:text-white data-[highlighted]:bg-[#184E48] data-[highlighted]:text-white data-[highlighted]:*:text-white cursor-pointer transition-all duration-150 data-[state=checked]:bg-[#184E48]/10 data-[state=checked]:text-[#184E48] data-[state=checked]:font-bold"
          >
            🇮🇳 हिन्दी
          </SelectItem>
        </SelectContent>
      </Select>
    </div>
  )
}
