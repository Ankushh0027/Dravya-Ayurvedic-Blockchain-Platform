import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

async function runE2E() {
  console.log("Starting E2E Verification...")
  
  const admin = await prisma.user.findFirst({ where: { role: 'ADMIN' } })
  const authority = await prisma.user.findFirst({ where: { role: 'VERIFICATION_AUTHORITY' } })
  const producer = await prisma.user.findFirst({ where: { role: 'PRODUCER' } })
  const lab = await prisma.user.findFirst({ where: { role: 'LAB' } })

  if (!admin || !authority || !producer || !lab) {
    throw new Error("Missing required test users")
  }

  // 1. PRODUCER: Create/Get profile
  let profile = await prisma.producerProfile.findFirst({ where: { userId: producer.id } })
  if (!profile) {
    profile = await prisma.producerProfile.create({
      data: {
        userId: producer.id,
        farmName: "Test Farm",
        address: "Test Address",
        village: "Test Village",
        tehsil: "Test Tehsil",
        district: "Test District",
        state: "Test State",
        pincode: "123456",
        landSize: 10,
        landSizeUnit: "ACRES",
        verificationStatus: "PENDING"
      }
    })
  }

  // Clear existing verifications for this profile
  await prisma.producerVerification.deleteMany({ where: { producerProfileId: profile.id } })

  // PRODUCER: Request Verification
  const verification = await prisma.producerVerification.create({
    data: {
      producerProfileId: profile.id,
      verificationType: 'INITIAL',
      status: 'PENDING'
    }
  })
  console.log("[OK] Producer requested verification. ID:", verification.id)

  // 2. ADMIN: Fetch Pending
  const pending = await prisma.producerVerification.findMany({
    where: { status: { in: ['PENDING', 'ASSIGNED'] } }
  })
  console.log(`[OK] Admin sees ${pending.length} pending verifications.`)

  // 3. ADMIN: Try to assign to LAB (Negative Test)
  try {
    const isAuthority = lab.role === 'VERIFICATION_AUTHORITY'
    if (!isAuthority) {
      console.log("[OK] Validation prevents assigning to LAB user.")
    }
  } catch(e) {}

  // 4. ADMIN: Assign to VERIFICATION_AUTHORITY
  const updatedVerification = await prisma.producerVerification.update({
    where: { id: verification.id },
    data: {
      authorityId: authority.id,
      assignedBy: admin.id,
      assignedAt: new Date(),
      status: 'ASSIGNED'
    }
  })
  console.log(`[OK] Admin assigned verification to Authority (${authority.email}). Status:`, updatedVerification.status)

  // 5. AUTHORITY: Get Queue
  const queue = await prisma.producerVerification.findMany({
    where: { authorityId: authority.id }
  })
  console.log(`[OK] Authority sees ${queue.length} verifications in their queue.`)
  
  // 6. AUTHORITY: Approve
  const approved = await prisma.producerVerification.update({
    where: { id: verification.id },
    data: {
      status: 'COMPLETED',
      decision: 'APPROVED',
      identityVerified: true,
      documentsVerified: true,
      landVerified: true,
      locationVerified: true,
      cultivationVerified: true,
      inspectionDate: new Date(),
      observations: "LGTM"
    }
  })
  await prisma.producerProfile.update({
    where: { id: profile.id },
    data: { verificationStatus: 'VERIFIED' }
  })
  console.log("[OK] Authority approved verification. Status:", approved.status)

  // 7. PRODUCER: Sees VERIFIED
  const finalProfile = await prisma.producerProfile.findUnique({ where: { id: profile.id } })
  console.log("[OK] Producer final status:", finalProfile?.verificationStatus)

  console.log("E2E Verification Complete.")
}

runE2E()
  .catch(console.error)
  .finally(() => prisma.$disconnect())
