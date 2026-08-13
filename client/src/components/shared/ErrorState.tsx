import React from 'react'
import { AlertCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'

export function ErrorState({ message = 'An error occurred', onRetry }: { message?: string, onRetry?: () => void }) {
  return (
    <div className="flex flex-col items-center justify-center p-8 h-full min-h-[200px] text-destructive">
      <AlertCircle className="w-8 h-8 mb-4" />
      <p className="mb-4">{message}</p>
      {onRetry && (
        <Button variant="outline" onClick={onRetry}>
          Try Again
        </Button>
      )}
    </div>
  )
}
