'use client'

import * as React from 'react'
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  type CarouselApi,
} from '@/components/ui/carousel'
import { LeafSprig } from './LeafSprig'
import Image from 'next/image'

const team = [
  { name: 'Anubhav Dwivedi', role: 'Team Lead & Backend Developer', bio: 'Leads the team and architects the core backend systems powering Dravya.', image: '/assets/team/Anubhav.png', position: 'object-top' },
  { name: 'Ankush Gangwar', role: 'AI/ML Engineer', bio: 'Works on the AI models used for herb authentication and quality verification.', image: '/assets/team/Ankush.jpeg', position: 'object-center' },
  { name: 'Anshuman Sabat', role: 'Frontend Developer', bio: 'Designs and builds the user-facing platform, from landing pages to the verification flow.', image: '/assets/team/Anshuman.jpeg', position: 'object-top' },
  { name: 'Gopal Shrivastav', role: 'Frontend Developer', bio: 'Builds and polishes the UI components across the Dravya platform.', image: '/assets/team/Gopal.jpeg', position: 'object-center' },
  { name: 'Aradhya Singh', role: 'Research & Documentation', bio: 'Handles research on Ayurvedic standards and documents the framework behind Dravya.', image: '/assets/team/Aradhya.jpeg', position: 'object-top' },
  { name: 'Shubhi Tiwari', role: 'Frontend Developer', bio: 'Works on the interface and user experience across key pages of the platform.', image: '/assets/team/Shubhi.jpeg', position: 'object-center' },
]

