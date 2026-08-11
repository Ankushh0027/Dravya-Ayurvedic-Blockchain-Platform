import { LandingNavbar } from '@/features/landing/components/LandingNavbar'
import { Footer } from '@/features/landing/components/Footer'
import { HowItWorks } from '@/features/landing/components/HowItWorks'
import { FloatingLeaf } from '@/features/landing/components/FloatingLeaf'
import {
  Leaf,
  FlaskConical,
  Factory,
  Package,
  Users,
  CheckCircle2,
  ArrowRight,
  ShieldCheck,
  Zap,
  UserCheck,
  QrCode,
  BrainCircuit,
  Landmark,
  Star,
  Award,
} from 'lucide-react'
import Link from 'next/link'
import { Button } from '@/components/ui/button'

const detailedSteps = [
  {
    icon: UserCheck,
    number: '01',
    title: 'Role Selection & Login',
    subtitle: 'Multi-Role Stakeholder Portal',
    description:
      'Any user accessing Dravya selects their specific role: Farmer, Distributor, Manufacturer, Verification Officer, or Consumer. Role-gated dashboards ensure each stakeholder accesses customized smart contract actions and verified access levels.',
    details: [
      'Role selection upon portal login (Farmer, Manufacturer, Distributor, Officer)',
      'Secure wallet & identity key creation',
      'Role-based access control (RBAC) for smart contracts',
      'Unified single sign-on with cryptographic verification',
    ],
  },
  {
    icon: QrCode,
    number: '02',
    title: 'Batch Creation & QR Match Verification',
    subtitle: 'Digital Genesis & Custody Transfer',
    description:
      'The farmer/collector registers a batch with farm GPS, species name, and harvest date. Dravya generates a unique batch QR code. At every custody transfer (Farmer → Distributor → Manufacturer), scanning the QR code instantly verifies if it is the exact registered batch.',
    details: [
      'GPS-tagged origin logging & digital batch minting',
      'Unique tamper-proof QR code generated for every batch',
      'Instant mobile QR scan to confirm batch identity on transfer',
      'Prevents batch substitution or counterfeiting',
    ],
  },
  {
    icon: BrainCircuit,
    number: '03',
    title: 'AI Species & Quality Prediction',
    subtitle: 'ML Botanical Authenticity Engine',
    description:
      'Before processing, raw herb samples are scanned by Dravya AI models. Computer vision and predictive analysis evaluate species purity, moisture levels, active compounds (e.g. Withanolides in Ashwagandha), and detect potential adulteration.',
    details: [
      'AI species prediction & visual purity check',
      'Active phytochemical compound estimation',
      'Automated adulteration detection alerts',
      'Instant confidence score stored alongside lab results',
    ],
  },
  {
    icon: Landmark,
    number: '04',
    title: 'Verification Officers (At Scale)',
    subtitle: 'Institutional & Government Audit Portal',
    description:
      'As Dravya expands to nationwide scale, certified AYUSH & Government Verification Officers log into specialized auditor dashboards. Officers inspect physical inventory, validate lab reports, and anchor digital verification sign-offs on the blockchain.',
    details: [
      'Dedicated Verification Officer login portal',
      'Institutional AYUSH compliance audit workflows',
      'Multi-signature on-chain verification stamps',
      'Nationwide scalable regulatory oversight',
    ],
  },
  {
    icon: Package,
    number: '05',
    title: 'Manufacturer & Logistics Ledger',
    subtitle: 'Immutable Processing & Custodial Trail',
    description:
      'Manufacturers accept verified batches and log processing parameters (temperature, extract ratio, batch splitting). Distributors update transit timestamps and environmental logs on the immutable blockchain ledger.',
    details: [
      'Unbroken chain of custody from farm to factory',
      'Environmental & temperature tracking integration',
      'Batch splitting & formulation lineage',
      'Tamper-proof blockchain transaction records',
    ],
  },
  {
    icon: Star,
    number: '06',
    title: 'Consumer Scan & Batch Rating System',
    subtitle: 'Public Transparency & Supplier Scores',
    description:
      'End consumers scan the QR code on the final packaging to view the complete journey map. Consumers can leave reviews and star ratings tied directly to that batch number, providing transparent public feedback on seller quality.',
    details: [
      'Instant consumer QR scan (<2 seconds) for complete origin map',
      'Batch-specific rating & review desk for consumers',
      'Transparent seller quality score based on verified batch reviews',
      'Builds market credibility for authentic Ayurvedic producers',
    ],
  },
]

