export interface Herb {
  id: string
  commonName: string
  botanicalName: string
  localName: string | null
  family: string
  description: string | null
  medicinalUse: string | null
  isActive: boolean
  createdAt: string
  updatedAt: string
}