export function TeamCarousel() {
  const [api, setApi] = React.useState<CarouselApi>()
  const [current, setCurrent] = React.useState(0)
  const [count, setCount] = React.useState(0)

  React.useEffect(() => {
    if (!api) return

    setCount(api.scrollSnapList().length)
    setCurrent(api.selectedScrollSnap() + 1)

    api.on('select', () => {
      setCurrent(api.selectedScrollSnap() + 1)
    })

    api.on('reInit', () => {
      setCount(api.scrollSnapList().length)
    })

    const interval = setInterval(() => {
      if (!api) return
      api.scrollNext()
    }, 3500)

    return () => clearInterval(interval)
  }, [api])

  return (
    <section id="team" className="relative overflow-hidden bg-[#E1E9E1]/35 border-t border-[#184E48]/10 py-24 lg:py-32">

      {/* Background Decorative Elements */}
      <div className="absolute top-[8%] -left-12 w-[280px] md:w-[380px] lg:w-[460px] pointer-events-none z-0 opacity-20 mix-blend-multiply">
        <LeafSprig className="w-full h-auto text-[#184E48]" />
      </div>

      <div className="absolute bottom-[4%] -right-12 w-[280px] md:w-[380px] lg:w-[460px] pointer-events-none z-0 opacity-20 mix-blend-multiply">
        <LeafSprig className="w-full h-auto text-[#184E48]" flip={true} />
      </div>

      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[600px] h-[600px] bg-[#184E48]/[0.03] rounded-full blur-3xl pointer-events-none" />
      <div className="absolute top-1/2 left-1/3 w-80 h-80 bg-[#184E48]/[0.04] rounded-full blur-2xl pointer-events-none" />

      <div className="relative z-10 mx-auto max-w-[1500px] px-4 sm:px-6 lg:px-8">

        {/* Header Tag & Section Title */}
        <div className="mx-auto max-w-3xl text-center mb-12 lg:mb-16">
          <h2 className="text-4xl font-serif font-extrabold tracking-tight text-slate-900 md:text-5xl lg:text-6xl mb-6 leading-[1.15]">
            Team Behind{' '}
            <span className="text-[#184E48] relative whitespace-nowrap">
              Dravya.
              <svg className="absolute -bottom-2 left-0 w-full h-3 text-[#184E48]/30" viewBox="0 0 100 10" preserveAspectRatio="none">
                <path d="M0 5 Q 50 10 100 5" fill="none" stroke="currentColor" strokeWidth="3" />
              </svg>
            </span>
          </h2>

          <p className="mx-auto mt-6 max-w-2xl text-base md:text-lg leading-relaxed text-slate-600 font-medium">
            A dedicated team of software developers, AI engineers, and researchers building the digital infrastructure for authentic Ayurveda.
          </p>
        </div>

        {/* Carousel Container */}
        <div className="relative max-w-[1350px] mx-auto px-4 md:px-12">

          <Carousel
            setApi={setApi}
            opts={{
              align: 'start',
              loop: true,
            }}
            className="w-full"
          >
            <CarouselContent className="-ml-3 md:-ml-4">
              {team.map((member, index) => (
                <CarouselItem
                  key={member.name}
                  className="pl-3 md:pl-4 basis-full md:basis-1/2 lg:basis-1/3"
                >
                  <div className="group relative flex flex-col justify-between h-full rounded-3xl bg-white p-7 shadow-md shadow-[#184E48]/[0.05] border border-[#184E48]/15 hover:border-[#184E48]/50 hover:shadow-2xl hover:shadow-[#184E48]/20 transition-all duration-500 overflow-hidden">

                    <div className="absolute top-0 left-0 right-0 h-1.5 bg-[#184E48] opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

                    <div className="absolute -right-2 -top-4 text-[95px] font-black text-slate-900/[0.04] group-hover:text-[#184E48]/[0.08] transition-colors duration-500 pointer-events-none select-none z-0">
                      0{index + 1}
                    </div>

                    <div className="relative z-10 flex-1 flex flex-col">

                      <div className="flex items-center justify-between mb-6">
                        
                        <span className="text-xs font-extrabold text-[#184E48]/60">
                          0{index + 1} / 0{team.length}
                        </span>
                      </div>

                      <div className="mb-6 relative inline-flex h-28 w-28 shrink-0 items-center justify-center rounded-3xl bg-[#184E48] text-white shadow-lg shadow-[#184E48]/25 group-hover:bg-white group-hover:text-[#184E48] group-hover:border-2 group-hover:border-[#184E48] transform group-hover:scale-105 group-hover:rotate-2 transition-all duration-500 font-bold text-4xl font-serif overflow-hidden">
                        {member.image ? (
                          <Image src={member.image} alt={member.name} fill className={`object-cover ${member.position}`} />
                        ) : (
                          member.name.charAt(0)
                        )}
                      </div>

                      <h3 className="text-xl font-bold text-slate-900 group-hover:text-[#184E48] transition-colors duration-300 mb-1">
                        {member.name}
                      </h3>
                      {member.role && (
                        <p className="text-xs font-semibold text-[#184E48] mb-3 tracking-wide">
                          {member.role}
                        </p>
                      )}

                      {member.bio && (
                        <p className="text-xs md:text-sm leading-relaxed text-slate-600">
                          {member.bio}
                        </p>
                      )}
                    </div>

                    <div className="absolute inset-0 bg-gradient-to-b from-transparent via-white/50 to-[#184E48]/[0.04] opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none z-0" />
                  </div>
                </CarouselItem>
              ))}
            </CarouselContent>

            {/* Dots */}
            <div className="mt-8 flex justify-center gap-2">
              {Array.from({ length: count }).map((_, index) => (
                <button
                  key={index}
                  className={`h-2.5 rounded-full transition-all duration-300 ${
                    current === index + 1
                      ? 'w-8 bg-[#184E48]'
                      : 'w-2.5 bg-[#184E48]/30 hover:bg-[#184E48]/50'
                  }`}
                  onClick={() => api?.scrollTo(index)}
                  aria-label={`Go to slide ${index + 1}`}
                />
              ))}
            </div>
          </Carousel>
        </div>
      </div>
    </section>
  )
}
