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
    icon: <Lightbulb/>,
    title: 'The Idea',
    desc: 'Noticed how often ayurvedic products like Adivasi Oil were being sold as counterfeit, and realized traceability across the Ayurvedic supply chain was almost non-existent.',
  },
  {
    id: 2,
    icon: <Code2/>,
    title: 'Development Begins',
    desc: 'Started building Dravya, referencing frameworks like Anvesha and Ministry of AYUSH guidelines to shape the traceability model.',
  },
  {
    id: 3,
    icon:<Shrub/> ,
    title: 'Scale & Go Live',
  desc: 'Expanding to more producers, manufacturers, and labs nationwide, while integrating AI — including a chatbot assistant — to make the platform more interactive and accessible.',
  },
   {
    id: 4,
    icon:<Sparkle/> ,
    title: 'Stay tuned for more features!'
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

      
      <section className="py-20 lg:py-28 bg-white max-w-5xl mx-auto px-6 w-full">
        <div className="text-center mb-16">
         
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-[#1e293b] font-serif">
            How we got here
          </h2>
          <p className="text-slate-600 mt-4 text-base max-w-lg mx-auto font-medium">
            Building the infrastructure for authentic, tamper-proof herbal medicine.
          </p>
        </div>

        <div className="relative">
          {/* Vertical line */}
          <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-[#184E48]/20" />
          <div className="space-y-10">
            {timeline.map((m) => (
              <div key={m.id} className="flex gap-8 items-start relative group">
                <div className="flex-shrink-0 w-16 h-16 rounded-full bg-[#184E48] flex items-center justify-center text-white font-bold text-base z-10 shadow-lg shadow-[#184E48]/30 group-hover:scale-110 transition-transform duration-300">
                  {m.icon}
                </div>
                <div className="bg-white rounded-2xl p-7 shadow-md border border-[#184E48] flex-1 hover:shadow-xl hover:scale-[1.02] transition-all duration-300">
                  <h3 className="text-xl font-bold text-[#1e293b] mb-2 font-serif">{m.title}</h3>
                  <p className="text-slate-600 leading-relaxed font-medium">{m.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Team Section - Warmer Herbal Background */}
      <section className="py-20 lg:py-28  relative overflow-hidden">
        
            
          <TeamCarousel/>
       
        
      </section>

      {/* Bottom CTA Banner - Sleek Forest Green Card Container */}
      <section className="py-16 px-6 bg-white">
        <div className="max-w-6xl mx-auto bg-[#184E48] rounded-[2.5rem] p-10 lg:p-16 text-center relative overflow-hidden shadow-2xl shadow-[#184E48]/25 text-white">
          {/* Background Leaf Accents */}
          <div className="absolute -top-10 -right-10 w-[160px] pointer-events-none opacity-20 text-white">
            <FloatingLeaf className="w-full h-auto" rotate={45} />
          </div>
          <div className="absolute -bottom-10 -left-10 w-[140px] pointer-events-none opacity-20 text-white">
            <FloatingLeaf className="w-full h-auto" rotate={-120} />
          </div>

          <div className="relative z-10 max-w-2xl mx-auto">
            <div className="w-14 h-14 rounded-2xl bg-white/10 flex items-center justify-center mx-auto mb-6 backdrop-blur-md border border-white/20">
              <Award className="w-7 h-7 text-teal-200" />
            </div>
            <h2 className="text-3xl md:text-4xl font-bold font-serif mb-4 leading-tight">
              Join the movement for authentic Ayurveda
            </h2>
            <p className="text-slate-200 text-base md:text-lg mb-8 leading-relaxed">
              Whether you're a farmer, manufacturer, lab, or retailer — Dravya has a place for you in the transparent supply chain.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/contact">
                <Button className="w-full sm:w-auto bg-white text-[#184E48] hover:bg-slate-100 font-bold rounded-xl px-8 py-6 text-base shadow-lg hover:-translate-y-0.5 transition-all">
                  Get in Touch
                </Button>
              </Link>
              <Link href="/features">
                <Button variant="outline" className="w-full sm:w-auto border-white/30 text-white bg-white/10 hover:bg-white/20 rounded-xl px-8 py-6 text-base font-semibold backdrop-blur-sm">
                  See Features
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      <Footer className="bg-[#184E48]" />
    </div>
  )
}
