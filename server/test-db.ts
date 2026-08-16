import { PrismaClient } from '@prisma/client'
const prisma = new PrismaClient()

async function test() {
  const users = await prisma.user.findMany({ select: { id: true, email: true, role: true } })
  console.log("Users:", users)

  const verifications = await prisma.producerVerification.findMany()
  console.log("Verifications:", verifications)
}
test().finally(() => prisma.$disconnect())
