import { PrismaClient } from '@prisma/client'
const prisma = new PrismaClient()
async function main() {
  const batch = await prisma.batch.findFirst({ orderBy: { createdAt: 'desc' }, include: { qualityTests: { include: { reports: true } } } })
  console.dir(batch?.qualityTests, { depth: null })
}
main()
