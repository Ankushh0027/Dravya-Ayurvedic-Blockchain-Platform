export type LabTestStatus =
  | 'PENDING_ASSIGNMENT'
  | 'ASSIGNED'
  | 'SAMPLE_RECEIVED'
  | 'UNDER_TESTING'
  | 'COMPLETED'

export type QualityResult = 'PASS' | 'FAIL'
export type ParameterResultStatus = 'PASS' | 'FAIL' | 'NOT_APPLICABLE'

export interface TestResult {
  id: string
  qualityTestId: string
  parameter: string
  value: number | null
  unit: string | null
  referenceRange: string | null
  resultStatus: ParameterResultStatus
  remarks: string | null
  createdAt: string
  updatedAt: string
}

export type ReportStatus = 'DRAFT' | 'FINALIZED'

export interface LabReport {
  id: string
  qualityTestId: string
  generatedBy: string
  reportNumber: string
  reportUrl: string
  reportFileName: string
  reportFileType: string
  status: ReportStatus
  finalizedAt: string | null
  createdAt: string
  updatedAt: string
}

export interface Herb {
  id: string
  commonName: string
  scientificName: string
}

export interface ProducerProfile {
  id: string
  farmName: string
  userId: string
}

export interface Batch {
  id: string
  batchNumber: string
  status: string
  quantity: number
  herb: Herb
  producerProfile?: ProducerProfile
  producerId?: string
  harvestDate?: string
  cultivationMethod?: string
}

export interface QualityTest {
  id: string
  batchId: string
  labId: string
  sampleId: string | null
  status: LabTestStatus
  overallResult: QualityResult | null
  assignedAt: string
  receivedAt: string | null
  testingStartedAt: string | null
  testingCompletedAt: string | null
  createdAt: string
  updatedAt: string
  batch: Batch
  results?: TestResult[]
  reports?: LabReport[]
}

export interface LabDashboardStats {
  dashboard: {
    assignedTests: number
    samplesReceived: number
    underTesting: number
    completedTests: number
    passedTests: number
    failedTests: number
  }
  recentAssigned: QualityTest[]
}
