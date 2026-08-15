import api from './axios'
import {
  AdminVerification,
  VerificationAuthority,
  AssignVerificationPayload
} from '@/types/admin'
import { ApiResponse } from '@/types/api'

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

  assignVerificationAuthority: (id: string, payload: AssignVerificationPayload) => 
    api.post<ApiResponse<{ verification: AdminVerification }>>(`/admin/verifications/${id}/assign`, payload),
}
