import api from './axios'
import {
  DashboardResponse,
  ProducerVerification,
  BatchInspection,
  ApproveVerificationPayload,
  RejectVerificationPayload,
  RecordInspectionPayload,
  RejectInspectionPayload,
} from '@/types/authority'
import { ApiResponse } from '@/types/api'

export const authorityApi = {
  // Dashboard
  getDashboard: () => 
    api.get<ApiResponse<DashboardResponse>>('/authority/dashboard'),

  // Producer Verifications
  getAssignedVerifications: () => 
    api.get<ApiResponse<{ verifications: ProducerVerification[] }>>('/authority/producer-verifications'),

  getVerificationDetails: (id: string) => 
    api.get<ApiResponse<{ verification: ProducerVerification }>>(`/authority/producer-verifications/${id}`),

  approveVerification: (id: string, payload: ApproveVerificationPayload) => 
    api.post<ApiResponse<{ verification: ProducerVerification }>>(`/authority/producer-verifications/${id}/approve`, payload),

  rejectVerification: (id: string, payload: RejectVerificationPayload) => 
    api.post<ApiResponse<{ verification: ProducerVerification }>>(`/authority/producer-verifications/${id}/reject`, payload),

  // Lot Inspections
  getAssignedInspections: () => 
    api.get<ApiResponse<{ inspections: BatchInspection[] }>>('/authority/lot-inspections'),

  getInspectionDetails: (id: string) => 
    api.get<ApiResponse<{ inspection: BatchInspection }>>(`/authority/lot-inspections/${id}`),

  startInspection: (id: string) => 
    api.post<ApiResponse<{ inspection: BatchInspection }>>(`/authority/lot-inspections/${id}/start`),

  approveLotInspection: (id: string, payload: RecordInspectionPayload) => 
    api.post<ApiResponse<{ inspection: BatchInspection }>>(`/authority/lot-inspections/${id}/approve`, payload),

  rejectLotInspection: (id: string, payload: RejectInspectionPayload) => 
    api.post<ApiResponse<{ inspection: BatchInspection }>>(`/authority/lot-inspections/${id}/reject`, payload),
}
