import { PrismaClient } from '@prisma/client'
const prisma = new PrismaClient()

async function testAssign() {
  const adminId = 'cmsteevpp0000y99l7x2ge977'
  const authorityId = 'cmsteevxb0001y99lug2p4h9u'
  const verificationId = 'cmsu48ua2000ay92cwk6bt3dh'

  const updated = await prisma.producerVerification.update({
    where: { id: verificationId },
    data: {
      authorityId,
      assignedBy: adminId,
      assignedAt: new Date(),
      status: 'ASSIGNED'
    }
  })
  console.log("Assigned:", updated)
}

testAssign().finally(() => prisma.$disconnect())
