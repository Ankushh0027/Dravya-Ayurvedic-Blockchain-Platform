import { Router } from 'express'
import {
  createBatch,
  getAllBatches,
  getBatchById,
  updateBatch,
  deleteBatch,
} from '../controllers/batch.controller'
import { authMiddleware } from '../middleware/auth.middleware'

const router = Router()

// All batch routes require authentication
router.use(authMiddleware)

router.post('/', createBatch)
router.get('/', getAllBatches)
router.get('/:id', getBatchById)
router.put('/:id', updateBatch)
router.delete('/:id', deleteBatch)

export default router
