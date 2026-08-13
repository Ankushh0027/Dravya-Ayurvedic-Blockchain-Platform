'use client'

import React, { useState } from 'react'
import {
  Sprout,
  FlaskConical,
  BadgeCheck,
  Factory,
  Database,
  MapPin,
} from 'lucide-react'

export interface FlowStep {
  id: string
  number: string
  stage: string
  title: string
  location: string
  description: string
  icon: React.ElementType
  mapPos: { x: number; y: number }
  labelSide: 'left' | 'right'
}

const flowSteps: FlowStep[] = [
  {
    id: 'harvested',
    number: '01',
    stage: 'Harvested',
    title: 'Herb Harvested & Geo-Tagged',
    location: 'Wayanad Farm, Kerala',
    description:
      'Raw organic Ashwagandha roots harvested by verified farmers. GPS coordinates & harvest timestamp registered on Dravya.',
    icon: Sprout,
    mapPos: { x: 210, y: 620 },
    labelSide: 'right',
  },
  {
    id: 'lab-verified',
    number: '02',
    stage: 'Lab Verified',
    title: 'AI Purity & Lab Test',
    location: 'AYUSH Testing Lab, Mysuru',
    description:
      'AI models evaluate species purity (99.6% match). Certified lab tests verify active phytochemical compounds.',
    icon: FlaskConical,
    mapPos: { x: 225, y: 520 },
    labelSide: 'left',
  },
  {
    id: 'ayush-certified',
    number: '03',
    stage: 'AYUSH Certified',
    title: 'Regulatory Officer Stamp',
    location: 'Verification Bureau, Bengaluru',
    description:
      'Certified AYUSH Officer verifies physical batch audit and stamps digital cryptographic sign-off.',
    icon: BadgeCheck,
    mapPos: { x: 270, y: 440 },
    labelSide: 'right',
  },
  {
    id: 'processed',
    number: '04',
    stage: 'Processed',
    title: 'GMP Extraction & Production',
    location: 'Extraction Unit, Hosur',
    description:
      'Standardized extraction & formulation processed under temperature-monitored GMP conditions.',
    icon: Factory,
    mapPos: { x: 220, y: 330 },
    labelSide: 'left',
  },
  {
    id: 'recorded',
    number: '05',
    stage: 'Recorded',
    title: 'Anchored On Blockchain',
    location: 'Polygon Blockchain Ledger',
    description:
      'Final batch lineage permanently stored on-chain. Consumers scan QR code to trace verified origin.',
    icon: Database,
    mapPos: { x: 215, y: 200 },
    labelSide: 'right',
  },
]

/* Vein path segments connecting consecutive nodes along India's main landmass */
const veinSegments = [
  'M 210 620 C 215 580, 220 550, 225 520',
  'M 225 520 C 240 490, 260 465, 270 440',
  'M 270 440 C 250 400, 230 365, 220 330',
  'M 220 330 C 210 280, 210 240, 215 200',
]



