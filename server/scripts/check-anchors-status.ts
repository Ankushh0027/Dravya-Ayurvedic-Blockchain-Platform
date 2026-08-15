import { PrismaClient } from '@prisma/client'
const prisma = new PrismaClient()
async function main() {
  const anchors = await prisma.blockchainRecord.findMany({ orderBy: { createdAt: 'desc' }, take: 10 })
  console.dir(anchors, { depth: null })
}
main()
