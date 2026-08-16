import { PrismaClient } from '@prisma/client'
import { HashingService } from '../src/services/hashing.service'
import { BlockchainService } from '../src/services/blockchain.service'
import { Role } from '@prisma/client'

const prisma = new PrismaClient()
async function main() {
  const batch = await prisma.batch.findFirst({ orderBy: { createdAt: 'desc' }, include: { producerProfile: { include: { verifications: true } }, inspections: true, qualityTests: true } })
  const pv = batch?.producerProfile.verifications[0]!
  const bi = batch?.inspections[0]!
  const qt = batch?.qualityTests[0]!

  console.log('PV Hash Match:', await BlockchainService.verifyRecord('PRODUCER_VERIFICATION', pv.id, 1, HashingService.getProducerVerificationPayload(pv), Role.ADMIN))
  console.log('BI Hash Match:', await BlockchainService.verifyRecord('BATCH_INSPECTION', bi.id, 1, HashingService.getBatchInspectionPayload(bi), Role.ADMIN))
  console.log('QT Hash Match:', await BlockchainService.verifyRecord('QUALITY_TEST', qt.id, 1, HashingService.getQualityTestPayload(qt), Role.ADMIN))
}
main()
