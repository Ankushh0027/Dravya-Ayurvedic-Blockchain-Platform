'use client'
import React, { useState } from 'react'
import { LandingNavbar } from '@/features/landing/components/LandingNavbar'
import { Footer } from '@/features/landing/components/Footer'
import { HowItWorks } from '@/features/landing/components/HowItWorks'
import { FloatingLeaf } from '@/features/landing/components/FloatingLeaf'
import { VeinMapJourney } from '@/features/landing/components/VeinMapJourney'
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
  Sprout,
  ScanLine,
  BadgeCheck,
  TrendingUp,
  FileText,
  ClipboardCheck,
  Search,
  BarChart3,
  Lock,
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
    accent: 'from-emerald-500/20 to-teal-500/10',
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
    accent: 'from-cyan-500/20 to-blue-500/10',
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
    accent: 'from-violet-500/20 to-purple-500/10',
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
    accent: 'from-amber-500/20 to-orange-500/10',
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
    accent: 'from-rose-500/20 to-pink-500/10',
  },
  {
    icon: Star,
    number: '06',
    title: 'Consumer Scan & Batch Rating System',
    subtitle: 'Public Transparency & Supplier Scores',
    description:
      'End consumers scan the QR code on the final packaging to view the complete journey map. Consumers can leave reviews and star ratings tied directly to that batch number, providing transparent public feedback on seller quality.',
    details: [
      'Instant consumer QR scan for complete origin map',
      'Batch-specific rating & review desk for consumers',
      'Transparent seller quality score based on verified batch reviews',
      'Builds market credibility for authentic Ayurvedic producers',
    ],
    accent: 'from-lime-500/20 to-green-500/10',
  },
]

const roleData = [
  {
    id: 'farmer',
    label: 'Farmer',
    icon: Sprout,
    headline: 'Your harvest earns the trust it deserves',
    tagline: 'From your field to the blockchain — every harvest verified.',
    description:
      'Dravya gives farmers a powerful digital identity for every herb batch they grow. Register your farm, log harvest details with GPS coordinates, and mint a tamper-proof QR code. Buyers instantly know your batch is genuine — and your reputation grows with every verified delivery.',
    steps: [
      { icon: Sprout,     title: 'Register Your Farm & Batch',      desc: 'Log your farm GPS location, herb species, harvest date and quantity. Dravya mints a unique on-chain batch record.' },
      { icon: QrCode,     title: 'Receive Your Batch QR Code',      desc: 'A tamper-proof QR code is generated for your batch — the digital passport that travels with your herbs.' },
      { icon: TrendingUp, title: 'Build Your Verified Reputation',   desc: 'Every successful delivery earns you a public quality score. Buyers prefer farmers with verified, rated batches.' },
      { icon: BarChart3,  title: 'Track Batch Journey in Real-Time', desc: 'See exactly where your batch is — from your farm to the manufacturer — with full custody transfer logs.' },
    ],
    badge: 'Farmer Portal',
  },
  {
    id: 'manufacturer',
    label: 'Manufacturer',
    icon: Factory,
    headline: 'Guarantee the purity of what you manufacture',
    tagline: 'Process with confidence. Every input verified before it enters your facility.',
    description:
      "Manufacturers receive blockchain-verified herb batches and log every processing step — from extraction ratios to environmental conditions. Dravya's AI pre-screens incoming raw material quality so you only work with authenticated inputs, protecting your brand and compliance record.",
    steps: [
      { icon: ScanLine,     title: 'Scan & Accept Incoming Batches', desc: "Scan the farmer's QR code to instantly verify batch origin, AI quality score, and chain of custody before accepting." },
      { icon: BrainCircuit, title: 'AI Quality Pre-Check',            desc: 'Dravya AI models run species purity and compound analysis on incoming batches, flagging adulterated or substandard inputs.' },
      { icon: FileText,     title: 'Log Processing Parameters',       desc: 'Record extraction ratios, temperature, formulation details and batch splits — every parameter anchored immutably on-chain.' },
      { icon: Package,      title: 'Mint Final Product QR',           desc: 'Generate a final product QR linking finished goods back to the verified raw input batch for end-to-end traceability.' },
    ],
    badge: 'Manufacturer Portal',
  },
  {
    id: 'lab',
    label: 'Lab',
    icon: FlaskConical,
    headline: 'Turn your lab reports into on-chain evidence',
    tagline: 'Your analysis anchors scientific truth on an immutable ledger.',
    description:
      'Accredited laboratories connect directly to Dravya to upload certified test results — phytochemical profiles, heavy metal panels, microbial counts — tied to a specific batch hash. Lab findings are immutably stored and instantly accessible to manufacturers, officers, and consumers.',
    steps: [
      { icon: FlaskConical, title: 'Receive Batch Sample Request',      desc: 'Dravya flags incoming batches requiring lab analysis. Labs receive sample metadata and batch QR hash for traceability.' },
      { icon: Search,       title: 'Run Certified Analysis',             desc: 'Conduct phytochemical, microbial, and heavy metal tests. Upload results with your accreditation certificate reference.' },
      { icon: FileText,     title: 'Anchor Report On-Chain',             desc: 'Your signed lab report is hashed and anchored on the blockchain alongside the batch record — tamper-proof and timestamped.' },
      { icon: CheckCircle2, title: 'Enable Downstream Verification',     desc: 'Manufacturers, verification officers, and consumers can instantly verify your lab report is genuine and unaltered.' },
    ],
    badge: 'Lab Portal',
  },
  {
    id: 'authority',
    label: 'Verification Authority',
    icon: BadgeCheck,
    headline: 'Anchor regulatory trust directly on the blockchain',
    tagline: 'Audit with confidence. Sign with authority. Enforce at scale.',
    description:
      'Certified AYUSH & Government Verification Officers get a dedicated auditor portal. Review physical inventory, validate laboratory reports, and stamp multi-signature digital approvals on-chain. Every officer action is immutably recorded, creating a nationwide, tamper-proof compliance trail.',
    steps: [
      { icon: Search,         title: 'Access Dedicated Auditor Dashboard', desc: 'View all pending batch verifications across registered farmers and manufacturers in your jurisdiction.' },
      { icon: ClipboardCheck, title: 'Inspect & Validate Lab Reports',      desc: 'Cross-reference physical inventory with AI predictions and submitted lab reports before issuing a compliance clearance.' },
      { icon: Lock,           title: 'Stamp Multi-Sig On-Chain Approval',   desc: 'Issue your cryptographic verification signature — anchored on-chain, visible to all downstream stakeholders.' },
      { icon: Landmark,       title: 'Nationwide Scalable Oversight',        desc: 'Monitor regulatory compliance across thousands of batches in real-time with AYUSH-grade audit trails.' },
    ],
    badge: 'Officer Portal',
  },
]

