import { RegisterForm } from "@/features/auth/components/registerform"
import { LandingNavbar } from '@/features/landing/components/LandingNavbar'
import { HowItWorks } from '@/features/landing/components/HowItWorks'
import { Footer } from '@/features/landing/components/Footer'
import { LoginForm } from '@/features/auth/components/LoginForm'
import { LeafSprig } from '@/features/landing/components/LeafSprig'
import { FloatingLeaf } from '@/features/landing/components/FloatingLeaf'

export default function RegisterPage(){
  return (
  <div className="min-h-screen  bg-[#F8F9FA] relative font-sans overflow-x-hidden">
    <LandingNavbar/>
    <div className="flex justify-center items-center ">
 <RegisterForm/>
    </div>
   



  </div>)
 
}