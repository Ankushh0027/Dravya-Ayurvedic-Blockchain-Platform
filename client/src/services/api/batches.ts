import api from './axios'
import { ApiResponse, PaginatedData } from '@/types/api'
import { Batch, BatchTimelineResponse, CreateBatchPayload, LotInspectionRequest } from '@/types/batch'

interface BatchPagination {
  page: number
  limit: number
  total: number
  totalPages: number
}

export const BatchService = {
  async getBatches(params?: { page?: number; limit?: number; status?: string }): Promise<{ batches: Batch[]; pagination: BatchPagination | undefined }> {
    const response = await api.get<ApiResponse<PaginatedData<Batch>>>('/batches', { params })
    return {
      batches: response.data.data!.batches || [],
      pagination: response.data.data!.pagination,
    }
  },

  async getBatchById(id: string): Promise<Batch> {
    const response = await api.get<ApiResponse<{ batch: Batch }>>(`/batches/${id}`)
    return response.data.data!.batch
  },

  async getBatchSupplyChain(id: string): Promise<BatchTimelineResponse> {
    const response = await api.get<ApiResponse<BatchTimelineResponse>>(`/batches/${id}/supply-chain`)
    return response.data.data!
  },

  async createBatch(data: CreateBatchPayload): Promise<Batch> {
    const response = await api.post<ApiResponse<{ batch: Batch }>>('/batches', data)
    return response.data.data!.batch
  },

  async updateBatch(id: string, data: Partial<CreateBatchPayload>): Promise<Batch> {
    const response = await api.patch<ApiResponse<{ batch: Batch }>>(`/batches/${id}`, data)
    return response.data.data!.batch
  },

  async submitBatch(id: string): Promise<Batch> {
    const response = await api.post<ApiResponse<{ batch: Batch }>>(`/batches/${id}/submit`)
    return response.data.data!.batch
  },

  async requestInspection(id: string): Promise<LotInspectionRequest> {
    const response = await api.post<ApiResponse<{ inspection: LotInspectionRequest }>>(`/batches/${id}/inspection/request`)
    return response.data.data!.inspection
  },
}
