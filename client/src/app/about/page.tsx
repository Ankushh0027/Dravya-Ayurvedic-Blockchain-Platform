'use client'
import { LandingNavbar } from '@/features/landing/components/LandingNavbar'
import { Footer } from '@/features/landing/components/Footer'
import { FloatingLeaf } from '@/features/landing/components/FloatingLeaf'
import {
  ShieldCheck,
  Leaf,
  Globe,
  Award,
  Sprout,
  FlaskConical,
  ArrowRight,
  Lightbulb,
  Code2,
  Shrub,
  Sparkle,
} from 'lucide-react'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { ContactPreviewCard } from '@/components/shared/contapre'
import { TeamCarousel } from '@/features/landing/components/teamScroll'

const timeline = [
  {
    id: 1,
    number: '01',
    icon: Lightbulb,
    title: 'The Idea',
    desc: 'Noticed how often ayurvedic products like Adivasi Oil were being sold as counterfeit, and realized traceability across the Ayurvedic supply chain was almost non-existent.',
    accent: 'from-emerald-500/20 to-teal-500/10',
  },
  {
    id: 2,
    number: '02',
    icon: Code2,
    title: 'Development Begins',
    desc: 'Started building Dravya, referencing frameworks like Anvesha and Ministry of AYUSH guidelines to shape the traceability model.',
    accent: 'from-cyan-500/20 to-blue-500/10',
  },
  {
    id: 3,
    number: '03',
    icon: Shrub,
    title: 'Scale & Go Live',
    desc: 'Expanding to more producers, manufacturers, and labs nationwide, while integrating AI — including a chatbot assistant — to make the platform more interactive and accessible.',
    accent: 'from-violet-500/20 to-purple-500/10',
  },
  {
    id: 4,
    number: '04',
    icon: Sparkle,
    title: 'Future Horizons',
    desc: 'We are constantly adding new AI capabilities, laboratory integrations, and enhanced blockchain auditing tools to Dravya. Stay tuned for more features!',
    accent: 'from-amber-500/20 to-orange-500/10',
  },
]

