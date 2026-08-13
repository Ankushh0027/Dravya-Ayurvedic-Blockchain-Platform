export type VerificationStatus = 'PENDING' | 'UNDER_REVIEW' | 'VERIFIED' | 'REJECTED'

export interface ProducerProfile {
  id: string
  farmName: string
  address: string
  village: string
  tehsil: string
  district: string
  state: string
  pincode: string
  latitude: number | null
  longitude: number | null
  landSize: number
  landSizeUnit: string
  verificationStatus: VerificationStatus
  createdAt: string
  updatedAt: string
}

export interface ProducerDashboardStats {
  dashboard: {
    totalBatches: number
    draftBatches: number
    pendingVerification: number
    verifiedBatches: number
    rejectedBatches: number
  }
  recentBatches: any[] // We'll type this fully when we add the Batch type
}
