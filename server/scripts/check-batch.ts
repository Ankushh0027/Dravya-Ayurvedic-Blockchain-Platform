import { PrismaClient } from '@prisma/client'
const prisma = new PrismaClient()
async function main() {
  const batch = await prisma.batch.findFirst({ orderBy: { createdAt: 'desc' }, include: { producerProfile: true, inspections: true, qualityTests: true } })
  console.dir(batch, { depth: null })
}
main()
