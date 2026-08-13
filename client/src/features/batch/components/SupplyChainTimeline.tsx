import React from 'react'
import { SupplyChainEvent } from '@/types/batch'
import { CheckCircle2, Circle } from 'lucide-react'

interface SupplyChainTimelineProps {
  events: SupplyChainEvent[]
}

export function SupplyChainTimeline({ events }: SupplyChainTimelineProps) {
  if (!events || events.length === 0) {
    return (
      <div className="py-8 text-center text-muted-foreground border rounded-lg bg-muted/10">
        No supply chain events recorded yet.
      </div>
    )
  }

  return (
    <div className="relative border-l-2 border-muted ml-3 space-y-8 py-4">
      {events.map((event, index) => (
        <div key={index} className="relative pl-6">
          {event.status === 'COMPLETED' ? (
            <CheckCircle2 className="absolute -left-[17px] top-0.5 w-8 h-8 text-green-500 bg-background rounded-full" />
          ) : (
            <Circle className="absolute -left-[13px] top-1.5 w-6 h-6 text-muted-foreground bg-background rounded-full" />
          )}
          
          <div className="mb-1">
            <h4 className="text-lg font-semibold capitalize">{event.type.replace(/_/g, ' ').toLowerCase()}</h4>
            <span className="text-sm text-muted-foreground">
              {new Date(event.timestamp).toLocaleString()}
            </span>
          </div>
          
          <div className="text-sm">
            {event.location && <p><strong>Location:</strong> {event.location}</p>}
            {event.quantity && event.unit && (
              <p><strong>Quantity:</strong> {event.quantity} {event.unit}</p>
            )}
          </div>
        </div>
      ))}
    </div>
  )
}
