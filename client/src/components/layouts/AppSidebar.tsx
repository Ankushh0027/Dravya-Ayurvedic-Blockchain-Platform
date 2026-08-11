'use client'

import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
} from '@/components/ui/sidebar'
import {
  Home,
  Package,
  FlaskConical,
  Factory,
  Truck,
  Store,
  LineChart,
  Settings,
} from 'lucide-react'
import Link from 'next/link'

import { useTranslation } from 'react-i18next'

export function AppSidebar() {
  const { t } = useTranslation()

  const navItems = [
    { title: t('nav.dashboard'), url: '/dashboard', icon: Home },
    { title: t('nav.batches'), url: '/dashboard/batches', icon: Package },
    { title: t('nav.laboratories'), url: '/dashboard/laboratories', icon: FlaskConical },
    { title: t('nav.manufacturers'), url: '/dashboard/manufacturers', icon: Factory },
    { title: t('nav.distributors'), url: '/dashboard/distributors', icon: Truck },
    { title: t('nav.retailers'), url: '/dashboard/retailers', icon: Store },
    { title: t('nav.analytics'), url: '/dashboard/analytics', icon: LineChart },
    { title: t('nav.settings'), url: '/dashboard/settings', icon: Settings },
  ]

  return (
    <Sidebar>
      <SidebarHeader>
        <div className="flex items-center gap-2 p-2">
          <div className="h-8 w-8 bg-primary rounded-md flex items-center justify-center text-primary-foreground font-bold">
            D
          </div>
          <span className="text-lg font-bold">Dravya</span>
        </div>
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>{t('nav.dashboard')}</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {navItems.map((item) => (
                <SidebarMenuItem key={item.url}>
                  <Link href={item.url}>
                    <SidebarMenuButton>
                      <item.icon />
                      <span>{item.title}</span>
                    </SidebarMenuButton>
                  </Link>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
    </Sidebar>
  )
}
