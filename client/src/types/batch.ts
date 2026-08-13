export type BatchStatus = 
  | 'DRAFT' 
  | 'SUBMITTED' 
  | 'PENDING_VERIFICATION' 
  | 'VERIFIED' 
  | 'REJECTED' 
  | 'READY_FOR_LAB' 
  | 'QUALITY_APPROVED' 
  | 'QUALITY_REJECTED' 
  | 'IN_TRANSIT' 
  | 'DELIVERED'

export interface Batch {
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
    commonName: string
    botanicalName: string
  }
  producerProfile?: {
    farmName: string
    verificationStatus?: string
  }
}

export interface SupplyChainEvent {
  type: string
  timestamp: string
  quantity: number | null
  unit: string | null
  location: string | null
  status: string
}

export interface BatchTimelineResponse {
  batchNumber: string
  currentStatus: BatchStatus
  events: SupplyChainEvent[]
}

export interface CreateBatchPayload {
  herbId: string
  farmLocation: string
  quantity: number
  unit?: string
  harvestDate: string
  cultivationMethod: string
  harvestDetails?: string
  latitude?: number
  longitude?: number
}
