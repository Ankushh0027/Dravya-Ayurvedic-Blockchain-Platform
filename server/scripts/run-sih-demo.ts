import { PrismaClient } from '@prisma/client'
import crypto from 'crypto'

const prisma = new PrismaClient()
const API_URL = 'http://localhost:8000/api'

// Helper for colored console output
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  cyan: '\x1b[36m',
  red: '\x1b[31m',
  magenta: '\x1b[35m',
}

function log(step: string, message: string, color: string = colors.cyan) {
  console.log(`${color}${colors.bright}[${step}]${colors.reset} ${message}`)
}

// Simple fetch wrapper that includes auth token
async function apiCall(method: string, endpoint: string, body?: any, token?: string): Promise<any> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  }
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const response = await fetch(`${API_URL}${endpoint}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  })

  const data = await response.json()
  if (!response.ok) {
    throw new Error(`API Error: ${response.status} ${response.statusText} - ${JSON.stringify(data)}`)
  }
  return data
}

async function login(email: string, pass: string): Promise<string> {
  const data = await apiCall('POST', '/auth/login', { email, password: pass })
  return data.data.token
}

async function runDemo() {
  console.log(`\n${colors.magenta}${colors.bright}==========================================`)
  console.log(`🌿 DRAVYA END-TO-END SIH DEMO EXECUTION 🌿`)
  console.log(`==========================================${colors.reset}\n`)

  try {
    // 1. Initial Logins
    log('1', 'Logging in as all required roles...')
    const adminToken = await login('admin@dravya.in', 'Admin@1234')
    const producerToken = await login('producer@dravya.in', 'Prod@1234')
    const vaToken = await login('verifier@dravya.in', 'Verify@1234')
    const labToken = await login('lab@dravya.in', 'Lab@1234')
    const distToken = await login('distributor@dravya.in', 'Dist@1234')
    log('1', 'All logins successful!', colors.green)

    // 2. Producer Profile Setup (Simulated if already setup)
    log('2', 'Producer submits farm profile...')
    let profileReq;
    let profileId;
    try {
      profileReq = await apiCall('GET', '/producers/me', undefined, producerToken)
      profileId = profileReq.data?.profile?.id
    } catch (e: any) {
      // Profile not found, we will create it below
    }
    if (!profileId) {
      const res = await apiCall('PATCH', '/producers/me', {
        farmName: 'Green Valley Farms',
        address: 'Kharadi',
        village: 'Kharadi',
        tehsil: 'Haveli',
        district: 'Pune',
        state: 'Maharashtra',
        pincode: '411014',
        landSize: 5.5,
        latitude: 18.5204,
        longitude: 73.8567,
      }, producerToken)
      profileId = res.data.profile.id
    }
    
    // Check if verification request exists
    const statusReq = await apiCall('GET', '/producers/me/verification', undefined, producerToken)
      let verificationId = statusReq.data.verification?.id
    if (!verificationId) {
       const reqRes = await apiCall('POST', '/producers/me/verification/request', undefined, producerToken)
       verificationId = reqRes.data.verification.id
    }
    log('2', `Producer profile ready (ID: ${profileId}, VerReq: ${verificationId})`, colors.green)

    // 3. Admin Assigns VA
    log('3', 'Admin assigns Verification Authority to Producer...')
    await apiCall('POST', `/admin/verifications/${verificationId}/assign`, {
      authorityId: (await prisma.user.findUnique({ where: { email: 'verifier@dravya.in' } }))?.id
    }, adminToken)
    log('3', 'Authority assigned.', colors.green)

    // 4. VA Approves Producer
    log('4', 'Verification Authority inspects and approves Producer...')
    await apiCall('POST', `/authority/producer-verifications/${verificationId}/approve`, {
      identityVerified: true,
      documentsVerified: true,
      landVerified: true,
      locationVerified: true,
      cultivationVerified: true,
      inspectionDate: new Date().toISOString(),
      latitude: 18.5204,
      longitude: 73.8567,
      observations: 'Farm inspected. Soil quality is excellent. Approved for organic cultivation.'
    }, vaToken)
    log('4', 'Producer VERIFIED and anchored to blockchain.', colors.green)

    // 5. Producer Creates Batch
    log('5', 'Producer creates a new batch of Ashwagandha...')
    const herbsReq = await apiCall('GET', '/herbs', undefined, producerToken)
    const ashwagandha = herbsReq.data.herbs.find((h: any) => h.commonName === 'Ashwagandha')
    const batchRes = await apiCall('POST', '/batches', {
      herbId: ashwagandha.id,
      quantity: 500, // kg
      farmLocation: 'Kharadi',
      harvestDate: new Date().toISOString(),
      cultivationMethod: 'Organic'
    }, producerToken)
    const batchId = batchRes.data.batch.id
    const batchNumber = batchRes.data.batch.batchNumber
    log('5', `Batch created successfully: ${batchNumber}`, colors.green)

    // Producer Submits Batch
    log('5.1', 'Producer submits batch...')
    await apiCall('POST', `/batches/${batchId}/submit`, undefined, producerToken)
    
    // Producer Requests Inspection
    log('5.2', 'Producer requests inspection...')
    const inspectReq = await apiCall('POST', `/batches/${batchId}/inspection/request`, undefined, producerToken)
    const inspectionId = inspectReq.data.inspection.id

    // 6. Admin assigns VA to Batch for Lot Inspection
    log('6', 'Admin assigns VA for Batch Lot Inspection...')
    await apiCall('POST', `/admin/inspections/${inspectionId}/assign`, {
      authorityId: (await prisma.user.findUnique({ where: { email: 'verifier@dravya.in' } }))?.id
    }, adminToken)
    log('6', 'Batch assigned to VA.', colors.green)

    // 7. VA Inspects Batch
    log('7', 'VA inspects the harvested batch...')
    // Note: authority must start inspection first
    await apiCall('POST', `/authority/lot-inspections/${inspectionId}/start`, undefined, vaToken)
    await apiCall('POST', `/authority/lot-inspections/${inspectionId}/approve`, {
      inspectedQuantity: 495, // 5kg moisture loss
      herbIdentityVerified: true,
      physicalQualityStatus: 'Excellent',
      packagingStatus: 'Sealed',
      documentsVerified: true,
      inspectionDate: new Date().toISOString(),
      latitude: 18.5204,
      longitude: 73.8567,
      observations: 'Batch looks fresh and well dried.'
    }, vaToken)
    log('7', 'Batch INSPECTED and anchored to blockchain.', colors.green)

    // 8. Admin assigns Lab
    log('8', 'Admin assigns Laboratory for Quality Testing...')
    const labAssignRes = await apiCall('POST', `/admin/assign-lab-test`, {
      batchId,
      labId: (await prisma.user.findUnique({ where: { email: 'lab@dravya.in' } }))?.id
    }, adminToken)
    const testId = labAssignRes.data.qualityTest.id
    log('8', 'Lab assigned.', colors.green)

    // 9. Lab Tests Batch
    log('9', 'Laboratory tests the batch...')
    await apiCall('POST', `/lab/tests/${testId}/receive`, undefined, labToken)
    await apiCall('POST', `/lab/tests/${testId}/start`, undefined, labToken)
    
    // Add test results
    await apiCall('POST', `/lab/tests/${testId}/results`, {
      parameter: 'Heavy Metals (Lead, Mercury)',
      resultStatus: 'PASS',
      remarks: 'Within AYUSH limits'
    }, labToken)
    
    await apiCall('POST', `/lab/tests/${testId}/results`, {
      parameter: 'Pesticide Residue',
      resultStatus: 'PASS',
      remarks: 'Not detected'
    }, labToken)

    // Complete test
    await apiCall('POST', `/lab/tests/${testId}/complete`, { overallResult: 'PASS' }, labToken)
    
    // Generate Report
    const reportRes = await apiCall('POST', `/lab/tests/${testId}/report`, {
      reportUrl: 'https://dravya.in/dummy-report.pdf',
      reportFileName: `AYUSH-LAB-${Date.now()}.pdf`,
      reportFileType: 'application/pdf'
    }, labToken)
    const reportId = reportRes.data.report.id

    // Finalize Report
    await apiCall('POST', `/lab/reports/${reportId}/finalize`, undefined, labToken)
    log('9', 'Batch QUALITY_APPROVED and anchored to blockchain.', colors.green)

    // 10. Admin Assigns Distributor
    log('10', 'Admin assigns Distributor...')
    await apiCall('POST', `/admin/batches/${batchId}/assign-distributor`, {
      distributorId: (await prisma.user.findUnique({ where: { email: 'distributor@dravya.in' } }))?.id
    }, adminToken)
    log('10', 'Distributor assigned.', colors.green)

    // 11. Distributor Updates Tracking
    log('11', 'Distributor picks up and dispatches batch...')
    await apiCall('POST', `/distributors/me/batches/${batchId}/receive`, {
      quantity: 495,
      unit: 'KG',
      location: 'Pune Logistics Hub',
      latitude: 18.5204,
      longitude: 73.8567,
      notes: 'Received from Producer.'
    }, distToken)
    log('11', 'Batch RECEIVED.', colors.green)

    await apiCall('POST', `/distributors/me/batches/${batchId}/dispatch`, {
      quantity: 495,
      unit: 'KG',
      location: 'Pune Logistics Hub',
      destination: 'Mumbai Central Warehouse',
      latitude: 18.5204,
      longitude: 73.8567,
      notes: 'Dispatched to Mumbai.'
    }, distToken)
    log('11', 'Batch DISPATCHED.', colors.green)

    await apiCall('POST', `/distributors/me/batches/${batchId}/deliver`, {
      quantity: 495,
      unit: 'KG',
      location: 'Mumbai Central Warehouse',
      latitude: 19.0760,
      longitude: 72.8777,
      notes: 'Delivered successfully.'
    }, distToken)
    log('11', 'Batch DELIVERED and anchored to blockchain.', colors.green)

    // Generate QR
    log('11.5', 'Admin Generates QR Code...')
    const qrRes = await apiCall('POST', `/admin/batches/${batchId}/qr`, undefined, adminToken)
    const qrCode = qrRes.data.code
    log('11.5', `QR Code generated: ${qrCode}`, colors.green)

    // 12. Public Verification
    log('12', 'Simulating Consumer Scanning QR Code...')
    let v1Data: any = null
    for (let i = 0; i < 15; i++) {
      const verifyRes1 = await apiCall('GET', `/public/verify/${qrCode}`)
      v1Data = verifyRes1.data.data || verifyRes1.data
      if (v1Data.data) {
        v1Data = v1Data.data
      }
      if (v1Data.verified && v1Data.blockchain?.integrityVerified) {
        break
      }
      console.log(`[12] Waiting for blockchain anchoring to complete (attempt ${i + 1}/15)...`)
      await new Promise(resolve => setTimeout(resolve, 1000))
    }
    if (v1Data.verified && v1Data.blockchain?.integrityVerified) {
      log('12', '✅ SUCCESS: Product Verified Authentic and Blockchain Integrity Intact.', colors.green)
    } else {
      throw new Error('Verification failed unexpectedly.')
    }

    // 13. Simulated Database Tampering Attack
    log('13', '🔥 SIMULATING DATABASE TAMPERING ATTACK 🔥', colors.red)
    console.log(`${colors.red}Attacker modifies the DB directly to change the lab status from PASS to FAIL...${colors.reset}`)
    
    // Direct DB modification bypassing the blockchain hashing layer
    await prisma.qualityTest.updateMany({
      where: { batchId: batchId },
      data: { overallResult: 'FAIL' }
    })
    log('13', 'Database successfully tampered.', colors.yellow)

    // 14. Consumer Scans QR Code Again
    log('14', 'Consumer Scans QR Code Again...')
    const verifyRes2 = await apiCall('GET', `/public/verify/${qrCode}`)
    let v2Data = verifyRes2.data.data || verifyRes2.data
    if (v2Data.data) {
      v2Data = v2Data.data
    }
    if (v2Data.verified === false && v2Data.status === 'BLOCKCHAIN_VERIFICATION_FAILED') {
      log('14', `🚨 TAMPER DETECTED: ${v2Data.message || v2Data.blockchain?.message}`, colors.red)
      console.log(`\n${colors.green}${colors.bright}🎉 SIH DEMO COMPLETED SUCCESSFULLY! 🎉${colors.reset}\n`)
    } else {
      throw new Error('Tamper detection failed. Verification passed despite DB tampering.')
    }

  } catch (error: any) {
    console.error(`\n${colors.red}${colors.bright}❌ DEMO FAILED: ${error.message}${colors.reset}\n`)
    console.error(error)
  } finally {
    await prisma.$disconnect()
  }
}

runDemo()
