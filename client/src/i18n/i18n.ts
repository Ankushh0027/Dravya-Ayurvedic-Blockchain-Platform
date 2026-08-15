import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import en from './locales/en.json'
import hi from './locales/hi.json'

if (!i18n.isInitialized) {
  i18n
    .use(initReactI18next)
    .init({
      resources: {
        en: { translation: en },
        hi: { translation: hi },
      },
      lng: 'en', // Always initialize with 'en' to match server SSR and prevent hydration mismatch
      fallbackLng: 'en',
      interpolation: {
        escapeValue: false,
      },
      react: {
        useSuspense: false,
      },
    })
}

if (typeof window !== 'undefined') {
  const saved = localStorage.getItem('dravya-language')
  if (saved && saved !== 'en' && i18n.language !== saved) {
    // Defer the language change until after initial hydration
    setTimeout(() => {
      i18n.changeLanguage(saved)
    }, 0)
  }

  i18n.on('languageChanged', (lng) => {
    localStorage.setItem('dravya-language', lng)
  })
}

export default i18n
