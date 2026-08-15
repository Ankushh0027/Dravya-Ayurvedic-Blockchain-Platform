import { PrismaClient } from '@prisma/client'
const prisma = new PrismaClient()
async function main() {
  const anchors = await prisma.blockchainRecord.findMany()
  console.log(anchors.length)
}
main()
