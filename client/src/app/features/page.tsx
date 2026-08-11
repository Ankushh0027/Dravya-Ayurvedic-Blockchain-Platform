import { LandingNavbar } from '@/features/landing/components/LandingNavbar'
import { Footer } from '@/features/landing/components/Footer'
import { FloatingLeaf } from '@/features/landing/components/FloatingLeaf'
import {
  ShieldCheck,
  FlaskConical,
  Link as LinkIcon,
  Tractor,
  QrCode,
  Brain,
  BarChart3,
  Lock,
  Smartphone,
  Zap,
  CheckCircle2,
  ArrowRight,
  Sprout,
} from 'lucide-react'
import Link from 'next/link'
import { Button } from '@/components/ui/button'

const mainFeatures = [
  {
    icon: Brain,
    title: 'AI-Powered Herb Authentication',
    desc: 'Our computer vision model analyzes herb morphology, color, and texture to detect adulteration with 97.4% accuracy — in seconds.',
    badge: 'Core AI',
    highlights: ['Spectral image analysis', 'Multi-herb detection', 'Instant lab integration', 'Continuous learning model'],
  },
  {
    icon: LinkIcon,
    title: 'Blockchain Traceability',
    desc: 'Every batch, transfer, and quality check is written as an immutable record on-chain. No one can alter or delete the history.',
    badge: 'Blockchain',
    highlights: ['Polygon-based ledger', 'Gas-optimized contracts', 'Cross-chain ready', 'Full audit trail'],
  },
  {
    icon: FlaskConical,
    title: 'Integrated Lab Reports',
    desc: 'Partner labs upload test results directly onto the platform. AI cross-references reports against batch data to flag anomalies.',
    badge: 'Quality',
    highlights: ['PDF upload & parsing', 'Heavy metal screening', 'Pesticide residue checks', 'AYUSH compliant'],
  },
  {
    icon: QrCode,
    title: 'QR-Based Consumer Verification',
    desc: 'Consumers scan a QR code on any product to instantly see the full journey — from the farm to their hands.',
    badge: 'Consumer',
    highlights: ['Works offline (cached)', 'Multi-language support', 'Batch lineage view', 'Authenticity badge'],
  },
]

const additionalFeatures = [
  { icon: Tractor, title: 'Producer Dashboard', desc: 'Farmers register batches, upload geo-tags, and track certification status in real-time.' },
  { icon: BarChart3, title: 'Analytics & Insights', desc: 'Supply chain analytics that reveal bottlenecks, quality trends, and regional performance.' },
  { icon: Lock, title: 'Role-Based Access', desc: 'Producer, Lab, Manufacturer, Distributor, Retailer — each with tailored permissions and dashboards.' },
  { icon: Smartphone, title: 'Mobile-First Design', desc: 'Designed for field agents with limited connectivity. Works on Android and iOS.' },
  { icon: Zap, title: 'Real-Time Alerts', desc: 'Instant notifications for failed quality checks, batch transfers, and certification expirations.' },
  { icon: ShieldCheck, title: 'Regulatory Compliance', desc: 'Built to comply with AYUSH, WHO GMP, and EU herbal medicine import standards.' },
]

