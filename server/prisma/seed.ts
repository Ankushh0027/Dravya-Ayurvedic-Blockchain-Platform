import { PrismaClient } from '@prisma/client'
import bcrypt from 'bcryptjs'

const prisma = new PrismaClient()

async function main() {
  console.log('🌱 Seeding database...\n')

  // ─── Create initial ADMIN account ──────────────────────
  const adminEmail = 'admin@dravya.in'
  const adminPassword = 'Admin@1234'

  const existingAdmin = await prisma.user.findUnique({
    where: { email: adminEmail },
  })

  if (existingAdmin) {
    console.log(`✅ Admin user already exists: ${adminEmail}`)
  } else {
    const salt = await bcrypt.genSalt(12)
    const hashedPassword = await bcrypt.hash(adminPassword, salt)

    const admin = await prisma.user.create({
      data: {
        name: 'Dravya Admin',
        email: adminEmail,
        password: hashedPassword,
        role: 'ADMIN',
        organization: 'Dravya Platform',
        isActive: true,
      },
    })

    console.log(`✅ Admin user created:`)
    console.log(`   Email:    ${admin.email}`)
    console.log(`   Password: ${adminPassword}`)
    console.log(`   Role:     ${admin.role}`)
    console.log(`   ID:       ${admin.id}`)
  }

  // ─── Create initial VERIFICATION_AUTHORITY account ─────
  const vaEmail = 'verifier@dravya.in'
  const vaPassword = 'Verify@1234'

  const existingVA = await prisma.user.findUnique({
    where: { email: vaEmail },
  })

  if (existingVA) {
    console.log(`✅ Verification Authority user already exists: ${vaEmail}`)
  } else {
    const salt = await bcrypt.genSalt(12)
    const hashedPassword = await bcrypt.hash(vaPassword, salt)

    const va = await prisma.user.create({
      data: {
        name: 'Government Verifier',
        email: vaEmail,
        password: hashedPassword,
        role: 'VERIFICATION_AUTHORITY',
        organization: 'Ministry of AYUSH',
        isActive: true,
      },
    })

    console.log(`✅ Verification Authority user created:`)
    console.log(`   Email:    ${va.email}`)
    console.log(`   Password: ${vaPassword}`)
    console.log(`   Role:     ${va.role}`)
    console.log(`   ID:       ${va.id}`)
  }

  // ─── Create initial PRODUCER account ───────────────────
  const prodEmail = 'producer@dravya.in'
  const prodPassword = 'Prod@1234'
  const existingProd = await prisma.user.findUnique({ where: { email: prodEmail } })
  if (!existingProd) {
    const salt = await bcrypt.genSalt(12)
    const hashedPassword = await bcrypt.hash(prodPassword, salt)
    const prod = await prisma.user.create({
      data: {
        name: 'Green Valley Farms',
        email: prodEmail,
        password: hashedPassword,
        role: 'PRODUCER',
        organization: 'Green Valley Farms',
        isActive: true,
      },
    })
    console.log(`✅ Producer user created: ${prodEmail} / ${prodPassword}`)
  }

  // ─── Create initial LAB account ────────────────────────
  const labEmail = 'lab@dravya.in'
  const labPassword = 'Lab@1234'
  const existingLab = await prisma.user.findUnique({ where: { email: labEmail } })
  if (!existingLab) {
    const salt = await bcrypt.genSalt(12)
    const hashedPassword = await bcrypt.hash(labPassword, salt)
    const lab = await prisma.user.create({
      data: {
        name: 'AYUSH Testing Lab',
        email: labEmail,
        password: hashedPassword,
        role: 'LAB',
        organization: 'AYUSH Certified Lab',
        isActive: true,
      },
    })
    console.log(`✅ Lab user created: ${labEmail} / ${labPassword}`)
  }

  // ─── Create initial DISTRIBUTOR account ────────────────
  const distEmail = 'distributor@dravya.in'
  const distPassword = 'Dist@1234'
  const existingDist = await prisma.user.findUnique({ where: { email: distEmail } })
  if (!existingDist) {
    const salt = await bcrypt.genSalt(12)
    const hashedPassword = await bcrypt.hash(distPassword, salt)
    const dist = await prisma.user.create({
      data: {
        name: 'National Distributors',
        email: distEmail,
        password: hashedPassword,
        role: 'DISTRIBUTOR',
        organization: 'National Logistics',
        isActive: true,
      },
    })
    console.log(`✅ Distributor user created: ${distEmail} / ${distPassword}`)
  }

  // ─── Create Herb Catalog ────────────────────────────────
  const herbs = [
    {
      commonName: 'Ashwagandha',
      botanicalName: 'Withania somnifera',
      family: 'Solanaceae',
      description: 'Adaptogenic herb known for reducing stress and anxiety.',
      medicinalUse: 'Stress relief, energy, immunity.',
    },
    {
      commonName: 'Tulsi',
      botanicalName: 'Ocimum sanctum',
      family: 'Lamiaceae',
      description: 'Holy Basil, revered for its medicinal and spiritual properties.',
      medicinalUse: 'Respiratory health, immunity, stress relief.',
    },
    {
      commonName: 'Brahmi',
      botanicalName: 'Bacopa monnieri',
      family: 'Plantaginaceae',
      description: 'Known for cognitive enhancement and memory improvement.',
      medicinalUse: 'Memory, concentration, anxiety reduction.',
    },
    {
      commonName: 'Shatavari',
      botanicalName: 'Asparagus racemosus',
      family: 'Asparagaceae',
      description: 'Traditionally used to support reproductive health.',
      medicinalUse: 'Female reproductive health, digestion, immunity.',
    },
    {
      commonName: 'Neem',
      botanicalName: 'Azadirachta indica',
      family: 'Meliaceae',
      description: 'Known for its powerful antibacterial and antifungal properties.',
      medicinalUse: 'Skin health, blood purification, immunity.',
    },
    {
      commonName: 'Turmeric',
      botanicalName: 'Curcuma longa',
      family: 'Zingiberaceae',
      description: 'Contains curcumin, a potent anti-inflammatory compound.',
      medicinalUse: 'Inflammation, joint health, digestion.',
    },
    {
      commonName: 'Ginger',
      botanicalName: 'Zingiber officinale',
      family: 'Zingiberaceae',
      description: 'A popular spice with powerful anti-nausea and anti-inflammatory effects.',
      medicinalUse: 'Digestion, nausea, cold and flu relief.',
    },
    {
      commonName: 'Amla',
      botanicalName: 'Phyllanthus emblica',
      family: 'Phyllanthaceae',
      description: 'Indian Gooseberry, exceptionally rich in Vitamin C and antioxidants.',
      medicinalUse: 'Immunity, hair and skin health, digestion.',
    },
    {
      commonName: 'Giloy',
      botanicalName: 'Tinospora cordifolia',
      family: 'Menispermaceae',
      description: 'An essential herb in Ayurveda known as the "root of immortality".',
      medicinalUse: 'Fever, immunity booster, digestion.',
    },
    {
      commonName: 'Aloe Vera',
      botanicalName: 'Aloe barbadensis',
      family: 'Asphodelaceae',
      description: 'A succulent plant species widely used for soothing skin and digestion.',
      medicinalUse: 'Skin burns, digestion, hydration.',
    },
    {
      commonName: 'Mulethi',
      botanicalName: 'Glycyrrhiza glabra',
      family: 'Fabaceae',
      description: 'Licorice root, traditionally used to soothe sore throats and digestive issues.',
      medicinalUse: 'Cough, sore throat, acidity.',
    },
    {
      commonName: 'Haritaki',
      botanicalName: 'Terminalia chebula',
      family: 'Combretaceae',
      description: 'A key ingredient in Triphala, highly regarded for digestive support.',
      medicinalUse: 'Detoxification, digestion, wound healing.',
    }
  ]

  let seededHerbsCount = 0
  for (const herbData of herbs) {
    const existing = await prisma.herb.findUnique({
      where: { botanicalName: herbData.botanicalName },
    })

    if (!existing) {
      await prisma.herb.create({ data: herbData })
      seededHerbsCount++
    }
  }

  if (seededHerbsCount > 0) {
    console.log(`✅ Seeded ${seededHerbsCount} herbs into the catalog.`)
  } else {
    console.log(`✅ Herb catalog already seeded.`)
  }

  console.log('\n🌿 Seeding complete.')
}

main()
  .then(async () => {
    await prisma.$disconnect()
  })
  .catch(async (e) => {
    console.error('Seeding error:', e)
    await prisma.$disconnect()
    process.exit(1)
  })
