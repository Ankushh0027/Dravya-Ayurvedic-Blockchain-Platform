import api from './axios'
import {
  AdminVerification,
  VerificationAuthority,
  AssignVerificationPayload,
  AdminLotInspection,
  AssignLabTestPayload,
  GeneratedQRCode,
  Laboratory,
  PendingLabAssignment,
} from '@/types/admin'
import { ApiResponse } from '@/types/api'
import { Batch } from '@/types/batch'

const QR_COMPATIBLE_BATCH_STATUSES = ['QUALITY_APPROVED', 'IN_TRANSIT', 'DELIVERED'] as const

interface BatchPagination {
  page: number
  limit: number
  total: number
  totalPages: number
}

interface BatchListResponse {
  batches: Batch[]
  pagination: BatchPagination
}

async function getBatchesForStatus(status: typeof QR_COMPATIBLE_BATCH_STATUSES[number]): Promise<Batch[]> {
  const batches: Batch[] = []
  let page = 1
  let totalPages = 1

  while (page <= totalPages) {
    const response = await api.get<ApiResponse<BatchListResponse>>('/batches', {
      params: { status, page, limit: 50 },
    })
    const data = response.data.data
    if (!data) {
      throw new Error('The server did not return batch data.')
    }
    batches.push(...data.batches)
    totalPages = data.pagination.totalPages
    page += 1
  }

  return batches
}

export const adminApi = {
  // Verifications
  getPendingVerifications: async () => {
    const response = await api.get<ApiResponse<{ verifications: AdminVerification[] }>>('/admin/verifications')
    return response.data.data as { verifications: AdminVerification[] }
  },

  getVerificationAuthorities: async () => {
    const response = await api.get<ApiResponse<{ authorities: VerificationAuthority[] }>>('/admin/authorities')
    return response.data.data as { authorities: VerificationAuthority[] }
  },

  getPendingLotInspections: async (): Promise<{ inspections: AdminLotInspection[] }> => {
    const response = await api.get<ApiResponse<{ inspections: AdminLotInspection[] }>>('/admin/inspections')
    return response.data.data ?? { inspections: [] }
  },

  getPendingLabAssignments: async (): Promise<{ batches: PendingLabAssignment[] }> => {
    const response = await api.get<ApiResponse<{ batches: PendingLabAssignment[] }>>('/admin/lab-tests')
    return response.data.data ?? { batches: [] }
  },

  getLaboratories: async (): Promise<{ laboratories: Laboratory[] }> => {
    const response = await api.get<ApiResponse<{ laboratories: Laboratory[] }>>('/admin/labs')
    return response.data.data ?? { laboratories: [] }
  },

  getQRCompatibleBatches: async (): Promise<Batch[]> => {
    const groupedBatches = await Promise.all(
      QR_COMPATIBLE_BATCH_STATUSES.map(getBatchesForStatus),
    )
    return Array.from(
      new Map(groupedBatches.flat().map(batch => [batch.id, batch])).values(),
    )
  },

  assignVerificationAuthority: (id: string, payload: AssignVerificationPayload) => 
    api.post<ApiResponse<{ verification: AdminVerification }>>(`/admin/verifications/${id}/assign`, payload),

  assignLotInspection: (id: string, payload: AssignVerificationPayload) =>
    api.post<ApiResponse<{ inspection: AdminLotInspection }>>(`/admin/inspections/${id}/assign`, payload),

  assignLabTest: async (batchId: string, payload: AssignLabTestPayload): Promise<void> => {
    await api.post<ApiResponse>(`/admin/batches/${batchId}/assign-lab-test`, payload)
  },

  generateQRCode: async (batchId: string): Promise<GeneratedQRCode> => {
    const response = await api.post<ApiResponse<GeneratedQRCode>>(`/admin/batches/${batchId}/qr`)
    if (!response.data.data) {
      throw new Error(response.data.message || 'The server did not return QR code details.')
    }
    return response.data.data
  },
}
