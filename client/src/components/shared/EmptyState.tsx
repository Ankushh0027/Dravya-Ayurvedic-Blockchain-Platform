import React from 'react'
import { Card } from '@/components/ui/card'

interface EmptyStateProps {
  icon: React.ReactNode
  title: string
  description: string
  action?: React.ReactNode
}

export function EmptyState({ icon, title, description, action }: EmptyStateProps) {
  return (
    <Card className="bg-white/70 backdrop-blur-xl border border-white/60 shadow-[0_8px_40px_rgb(0,0,0,0.04)] rounded-[24px] p-12 flex flex-col items-center justify-center text-center">
      <div className="w-20 h-20 rounded-full bg-slate-50 flex items-center justify-center mb-6">
        {icon}
      </div>
      <h3 className="text-xl font-bold text-[#1e293b] mb-2">{title}</h3>
      <p className="text-slate-500 font-medium max-w-md mb-6">{description}</p>
      {action}
    </Card>
  )
}
