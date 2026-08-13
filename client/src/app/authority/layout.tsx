'use client'

import { AuthorityNavbar } from '@/components/layouts/AuthorityNavbar'

export default function AuthorityLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <AuthorityNavbar />
      
      {/* Main Content Area */}
      <main className="flex-1 w-full relative z-10 overflow-x-hidden">
        {/* Decorative background matching producer */}
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px] -z-10" />
        <div className="absolute left-0 right-0 top-0 -z-10 m-auto h-[310px] w-[310px] rounded-full bg-[#184E48] opacity-[0.03] blur-[100px]" />
        
        {children}
      </main>
    </div>
  )
}
