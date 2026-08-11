'use client'

import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Badge } from '@/components/ui/badge'
import { mockBatches, type BatchStatus } from '../data/batches'
import { useTranslation } from 'react-i18next'

const statusStyles: Record<BatchStatus, string> = {
  verified: 'bg-green-100 text-green-800 hover:bg-green-100',
  pending: 'bg-amber-100 text-amber-800 hover:bg-amber-100',
  rejected: 'bg-red-100 text-red-800 hover:bg-red-100',
}

export function BatchesTable() {
  const { t } = useTranslation()

  const statusLabels: Record<BatchStatus, string> = {
    verified: t('producer.statusVerified'),
    pending: t('producer.statusPending'),
    rejected: t('producer.statusRejected'),
  }

  return (
    <div className="rounded-lg border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>{t('producer.tableHerb')}</TableHead>
            <TableHead>{t('producer.tableBatchId')}</TableHead>
            <TableHead>{t('producer.tableQuantity')}</TableHead>
            <TableHead>{t('producer.tableHarvestDate')}</TableHead>
            <TableHead>{t('producer.tableStatus')}</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {mockBatches.map((batch) => (
            <TableRow key={batch.id}>
              <TableCell className="font-medium">{batch.herbName}</TableCell>
              <TableCell>{batch.id}</TableCell>
              <TableCell>{batch.quantityKg} kg</TableCell>
              <TableCell>{batch.harvestDate}</TableCell>
              <TableCell>
                <Badge className={statusStyles[batch.status]} variant="secondary">
                  {statusLabels[batch.status]}
                </Badge>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  )
}