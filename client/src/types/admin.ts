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

export interface Laboratory {
  id: string
  name: string
  email: string
  organization: string | null
}

export interface PendingLabAssignment {
  id: string
  batchNumber: string
  quantity: number
  unit: string
  status: 'READY_FOR_LAB'
  updatedAt: string
  herb: {
    commonName: string
  }
  producerProfile: {
    farmName: string
  }
}

export interface AssignLabTestPayload {
  labId: string
}

export interface GeneratedQRCode {
  code: string
  verificationUrl: string
}

export interface AdminLotInspection {
  id: string
  batchId: string
  authorityId: string | null
  assignedBy: string | null
  assignedAt: string | null
  status: 'PENDING' | 'UNDER_INSPECTION' | 'APPROVED' | 'REJECTED'
  declaredQuantity: number
  createdAt: string
  authority: VerificationAuthority | null
  batch: {
    batchNumber: string
    quantity: number
    unit: string
    herb: {
      commonName: string
    }
    producerProfile: {
      farmName: string
    }
  }
}