export default function AboutPage() {
  return (
    <div className="min-h-screen flex flex-col bg-white relative font-sans overflow-x-hidden">
      <LandingNavbar className="bg-[#184E48]" />

      {/* Hero Section - Matching Home Page Light Style */}
      <section className="relative flex-1 flex flex-col justify-center items-center px-6 lg:px-24 py-16 lg:py-24 relative z-10 w-full max-w-[1600px] mx-auto text-center">
        {/* Logo Watermark Background */}
        <div
          className="absolute inset-0 z-0 opacity-[0.07] pointer-events-none mix-blend-multiply flex items-center justify-center"
          style={{
            backgroundImage: 'url("/logo.png")',
            backgroundSize: '800px',
            backgroundPosition: 'center center',
            backgroundRepeat: 'no-repeat',
          }}
        />

        {/* Decorative Floating Leaves */}
        <div className="absolute top-12 left-10 w-[90px] lg:w-[120px] pointer-events-none z-0 opacity-25 mix-blend-multiply">
          <FloatingLeaf className="w-full h-auto text-[#184E48]" rotate={-35} />
        </div>
        <div className="absolute bottom-10 right-12 w-[85px] lg:w-[110px] pointer-events-none z-0 opacity-25 mix-blend-multiply">
          <FloatingLeaf className="w-full h-auto text-[#184E48]" rotate={105} />
        </div>

        <div className="relative z-10 max-w-4xl mx-auto">
         

          {/* Heading */}
          <h1 className="text-4xl md:text-6xl lg:text-[4.75rem] font-bold tracking-tight text-[#1e293b] leading-[1.08] font-serif mb-6">
            Ayurveda Deserves
            <span className="block text-[#184E48] mt-2">Proof, Not Promises.</span>
          </h1>

          {/* Subtitle */}
          <p className="text-[17px] md:text-[19px] lg:text-[20px] text-slate-600 leading-relaxed font-medium max-w-2xl mx-auto mb-10">
            Ayurvedic medicine runs on trust — but trust without proof is just a promise. Dravya
  makes that proof possible, tracking every herb from the soil it grew in to the shelf
  it reaches.
          </p>

          {/* Action CTAs */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link href="/features">
              <Button
                size="lg"
                className="bg-[#184E48] hover:bg-[#184E48]/90 text-white rounded-xl px-8 py-6 text-[16px] font-semibold shadow-[0_8px_30px_rgb(24,78,72,0.2)] hover:shadow-[0_8px_30px_rgb(24,78,72,0.3)] hover:-translate-y-0.5 transition-all duration-300 group flex items-center justify-center gap-2"
              >
                Explore Features
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </Button>
            </Link>
            <Link href="/contact">
              <Button
                size="lg"
                variant="outline"
                className="border-[#184E48] bg-white hover:bg-slate-50 text-[#184E48] rounded-xl px-8 py-6 text-[16px] font-bold shadow-sm hover:shadow-md hover:-translate-y-0.5 transition-all duration-300"
              >
                Get in Touch
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Mission Section - Warmer Herbal Background */}
      <section className="relative py-20 lg:py-28 bg-[#E1E9E1]/30 border-y border-[#184E48]/10 overflow-hidden">
        {/* Glow & Leaves */}
        <div className="absolute top-1/2 left-0 -translate-y-1/2 w-[600px] h-[600px] bg-[#184E48]/5 rounded-full blur-[100px] pointer-events-none" />
        <div className="absolute top-8 right-16 w-[110px] pointer-events-none z-0 opacity-15 mix-blend-multiply animate-pulse">
          <FloatingLeaf className="w-full h-auto text-[#184E48]" rotate={45} />
        </div>

        <div className="relative z-10 max-w-7xl mx-auto px-6 lg:px-12">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
      <div>
 
  <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-[#1e293b] font-serif mt-2 mb-6 leading-tight">
    Bringing transparency to Ayurveda
  </h2>
  <p className="text-slate-600 text-lg leading-relaxed mb-6 font-medium">
    Adulteration, mislabeling, and counterfeit herbs quietly erode trust in Ayurvedic
    medicine. Dravya exists to close that gap — connecting ancient wisdom with modern
    accountability.
  </p>
  <p className="text-slate-600 text-lg leading-relaxed mb-8 font-medium">
    We combine blockchain immutability with AI-powered verification to create an unbroken,
    tamper-proof record — from farm to pharmacy.
  </p>
  <Link href="/features">
    <Button className="bg-[#184E48] hover:bg-[#184E48]/90 text-white rounded-xl px-7 py-6 text-[15px] font-semibold gap-2 flex items-center shadow-md shadow-[#184E48]/20 hover:-translate-y-0.5 transition-all">
      Explore Platform Capabilities <ArrowRight className="w-4 h-4" />
    </Button>
  </Link>
</div>

          <ContactPreviewCard headerClassName="bg-[#184E48]" />
        
          </div>
        </div>
      </section>

      
      {/* Timeline Section */}
      <section className="py-20 lg:py-28 bg-white max-w-5xl mx-auto px-6 w-full">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-[#184E48] font-serif">
            How We Got Here
          </h2>
          <p className="text-slate-600 mt-4 text-base max-w-lg mx-auto font-medium">
            Building the infrastructure for authentic, tamper-proof herbal medicine.
          </p>
        </div>

        <div className="relative">
          {/* Vertical connector line */}
          <div className="hidden lg:block absolute left-[2.75rem] top-8 bottom-8 w-px bg-gradient-to-b from-[#184E48]/30 via-[#184E48]/60 to-[#184E48]/30" />

          <div className="space-y-6 lg:space-y-8">
            {timeline.map((m) => {
              const Icon = m.icon
              return (
                <div
                  key={m.id}
                  className="group relative flex flex-col lg:flex-row gap-6 lg:gap-8"
                >
                  {/* Left side: icon + number */}
                  <div className="flex-shrink-0 flex lg:flex-col items-center lg:items-center gap-4 lg:gap-2 lg:w-[5.5rem]">
                    <div className="w-14 h-14 lg:w-[5.5rem] lg:h-14 rounded-2xl bg-gradient-to-br from-[#184E48] to-[#0f3530] flex items-center justify-center shadow-xl shadow-[#184E48]/20 group-hover:scale-105 group-hover:shadow-[#184E48]/40 transition-all duration-300 flex-shrink-0 lg:ml-1">
                      <Icon className="w-7 h-7 text-white" />
                    </div>
                    <span className="text-2xl lg:text-3xl font-black text-[#184E48]/20 font-serif lg:ml-2 lg:mt-1 select-none">
                      {m.number}
                    </span>
                  </div>

                  {/* Card with semicircle accent corner */}
                  <div className="flex-1 bg-white border border-slate-200/80 rounded-3xl p-7 lg:p-8 hover:shadow-2xl hover:shadow-[#184E48]/8 hover:border-[#184E48]/20 transition-all duration-500 relative overflow-hidden">
                    <div className={`absolute top-0 right-0 w-40 h-40 bg-gradient-to-bl ${m.accent} rounded-bl-full opacity-60 pointer-events-none`} />

                    <div className="relative z-10">
                      <h3 className="text-2xl font-bold text-[#184E48] font-serif mb-3">{m.title}</h3>
                      <p className="text-slate-600 leading-relaxed font-medium text-base">
                        {m.desc}
                      </p>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </section>

      {/* Team Section - Warmer Herbal Background */}
      <section className="py-20 lg:py-28  relative overflow-hidden">
        
            
          <TeamCarousel/>
       
        
      </section>

     

      <Footer className="bg-[#184E48]" />
    </div>
  )
}
