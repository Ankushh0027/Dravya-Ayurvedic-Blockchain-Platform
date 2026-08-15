import api from './axios'
import {
  AdminVerification,
  VerificationAuthority,
  AssignVerificationPayload
} from '@/types/admin'
import { ApiResponse } from '@/types/api'

export const adminApi = {
  // Verifications
  getPendingVerifications: () => 
    api.get<ApiResponse<{ verifications: AdminVerification[] }>>('/admin/verifications'),

  getVerificationAuthorities: () => 
    api.get<ApiResponse<{ authorities: VerificationAuthority[] }>>('/admin/authorities'),

  assignVerificationAuthority: (id: string, payload: AssignVerificationPayload) => 
    api.post<ApiResponse<{ verification: AdminVerification }>>(`/admin/verifications/${id}/assign`, payload),
}
