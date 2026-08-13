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
  SidebarFooter,
} from '@/components/ui/sidebar'
import {
  Home,
  Package,
  FlaskConical,
  Truck,
  LineChart,
  Settings,
  LogOut,
} from 'lucide-react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/store/authStore'
import { useTranslation } from 'react-i18next'

export function AppSidebar() {
  const { t } = useTranslation()
  const router = useRouter()
  const logout = useAuthStore(state => state.logout)

  const handleLogout = () => {
    // Clear Zustand store
    logout()
    // Clear localStorage
    localStorage.removeItem('token')
    localStorage.removeItem('auth_token')
    // Clear cookies
    document.cookie = 'auth_token=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT;'
    // Redirect to home
    router.push('/')
  }

  const navItems = [
    { title: t('nav.dashboard'), url: '/admin/dashboard', icon: Home },
    { title: t('nav.batches'), url: '/admin/batches', icon: Package },
    { title: t('nav.laboratories'), url: '/admin/lab', icon: FlaskConical },
    { title: t('nav.distributors'), url: '/admin/distributors', icon: Truck },
    { title: t('nav.analytics'), url: '/admin/audit', icon: LineChart },
    { title: t('nav.settings'), url: '/admin/settings', icon: Settings },
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
      
      <SidebarFooter>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton onClick={handleLogout} className="text-red-500 hover:text-red-600 hover:bg-red-50 font-medium">
              <LogOut className="w-4 h-4 mr-2" />
              <span>{t('auth.logout') || 'Logout'}</span>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarFooter>
    </Sidebar>
  )
}
