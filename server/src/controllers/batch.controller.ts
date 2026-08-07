import { Request, Response } from 'express'
import { prisma } from '../lib/prisma'
import { z } from 'zod'
import { AuthRequest } from '../middleware/auth.middleware'

// ─── Validation Schemas ──────────────────────────────────

const createBatchSchema = z.object({
  name: z.string().min(1, 'Batch name is required'),
  herbName: z.string().min(1, 'Herb name is required'),
  origin: z.string().min(1, 'Origin is required'),
  quantity: z.number().positive('Quantity must be positive'),
  unit: z.string().optional(),
  description: z.string().optional(),
})

const updateBatchSchema = z.object({
  name: z.string().min(1).optional(),
  herbName: z.string().min(1).optional(),
  origin: z.string().min(1).optional(),
  quantity: z.number().positive().optional(),
  unit: z.string().optional(),
  status: z.enum(['CREATED', 'TESTED', 'MANUFACTURED', 'IN_TRANSIT', 'DELIVERED', 'SOLD']).optional(),
  description: z.string().optional(),
})

// ─── Helpers ─────────────────────────────────────────────

function getParamString(param: string | string[] | undefined): string | undefined {
  if (Array.isArray(param)) return param[0]
  return param
}

function getQueryString(param: unknown): string | undefined {
  if (typeof param === 'string') return param
  if (Array.isArray(param) && typeof param[0] === 'string') return param[0]
  return undefined
}

// ─── Controllers ─────────────────────────────────────────

export async function createBatch(req: AuthRequest, res: Response): Promise<void> {
  try {
    const validation = createBatchSchema.safeParse(req.body)
    if (!validation.success) {
      res.status(400).json({
        error: 'Validation failed',
        details: validation.error.flatten().fieldErrors,
      })
      return
    }

    const batch = await prisma.batch.create({
      data: {
        ...validation.data,
        createdById: req.userId!,
      },
      include: {
        createdBy: {
          select: { id: true, name: true, email: true, role: true },
        },
      },
    })

    res.status(201).json({ message: 'Batch created successfully', batch })
  } catch (error) {
    console.error('Create batch error:', error)
    res.status(500).json({ error: 'Internal server error' })
  }
}

export async function getAllBatches(req: Request, res: Response): Promise<void> {
  try {
    const page = parseInt(getQueryString(req.query.page) || '1')
    const limit = parseInt(getQueryString(req.query.limit) || '10')
    const skip = (page - 1) * limit

    const [batches, total] = await Promise.all([
      prisma.batch.findMany({
        skip,
        take: limit,
        orderBy: { createdAt: 'desc' },
        include: {
          createdBy: {
            select: { id: true, name: true, role: true },
          },
          _count: {
            select: { qualityTests: true, supplyChainEvents: true },
          },
        },
      }),
      prisma.batch.count(),
    ])

    res.json({
      batches,
      pagination: {
        page,
        limit,
        total,
        totalPages: Math.ceil(total / limit),
      },
    })
  } catch (error) {
    console.error('Get batches error:', error)
    res.status(500).json({ error: 'Internal server error' })
  }
}

export async function getBatchById(req: Request, res: Response): Promise<void> {
  try {
    const id = getParamString(req.params.id)
    if (!id) {
      res.status(400).json({ error: 'Batch ID is required.' })
      return
    }

    const batch = await prisma.batch.findUnique({
      where: { id },
      include: {
        createdBy: {
          select: { id: true, name: true, email: true, role: true },
        },
        qualityTests: {
          include: {
            conductedBy: {
              select: { id: true, name: true, role: true },
            },
          },
          orderBy: { testedAt: 'desc' },
        },
        supplyChainEvents: {
          include: {
            actor: {
              select: { id: true, name: true, role: true },
            },
          },
          orderBy: { timestamp: 'desc' },
        },
      },
    })

    if (!batch) {
      res.status(404).json({ error: 'Batch not found.' })
      return
    }

    res.json({ batch })
  } catch (error) {
    console.error('Get batch error:', error)
    res.status(500).json({ error: 'Internal server error' })
  }
}

export async function updateBatch(req: AuthRequest, res: Response): Promise<void> {
  try {
    const id = getParamString(req.params.id)
    if (!id) {
      res.status(400).json({ error: 'Batch ID is required.' })
      return
    }

    const validation = updateBatchSchema.safeParse(req.body)
    if (!validation.success) {
      res.status(400).json({
        error: 'Validation failed',
        details: validation.error.flatten().fieldErrors,
      })
      return
    }

    const existingBatch = await prisma.batch.findUnique({ where: { id } })
    if (!existingBatch) {
      res.status(404).json({ error: 'Batch not found.' })
      return
    }

    const batch = await prisma.batch.update({
      where: { id },
      data: validation.data,
      include: {
        createdBy: {
          select: { id: true, name: true, email: true, role: true },
        },
      },
    })

    res.json({ message: 'Batch updated successfully', batch })
  } catch (error) {
    console.error('Update batch error:', error)
    res.status(500).json({ error: 'Internal server error' })
  }
}

export async function deleteBatch(req: Request, res: Response): Promise<void> {
  try {
    const id = getParamString(req.params.id)
    if (!id) {
      res.status(400).json({ error: 'Batch ID is required.' })
      return
    }

    const existingBatch = await prisma.batch.findUnique({ where: { id } })
    if (!existingBatch) {
      res.status(404).json({ error: 'Batch not found.' })
      return
    }

    await prisma.batch.delete({ where: { id } })

    res.json({ message: 'Batch deleted successfully' })
  } catch (error) {
    console.error('Delete batch error:', error)
    res.status(500).json({ error: 'Internal server error' })
  }
}
