'use client'

import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
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

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'

import { Card, CardContent, CardFooter, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'

import { useRouter } from 'next/navigation'
import { toast } from 'sonner'
import { Eye, EyeOff, ShieldCheck } from 'lucide-react'
import { useState } from 'react'


const formSchema = z.object({

  name: z.string().min(2,{
    message:"Name is required."
  }),
   

  email:z.string().email({
    message:"Please enter a valid email address."
  }),

  password:z.string().min(6,{
    message:"Password must be at least 6 characters."
  }),

  confirmPassword:z.string(),

  role:z.string({
    message:"Please select a role."
  })

}).refine((data)=>data.password===data.confirmPassword,{
  message:"Passwords don't match.",
  path:["confirmPassword"]
})



export function RegisterForm(){

const router = useRouter()

const [showPassword,setShowPassword] = useState(false)
const [showConfirmPassword,setShowConfirmPassword] = useState(false)



const form = useForm<z.infer<typeof formSchema>>({

resolver:zodResolver(formSchema),

defaultValues:{
  name:"",
  email:"",
  password:"",
  confirmPassword:"",
  role:"",
  
}

})



function onSubmit(values:z.infer<typeof formSchema>){

console.log(values)

document.cookie="auth_token=mock_token; path=/"

toast.success("Account created successfully!")

router.push("/dashboard")

}



return (

<Card className="w-[75%] mx-auto shadow-[0_8px_30px_rgb(0,0,0,0.08)] border-0 rounded-2xl bg-[var(--ww)] backdrop-blur-xl">

<CardHeader className="text-center">



</CardHeader>


<CardContent>


<Form {...form}>

<form 
onSubmit={form.handleSubmit(onSubmit)}
className="space-y-4"
>



<FormField

control={form.control}

name="name"

render={({field})=>(

<FormItem>

<FormLabel className="text-slate-700 font-semibold text-sm ml-1">Full Name</FormLabel>

<FormControl>

<Input
placeholder="Enter your name"
 style={{ caretColor: 'black', color: field.value ? 'black' : undefined }}
                        className="pl-9 h-10 border-slate-200/80 bg-slate-50/50 hover:bg-slate-50 rounded-lg focus-visible:ring-[var(--accent)]/40 focus-visible:border-[var(--accent)] transition-all text-base shadow-sm"
{...field}
/>

</FormControl>

<FormMessage/>

</FormItem>

)}

/>



<FormField

control={form.control}

name="email"

render={({field})=>(

<FormItem>

<FormLabel className="text-slate-700 font-semibold text-sm ml-1">Email Address</FormLabel>

<FormControl>

<Input
placeholder="Enter your email"
 style={{ caretColor: 'black', color: field.value ? 'black' : undefined }}
                        className="pl-9 h-10 border-slate-200/80 bg-slate-50/50 hover:bg-slate-50 rounded-lg focus-visible:ring-[var(--accent)]/40 focus-visible:border-[var(--accent)] transition-all text-base shadow-sm"
{...field}
/>

</FormControl>

<FormMessage/>

</FormItem>

)}

/>





<FormField

control={form.control}

name="role"

render={({field})=>(

<FormItem>

<FormLabel className="text-slate-700 font-semibold text-sm ml-1">Select Your Role</FormLabel>


<Select

onValueChange={field.onChange}

defaultValue={field.value}

>

<FormControl>

<SelectTrigger className="h-10 rounded-lg">

<SelectValue placeholder="Select your role"/>

</SelectTrigger>

</FormControl>


<SelectContent>

<SelectItem value="admin">
Admin
</SelectItem>


<SelectItem value="processor">
Processor
</SelectItem>


<SelectItem value="manufacturer">
Manufacturer
</SelectItem>


<SelectItem value="lab">
Lab
</SelectItem>


</SelectContent>


</Select>


<FormMessage/>

</FormItem>

)}

/>




<FormField

control={form.control}

name="password"

render={({field})=>(

<FormItem>

<FormLabel className="text-slate-700 font-semibold text-sm ml-1">Password</FormLabel>


<div className="relative">

<FormControl>

<Input

type={showPassword ? "text":"password"}

placeholder="Create password"

 style={{ caretColor: 'black', color: field.value ? 'black' : undefined }}
                        className="pl-9 h-10 border-slate-200/80 bg-slate-50/50 hover:bg-slate-50 rounded-lg focus-visible:ring-[var(--accent)]/40 focus-visible:border-[var(--accent)] transition-all text-base shadow-sm"

{...field}

/>

</FormControl>


<button

type="button"

onClick={()=>setShowPassword(!showPassword)}

className="absolute right-3 top-2.5 text-slate-400"

>

{

showPassword ?

<EyeOff size={18}/>:

<Eye size={18}/>

}

</button>


</div>


<FormMessage/>

</FormItem>

)}

/>




<FormField

control={form.control}

name="confirmPassword"

render={({field})=>(

<FormItem>

<FormLabel className="text-slate-700 font-semibold text-sm ml-1">Confirm Password</FormLabel>


<div className="relative">


<FormControl>

<Input

type={showConfirmPassword ? "text":"password"}

placeholder="Confirm password"

 style={{ caretColor: 'black', color: field.value ? 'black' : undefined }}
                        className="pl-9 h-10 border-slate-200/80 bg-slate-50/50 hover:bg-slate-50 rounded-lg focus-visible:ring-[var(--accent)]/40 focus-visible:border-[var(--accent)] transition-all text-base shadow-sm"

{...field}

/>

</FormControl>


<button

type="button"

onClick={()=>setShowConfirmPassword(!showConfirmPassword)}

className="absolute right-3 top-2.5 text-slate-400"

>

{

showConfirmPassword ?

<EyeOff size={18}/>:

<Eye size={18}/>

}

</button>


</div>


<FormMessage/>

</FormItem>

)}

/>



<Button

type="submit"

className="w-full h-11 rounded-lg text-base font-semibold"

>

Create Account

</Button>



</form>

</Form>


</CardContent>



<CardFooter className="justify-center border-t pt-4">


<div className="flex items-center gap-2 text-xs text-primary font-semibold">

<ShieldCheck className="w-4 h-4"/>

Secure registration

</div>


</CardFooter>


</Card>


)

}