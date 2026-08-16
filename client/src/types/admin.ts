export type AdminVerificationStatus = 'PENDING' | 'ASSIGNED' | 'UNDER_REVIEW' | 'COMPLETED'

export interface VerificationAuthority {
  id: string
  name: string
  email: string
  organization: string | null
}

export interface AdminVerification {
  id: string
  producerProfileId: string
  authorityId: string | null
  assignedBy: string | null
  assignedAt: string | null
  status: AdminVerificationStatus
  decision: string | null
  verificationType: string
  createdAt: string
  updatedAt: string
  producerProfile: {
    id: string
    farmName: string
    address: string
    village: string
    tehsil: string
    district: string
    state: string
    pincode: string
    landSize: number
    landSizeUnit: string
    user: {
      name: string
      email: string
    }
  }
  authority: VerificationAuthority | null
}

export interface AssignVerificationPayload {
  authorityId: string
}
