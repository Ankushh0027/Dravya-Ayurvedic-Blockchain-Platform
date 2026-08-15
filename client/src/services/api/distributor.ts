import api from './axios'
import {
  DistributorDashboardResponse,
  DistributorBatchesResponse,
  ReceiveBatchPayload,
  DispatchBatchPayload,
  DeliverBatchPayload,
  SupplyChainEvent
} from '@/types/distributor'

export const distributorApi = {
  getDashboard: async (): Promise<DistributorDashboardResponse['data']> => {
    const { data } = await api.get<DistributorDashboardResponse>('/distributors/me/dashboard')
    return data.data
  },

  getAssignedBatches: async (): Promise<DistributorBatchesResponse['data']> => {
    const { data } = await api.get<DistributorBatchesResponse>('/distributors/me/batches')
    return data.data
  },

  receiveBatch: async (id: string, payload: ReceiveBatchPayload): Promise<{ event: SupplyChainEvent }> => {
    const { data } = await api.post(`/distributors/me/batches/${id}/receive`, payload)
    return data.data
  },

  dispatchBatch: async (id: string, payload: DispatchBatchPayload): Promise<{ event: SupplyChainEvent }> => {
    const { data } = await api.post(`/distributors/me/batches/${id}/dispatch`, payload)
    return data.data
  },

  deliverBatch: async (id: string, payload: DeliverBatchPayload): Promise<{ event: SupplyChainEvent }> => {
    const { data } = await api.post(`/distributors/me/batches/${id}/deliver`, payload)
    return data.data
  }
}
