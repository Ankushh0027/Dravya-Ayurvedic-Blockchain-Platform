import  {RegisterForm}  from '@/features/auth/components/registerform'
import { LandingNavbar } from '@/features/landing/components/LandingNavbar'
import { Footer } from '@/features/landing/components/Footer'
import { LeafSprig } from '@/features/landing/components/LeafSprig'
import {UserRoundPen, Sprout, Factory, Truck, Store, ShieldCheck,FlaskConical,BadgeCheck} from "lucide-react"
import { Button } from '@/components/ui/button'
import { Smartphone, ChevronDown,ArrowLeft } from 'lucide-react'
import Link from 'next/link'

const roles = [
  {
    icon: Sprout,
    title: "Processor",
    desc: "Handles freshly harvested medicinal herbs, including collection, cleaning, drying, grading, and initial processing before they move to manufacturing."
  },
  {
    icon: Factory,
    title: "Manufacturer",
    desc: "Converts processed medicinal herbs into finished Ayurvedic products while recording formulation, production, batch, and sourcing details."
  },
  {
    icon: FlaskConical,
    title: "Laboratory",
    desc: "Tests medicinal herbs and finished products for identity, purity, quality, and safety, and records verified laboratory results."
  },
  {
    icon: BadgeCheck,
    title: "Verification Authority",
    desc: "Reviews submitted records, laboratory reports, and certifications to verify the authenticity, quality, and traceability of medicinal products."
  },
  {
    icon: ShieldCheck,
    title: "Admin",
    desc: "Manages the Dravya platform, user roles, registrations, verification workflows, records, and overall system activity."
  },
];

export default function RegisterPage(){
  return (
  <div className="min-h-screen bg-[#F8F9FA] relative font-sans overflow-x-hidden">
    <div className="absolute top-[10%] left-0 w-[200px] md:w-[300px] lg:w-[400px] pointer-events-none z-0 opacity-75 mix-blend-multiply transform -translate-x-[15%]">
      <LeafSprig className="w-full h-auto text-primary" />
    </div>
    <div className="absolute top-[44%] left-[36.7%] w-[200px] md:w-[300px] lg:w-[300px] pointer-events-none z-0 opacity-75 mix-blend-multiply transform -translate-x-[15%]">
      <LeafSprig className="w-full h-auto text-primary" flip={true} />
    </div>

      <div className="w-full bg-[#184E48] backdrop-blur-xl border-b border-white/10 shadow-[0_4px_20px_rgb(0,0,0,0.1)] transition-all duration-300">
    <nav className="flex items-center justify-between px-6 py-2.5 max-w-7xl mx-auto w-full">
  <div className="flex items-center gap-3">
    <div className="w-[66px] h-[66px] rounded-full overflow-hidden flex-shrink-0">
      <img
        src="/logo-out.png"
        alt="Dravya"
        className="w-full h-full object-cover object-center"
      />
    </div>

    <div className="flex flex-col justify-center">
      <div className="flex items-center gap-2.5">
        <h1 className="text-xl md:text-2xl font-bold leading-none text-white tracking-tight font-serif">
          Dravya
        </h1>
        <div className="w-[1.5px] h-4 bg-white/30 rounded-full" />
        <span className="text-lg font-medium text-[var(--accent)] leading-none mt-0.5">
          द्रव्य
        </span>
      </div>

      <p className="text-[10px] text-slate-300 font-bold tracking-[0.15em] uppercase mt-1">
        Trust in every herb
      </p>
    </div>
  </div>

  <div className="flex items-center gap-4">
<Link
  href="/"
  className="flex items-center gap-2 text-sm font-bold text-white bg-teal-800 hover:bg-teal-700 transition-colors rounded-lg py-2 px-4"
>
  <ArrowLeft className="w-4 h-4" />
  Back to Home
</Link>

    <Button
      variant="outline"
      className="hidden lg:flex items-center gap-2 rounded-lg border-white/20 bg-white/5 text-white hover:bg-white/10 hover:text-white px-5"
    >
      <Smartphone className="w-4 h-4 text-teal-200" />
      Download App
    </Button>

    <Button
      variant="outline"
      className="flex items-center gap-2 rounded-lg border-white/20 bg-white/5 text-white hover:bg-white/10 hover:text-white px-4"
    >
      English
      <ChevronDown className="w-4 h-4 text-slate-300" />
    </Button>
  </div>
</nav>
    </div>

    <div className="flex flex-col lg:flex-row min-h-[calc(100vh-80px)] relative z-10">

      <div className="w-full lg:w-1/2 flex flex-col items-center justify-center px-6 py-12">
        <UserRoundPen className='h-16 w-16 p-3 bg-accent rounded-full text-white mb-4'/>
      <h1 className="text-2xl md:text-3xl font-extrabold tracking-tight text-[#184E48] leading-[1.1] text-center mb-8 max-w-md font-serif">
          Set up your account to start tracing your batches
        </h1>
        <RegisterForm/>
      </div>

   <div className="w-full lg:w-1/2 bg-gradient-to-br from-[var(--accent)]/10 to-[var(--accent)]/5 border-l border-accent/30 flex flex-col justify-center px-6 py-12 lg:px-16">
        <h2 className="text-2xl md:text-5xl font-sans font-extrabold tracking-tight text-[#184E48] mb-2">
          Who uses Dravya?
        </h2>
        <p className="text-xl text-accent font-bold  mb-10">
          New here? Pick the role that matches what you do.
        </p>

        <div className="flex flex-col gap-4">
          {roles.map(({icon: Icon, title, desc}) => (
            <div key={title} className="group flex gap-4 items-start bg-white/60 hover:bg-white p-4 rounded-2xl border border-accent/20 hover:border-accent/50 border-2 hover:shadow-xl transition-all duration-200">
              <div className="shrink-0 h-12 w-12 rounded-full bg-accent flex items-center justify-center group-hover:scale-105 transition-transform">
                <Icon className="h-5 w-5 text-white"/>
              </div>
              <div>
                <h3 className="font-bold text-[#184E48] text-2xl">{title}</h3>
                <p className="text-sm text-gray-600 leading-snug">{desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

    </div>

    <Footer/>
  </div>)
}