function RoleSelector() {
  const [activeRole, setActiveRole] = useState('farmer')
  const role = roleData.find((r) => r.id === activeRole)!
  const Icon = role.icon

  return (
    <section className="py-20 lg:py-28 bg-[#E1E9E1]/30 border-b border-[#184E48]/10 relative overflow-hidden">
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[500px] h-[500px] bg-[#184E48]/[0.03] rounded-full blur-3xl pointer-events-none" />
      <div className="absolute top-1/2 left-1/3 w-72 h-72 bg-[#184E48]/[0.04] rounded-full blur-2xl pointer-events-none" />

      <div className="max-w-5xl mx-auto px-6 relative z-10">
        <div className="text-center mb-12">
          
          <h2 className="text-2xl md:text-3xl lg:text-5xl font-bold font-serif text-slate-900 leading-tight">
            See how Dravya works{' '}
            <span className="text-[#184E48]">for you</span>
          </h2>
          <p className="mt-4 text-slate-600 text-base max-w-xl mx-auto font-medium">
            Select your role to see a tailored walkthrough of your Dravya experience.
          </p>
        </div>

        <div className="flex flex-wrap justify-center gap-4 mb-10">
          {roleData.map((r) => {
            const RIcon = r.icon
            const isActive = activeRole === r.id
            return (
              <button
                key={r.id}
                onClick={() => setActiveRole(r.id)}
                className={[
                  'inline-flex items-center gap-2.5 px-6 py-3 rounded-2xl text-sm font-bold border transition-all duration-300 cursor-pointer select-none',
                  isActive
                    ? 'bg-[#184E48] text-white border-[#184E48] shadow-lg shadow-[#184E48]/25 scale-105'
                    : 'bg-[#E1E9E1]/30 text-[#184E48] border-[#184E48]/20 hover:border-[#184E48]/50 hover:bg-white hover:shadow-md hover:scale-[1.02]',
                ].join(' ')}
              >
                <RIcon className="w-5 h-5 flex-shrink-0" strokeWidth={2} />
                <span>{r.label}</span>
              </button>
            )
          })}
        </div>

        <div
          key={activeRole}
          className="group relative rounded-3xl bg-white border border-[#184E48]/15 shadow-md shadow-[#184E48]/[0.05] hover:border-[#184E48]/40 hover:shadow-2xl hover:shadow-[#184E48]/15 transition-all duration-500 overflow-hidden"
          style={{ animation: 'roleFadeIn 0.38s cubic-bezier(0.22,1,0.36,1)' }}
        >
          <div className="absolute top-0 left-0 right-0 h-1.5 bg-[#184E48] opacity-100 transition-opacity duration-500" />

          <div className="absolute -right-4 -top-6 text-[120px] font-black text-slate-900/[0.03] pointer-events-none select-none z-0">
            {String(roleData.findIndex((r) => r.id === activeRole) + 1).padStart(2, '0')}
          </div>

          <div className="relative z-10 p-8 lg:p-10">
            <div className="flex flex-col sm:flex-row sm:items-start gap-5 mb-8">
              <div className="flex-shrink-0 w-16 h-16 rounded-2xl bg-[#184E48] text-white flex items-center justify-center shadow-lg shadow-[#184E48]/25 group-hover:bg-white group-hover:text-[#184E48] group-hover:border-2 group-hover:border-[#184E48] transform group-hover:scale-110 group-hover:rotate-3 transition-all duration-500">
                <Icon className="w-8 h-8 transition-colors duration-300" strokeWidth={1.75} />
              </div>

              <div className="flex-1">
                <div className="flex flex-wrap items-center gap-3 mb-2">
                  <h3 className="text-2xl md:text-3xl font-bold font-serif text-slate-900 group-hover:text-[#184E48] transition-colors duration-300">
                    {role.headline}
                  </h3>
                  <span className="inline-flex items-center gap-1 text-[11px] font-bold uppercase tracking-wider px-2.5 py-1 rounded-md bg-[#184E48]/10 text-[#184E48] border border-[#184E48]/20">
                    {role.badge}
                  </span>
                </div>
                <p className="text-slate-600 text-sm md:text-base leading-relaxed font-medium max-w-2xl">
                  {role.description}
                </p>
              </div>
            </div>

            <div className="grid sm:grid-cols-2 gap-4">
              {role.steps.map((step, i) => {
                const SIcon = step.icon
                return (
                  <div
                    key={i}
                    className="bg-[#f8faf8] border border-[#184E48]/10 rounded-2xl p-5 flex gap-4 hover:border-[#184E48]/30 hover:shadow-md transition-all duration-300"
                  >
                    <div className="flex-shrink-0 w-10 h-10 rounded-xl bg-[#184E48] text-white flex items-center justify-center shadow shadow-[#184E48]/20">
                      <SIcon className="w-5 h-5" strokeWidth={1.75} />
                    </div>
                    <div>
                      <p className="text-sm font-bold text-[#184E48] mb-1">{step.title}</p>
                      <p className="text-xs text-slate-600 leading-relaxed">{step.desc}</p>
                    </div>
                  </div>
                )
              })}
            </div>

            <div className="pt-5 mt-6 border-t border-slate-100 flex flex-col sm:flex-row items-center justify-between gap-4">
              <p className="text-[12px] font-semibold italic text-slate-500 group-hover:text-[#184E48] transition-colors duration-300">
                "{role.tagline}"
              </p>
              <Link href="/register">
                <span className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-bold text-white bg-[#184E48] shadow shadow-[#184E48]/25 hover:shadow-lg hover:shadow-[#184E48]/30 hover:-translate-y-0.5 transition-all duration-200 cursor-pointer">
                  Get Started as {role.label}
                  <ArrowRight className="w-4 h-4" />
                </span>
              </Link>
            </div>
          </div>

          <div className="absolute inset-0 bg-gradient-to-b from-transparent via-white/50 to-[#184E48]/[0.04] opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none z-0" />
        </div>
      </div>

      <style>{`
        @keyframes roleFadeIn {
          from { opacity: 0; transform: translateY(14px) scale(0.985); }
          to   { opacity: 1; transform: translateY(0)    scale(1);     }
        }
      `}</style>
    </section>
  )
}

export default function HowItWorksPage() {
  return (
    <div className="min-h-screen flex flex-col bg-white relative font-sans overflow-x-hidden">
      <LandingNavbar className="bg-[#184E48]" />

      {/* Hero Section — White bg */}
      <section className="relative flex flex-col justify-center items-center px-6 lg:px-24 py-16 lg:py-24 z-10 w-full max-w-[1600px] mx-auto text-center">
        {/* Decorative Floating Leaves */}
        <div className="absolute top-12 left-10 w-[90px] lg:w-[120px] pointer-events-none z-0 opacity-25 mix-blend-multiply">
          <FloatingLeaf className="w-full h-auto text-[#184E48]" rotate={-40} />
        </div>
        <div className="absolute bottom-10 right-12 w-[85px] lg:w-[110px] pointer-events-none z-0 opacity-25 mix-blend-multiply">
          <FloatingLeaf className="w-full h-auto text-[#184E48]" rotate={110} />
        </div>

        <div className="relative z-10 max-w-6xl mx-auto">
          <h1 className="text-4xl md:text-6xl lg:text-[4.5rem] font-bold tracking-tight text-[#1e293b] leading-[1.08] font-serif mb-6">
            Transparency, Built Into
            <span className="block text-[#184E48] mt-2">Every Batch.</span>
          </h1>

          <p className="text-[17px] md:text-[19px] lg:text-[20px] text-slate-600 leading-relaxed font-medium max-w-3xl mx-auto mb-8">
            Learn how Dravya empowers Farmers, Distributors, Manufacturers, Verification Officers, and Consumers with role-based access, QR batch verification, AI prediction models, and a consumer batch rating system.
          </p>

          <VeinMapJourney />
        </div>
      </section>

      {/* Role Selector Section — Warmer bg */}
      <section className="bg-[#E1E9E1]/30 border-y border-[#184E48]/10">
        <RoleSelector />
      </section>

      {/* Deep Dive Section — Vertical Timeline — White bg */}
      <section className="py-20 lg:py-28 bg-white relative overflow-hidden">
        <div className="max-w-5xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-6xl lg:text-[4.5rem] font-bold tracking-tight text-[#184E48] leading-[1.08] font-serif mb-4">
              WorkFlow Breakdown
            </h2>
            <h3 className="text-3xl md:text-4xl lg:text-5xl font-bold text-[#1e293b] font-serif">
              What happens at each stage of Dravya?
            </h3>
            <p className="text-slate-600 mt-4 max-w-2xl mx-auto text-base font-medium">
              Detailed breakdown of how user roles, batch QR code verification, AI predictions, AYUSH verification officers, and batch rating systems work together.
            </p>
          </div>

          {/* Timeline */}
          <div className="relative">
            {/* Vertical connector line — desktop only */}
            <div className="hidden lg:block absolute left-[2.75rem] top-8 bottom-8 w-px bg-gradient-to-b from-[#184E48]/30 via-[#184E48]/60 to-[#184E48]/30" />

            <div className="space-y-6 lg:space-y-8">
              {detailedSteps.map((step) => {
                const Icon = step.icon
                return (
                  <div
                    key={step.title}
                    className="group relative flex flex-col lg:flex-row gap-6 lg:gap-8"
                  >
                    {/* Left side: icon + number */}
                    <div className="flex-shrink-0 flex lg:flex-col items-center lg:items-center gap-4 lg:gap-2 lg:w-[5.5rem]">
                      <div className="w-14 h-14 lg:w-[5.5rem] lg:h-14 rounded-2xl bg-gradient-to-br from-[#184E48] to-[#0f3530] flex items-center justify-center shadow-xl shadow-[#184E48]/20 group-hover:scale-105 group-hover:shadow-[#184E48]/40 transition-all duration-300 flex-shrink-0 lg:ml-1">
                        <Icon className="w-7 h-7 text-white" />
                      </div>
                      <span className="text-2xl lg:text-3xl font-black text-[#184E48]/20 font-serif lg:ml-2 lg:mt-1 select-none">
                        {step.number}
                      </span>
                    </div>

                    {/* Card */}
                    <div className="flex-1 bg-white border border-slate-200/80 rounded-3xl p-7 lg:p-8 hover:shadow-2xl hover:shadow-[#184E48]/8 hover:border-[#184E48]/20 transition-all duration-500 relative overflow-hidden">
                      {/* Accent gradient corner */}
                      <div className={`absolute top-0 right-0 w-40 h-40 bg-gradient-to-bl ${step.accent} rounded-bl-full opacity-60 pointer-events-none`} />

                      <div className="relative z-10">
                        <div className="flex flex-wrap items-center justify-between gap-3 mb-3">
                          <h3 className="text-2xl font-bold text-[#184E48] font-serif">{step.title}</h3>
                          {step.subtitle && (
                            <span className="inline-flex items-center gap-1 text-[11px] font-bold uppercase tracking-wider px-2.5 py-1 rounded-md bg-[#184E48]/10 text-[#184E48] border border-[#184E48]/20">
                              {step.subtitle}
                            </span>
                          )}
                        </div>

                        <p className="text-slate-600 leading-relaxed mb-6 font-medium text-base">
                          {step.description}
                        </p>

                        <div className="grid sm:grid-cols-2 gap-3 bg-[#f8faf8] p-5 rounded-2xl border border-[#184E48]/10">
                          {step.details.map((d) => (
                            <div key={d} className="flex items-start gap-2.5">
                              <CheckCircle2 className="w-4 h-4 text-[#184E48] flex-shrink-0 mt-0.5" />
                              <span className="text-xs md:text-sm text-slate-700 font-semibold">{d}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        </div>
      </section>

      {/* Core Innovation Highlights Section — Warmer bg */}
      <section className="py-20 bg-[#E1E9E1]/30 border-t border-[#184E48]/10">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center mb-14">
           
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

   

      <Footer className="bg-[#184E48]" />
    </div>
  )
}
