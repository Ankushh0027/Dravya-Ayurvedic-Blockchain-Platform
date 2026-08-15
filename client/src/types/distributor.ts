import { BatchStatus } from './batch'

export type AssignmentStatus =
  | 'ASSIGNED'
  | 'ACCEPTED'
  | 'COMPLETED'
  | 'CANCELLED'

export interface DistributorAssignment {
  id: string
  batchId: string
  distributorId: string
  assignedBy: string
  assignedAt: string
  status: AssignmentStatus
  acceptedAt: string | null
  completedAt: string | null
  createdAt: string
  updatedAt: string
  batch?: DistributorBatch
}

export interface DistributorBatch {
  id: string
  batchNumber: string
  herbId: string
  producerProfileId: string
  farmLocation: string
  latitude: number | null
  longitude: number | null
  quantity: number
  unit: string
  harvestDate: string
  cultivationMethod: string
  harvestDetails: string | null
  status: BatchStatus
  createdAt: string
  updatedAt: string
  herb?: {
    id: string
    commonName: string
    botanicalName: string
    localName: string | null
  }
  distributorAssignments?: DistributorAssignment[]
  supplyChainEvents?: SupplyChainEvent[]
  producerProfile?: {
    userId: string
    farmName: string
  }
}

export interface SupplyChainEvent {
  id: string
  batchId: string
  actorId: string
  action: string // e.g. BATCH_RECEIVED, BATCH_DISPATCHED, BATCH_DELIVERED
  quantity: number | null
  unit: string | null
  location: string | null
  latitude: number | null
  longitude: number | null
  referenceNumber: string | null
  notes: string | null
  timestamp: string
}

export interface DistributorDashboardStats {
  assigned: number
  awaitingAcceptance: number
  accepted: number
  inTransit: number
  delivered: number
}

export interface DistributorDashboardResponse {
  success: boolean
  message: string
  data: DistributorDashboardStats
}

export interface DistributorBatchesResponse {
  success: boolean
  message: string
  data: {
    assignments: DistributorAssignment[]
  }
}

export interface ReceiveBatchPayload {
  quantity: number
  unit?: string
  location?: string
  latitude?: number
  longitude?: number
  referenceNumber?: string
  notes?: string
}

export interface DispatchBatchPayload {
  quantity: number
  unit?: string
  destination?: string
  latitude?: number
  longitude?: number
  referenceNumber?: string
  notes?: string
}

export interface DeliverBatchPayload {
  quantity: number
  unit?: string
  destination?: string
  latitude?: number
  longitude?: number
  referenceNumber?: string
  notes?: string
}
