import api from './axios'

export interface PublicVerificationTimelineItem {
  type: string
  label: string
  date: string
  status: string
}

export interface PublicVerificationResponse {
  verified: boolean
  status?: string
  message?: string
  product?: {
    herb: string
    botanicalName: string
    batchNumber: string
    harvestDate: string
    cultivationMethod: string
  }
  producer?: {
    name: string
    village: string
    district: string
    state: string
  }
  governmentVerification?: {
    status: string
  }
  lotInspection?: {
    status: string
    inspectionDate: string | null
    inspectedQuantity: number
  }
  laboratory?: {
    status: string
    reportNumber: string
    testingCompletedAt: string | null
  }
  blockchain?: {
    status: string
    integrityVerified: boolean
    details?: {
      producerVerificationTx?: string
      batchInspectionTx?: string
      qualityTestTx?: string
      labReportTx?: string
      network?: string
    }
  }
  timeline?: PublicVerificationTimelineItem[]
  supplyChain?: {
    currentStatus: string
    events: {
      type: string
      date: string
      status: string
    }[]
  }
}

export const publicApi = {
  verifyQR: async (code: string): Promise<PublicVerificationResponse> => {
    const { data } = await api.get<{ success: boolean, message: string, data: PublicVerificationResponse }>(`/public/verify/${code}`)
    return data.data
  }
}
