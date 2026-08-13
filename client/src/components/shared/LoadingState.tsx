import React from 'react'
import { Loader2 } from 'lucide-react'

export function LoadingState({ message = 'Loading...' }: { message?: string }) {
  return (
    <div className="flex flex-col items-center justify-center p-8 h-full min-h-[200px] text-muted-foreground">
      <Loader2 className="w-8 h-8 animate-spin mb-4" />
      <p>{message}</p>
    </div>
  )
}
