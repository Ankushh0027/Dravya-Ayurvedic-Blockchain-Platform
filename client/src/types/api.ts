export interface ApiResponse<T = any> {
  success: boolean
  message: string
  data?: T
  errors?: any
}

export interface PaginatedData<T> {
  [key: string]: any // To accommodate dynamic keys like 'batches': T[]
  pagination?: {
    page: number
    limit: number
    total: number
    totalPages: number
  }
}
