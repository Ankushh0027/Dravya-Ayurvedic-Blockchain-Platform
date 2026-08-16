'use client'
import React, { useState } from 'react'
import { LandingNavbar } from '@/features/landing/components/LandingNavbar'
import { Footer } from '@/features/landing/components/Footer'
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
import { useTranslation } from 'react-i18next'

function RoleSelector() {
  const { t } = useTranslation()
  const [activeRole, setActiveRole] = useState('farmer')

  const roleData = [
    {
      id: 'farmer',
      label: t('howItWorks.roles.farmer.label'),
      icon: Sprout,
      headline: t('howItWorks.roles.farmer.headline'),
      tagline: t('howItWorks.roles.farmer.tagline'),
      description: t('howItWorks.roles.farmer.description'),
      steps: [
        { icon: Sprout,     title: t('howItWorks.roles.farmer.step1Title'), desc: t('howItWorks.roles.farmer.step1Desc') },
        { icon: QrCode,     title: t('howItWorks.roles.farmer.step2Title'), desc: t('howItWorks.roles.farmer.step2Desc') },
        { icon: TrendingUp, title: t('howItWorks.roles.farmer.step3Title'), desc: t('howItWorks.roles.farmer.step3Desc') },
        { icon: BarChart3,  title: t('howItWorks.roles.farmer.step4Title'), desc: t('howItWorks.roles.farmer.step4Desc') },
      ],
      badge: t('howItWorks.roles.farmer.badge'),
    },
    {
      id: 'manufacturer',
      label: t('howItWorks.roles.manufacturer.label'),
      icon: Factory,
      headline: t('howItWorks.roles.manufacturer.headline'),
      tagline: t('howItWorks.roles.manufacturer.tagline'),
      description: t('howItWorks.roles.manufacturer.description'),
      steps: [
        { icon: ScanLine,     title: t('howItWorks.roles.manufacturer.step1Title'), desc: t('howItWorks.roles.manufacturer.step1Desc') },
        { icon: BrainCircuit, title: t('howItWorks.roles.manufacturer.step2Title'), desc: t('howItWorks.roles.manufacturer.step2Desc') },
        { icon: FileText,     title: t('howItWorks.roles.manufacturer.step3Title'), desc: t('howItWorks.roles.manufacturer.step3Desc') },
        { icon: Package,      title: t('howItWorks.roles.manufacturer.step4Title'), desc: t('howItWorks.roles.manufacturer.step4Desc') },
      ],
      badge: t('howItWorks.roles.manufacturer.badge'),
    },
    {
      id: 'lab',
      label: t('howItWorks.roles.lab.label'),
      icon: FlaskConical,
      headline: t('howItWorks.roles.lab.headline'),
      tagline: t('howItWorks.roles.lab.tagline'),
      description: t('howItWorks.roles.lab.description'),
      steps: [
        { icon: FlaskConical, title: t('howItWorks.roles.lab.step1Title'), desc: t('howItWorks.roles.lab.step1Desc') },
        { icon: Search,       title: t('howItWorks.roles.lab.step2Title'), desc: t('howItWorks.roles.lab.step2Desc') },
        { icon: FileText,     title: t('howItWorks.roles.lab.step3Title'), desc: t('howItWorks.roles.lab.step3Desc') },
        { icon: CheckCircle2, title: t('howItWorks.roles.lab.step4Title'), desc: t('howItWorks.roles.lab.step4Desc') },
      ],
      badge: t('howItWorks.roles.lab.badge'),
    },
    {
      id: 'authority',
      label: t('howItWorks.roles.authority.label'),
      icon: BadgeCheck,
      headline: t('howItWorks.roles.authority.headline'),
      tagline: t('howItWorks.roles.authority.tagline'),
      description: t('howItWorks.roles.authority.description'),
      steps: [
        { icon: Search,         title: t('howItWorks.roles.authority.step1Title'), desc: t('howItWorks.roles.authority.step1Desc') },
        { icon: ClipboardCheck, title: t('howItWorks.roles.authority.step2Title'), desc: t('howItWorks.roles.authority.step2Desc') },
        { icon: Lock,           title: t('howItWorks.roles.authority.step3Title'), desc: t('howItWorks.roles.authority.step3Desc') },
        { icon: Landmark,       title: t('howItWorks.roles.authority.step4Title'), desc: t('howItWorks.roles.authority.step4Desc') },
      ],
      badge: t('howItWorks.roles.authority.badge'),
    },
  ]

  const role = roleData.find((r) => r.id === activeRole) || roleData[0]
  const Icon = role.icon

  return (
    <section className="py-20 lg:py-28 bg-[#E1E9E1]/30 border-b border-[#184E48]/10 relative overflow-hidden">
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[500px] h-[500px] bg-[#184E48]/[0.03] rounded-full blur-3xl pointer-events-none" />
      <div className="absolute top-1/2 left-1/3 w-72 h-72 bg-[#184E48]/[0.04] rounded-full blur-2xl pointer-events-none" />

      <div className="max-w-5xl mx-auto px-6 relative z-10">
        <div className="text-center mb-12">
          <h2 className="text-2xl md:text-3xl lg:text-5xl font-bold font-serif text-slate-900 leading-tight">
            {t('howItWorks.rolesTitle')}{' '}
            <span className="text-[#184E48]">{t('howItWorks.rolesTitleHighlight')}</span>
          </h2>
          <p className="mt-4 text-slate-600 text-base max-w-xl mx-auto font-medium">
            {t('howItWorks.rolesSubtitle')}
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
          className="group relative rounded-3xl bg-white border border-black shadow-md shadow-[#184E48]/[0.05] hover:border-black hover:shadow-2xl hover:shadow-[#184E48]/15 transition-all duration-500 overflow-hidden"
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
                  {t('howItWorks.getStartedAs')} {role.label}
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
  const { t } = useTranslation()

  const detailedSteps = [
    {
      icon: UserCheck,
      number: '01',
      title: t('howItWorks.workflow.step1Title'),
      subtitle: t('howItWorks.workflow.step1Sub'),
      description: t('howItWorks.workflow.step1Desc'),
      details: [
        t('howItWorks.workflow.step1D1'),
        t('howItWorks.workflow.step1D2'),
        t('howItWorks.workflow.step1D3'),
        t('howItWorks.workflow.step1D4'),
      ],
      accent: 'from-emerald-500/20 to-teal-500/10',
    },
    {
      icon: QrCode,
      number: '02',
      title: t('howItWorks.workflow.step2Title'),
      subtitle: t('howItWorks.workflow.step2Sub'),
      description: t('howItWorks.workflow.step2Desc'),
      details: [
        t('howItWorks.workflow.step2D1'),
        t('howItWorks.workflow.step2D2'),
        t('howItWorks.workflow.step2D3'),
        t('howItWorks.workflow.step2D4'),
      ],
      accent: 'from-cyan-500/20 to-blue-500/10',
    },
    {
      icon: BrainCircuit,
      number: '03',
      title: t('howItWorks.workflow.step3Title'),
      subtitle: t('howItWorks.workflow.step3Sub'),
      description: t('howItWorks.workflow.step3Desc'),
      details: [
        t('howItWorks.workflow.step3D1'),
        t('howItWorks.workflow.step3D2'),
        t('howItWorks.workflow.step3D3'),
        t('howItWorks.workflow.step3D4'),
      ],
      accent: 'from-violet-500/20 to-purple-500/10',
    },
    {
      icon: Landmark,
      number: '04',
      title: t('howItWorks.workflow.step4Title'),
      subtitle: t('howItWorks.workflow.step4Sub'),
      description: t('howItWorks.workflow.step4Desc'),
      details: [
        t('howItWorks.workflow.step4D1'),
        t('howItWorks.workflow.step4D2'),
        t('howItWorks.workflow.step4D3'),
        t('howItWorks.workflow.step4D4'),
      ],
      accent: 'from-amber-500/20 to-orange-500/10',
    },
    {
      icon: Package,
      number: '05',
      title: t('howItWorks.workflow.step5Title'),
      subtitle: t('howItWorks.workflow.step5Sub'),
      description: t('howItWorks.workflow.step5Desc'),
      details: [
        t('howItWorks.workflow.step5D1'),
        t('howItWorks.workflow.step5D2'),
        t('howItWorks.workflow.step5D3'),
        t('howItWorks.workflow.step5D4'),
      ],
      accent: 'from-rose-500/20 to-pink-500/10',
    },
    {
      icon: Star,
      number: '06',
      title: t('howItWorks.workflow.step6Title'),
      subtitle: t('howItWorks.workflow.step6Sub'),
      description: t('howItWorks.workflow.step6Desc'),
      details: [
        t('howItWorks.workflow.step6D1'),
        t('howItWorks.workflow.step6D2'),
        t('howItWorks.workflow.step6D3'),
        t('howItWorks.workflow.step6D4'),
      ],
      accent: 'from-lime-500/20 to-green-500/10',
    },
  ]

  return (
    <div className="min-h-screen flex flex-col bg-white relative font-sans overflow-x-hidden">
      <LandingNavbar />

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
            {t('howItWorks.heroTitle')}
            <span className="block text-[#184E48] mt-2">{t('howItWorks.heroTitleSub')}</span>
          </h1>

          <p className="text-[17px] md:text-[19px] lg:text-[20px] text-slate-600 leading-relaxed font-medium max-w-3xl mx-auto mb-8">
            {t('howItWorks.heroDesc')}
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
              {t('howItWorks.workflow.tag')}
            </h2>
            <h3 className="text-3xl md:text-4xl lg:text-5xl font-bold text-[#1e293b] font-serif">
              {t('howItWorks.workflow.title')}
            </h3>
            <p className="text-slate-600 mt-4 max-w-2xl mx-auto text-base font-medium">
              {t('howItWorks.workflow.subtitle')}
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
                    <div className="flex-1 bg-white border border-black rounded-3xl p-7 lg:p-8 hover:shadow-2xl hover:shadow-[#184E48]/8 hover:border-black transition-all duration-500 relative overflow-hidden">
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
              {t('howItWorks.goldStandard.title')}
            </h2>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="bg-[#E1E9E1]/20 border border-[#184E48]/15 rounded-3xl p-8 hover:shadow-xl transition-all duration-300">
              <div className="w-14 h-14 rounded-2xl bg-[#184E48] text-white flex items-center justify-center mb-6 shadow-md shadow-[#184E48]/20">
                <BrainCircuit className="w-7 h-7" />
              </div>
              <h3 className="text-xl font-bold text-[#1e293b] mb-3 font-serif">
                {t('howItWorks.goldStandard.f1Title')}
              </h3>
              <p className="text-slate-600 text-sm leading-relaxed">
                {t('howItWorks.goldStandard.f1Desc')}
              </p>
            </div>

            {/* Feature 2 */}
            <div className="bg-[#E1E9E1]/20 border border-[#184E48]/15 rounded-3xl p-8 hover:shadow-xl transition-all duration-300">
              <div className="w-14 h-14 rounded-2xl bg-[#184E48] text-white flex items-center justify-center mb-6 shadow-md shadow-[#184E48]/20">
                <Landmark className="w-7 h-7" />
              </div>
              <h3 className="text-xl font-bold text-[#1e293b] mb-3 font-serif">
                {t('howItWorks.goldStandard.f2Title')}
              </h3>
              <p className="text-slate-600 text-sm leading-relaxed">
                {t('howItWorks.goldStandard.f2Desc')}
              </p>
            </div>

            {/* Feature 3 */}
            <div className="bg-[#E1E9E1]/20 border border-[#184E48]/15 rounded-3xl p-8 hover:shadow-xl transition-all duration-300">
              <div className="w-14 h-14 rounded-2xl bg-[#184E48] text-white flex items-center justify-center mb-6 shadow-md shadow-[#184E48]/20">
                <Star className="w-7 h-7" />
              </div>
              <h3 className="text-xl font-bold text-[#1e293b] mb-3 font-serif">
                {t('howItWorks.goldStandard.f3Title')}
              </h3>
              <p className="text-slate-600 text-sm leading-relaxed">
                {t('howItWorks.goldStandard.f3Desc')}
              </p>
            </div>
          </div>
        </div>
      </section>

      <Footer className="bg-[#184E48]" />
    </div>
  )
}
