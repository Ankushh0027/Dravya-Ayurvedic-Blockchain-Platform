'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { useTranslation } from 'react-i18next'

export function RegisterBatchForm() {
  const { t } = useTranslation()
  const [submitted, setSubmitted] = useState(false)
  const [cultivationFile, setCultivationFile] = useState<File | null>(null)
  const [harvestFiles, setHarvestFiles] = useState<File[]>([])
  const [form, setForm] = useState({
    herbName: '',
    botanicalName: '',
    harvestDate: '',
    farmLocation: '',
    description: '',
  })

  function handleChange(e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }))
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    console.log('Submitting batch:', form, { cultivationFile, harvestFiles })
    setSubmitted(true)
  }

  if (submitted) {
    return (
      <div className="rounded-lg border p-6 text-center">
        <p className="font-medium">{t('producer.submittedTitle')}</p>
        <p className="text-sm text-muted-foreground mt-1">
          {t('producer.submittedSubtitle')}
        </p>
        <Button className="mt-4" variant="outline" onClick={() => setSubmitted(false)}>
          {t('producer.registerAnother')}
        </Button>
      </div>
    )
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 rounded-lg border p-6">
      <div className="grid gap-4 md:grid-cols-2">
        <div className="space-y-2">
          <Label htmlFor="herbName">{t('producer.herbName')}</Label>
          <Input id="herbName" name="herbName" placeholder="Ashwagandha" value={form.herbName} onChange={handleChange} required />
        </div>
        <div className="space-y-2">
          <Label htmlFor="botanicalName">{t('producer.botanicalName')}</Label>
          <Input id="botanicalName" name="botanicalName" placeholder="Withania somnifera" value={form.botanicalName} onChange={handleChange} required />
        </div>
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        <div className="space-y-2">
          <Label htmlFor="harvestDate">{t('producer.harvestDate')}</Label>
          <Input id="harvestDate" name="harvestDate" type="date" value={form.harvestDate} onChange={handleChange} required />
        </div>
        <div className="space-y-2">
          <Label htmlFor="farmLocation">{t('producer.farmLocation')}</Label>
          <Input id="farmLocation" name="farmLocation" placeholder="Sehore, Madhya Pradesh" value={form.farmLocation} onChange={handleChange} required />
        </div>
      </div>
      <div className="space-y-2">
        <Label htmlFor="description">{t('producer.descriptionOptional')}</Label>
        <Textarea id="description" name="description" placeholder="..." value={form.description} onChange={handleChange} />
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        <div className="space-y-2">
          <Label htmlFor="cultivationFile">{t('producer.cultivationDetails')}</Label>
          <label
            htmlFor="cultivationFile"
            className="flex cursor-pointer flex-col items-center justify-center rounded-md border border-dashed p-4 text-center text-sm text-muted-foreground hover:bg-muted/50"
          >
            {cultivationFile ? cultivationFile.name : t('producer.clickUploadOrDrag')}
          </label>
          <input
            id="cultivationFile"
            type="file"
            accept=".pdf,.doc,.docx,image/*"
            className="hidden"
            onChange={(e) => setCultivationFile(e.target.files?.[0] ?? null)}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="harvestFiles">{t('producer.harvestImages')}</Label>
          <label
            htmlFor="harvestFiles"
            className="flex cursor-pointer flex-col items-center justify-center rounded-md border border-dashed p-4 text-center text-sm text-muted-foreground hover:bg-muted/50"
          >
            {harvestFiles.length > 0 ? `${harvestFiles.length} ${t('producer.filesSelected')}` : t('producer.clickUploadOrDrag')}
          </label>
          <input
            id="harvestFiles"
            type="file"
            accept="image/*"
            multiple
            className="hidden"
            onChange={(e) => setHarvestFiles(e.target.files ? Array.from(e.target.files) : [])}
          />
        </div>
      </div>
      <Button type="submit">{t('producer.submitBatch')}</Button>
    </form>
  )
}