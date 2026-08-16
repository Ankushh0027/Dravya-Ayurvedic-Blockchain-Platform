'use client'

import { Button } from '@/components/ui/button'
import { LogOut, LayoutDashboard, ShieldCheck, SearchCheck } from 'lucide-react'
import Link from 'next/link'
import { useTranslation } from 'react-i18next'
import { LanguageSelector } from '@/components/shared/LanguageSelector'
import { NotificationBell } from '@/components/shared/NotificationBell'
import { useAuthStore } from '@/store/authStore'
import { useRouter, usePathname } from 'next/navigation'

export function AuthorityNavbar() {
  const { t } = useTranslation()
  const router = useRouter()
  const pathname = usePathname()
  const logout = useAuthStore(state => state.logout)
  const user = useAuthStore(state => state.user)

  const handleLogout = () => {
    logout()
  }

  const isActive = (path: string) => pathname.startsWith(path)

  return (
    <div className="w-full bg-[#184E48] backdrop-blur-xl border-b border-white/10 shadow-[0_4px_20px_rgb(0,0,0,0.1)] transition-all duration-300 sticky top-0 z-50">
      <nav className="flex items-center justify-between px-4 sm:px-6 py-2.5 max-w-[1600px] mx-auto w-full">
        {/* Logo Section */}
        <div className="flex items-center gap-3">
          <Link href="/authority/dashboard" className="flex items-center gap-3 group">
            <div className="w-[45px] h-[45px] sm:w-[50px] sm:h-[50px] rounded-full overflow-hidden flex-shrink-0 group-hover:scale-105 transition-transform duration-300 shadow-sm border border-white/20">
              <img
                src="/logo-out.png"
                alt="Dravya"
                className="w-full h-full object-cover object-center bg-white"
              />
            </div>
            <div className="flex flex-col justify-center hidden sm:flex">
              <div className="flex items-center gap-2.5">
                <h1 className="text-xl font-bold leading-none text-white tracking-tight font-serif">
                  Dravya
                </h1>
                <div className="w-[1.5px] h-3.5 bg-white/30 rounded-full" />
                <span className="text-base font-medium text-[var(--accent)] leading-none mt-0.5">
                  Authority
                </span>
              </div>
            </div>
          </Link>
        </div>

        {/* Desktop Links */}
        <div className="hidden lg:flex items-center gap-1 mx-4">
          <Link href="/authority/dashboard">
            <Button variant="ghost" className={`text-sm font-semibold rounded-xl px-4 transition-all duration-300 ${isActive('/authority/dashboard') ? 'bg-white/10 text-white shadow-inner' : 'text-slate-300 hover:text-white hover:bg-white/5'}`}>
              <LayoutDashboard className="w-4 h-4 mr-2" />
              Dashboard
            </Button>
          </Link>
          <Link href="/authority/verifications">
            <Button variant="ghost" className={`text-sm font-semibold rounded-xl px-4 transition-all duration-300 ${isActive('/authority/verifications') ? 'bg-white/10 text-white shadow-inner' : 'text-slate-300 hover:text-white hover:bg-white/5'}`}>
              <ShieldCheck className="w-4 h-4 mr-2" />
              Verifications
            </Button>
          </Link>
          <Link href="/authority/inspections">
            <Button variant="ghost" className={`text-sm font-semibold rounded-xl px-4 transition-all duration-300 ${isActive('/authority/inspections') ? 'bg-white/10 text-white shadow-inner' : 'text-slate-300 hover:text-white hover:bg-white/5'}`}>
              <SearchCheck className="w-4 h-4 mr-2" />
              Inspections
            </Button>
          </Link>
        </div>

        {/* Right Section */}
        <div className="flex items-center gap-3">
          <div className="hidden sm:block">
            <NotificationBell />
          </div>
          <div className="hidden sm:block">
            <LanguageSelector variant="navbar" />
          </div>
          
          <div className="w-[1.5px] h-6 bg-white/10 rounded-full hidden sm:block mx-1" />

          <div className="flex items-center gap-3">
            <div className="hidden md:flex flex-col items-end mr-2">
              <span className="text-sm font-bold text-white leading-tight">{user?.name}</span>
              <span className="text-[10px] text-teal-200 font-medium uppercase tracking-wider">{user?.role}</span>
            </div>
            
            <Button
              onClick={handleLogout}
              variant="outline"
              className="flex items-center gap-2 rounded-xl border-white/20 bg-white/5 text-white hover:bg-red-500/90 hover:text-white hover:border-red-500/50 px-4 transition-all duration-300"
            >
              <LogOut className="w-4 h-4" />
              <span className="hidden sm:inline">Logout</span>
            </Button>
          </div>
        </div>
      </nav>
    </div>
  )
}
