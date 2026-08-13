import { ProducerProfile } from './producer'
import { Batch } from './batch'

export type RequestStatus = 'PENDING' | 'ASSIGNED' | 'UNDER_REVIEW' | 'COMPLETED'
export type VerificationDecision = 'APPROVED' | 'REJECTED'
export type InspectionStatus = 'PENDING' | 'UNDER_INSPECTION' | 'APPROVED' | 'REJECTED'

export interface AuthorityDashboardStats {
  pendingProducerVerifications: number
  pendingLotInspections: number
  approvedProducers: number
  rejectedProducers: number
  inspectionsThisMonth: number
}

export interface DashboardResponse {
  dashboard: AuthorityDashboardStats
}

export interface VerificationUser {
  name: string
  email: string
  phone: string | null
}

export interface VerificationDocument {
  id: string
  producerProfileId: string
  type: string
  fileUrl: string
  fileName: string
  fileType: string
  uploadedBy: string
  createdAt: string
}

export interface ProducerVerificationProfile extends ProducerProfile {
  user: VerificationUser
  verificationDocuments?: VerificationDocument[]
}

export interface ProducerVerification {
  id: string
  producerProfileId: string
  authorityId: string | null
  assignedBy: string | null
  assignedAt: string | null
  status: RequestStatus
  decision: VerificationDecision | null
  verificationType: string
  identityVerified: boolean | null
  documentsVerified: boolean | null
  landVerified: boolean | null
  locationVerified: boolean | null
  cultivationVerified: boolean | null
  inspectionDate: string | null
  latitude: number | null
  longitude: number | null
  observations: string | null
  rejectionReason: string | null
  createdAt: string
  updatedAt: string
  producerProfile?: ProducerVerificationProfile
}

export interface BatchInspection {
  id: string
  batchId: string
  authorityId: string | null
  assignedBy: string | null
  assignedAt: string | null
  status: InspectionStatus
  decision: VerificationDecision | null
  declaredQuantity: number
  inspectedQuantity: number | null
  herbIdentityVerified: boolean | null
  physicalQualityStatus: string | null
  packagingStatus: string | null
  documentsVerified: boolean | null
  inspectionDate: string | null
  latitude: number | null
  longitude: number | null
  observations: string | null
  rejectionReason: string | null
  createdAt: string
  updatedAt: string
  batch?: Batch & {
    herb?: {
      commonName: string
      botanicalName: string
    }
    producerProfile?: {
      farmName: string
      user?: VerificationUser
    }
  }
}

export interface ApproveVerificationPayload {
  identityVerified: boolean
  documentsVerified: boolean
  landVerified: boolean
  locationVerified: boolean
  cultivationVerified: boolean
  inspectionDate: Date | string
  latitude: number
  longitude: number
  observations?: string
}

export interface RejectVerificationPayload {
  rejectionReason: string
}

export interface RecordInspectionPayload {
  inspectedQuantity: number
  herbIdentityVerified: boolean
  physicalQualityStatus: string
  packagingStatus: string
  documentsVerified: boolean
  inspectionDate: Date | string
  latitude: number
  longitude: number
  observations?: string
}

export interface RejectInspectionPayload {
  rejectionReason: string
}
