import { PrismaClient } from '@prisma/client'
const prisma = new PrismaClient()
async function main() {
  const qr = await prisma.qRCode.findFirst({ orderBy: { createdAt: 'desc' } })
  const res = await fetch('http://localhost:8000/api/public/verify/' + qr?.code)
  const data = await res.json()
  console.dir(data, { depth: null })
}
main()
