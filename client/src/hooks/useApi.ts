import { useState, useCallback } from 'react'

export interface UseApiResult<T> {
  data: T | null
  error: string | null
  isLoading: boolean
  execute: (...args: any[]) => Promise<T | null>
  reset: () => void
}

/**
 * A generic hook to handle API loading states and errors manually.
 * Note: Use this mostly for mutations, or simple client-side fetches.
 */
export function useApi<T, P extends any[] = any[]>(
  apiFunc: (...args: P) => Promise<T>,
  initialData: T | null = null
): UseApiResult<T> {
  const [data, setData] = useState<T | null>(initialData)
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState<boolean>(false)

  const execute = useCallback(
    async (...args: P): Promise<T | null> => {
      setIsLoading(true)
      setError(null)
      try {
        const result = await apiFunc(...args)
        setData(result)
        return result
      } catch (err: any) {
        const message = err?.response?.data?.message || err?.message || 'An unexpected error occurred'
        setError(message)
        return null
      } finally {
        setIsLoading(false)
      }
    },
    [apiFunc]
  )

  const reset = useCallback(() => {
    setData(initialData)
    setError(null)
    setIsLoading(false)
  }, [initialData])

  return {
    data,
    error,
    isLoading,
    execute,
    reset,
  }
}
