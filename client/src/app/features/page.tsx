'use client'
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
  Package,
  Hash,
  BadgeCheck,
  Database,
  ClipboardList,
  TestTube,
} from 'lucide-react'
import { useTranslation } from 'react-i18next'

export default function FeaturesPage() {
  const { t } = useTranslation()

  const mainFeatures = [
    {
      icon: Brain,
      title: t('features.cards.coreAi.title'),
      desc: t('features.cards.coreAi.desc'),
      badge: t('features.cards.coreAi.badge'),
      highlights: [
        t('features.cards.coreAi.h1'),
        t('features.cards.coreAi.h2'),
        t('features.cards.coreAi.h3'),
        t('features.cards.coreAi.h4'),
        t('features.cards.coreAi.h5'),
        t('features.cards.coreAi.h6'),
      ],
    },
    {
      icon: Package,
      title: t('features.cards.batchEngine.title'),
      desc: t('features.cards.batchEngine.desc'),
      badge: t('features.cards.batchEngine.badge'),
      highlights: [
        t('features.cards.batchEngine.h1'),
        t('features.cards.batchEngine.h2'),
        t('features.cards.batchEngine.h3'),
        t('features.cards.batchEngine.h4'),
        t('features.cards.batchEngine.h5'),
        t('features.cards.batchEngine.h6'),
      ],
    },
    {
      icon: LinkIcon,
      title: t('features.cards.blockchain.title'),
      desc: t('features.cards.blockchain.desc'),
      badge: t('features.cards.blockchain.badge'),
      highlights: [
        t('features.cards.blockchain.h1'),
        t('features.cards.blockchain.h2'),
        t('features.cards.blockchain.h3'),
        t('features.cards.blockchain.h4'),
        t('features.cards.blockchain.h5'),
        t('features.cards.blockchain.h6'),
      ],
    },
    {
      icon: ShieldCheck,
      title: t('features.cards.quality.title'),
      desc: t('features.cards.quality.desc'),
      badge: t('features.cards.quality.badge'),
      highlights: [
        t('features.cards.quality.h1'),
        t('features.cards.quality.h2'),
        t('features.cards.quality.h3'),
        t('features.cards.quality.h4'),
        t('features.cards.quality.h5'),
        t('features.cards.quality.h6'),
      ],
    },
  ]

  const additionalFeatures = [
    { icon: ClipboardList, title: 'POST /batches/create', desc: t('features.additional.batchCreate') },
    { icon: TestTube,      title: 'POST /batches/create-from-image', desc: t('features.additional.batchCreateImg') },
    { icon: Database,      title: 'GET /batches/{batch_id}', desc: t('features.additional.batchGet') },
    { icon: Hash,          title: 'GET /batches/{batch_id}/traceability', desc: t('features.additional.batchTrace') },
    { icon: BarChart3,     title: 'GET /inventory/summary', desc: t('features.additional.invSummary') },
    { icon: Zap,           title: t('features.additional.realtimeAlertsTitle'), desc: t('features.additional.realtimeAlertsDesc') },
  ]

  return (
    <div className="min-h-screen flex flex-col bg-white relative font-sans overflow-x-hidden">
      <LandingNavbar />

      {/* Hero Section */}
      <section className="relative flex-1 flex flex-col justify-center items-center px-6 lg:px-24 py-16 lg:py-20 relative z-10 w-full max-w-[1600px] mx-auto text-center">
        {/* Subtle Watermark Logo */}
        <div
          className="absolute inset-0 z-0 opacity-[0.06] pointer-events-none mix-blend-multiply flex items-center justify-center"
          style={{
            backgroundImage: 'url("/logo.png")',
            backgroundSize: '750px',
            backgroundPosition: 'center 40%',
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

        <div className="relative z-10 max-w-5xl mx-auto">
          {/* Heading */}
          <h1 className="text-4xl md:text-6xl lg:text-[4.75rem] font-bold tracking-tight text-[#1e293b] leading-[1.08] font-serif mb-6">
            {t('features.titleMain')}
            <span className="block text-[#184E48] mt-2">{t('features.titleSub')}</span>
          </h1>

          {/* Subtitle */}
          <p className="text-[17px] md:text-[19px] lg:text-[20px] text-slate-600 leading-relaxed font-medium max-w-3xl mx-auto mb-10">
            {t('features.subtitle')}
          </p>

          {/* Hero Scanner Featured Card */}
          <div className="mt-6 max-w-4xl mx-auto bg-white border border-black rounded-3xl p-6 sm:p-8 flex flex-col md:flex-row gap-6 hover:scale-[1.02] transition-all duration-300 lg:gap-8 items-center text-left shadow-sm">
            {/* Animated Dark Scanner Visual */}
            <div className="w-full md:w-72 h-64 bg-[#0c2e2a] rounded-2xl relative flex flex-col items-center justify-between p-4 flex-shrink-0 overflow-hidden border border-[#184E48]/40 shadow-inner">
              {/* Animated Scan Line */}
              <div className="absolute inset-x-0 h-1 bg-gradient-to-r from-transparent via-emerald-400 to-transparent shadow-[0_0_15px_#34d399] z-20 animate-scanLine" />

              {/* Corner Brackets (Gold Accent) */}
              <div className="absolute top-3 left-3 w-4 h-4 border-t-2 border-l-2 border-amber-400 z-10" />
              <div className="absolute top-3 right-3 w-4 h-4 border-t-2 border-r-2 border-amber-400 z-10" />
              <div className="absolute bottom-3 left-3 w-4 h-4 border-b-2 border-l-2 border-amber-400 z-10" />
              <div className="absolute bottom-3 right-3 w-4 h-4 border-b-2 border-r-2 border-amber-400 z-10" />

              {/* Top Status Badge with Pulsing Live Dot */}
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-950/80 border border-emerald-500/40 text-[11px] font-mono text-emerald-300 z-20">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
                </span>
                <span>{t('features.scanner.badge')}</span>
              </div>

              {/* Center Scanner Radar/Graphic */}
              <div className="relative w-32 h-32 flex items-center justify-center my-auto">
                <div className="absolute inset-0 rounded-full border border-teal-500/30 animate-pulse" />
                <div className="absolute inset-3 rounded-full border border-teal-500/40" />
                <div className="w-full h-0.5 bg-teal-500/30" />
                <div className="h-full w-0.5 bg-teal-500/30" />

                {/* Rotating Sweep Beam */}
                <div className="absolute inset-0 rounded-full bg-conic-beam opacity-25 animate-spinSlow pointer-events-none" />

                {/* Center Target Indicator */}
                <div className="w-4 h-4 rounded-full border-2 border-amber-400 bg-amber-400/20 z-10" />
              </div>

              {/* Bottom Tech Label */}
              <div className="text-[10px] font-mono text-emerald-400/70 tracking-wider uppercase z-20">
                FastAPI · HerbPredictor
              </div>
            </div>

            {/* Card Content */}
            <div className="flex-1">
              <h3 className="text-2xl md:text-3xl font-bold font-serif text-slate-900 mb-3 leading-snug">
                {t('features.scannerTitle')}
              </h3>

              <p className="text-slate-600 text-sm md:text-base leading-relaxed font-medium mb-3">
                {t('features.scannerDesc')}
              </p>

              <p className="text-[11px] font-mono text-slate-400 mb-5 leading-relaxed">
                Python · FastAPI · Pydantic · Deep Learning / PlantPredictor · REST API · SHA-256 · Batch/Inventory Aggregation · Blockchain-ready Traceability
              </p>

              {/* Practical Platform Features */}
              <div className="grid grid-cols-3 gap-3">
                <div className="bg-[#fcfdfc] border border-[#184E48]/20 rounded-xl p-3">
                  <p className="text-[11px] font-medium text-slate-500 mb-0.5">{t('features.scanner.analysisEngineLabel')}</p>
                  <p className="text-xs md:text-sm font-bold text-[#184E48]">{t('features.scanner.analysisEngineVal')}</p>
                </div>
                <div className="bg-[#fcfdfc] border border-[#184E48]/20 rounded-xl p-3">
                  <p className="text-[11px] font-medium text-slate-500 mb-0.5">{t('features.scanner.modelLabel')}</p>
                  <p className="text-xs md:text-sm font-bold text-[#184E48]">{t('features.scanner.modelVal')}</p>
                </div>
                <div className="bg-[#fcfdfc] border border-[#184E48]/20 rounded-xl p-3">
                  <p className="text-[11px] font-medium text-slate-500 mb-0.5">{t('features.scanner.outputLabel')}</p>
                  <p className="text-xs md:text-sm font-bold text-[#184E48]">{t('features.scanner.outputVal')}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Main Core Features Section - White Background */}
      <section className="py-20 lg:py-24 max-w-7xl mx-auto px-6 w-full">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-[#1e293b] font-serif">
            {t('features.builtForEveryLink')}
          </h2>
          <p className="text-slate-600 mt-4 max-w-xl mx-auto text-base font-medium">
            {t('features.builtForEveryLinkSub')}
          </p>
        </div>

        <div className="space-y-8">
          {mainFeatures.map((feature, i) => {
            const Icon = feature.icon
            const isEven = i % 2 === 0
            return (
              <div
                key={feature.title}
                className={`group flex flex-col ${isEven ? 'lg:flex-row' : 'lg:flex-row-reverse'} gap-10 items-center bg-white border border-black rounded-3xl p-8 lg:p-12 hover:shadow-2xl hover:shadow-[#184E48]/8 hover:border-black transition-all duration-500`}
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
            <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-[#1e293b] font-serif">
              {t('features.everythingElse')}
            </h2>
            <p className="text-slate-600 mt-4 max-w-xl mx-auto text-base font-medium">
              {t('features.everythingElseSub')}
            </p>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {additionalFeatures.map(({ icon: Icon, title, desc }) => (
              <div
                key={title}
                className="bg-white rounded-3xl p-7 border border-black hover:border-black hover:shadow-xl hover:shadow-[#184E48]/8 hover:-translate-y-1.5 transition-all duration-300 group cursor-default"
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

      <Footer className="bg-[#184E48]" />

      <style>{`
        @keyframes scanLineAnimation {
          0% { top: 0%; opacity: 0; }
          15% { opacity: 1; }
          85% { opacity: 1; }
          100% { top: 100%; opacity: 0; }
        }
        @keyframes spinSlowAnimation {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        .animate-scanLine {
          animation: scanLineAnimation 2.8s ease-in-out infinite alternate;
        }
        .animate-spinSlow {
          animation: spinSlowAnimation 8s linear infinite;
        }
        .bg-conic-beam {
          background: conic-gradient(from 0deg, transparent 0deg, transparent 270deg, rgba(52, 211, 153, 0.4) 360deg);
        }
      `}</style>
    </div>
  )
}
