import express from 'express'
import cors from 'cors'
import dotenv from 'dotenv'

// Load environment variables
dotenv.config()

import authRoutes from './routes/auth.routes'
import batchRoutes from './routes/batch.routes'
import userRoutes from './routes/user.routes'

const app = express()
const PORT = process.env.PORT || 8000

// ─── Middleware ──────────────────────────────────────────

app.use(cors({
  origin: process.env.CLIENT_URL || 'http://localhost:3000',
  credentials: true,
}))

app.use(express.json())
app.use(express.urlencoded({ extended: true }))

// ─── Health Check ────────────────────────────────────────

app.get('/api/health', (_req, res) => {
  res.json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    service: 'dravya-server',
  })
})

// ─── Routes ─────────────────────────────────────────────

app.use('/api/auth', authRoutes)
app.use('/api/batches', batchRoutes)
app.use('/api/users', userRoutes)

// ─── 404 Handler ────────────────────────────────────────

app.use((_req, res) => {
  res.status(404).json({ error: 'Route not found' })
})

// ─── Start Server ───────────────────────────────────────

app.listen(PORT, () => {
  console.log(`🌿 Dravya server running on http://localhost:${PORT}`)
  console.log(`📋 Health check: http://localhost:${PORT}/api/health`)
})

export default app