export function VeinMapJourney() {
  const [activeStepId, setActiveStepId] = useState<string>('harvested')
  const currentStep =
    flowSteps.find((s) => s.id === activeStepId) || flowSteps[0]
  const activeIdx = flowSteps.findIndex((s) => s.id === activeStepId)
  const StepIcon = currentStep.icon

  return (
    <div className="w-full my-8 font-sans">
      <div className="bg-[#fcfdfc] border border-[#184E48]/20 rounded-3xl p-6 lg:p-10 shadow-sm relative overflow-hidden">
        {/* Header */}
        <div className="text-center max-w-2xl mx-auto mb-10 relative z-10">
          
          <h3 className="text-3xl md:text-4xl lg:text-[2.75rem] font-bold font-serif text-[#184E48] leading-tight">
            Supply Chain Across India
          </h3>
          <p className="text-slate-600 text-base mt-3 font-medium max-w-xl mx-auto">
            Trace the verified journey of Ayurvedic herbs — from farm to
            blockchain, state by state.
          </p>
        </div>

        {/* Grid: Map + Card */}
        <div className="grid lg:grid-cols-12 gap-8 items-center relative z-10">
          {/* ─── India Map with Clean Vein Paths ─── */}
          <div className="lg:col-span-7 flex justify-center">
            <div className="relative w-full max-w-[560px] aspect-[56/75]">
              {/* India Map Image */}
              <div
                className="absolute inset-0 pointer-events-none"
                style={{
                  backgroundImage: 'url("/india_map_white_bg.png")',
                  backgroundSize: 'contain',
                  backgroundPosition: 'center',
                  backgroundRepeat: 'no-repeat',
                  opacity: 0.28,
                }}
              />

              {/* Clean SVG Overlay */}
              <svg
                viewBox="0 0 600 804"
                className="absolute inset-0 w-full h-full"
                preserveAspectRatio="xMidYMid meet"
              >
           

                {/* Main supply chain connection paths */}
                {veinSegments.map((d, i) => {
                  const isDone = i < activeIdx
                  return (
                    <path
                      key={`seg-${i}`}
                      d={d}
                      fill="none"
                      stroke={isDone ? '#184E48' : '#88A399'}
                      strokeWidth={isDone ? '5.5' : '3.5'}
                      strokeLinecap="round"
                      strokeDasharray={isDone ? 'none' : '6 6'}
                      opacity={isDone ? 0.9 : 0.45}
                    />
                  )
                })}

                {/* Nodes on Map */}
                {flowSteps.map((step, idx) => {
                  const isActive = activeStepId === step.id
                  const isPast = idx <= activeIdx
                  const Icon = step.icon
                  const { x, y } = step.mapPos

                  return (
                    <g
                      key={step.id}
                      transform={`translate(${x},${y})`}
                      className="cursor-pointer"
                      onClick={() => setActiveStepId(step.id)}
                    >
                      {/* Background Circle */}
                      <circle
                        r={isActive ? '32' : '25'}
                        fill={isActive ? '#184E48' : isPast ? '#2D5A52' : '#ffffff'}
                        stroke={isActive ? '#184E48' : isPast ? '#184E48' : '#94a3b8'}
                        strokeWidth={isActive ? '4' : '2.5'}
                        style={{
                          filter: isActive
                            ? 'drop-shadow(0 6px 12px rgba(24,78,72,0.35))'
                            : 'drop-shadow(0 2px 6px rgba(0,0,0,0.12))',
                          transition: 'all 0.2s ease',
                        }}
                      />

                      {/* Large Icon */}
                      <foreignObject
                        x={isActive ? -18 : -14}
                        y={isActive ? -18 : -14}
                        width={isActive ? 36 : 28}
                        height={isActive ? 36 : 28}
                        className="pointer-events-none overflow-visible"
                      >
                        <div className="w-full h-full flex items-center justify-center">
                          <Icon
                            className={isActive ? 'w-6 h-6' : 'w-4 h-4'}
                            strokeWidth={2.2}
                            color={isActive || isPast ? '#ffffff' : '#184E48'}
                          />
                        </div>
                      </foreignObject>

                      {/* Number Badge */}
                      <circle
                        cx={isActive ? 20 : 16}
                        cy={isActive ? -20 : -16}
                        r="10"
                        fill={isActive ? '#D97706' : '#184E48'}
                        stroke="#ffffff"
                        strokeWidth="2"
                      />
                      <text
                        x={isActive ? 20 : 16}
                        y={isActive ? -20 : -16}
                        textAnchor="middle"
                        dominantBaseline="central"
                        fontSize="9"
                        fontWeight="800"
                        fill="white"
                        className="select-none"
                      >
                        {step.number}
                      </text>

                      {/* Stage Label */}
                      <foreignObject
                        x={step.labelSide === 'left' ? -155 : 36}
                        y="-15"
                        width="135"
                        height="32"
                        className="overflow-visible pointer-events-none"
                      >
                        <div
                          className={`px-2.5 py-1 rounded-lg text-xs font-bold border transition-all duration-200 w-fit whitespace-nowrap ${
                            isActive
                              ? 'bg-[#184E48] text-white border-[#184E48] shadow-md'
                              : 'bg-white text-slate-800 border-slate-200 shadow-sm'
                          } ${step.labelSide === 'left' ? 'ml-auto' : ''}`}
                        >
                          {step.stage}
                        </div>
                      </foreignObject>
                    </g>
                  )
                })}
              </svg>
            </div>
          </div>

          {/* ─── Clean Detail Card ─── */}
          <div className="lg:col-span-5 flex flex-col justify-between h-full">
            <div className="bg-white border border-[#184E48]/15 rounded-2xl p-7 lg:p-8 shadow-md">
              {/* Badge Row */}
              <div className="flex items-center justify-between gap-2 mb-6">
                
                <span className="text-sm font-bold text-slate-400 font-mono">
                  Step {currentStep.number} / 05
                </span>
              </div>

              {/* Icon & Title */}
              <div className="flex items-start gap-4 mb-6">
                <div className="flex-shrink-0 w-14 h-14 rounded-2xl bg-[#184E48] text-white flex items-center justify-center shadow-lg shadow-[#184E48]/20">
                  <StepIcon className="w-7 h-7" strokeWidth={2} />
                </div>
                <div className="flex-1 min-w-0">
                  <h4 className="text-xl md:text-2xl font-bold font-serif text-slate-900 mb-1 leading-tight">
                    {currentStep.title}
                  </h4>
                  <div className="flex items-center gap-2 text-sm font-semibold text-[#184E48]">
                    <MapPin className="w-4 h-4 flex-shrink-0" />
                    <span className="truncate">{currentStep.location}</span>
                  </div>
                </div>
              </div>

           

              {/* Description */}
              <p className="text-slate-600 text-sm md:text-base leading-relaxed font-medium mb-6 bg-[#f8faf8] p-5 rounded-xl border border-[#184E48]/10">
                {currentStep.description}
              </p>

              {/* Stage selector buttons */}
              <div className="pt-5 border-t border-slate-100">
                <p className="text-xs font-bold text-slate-500 mb-3">
                  Click a stage to view details:
                </p>
                <div className="flex flex-wrap gap-2">
                  {flowSteps.map((s) => {
                    const active = activeStepId === s.id
                    return (
                      <button
                        key={s.id}
                        onClick={() => setActiveStepId(s.id)}
                        className={`px-3.5 py-2 rounded-xl text-xs md:text-sm font-bold transition-all duration-150 border cursor-pointer ${
                          active
                            ? 'bg-[#184E48] text-white border-[#184E48] shadow-sm'
                            : 'bg-[#f8faf8] text-slate-700 border-slate-200 hover:border-[#184E48]/40 hover:text-[#184E48]'
                        }`}
                      >
                        {s.number}. {s.stage}
                      </button>
                    )
                  })}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}