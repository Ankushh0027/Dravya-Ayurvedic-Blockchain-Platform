'use client'

import React from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useAuthStore } from '@/store/authStore'
import { LayoutDashboard, Truck, LogOut, User as UserIcon } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { NotificationBell } from '@/components/shared/NotificationBell'

export function DistributorNavbar() {
  const pathname = usePathname()
  const { user, logout } = useAuthStore()

  const navItems = [
    { name: 'Dashboard', href: '/distributor/dashboard', icon: LayoutDashboard },
    { name: 'Assigned Batches', href: '/distributor/batches', icon: Truck },
  ]

  const isActive = (path: string) => {
    if (path === '/distributor/dashboard' && pathname === path) return true
    if (path !== '/distributor/dashboard' && pathname.startsWith(path)) return true
    return false
  }

  return (
    <nav className="fixed top-0 w-full z-50 bg-white/70 backdrop-blur-xl border-b border-slate-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            <div className="flex-shrink-0 flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-[#184E48] flex items-center justify-center">
                <span className="text-white font-bold font-serif text-sm">D</span>
              </div>
              <span className="font-serif font-bold text-xl text-[#184E48]">Dravya</span>
            </div>
            <div className="hidden sm:ml-8 sm:flex sm:space-x-1">
              {navItems.map((item) => {
                const active = isActive(item.href)
                return (
                  <Link
                    key={item.name}
                    href={item.href}
                    className={`inline-flex items-center px-4 py-2 mt-3 mb-3 rounded-lg text-sm font-medium transition-colors ${
                      active
                        ? 'bg-[#184E48]/10 text-[#184E48]'
                        : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                    }`}
                  >
                    <item.icon className={`mr-2 h-4 w-4 ${active ? 'text-[#184E48]' : 'text-slate-400'}`} />
                    {item.name}
                  </Link>
                )
              })}
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="hidden sm:block">
              <NotificationBell />
            </div>
            <div className="hidden sm:flex items-center gap-3 px-3 py-1.5 rounded-full border border-slate-200 bg-white shadow-sm">
              <div className="w-7 h-7 rounded-full bg-slate-100 flex items-center justify-center">
                <UserIcon className="w-4 h-4 text-slate-600" />
              </div>
              <div className="flex flex-col">
                <span className="text-xs font-semibold text-slate-900 leading-none">{user?.name}</span>
                <span className="text-[10px] text-slate-500 font-medium">Distributor</span>
              </div>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => logout()}
              className="text-slate-500 hover:text-red-600 hover:bg-red-50 rounded-lg"
            >
              <LogOut className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>

      {/* Mobile nav */}
      <div className="sm:hidden border-t border-slate-200 bg-white">
        <div className="flex justify-around px-2 py-2">
          {navItems.map((item) => {
            const active = isActive(item.href)
            return (
              <Link
                key={item.name}
                href={item.href}
                className={`flex flex-col items-center p-2 rounded-lg min-w-[4rem] transition-colors ${
                  active ? 'text-[#184E48]' : 'text-slate-500 hover:text-slate-900 hover:bg-slate-50'
                }`}
              >
                <item.icon className={`h-5 w-5 mb-1 ${active ? 'text-[#184E48]' : 'text-slate-400'}`} />
                <span className="text-[10px] font-medium">{item.name}</span>
              </Link>
            )
          })}
        </div>
      </div>
    </nav>
  )
}