export default function FeaturesPage() {
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
        <div className="absolute top-10 left-12 w-[90px] lg:w-[120px] pointer-events-none z-0 opacity-25 mix-blend-multiply">
          <FloatingLeaf className="w-full h-auto text-[#184E48]" rotate={-45} />
        </div>
        <div className="absolute bottom-8 right-14 w-[85px] lg:w-[115px] pointer-events-none z-0 opacity-25 mix-blend-multiply">
          <FloatingLeaf className="w-full h-auto text-[#184E48]" rotate={120} />
        </div>

        <div className="relative z-10 max-w-4xl mx-auto">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 bg-[#184E48]/10 text-[#184E48] text-sm font-semibold px-4 py-2 rounded-full mb-6 border border-[#184E48]/20">
            <Zap className="w-4 h-4 text-[#184E48]" />
            Platform Capabilities
          </div>

          {/* Heading */}
          <h1 className="text-4xl md:text-6xl lg:text-[4.75rem] font-bold tracking-tight text-[#1e293b] leading-[1.08] font-serif mb-6">
            Everything you need for
            <span className="block text-[#184E48] mt-2">radical transparency.</span>
          </h1>

          {/* Subtitle */}
          <p className="text-[17px] md:text-[19px] lg:text-[20px] text-slate-600 leading-relaxed font-medium max-w-2xl mx-auto mb-10">
            Dravya brings together AI, blockchain, and real-time data to give every stakeholder
            in the Ayurvedic supply chain complete visibility and control.
          </p>

          {/* Action CTAs */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link href="/verify">
              <Button
                size="lg"
                className="bg-[#184E48] hover:bg-[#184E48]/90 text-white rounded-xl px-8 py-6 text-[16px] font-semibold shadow-[0_8px_30px_rgb(24,78,72,0.2)] hover:shadow-[0_8px_30px_rgb(24,78,72,0.3)] hover:-translate-y-0.5 transition-all duration-300 group flex items-center justify-center gap-2"
              >
                Try Verification
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </Button>
            </Link>
            <Link href="/contact">
              <Button
                size="lg"
                variant="outline"
                className="border-[#184E48] bg-white hover:bg-slate-50 text-[#184E48] rounded-xl px-8 py-6 text-[16px] font-bold shadow-sm hover:shadow-md hover:-translate-y-0.5 transition-all duration-300"
              >
                Schedule Demo
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Main Core Features Section - White Background */}
      <section className="py-20 lg:py-28 max-w-7xl mx-auto px-6 w-full">
        <div className="text-center mb-16">
          <span className="text-[#184E48] font-bold text-xs uppercase tracking-widest bg-[#184E48]/10 px-3.5 py-1.5 rounded-full inline-block mb-3">
            Core Capabilities
          </span>
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-[#1e293b] font-serif">
            Built for every link in the chain
          </h2>
          <p className="text-slate-600 mt-4 max-w-xl mx-auto text-base font-medium">
            Seamlessly integrating AI computer vision with decentralized blockchain record-keeping.
          </p>
        </div>

        <div className="space-y-8">
          {mainFeatures.map((feature, i) => {
            const Icon = feature.icon
            const isEven = i % 2 === 0
            return (
              <div
                key={feature.title}
                className={`group flex flex-col ${isEven ? 'lg:flex-row' : 'lg:flex-row-reverse'} gap-10 items-center bg-white border border-slate-100 rounded-3xl p-8 lg:p-12 hover:shadow-2xl hover:shadow-[#184E48]/8 hover:border-[#184E48]/20 transition-all duration-500`}
              >
                {/* Icon Side */}
                <div className="flex-shrink-0 flex flex-col items-center gap-4 w-full lg:w-64">
                  <div className="w-24 h-24 rounded-3xl bg-[#184E48] flex items-center justify-center shadow-xl shadow-[#184E48]/30 group-hover:scale-110 transition-transform duration-500">
                    <Icon className="w-12 h-12 text-white" />
                  </div>
                  <span className="text-xs font-bold text-[#184E48] bg-[#184E48]/10 px-3.5 py-1.5 rounded-full tracking-widest uppercase">
                    {feature.badge}
                  </span>
                </div>

                {/* Content Side */}
                <div className="flex-1">
                  <h3 className="text-2xl lg:text-3xl font-bold text-[#1e293b] mb-4 font-serif">{feature.title}</h3>
                  <p className="text-slate-600 text-lg leading-relaxed mb-7 font-medium">{feature.desc}</p>
                  <div className="grid sm:grid-cols-2 gap-3">
                    {feature.highlights.map((h) => (
                      <div key={h} className="flex items-center gap-3">
                        <CheckCircle2 className="w-5 h-5 text-[#184E48] flex-shrink-0" />
                        <span className="text-slate-700 font-semibold text-sm">{h}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </section>

      {/* Additional Features Grid - Soft Herbal Tinted Background */}
      <section className="py-20 lg:py-28 bg-[#E1E9E1]/30 border-y border-[#184E48]/10 relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <span className="text-[#184E48] font-bold text-xs uppercase tracking-widest bg-[#184E48]/10 px-3.5 py-1.5 rounded-full inline-block mb-3">
              And More
            </span>
            <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-[#1e293b] font-serif">
              Everything else that matters
            </h2>
            <p className="text-slate-600 mt-4 max-w-xl mx-auto text-base font-medium">
              Enterprise-grade tools designed for speed, security, and effortless adoption.
            </p>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {additionalFeatures.map(({ icon: Icon, title, desc }) => (
              <div
                key={title}
                className="bg-white rounded-3xl p-7 border border-slate-100 hover:border-[#184E48]/20 hover:shadow-xl hover:shadow-[#184E48]/8 hover:-translate-y-1.5 transition-all duration-300 group cursor-default"
              >
                <div className="w-12 h-12 rounded-2xl bg-[#184E48]/10 flex items-center justify-center mb-5 group-hover:bg-[#184E48] transition-colors duration-300">
                  <Icon className="w-6 h-6 text-[#184E48] group-hover:text-white transition-colors duration-300" />
                </div>
                <h3 className="text-lg font-bold text-[#1e293b] mb-2 font-serif">{title}</h3>
                <p className="text-slate-600 text-sm leading-relaxed font-medium">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Comparison Section - White Background */}
      <section className="py-20 lg:py-28 max-w-5xl mx-auto px-6 w-full">
        <div className="text-center mb-16">
          <span className="text-[#184E48] font-bold text-xs uppercase tracking-widest bg-[#184E48]/10 px-3.5 py-1.5 rounded-full inline-block mb-3">
            Why Dravya
          </span>
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-[#1e293b] font-serif">
            Old way vs. Dravya way
          </h2>
        </div>
        <div className="grid md:grid-cols-2 gap-6">
          {/* Old Way */}
          <div className="bg-red-50/70 border border-red-100 rounded-3xl p-8 shadow-sm">
            <h3 className="text-xl font-bold text-red-700 mb-6 flex items-center gap-2 font-serif">
              <span className="text-2xl">😞</span> Without Dravya
            </h3>
            <ul className="space-y-4">
              {[
                'Paper certificates — easily forged',
                'No farm-to-pharmacy visibility',
                'Lab reports isolated, not linked to batches',
                'No consumer verification method',
                'Compliance done manually',
                'Fraud discovered only after harm',
              ].map((item) => (
                <li key={item} className="flex items-start gap-3 text-slate-700 font-medium">
                  <span className="text-red-400 font-bold mt-0.5">✕</span>
                  <span className="text-sm">{item}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Dravya Way */}
          <div className="bg-[#184E48]/5 border border-[#184E48]/20 rounded-3xl p-8 shadow-sm">
            <h3 className="text-xl font-bold text-[#184E48] mb-6 flex items-center gap-2 font-serif">
              <Sprout className="w-6 h-6 text-[#184E48]" /> With Dravya
            </h3>
            <ul className="space-y-4">
              {[
                'Immutable blockchain records, tamper-proof',
                'Complete end-to-end traceability',
                'AI cross-validates lab reports & batches',
                'QR code consumer verification in 2 seconds',
                'Automated AYUSH & WHO compliance checks',
                'Anomalies flagged before product ships',
              ].map((item) => (
                <li key={item} className="flex items-start gap-3 text-slate-700 font-medium">
                  <CheckCircle2 className="w-5 h-5 text-[#184E48] flex-shrink-0 mt-0.5" />
                  <span className="text-sm font-semibold">{item}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
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
            <h2 className="text-3xl md:text-4xl font-bold font-serif mb-4 leading-tight">
              Ready to verify your supply chain?
            </h2>
            <p className="text-slate-200 text-base md:text-lg mb-8 leading-relaxed">
              Join thousands of producers, labs, and manufacturers already building trust on the Dravya platform.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/verify">
                <Button className="w-full sm:w-auto bg-white text-[#184E48] hover:bg-slate-100 font-bold rounded-xl px-8 py-6 text-base shadow-lg hover:-translate-y-0.5 transition-all gap-2">
                  Start Verifying <ArrowRight className="w-4 h-4" />
                </Button>
              </Link>
              <Link href="/contact">
                <Button variant="outline" className="w-full sm:w-auto border-white/30 text-white bg-white/10 hover:bg-white/20 rounded-xl px-8 py-6 text-base font-semibold backdrop-blur-sm">
                  Talk to Sales
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
