import api from './axios'

export interface BlockchainVerificationResponse {
  verified: boolean
  message: string
  data?: {
    entityType: string
    entityId: string
    currentHash: string
    blockchainHash: string
    verified: boolean
    transactionId?: string
    network?: string
  }
}

export interface BlockchainRecord {
  id: string
  entityType: string
  entityId: string
  recordVersion: number
  dataHash: string
  status: 'PENDING' | 'SUBMITTED' | 'CONFIRMED' | 'FAILED'
  transactionId?: string
  network?: string
  channel?: string
  chaincode?: string
  anchoredAt?: string
  createdAt: string
  updatedAt: string
}

export const blockchainApi = {
  anchorRecord: async (entityType: string, entityId: string): Promise<{ message: string, status: string }> => {
    const { data } = await api.post(`/blockchain/anchor/${entityType}/${entityId}`)
    return data.data
  },

  verifyRecord: async (entityType: string, entityId: string): Promise<BlockchainVerificationResponse> => {
    const { data } = await api.get(`/blockchain/verify/${entityType}/${entityId}`)
    return data.data
  },

  getHistory: async (entityType: string, entityId: string): Promise<{ records: BlockchainRecord[] }> => {
    const { data } = await api.get(`/blockchain/history/${entityType}/${entityId}`)
    return data.data
  }
}
