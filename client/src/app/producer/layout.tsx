import React from 'react'
import { ProducerNavbar } from '@/components/layouts/ProducerNavbar'

export default function ProducerLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col relative font-sans overflow-x-hidden">
      {/* Background Watermark / Glows to match landing page */}
      <div className="fixed inset-0 z-0 pointer-events-none">
        {/* Subtle Watermark */}
        <div
          className="absolute inset-0 opacity-[0.03] mix-blend-multiply flex items-center justify-center"
          style={{
            backgroundImage: 'url("/logo.png")',
            backgroundSize: '800px',
            backgroundPosition: 'center center',
            backgroundRepeat: 'no-repeat',
          }}
        />
        {/* Glows */}
        <div className="absolute top-0 right-0 w-[600px] h-[600px] bg-[#184E48]/5 rounded-full blur-[100px]" />
        <div className="absolute bottom-0 left-0 w-[600px] h-[600px] bg-[#184E48]/5 rounded-full blur-[100px]" />
      </div>

      <ProducerNavbar />
      
      <main className="flex-1 relative z-10 w-full">
        {children}
      </main>
    </div>
  )
}
