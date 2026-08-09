import { ProducerSidebar } from './_components/ProducerSidebar'
import { TopNavbar } from '@/components/layouts/TopNavbar'
import { SidebarProvider, SidebarInset } from '@/components/ui/sidebar'
import './producer-theme.css'

export default function ProducerLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="producer-theme">
      <SidebarProvider>
        <ProducerSidebar />
        <SidebarInset>
          <TopNavbar />
          <main className="p-6">{children}</main>
        </SidebarInset>
      </SidebarProvider>
    </div>
  )
}