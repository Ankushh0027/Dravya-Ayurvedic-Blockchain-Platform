'use client'

import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import { Button } from '@/components/ui/button'
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import { ProducerProfile } from '@/types/producer'
import { Navigation } from 'lucide-react'

const profileSchema = z.object({
  farmName: z.string().min(2, 'Farm name must be at least 2 characters'),
  address: z.string().min(5, 'Address must be at least 5 characters'),
  village: z.string().min(2, 'Village is required'),
  tehsil: z.string().min(2, 'Tehsil is required'),
  district: z.string().min(2, 'District is required'),
  state: z.string().min(2, 'State is required'),
  pincode: z.string().regex(/^\d{6}$/, 'Pincode must be 6 digits'),
  landSize: z.coerce.number().positive('Land size must be positive'),
  landSizeUnit: z.string().optional().default('acres'),
  latitude: z.string().optional(),
  longitude: z.string().optional(),
})

type ProfileFormValues = z.infer<typeof profileSchema>

interface ProducerProfileFormProps {
  initialData: ProducerProfile | null
  onSubmit: (data: Partial<ProducerProfile>) => Promise<void>
  isLoading: boolean
}

export function ProducerProfileForm({ initialData, onSubmit, isLoading }: ProducerProfileFormProps) {
  const form = useForm<z.infer<typeof profileSchema>>({
    resolver: zodResolver(profileSchema) as any,
    defaultValues: {
      farmName: initialData?.farmName || '',
      address: initialData?.address || '',
      village: initialData?.village || '',
      tehsil: initialData?.tehsil || '',
      district: initialData?.district || '',
      state: initialData?.state || '',
      pincode: initialData?.pincode || '',
      landSize: initialData?.landSize || 0,
      landSizeUnit: initialData?.landSizeUnit || 'acres',
      latitude: initialData?.latitude?.toString() || '',
      longitude: initialData?.longitude?.toString() || '',
    },
  })

  const handleSubmit = async (values: ProfileFormValues) => {
    // Clean up empty strings to undefined for optional fields
    const payload = {
      ...values,
      latitude: values.latitude === '' ? undefined : Number(values.latitude),
      longitude: values.longitude === '' ? undefined : Number(values.longitude),
    }
    await onSubmit(payload as Partial<ProducerProfile>)
  }

  const isReadOnly = initialData?.verificationStatus === 'VERIFIED' || initialData?.verificationStatus === 'UNDER_REVIEW'

  const inputStyles = "px-4 h-12 border-slate-200 bg-slate-50/50 hover:bg-slate-50 rounded-xl focus-visible:ring-[#184E48]/20 focus-visible:border-[#184E48] transition-all text-sm shadow-sm text-slate-900"
  const labelStyles = "text-slate-700 font-semibold text-sm ml-1"

  return (
    <div className="bg-white/80 backdrop-blur-xl border border-white/60 shadow-[0_8px_40px_rgb(0,0,0,0.04)] rounded-[24px] p-6 md:p-8 relative overflow-hidden">
      {/* Decorative Glow */}
      <div className="absolute top-0 right-0 w-[400px] h-[400px] bg-[#184E48]/5 rounded-full blur-[80px] pointer-events-none" />
      
      <Form {...form}>
        <form onSubmit={form.handleSubmit(handleSubmit as any)} className="space-y-6 relative z-10">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-5">
            <FormField
              control={form.control as any}
              name="farmName"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className={labelStyles}>Farm Name</FormLabel>
                  <FormControl>
                    <Input className={inputStyles} placeholder="Enter farm name" disabled={isReadOnly || isLoading} {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control as any}
              name="address"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className={labelStyles}>Address</FormLabel>
                  <FormControl>
                    <Input className={inputStyles} placeholder="Enter full address" disabled={isReadOnly || isLoading} {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control as any}
              name="village"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className={labelStyles}>Village</FormLabel>
                  <FormControl>
                    <Input className={inputStyles} placeholder="Enter village" disabled={isReadOnly || isLoading} {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control as any}
              name="tehsil"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className={labelStyles}>Tehsil</FormLabel>
                  <FormControl>
                    <Input className={inputStyles} placeholder="Enter tehsil" disabled={isReadOnly || isLoading} {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control as any}
              name="district"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className={labelStyles}>District</FormLabel>
                  <FormControl>
                    <Input className={inputStyles} placeholder="Enter district" disabled={isReadOnly || isLoading} {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control as any}
              name="state"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className={labelStyles}>State</FormLabel>
                  <FormControl>
                    <Input className={inputStyles} placeholder="Enter state" disabled={isReadOnly || isLoading} {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control as any}
              name="pincode"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className={labelStyles}>Pincode</FormLabel>
                  <FormControl>
                    <Input className={inputStyles} placeholder="6 digit pincode" disabled={isReadOnly || isLoading} {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <div className="flex space-x-4">
              <FormField
                control={form.control as any}
                name="landSize"
                render={({ field }) => (
                  <FormItem className="flex-1">
                    <FormLabel className={labelStyles}>Land Size</FormLabel>
                    <FormControl>
                      <Input className={inputStyles} type="number" step="0.01" disabled={isReadOnly || isLoading} {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              
              <FormField
                control={form.control as any}
                name="landSizeUnit"
                render={({ field }) => (
                  <FormItem className="w-1/3">
                    <FormLabel className={labelStyles}>Unit</FormLabel>
                    <FormControl>
                      <Input className={inputStyles} disabled={isReadOnly || isLoading} {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <FormField
              control={form.control as any}
              name="latitude"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className={labelStyles}>Latitude (Optional)</FormLabel>
                  <FormControl>
                    <Input className={inputStyles} type="text" placeholder="e.g. 28.6139" disabled={isReadOnly || isLoading} {...field} value={field.value ?? ''} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control as any}
              name="longitude"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className={labelStyles}>Longitude (Optional)</FormLabel>
                  <FormControl>
                    <Input className={inputStyles} type="text" placeholder="e.g. 77.2090" disabled={isReadOnly || isLoading} {...field} value={field.value ?? ''} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>

          <div className="pt-4 border-t border-slate-100 flex flex-col md:flex-row justify-between items-center gap-4">
            {isReadOnly ? (
              <div className="w-full bg-blue-50/50 border border-blue-100 p-4 rounded-xl flex items-start gap-3">
                <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <Navigation className="w-4 h-4 text-blue-600" />
                </div>
                <div>
                  <h4 className="font-semibold text-blue-900 text-sm">Profile Under Review</h4>
                  <p className="text-sm text-blue-700/80 mt-0.5">
                    Your profile is currently {initialData.verificationStatus}. You cannot edit your details at this time.
                  </p>
                </div>
              </div>
            ) : (
              <>
                <p className="text-sm text-slate-500 font-medium hidden md:block">
                  Ensure all farm details are accurate before submitting for verification.
                </p>
                <Button 
                  type="submit" 
                  disabled={isLoading} 
                  className="w-full md:w-auto min-w-[200px] bg-[#184E48] hover:bg-[#184E48]/90 text-white rounded-xl py-6 text-[15px] font-bold shadow-[0_8px_30px_rgb(24,78,72,0.2)] hover:shadow-[0_8px_30px_rgb(24,78,72,0.3)] hover:-translate-y-0.5 transition-all duration-300"
                >
                  {isLoading ? 'Saving...' : (initialData ? 'Update Profile' : 'Create Profile')}
                </Button>
              </>
            )}
          </div>
        </form>
      </Form>
    </div>
  )
}

