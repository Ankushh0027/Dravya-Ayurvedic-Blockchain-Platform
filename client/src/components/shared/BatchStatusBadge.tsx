import React from 'react'
import { Badge } from '@/components/ui/badge'
import { BatchStatus } from '@/types/batch'

interface BatchStatusBadgeProps {
  status: BatchStatus
}

export function BatchStatusBadge({ status }: BatchStatusBadgeProps) {
  const getConfig = () => {
    switch (status) {
      case 'DRAFT':
        return { label: 'Draft', variant: 'secondary' as const, className: 'bg-gray-100 text-gray-800 hover:bg-gray-200' }
      case 'SUBMITTED':
      case 'PENDING_VERIFICATION':
        return { label: 'Pending Verification', variant: 'outline' as const, className: 'bg-yellow-100 text-yellow-800 border-yellow-200 hover:bg-yellow-200' }
      case 'VERIFIED':
        return { label: 'Verified', variant: 'default' as const, className: 'bg-blue-100 text-blue-800 border-blue-200 hover:bg-blue-200' }
      case 'REJECTED':
      case 'QUALITY_REJECTED':
        return { label: 'Rejected', variant: 'destructive' as const, className: '' }
      case 'READY_FOR_LAB':
        return { label: 'Ready for Lab', variant: 'default' as const, className: 'bg-indigo-100 text-indigo-800 hover:bg-indigo-200' }
      case 'QUALITY_APPROVED':
        return { label: 'Quality Approved', variant: 'default' as const, className: 'bg-green-100 text-green-800 hover:bg-green-200' }
      case 'IN_TRANSIT':
        return { label: 'In Transit', variant: 'default' as const, className: 'bg-purple-100 text-purple-800 hover:bg-purple-200' }
      case 'DELIVERED':
        return { label: 'Delivered', variant: 'default' as const, className: 'bg-emerald-100 text-emerald-800 hover:bg-emerald-200' }
      default:
        return { label: status, variant: 'outline' as const, className: '' }
    }
  }

  const config = getConfig()

  return (
    <Badge variant={config.variant} className={config.className}>
      {config.label}
    </Badge>
  )
}
