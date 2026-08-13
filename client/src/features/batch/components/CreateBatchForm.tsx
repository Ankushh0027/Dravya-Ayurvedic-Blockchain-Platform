'use client'

import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import { Button } from '@/components/ui/button'
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { CreateBatchPayload } from '@/types/batch'
import { Herb } from '@/types/herb'
import { Package } from 'lucide-react'

const createBatchSchema = z.object({
  herbId: z.string().min(1, 'Herb is required'),
  farmLocation: z.string().min(1, 'Farm location is required'),
  quantity: z.coerce.number().positive('Quantity must be greater than 0'),
  unit: z.string().default('kg'),
  harvestDate: z.string().min(1, 'Harvest date is required'),
  cultivationMethod: z.string().min(1, 'Cultivation method is required'),
  harvestDetails: z.string().optional(),
  latitude: z.string().optional(),
  longitude: z.string().optional(),
})

type FormValues = z.infer<typeof createBatchSchema>

interface CreateBatchFormProps {
  herbs: Herb[]
  onSubmit: (data: CreateBatchPayload) => Promise<void>
  isLoading: boolean
}

export function CreateBatchForm({ herbs, onSubmit, isLoading }: CreateBatchFormProps) {
  const form = useForm<z.infer<typeof createBatchSchema>>({
    resolver: zodResolver(createBatchSchema),
    defaultValues: {
      herbId: '',
      farmLocation: '',
      quantity: 0,
      unit: 'kg',
      harvestDate: new Date().toISOString().split('T')[0],
      cultivationMethod: '',
      harvestDetails: '',
      latitude: '',
      longitude: '',
    },
  })

  const handleSubmit = async (values: FormValues) => {
    const payload: CreateBatchPayload = {
      ...values,
      harvestDate: new Date(values.harvestDate).toISOString(),
      latitude: values.latitude === '' ? undefined : Number(values.latitude),
      longitude: values.longitude === '' ? undefined : Number(values.longitude),
    }
    await onSubmit(payload)
  }

  const activeHerbs = herbs.filter(h => h.isActive)

  const inputStyles = "px-4 h-12 border-slate-200 bg-slate-50/50 hover:bg-slate-50 rounded-xl focus-visible:ring-[#184E48]/20 focus-visible:border-[#184E48] transition-all text-sm shadow-sm"
  const labelStyles = "text-slate-700 font-semibold text-sm ml-1"

  return (
    <div className="bg-white/80 backdrop-blur-xl border border-white/60 shadow-[0_8px_40px_rgb(0,0,0,0.04)] rounded-[24px] p-6 md:p-8 relative overflow-hidden">
      {/* Decorative Glow */}
      <div className="absolute top-0 right-0 w-[400px] h-[400px] bg-[#184E48]/5 rounded-full blur-[80px] pointer-events-none" />
      
      <Form {...form}>
        <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-6 relative z-10">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-5">
            <FormField
              control={form.control}
              name="herbId"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className={labelStyles}>Herb Type <span className="text-red-500">*</span></FormLabel>
                  <Select onValueChange={field.onChange} value={field.value} disabled={isLoading}>
                    <FormControl>
                      <SelectTrigger className={`${inputStyles} flex items-center`}>
                        <SelectValue placeholder="Select an herb" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent className="rounded-xl border-slate-200 shadow-xl">
                      {activeHerbs.map(herb => (
                        <SelectItem key={herb.id} value={herb.id} className="rounded-lg cursor-pointer hover:bg-slate-50">
                          {herb.commonName}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="farmLocation"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className={labelStyles}>Farm Location <span className="text-red-500">*</span></FormLabel>
                  <FormControl>
                    <Input className={inputStyles} placeholder="e.g. Plot 4, North Field" disabled={isLoading} {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <div className="flex space-x-4">
              <FormField
                control={form.control}
                name="quantity"
                render={({ field }) => (
                  <FormItem className="flex-1">
                    <FormLabel className={labelStyles}>Quantity <span className="text-red-500">*</span></FormLabel>
                    <FormControl>
                      <Input className={inputStyles} type="number" step="0.01" disabled={isLoading} {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              
              <FormField
                control={form.control}
                name="unit"
                render={({ field }) => (
                  <FormItem className="w-1/3">
                    <FormLabel className={labelStyles}>Unit</FormLabel>
                    <FormControl>
                      <Input className={inputStyles} disabled={isLoading} {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <FormField
              control={form.control}
              name="harvestDate"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className={labelStyles}>Harvest Date <span className="text-red-500">*</span></FormLabel>
                  <FormControl>
                    <Input className={inputStyles} type="date" disabled={isLoading} {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="cultivationMethod"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className={labelStyles}>Cultivation Method <span className="text-red-500">*</span></FormLabel>
                  <Select onValueChange={field.onChange} value={field.value} disabled={isLoading}>
                    <FormControl>
                      <SelectTrigger className={`${inputStyles} flex items-center`}>
                        <SelectValue placeholder="Select method" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent className="rounded-xl border-slate-200 shadow-xl">
                      <SelectItem value="ORGANIC" className="rounded-lg cursor-pointer">Organic</SelectItem>
                      <SelectItem value="CONVENTIONAL" className="rounded-lg cursor-pointer">Conventional</SelectItem>
                      <SelectItem value="GAP" className="rounded-lg cursor-pointer">GAP (Good Agricultural Practices)</SelectItem>
                      <SelectItem value="WILD_CRAFTED" className="rounded-lg cursor-pointer">Wild Crafted</SelectItem>
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="latitude"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className={labelStyles}>Latitude (Optional)</FormLabel>
                  <FormControl>
                    <Input className={inputStyles} type="text" placeholder="e.g. 28.6139" disabled={isLoading} {...field} value={field.value ?? ''} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="longitude"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className={labelStyles}>Longitude (Optional)</FormLabel>
                  <FormControl>
                    <Input className={inputStyles} type="text" placeholder="e.g. 77.2090" disabled={isLoading} {...field} value={field.value ?? ''} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>

          <FormField
            control={form.control}
            name="harvestDetails"
            render={({ field }) => (
              <FormItem>
                <FormLabel className={labelStyles}>Harvest Details (Optional)</FormLabel>
                <FormControl>
                  <Textarea 
                    className="min-h-[120px] p-4 border-slate-200 bg-slate-50/50 hover:bg-slate-50 rounded-xl focus-visible:ring-[#184E48]/20 focus-visible:border-[#184E48] transition-all text-sm shadow-sm resize-y"
                    placeholder="Any specific notes about this harvest..." 
                    disabled={isLoading} 
                    {...field} 
                    value={field.value ?? ''}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <div className="pt-4 border-t border-slate-100 flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-sm text-slate-500 font-medium hidden md:flex items-center gap-2">
              <Package className="w-4 h-4" />
              This batch will be immediately available for testing by laboratories.
            </p>
            <Button 
              type="submit" 
              disabled={isLoading}
              className="w-full md:w-auto min-w-[200px] bg-[#184E48] hover:bg-[#184E48]/90 text-white rounded-xl py-6 text-[15px] font-bold shadow-[0_8px_30px_rgb(24,78,72,0.2)] hover:shadow-[0_8px_30px_rgb(24,78,72,0.3)] hover:-translate-y-0.5 transition-all duration-300"
            >
              {isLoading ? 'Creating Batch...' : 'Create Batch'}
            </Button>
          </div>
        </form>
      </Form>
    </div>
  )
}

