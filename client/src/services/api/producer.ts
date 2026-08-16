import api from './axios'
import { ApiResponse } from '@/types/api'
import { ProducerProfile, ProducerDashboardStats, VerificationStatus } from '@/types/producer'

export const ProducerService = {
  async getProfile(): Promise<ProducerProfile> {
    const response = await api.get<ApiResponse<{ profile: ProducerProfile }>>('/producers/me')
    return response.data.data!.profile
  },

  async updateProfile(data: Partial<ProducerProfile>): Promise<ProducerProfile> {
    const response = await api.patch<ApiResponse<{ profile: ProducerProfile }>>('/producers/me', data)
    return response.data.data!.profile
  },

  async getVerificationStatus(): Promise<{ status: VerificationStatus }> {
    const response = await api.get<ApiResponse<{ status: VerificationStatus }>>('/producers/me/verification')
    return response.data.data!
  },

  async requestVerification(): Promise<{ status: string }> {
    const response = await api.post<ApiResponse<{ status: string }>>('/producers/me/verification/request')
    return response.data.data!
  },

  async getVerificationHistory(): Promise<any[]> {
    const response = await api.get<ApiResponse<{ history: any[] }>>('/producers/me/verification/history')
    return response.data.data!.history
  },

  async getDashboard(): Promise<ProducerDashboardStats> {
    const response = await api.get<ApiResponse<ProducerDashboardStats>>('/producers/me/dashboard')
    return response.data.data!
  },
}