export default function HowItWorksPage() {
  return (
    <div className="min-h-screen flex flex-col bg-white relative font-sans overflow-x-hidden">
      <LandingNavbar className="bg-[#184E48]" />

      {/* Hero Section */}
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
          <FloatingLeaf className="w-full h-auto text-[#184E48]" rotate={-40} />
        </div>
        <div className="absolute bottom-10 right-12 w-[85px] lg:w-[110px] pointer-events-none z-0 opacity-25 mix-blend-multiply">
          <FloatingLeaf className="w-full h-auto text-[#184E48]" rotate={110} />
        </div>

        <div className="relative z-10 max-w-4xl mx-auto">
          {/* AYUSH Anveshan Reference Tag */}
          <div className="inline-flex items-center gap-2 bg-[#184E48]/10 text-[#184E48] text-sm font-semibold px-5 py-2 rounded-full mb-6 border border-[#184E48]/20 shadow-sm">
            <Award className="w-4 h-4 text-[#184E48]" />
            Referencing Anveshan — Ministry of AYUSH Initiative
          </div>

          {/* Heading */}
          <h1 className="text-4xl md:text-6xl lg:text-[4.5rem] font-bold tracking-tight text-[#1e293b] leading-[1.08] font-serif mb-6">
            Dravya Traceability Architecture.
            <span className="block text-[#184E48] mt-2">AI & Blockchain Powered.</span>
          </h1>

          {/* Subtitle */}
          <p className="text-[17px] md:text-[19px] lg:text-[20px] text-slate-600 leading-relaxed font-medium max-w-3xl mx-auto mb-10">
            Learn how Dravya empowers Farmers, Distributors, Manufacturers, Verification Officers, and Consumers with role-based access, QR batch verification, AI prediction models, and a consumer batch rating system.
          </p>

          {/* Action CTAs */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link href="/verify">
              <Button
                size="lg"
                className="bg-[#184E48] hover:bg-[#184E48]/90 text-white rounded-xl px-8 py-6 text-[16px] font-semibold shadow-[0_8px_30px_rgb(24,78,72,0.2)] hover:shadow-[0_8px_30px_rgb(24,78,72,0.3)] hover:-translate-y-0.5 transition-all duration-300 group flex items-center justify-center gap-2"
              >
                Start Batch Verification
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </Button>
            </Link>
            <Link href="/register">
              <Button
                size="lg"
                variant="outline"
                className="border-[#184E48] bg-white hover:bg-slate-50 text-[#184E48] rounded-xl px-8 py-6 text-[16px] font-bold shadow-sm hover:shadow-md hover:-translate-y-0.5 transition-all duration-300"
              >
                Choose Your Role
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Interactive Step Carousel Component */}
      <HowItWorks />

      {/* Deep Dive Section - Soft Herbal Background */}
      <section className="py-20 lg:py-28 bg-[#E1E9E1]/30 border-y border-[#184E48]/10 relative overflow-hidden">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center mb-16">
            <span className="text-[#184E48] font-bold text-xs uppercase tracking-widest bg-[#184E48]/10 px-3.5 py-1.5 rounded-full inline-block mb-3">
              Comprehensive Workflow Breakdown
            </span>
            <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-[#1e293b] font-serif">
              What happens at each stage of Dravya?
            </h2>
            <p className="text-slate-600 mt-4 max-w-2xl mx-auto text-base font-medium">
              Detailed breakdown of how user roles, batch QR code verification, AI predictions, AYUSH verification officers, and batch rating systems work together.
            </p>
          </div>

          <div className="space-y-8">
            {detailedSteps.map((step) => {
              const Icon = step.icon
              return (
                <div
                  key={step.title}
                  className="group flex flex-col lg:flex-row gap-8 bg-white border border-slate-200/80 rounded-3xl p-8 hover:shadow-2xl hover:shadow-[#184E48]/10 hover:border-[#184E48]/30 transition-all duration-500"
                >
                  {/* Step icon + number */}
                  <div className="flex-shrink-0 flex flex-row lg:flex-col items-center lg:items-start gap-4">
                    <div className="w-16 h-16 rounded-2xl bg-[#184E48] flex items-center justify-center shadow-lg shadow-[#184E48]/30 group-hover:scale-110 transition-transform duration-400">
                      <Icon className="w-8 h-8 text-white" />
                    </div>
                    <div>
                      <span className="text-3xl font-black text-[#184E48]/30 font-serif">
                        {step.number}
                      </span>
                    </div>
                  </div>

                  {/* Content */}
                  <div className="flex-1">
                    <div className="flex flex-wrap items-center gap-3 mb-3">
                      <h3 className="text-2xl font-bold text-[#1e293b] font-serif">{step.title}</h3>
                      <span className="text-xs font-bold text-[#184E48] bg-[#184E48]/10 px-3 py-1 rounded-full uppercase tracking-widest border border-[#184E48]/20">
                        {step.subtitle}
                      </span>
                    </div>
                    <p className="text-slate-600 leading-relaxed mb-6 font-medium text-base">{step.description}</p>
                    <div className="grid sm:grid-cols-2 gap-3 bg-slate-50 p-5 rounded-2xl border border-slate-100">
                      {step.details.map((d) => (
                        <div key={d} className="flex items-start gap-2.5">
                          <CheckCircle2 className="w-4 h-4 text-[#184E48] flex-shrink-0 mt-0.5" />
                          <span className="text-xs md:text-sm text-slate-700 font-semibold">{d}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </section>

      {/* Core Innovation Highlights Section */}
      <section className="py-20 bg-white border-b border-slate-100">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center mb-14">
            <span className="text-[#184E48] font-bold text-xs uppercase tracking-widest bg-[#184E48]/10 px-3.5 py-1.5 rounded-full inline-block mb-3">
              Platform Pillars
            </span>
            <h2 className="text-3xl md:text-4xl font-bold text-[#1e293b] font-serif">
              Why Dravya sets the gold standard for Ayurvedic herbs
            </h2>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="bg-[#E1E9E1]/20 border border-[#184E48]/15 rounded-3xl p-8 hover:shadow-xl transition-all duration-300">
              <div className="w-14 h-14 rounded-2xl bg-[#184E48] text-white flex items-center justify-center mb-6 shadow-md shadow-[#184E48]/20">
                <BrainCircuit className="w-7 h-7" />
              </div>
              <h3 className="text-xl font-bold text-[#1e293b] mb-3 font-serif">AI Prediction & Verification</h3>
              <p className="text-slate-600 text-sm leading-relaxed">
                Using machine learning to predict herb authenticity and active compound levels before batch approval, preventing market adulteration.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="bg-[#E1E9E1]/20 border border-[#184E48]/15 rounded-3xl p-8 hover:shadow-xl transition-all duration-300">
              <div className="w-14 h-14 rounded-2xl bg-[#184E48] text-white flex items-center justify-center mb-6 shadow-md shadow-[#184E48]/20">
                <Landmark className="w-7 h-7" />
              </div>
              <h3 className="text-xl font-bold text-[#1e293b] mb-3 font-serif">Scalable Verification Officers</h3>
              <p className="text-slate-600 text-sm leading-relaxed">
                Enabling certified AYUSH & Government Verification Officers to audit batches physically and stamp digital signatures on the blockchain.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="bg-[#E1E9E1]/20 border border-[#184E48]/15 rounded-3xl p-8 hover:shadow-xl transition-all duration-300">
              <div className="w-14 h-14 rounded-2xl bg-[#184E48] text-white flex items-center justify-center mb-6 shadow-md shadow-[#184E48]/20">
                <Star className="w-7 h-7" />
              </div>
              <h3 className="text-xl font-bold text-[#1e293b] mb-3 font-serif">Batch Rating & Reviews</h3>
              <p className="text-slate-600 text-sm leading-relaxed">
                Empowering consumers and buyers to review specific batches, creating transparent quality ratings for farmers, manufacturers, and sellers.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Bottom CTA Banner */}
      <section className="py-16 px-6 bg-white">
        <div className="max-w-6xl mx-auto bg-[#184E48] rounded-[2.5rem] p-10 lg:p-16 text-center relative overflow-hidden shadow-2xl shadow-[#184E48]/25 text-white">
          <div className="absolute -top-10 -right-10 w-[160px] pointer-events-none opacity-20 text-white">
            <FloatingLeaf className="w-full h-auto" rotate={45} />
          </div>
          <div className="absolute -bottom-10 -left-10 w-[140px] pointer-events-none opacity-20 text-white">
            <FloatingLeaf className="w-full h-auto" rotate={-120} />
          </div>

          <div className="relative z-10 max-w-2xl mx-auto">
            <h2 className="text-3xl md:text-4xl font-bold font-serif mb-4 leading-tight">
              Ready to verify or log your herb batch?
            </h2>
            <p className="text-slate-200 text-base md:text-lg mb-8 leading-relaxed">
              Join Dravya — whether you are a Farmer, Manufacturer, Distributor, Verification Officer, or Consumer.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/register">
                <Button className="w-full sm:w-auto bg-white text-[#184E48] hover:bg-slate-100 font-bold rounded-xl px-8 py-6 text-base shadow-lg hover:-translate-y-0.5 transition-all gap-2">
                  Select Your Role & Join <ArrowRight className="w-4 h-4" />
                </Button>
              </Link>
              <Link href="/verify">
                <Button variant="outline" className="w-full sm:w-auto border-white/30 text-white bg-white/10 hover:bg-white/20 rounded-xl px-8 py-6 text-base font-semibold backdrop-blur-sm">
                  Scan / Verify Batch
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
