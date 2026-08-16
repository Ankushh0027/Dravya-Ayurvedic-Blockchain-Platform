import api from './axios'
import { LabDashboardStats, QualityTest, TestResult, LabReport } from '@/types/lab'

export const labApi = {
  getDashboard: async (): Promise<LabDashboardStats> => {
    const response = await api.get('/lab/dashboard')
    return response.data.data
  },

  getAssignedTests: async (): Promise<QualityTest[]> => {
    const response = await api.get('/lab/tests')
    return response.data.data.tests
  },

  getTestDetails: async (id: string): Promise<QualityTest> => {
    const response = await api.get(`/lab/tests/${id}`)
    return response.data.data.test
  },

  receiveSample: async (id: string): Promise<QualityTest> => {
    const response = await api.post(`/lab/tests/${id}/receive`)
    return response.data.data.test
  },

  startTest: async (id: string): Promise<QualityTest> => {
    const response = await api.post(`/lab/tests/${id}/start`)
    return response.data.data.test
  },

  addTestResult: async (id: string, payload: any): Promise<TestResult> => {
    const response = await api.post(`/lab/tests/${id}/results`, payload)
    return response.data.data.testResult
  },

  completeTest: async (id: string): Promise<QualityTest> => {
    const response = await api.post(`/lab/tests/${id}/complete`)
    return response.data.data.test
  },

  generateReport: async (id: string, payload: any): Promise<LabReport> => {
    const response = await api.post(`/lab/tests/${id}/report`, payload)
    return response.data.data.report
  },

  finalizeReport: async (id: string): Promise<LabReport> => {
    const response = await api.post(`/lab/reports/${id}/finalize`)
    return response.data.data.report
  }
}
