"use client"

import React from "react"
import {
  Leaf,
  FlaskConical,
  Factory,
  Package,
  Users,
  CheckCircle2,
  ArrowRight,
} from "lucide-react"
import { LeafSprig } from './LeafSprig'
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  type CarouselApi,
} from "@/components/ui/carousel"
import { useTranslation } from "react-i18next"

interface StepCardData {
  icon: React.ElementType
  number: string
  title: string
  subtitle: string
  description: string
  badge: string
  image: string
}

export function StepShowcaseCarousel() {
  const { t } = useTranslation()
  const [api, setApi] = React.useState<CarouselApi>()
  const [current, setCurrent] = React.useState(0)

  const steps: StepCardData[] = [
    {
      icon: Leaf,
      number: "01",
      title: t('landing.step1Title') || "Harvest",
      subtitle: t('landing.step1Subtitle') || "Origin & Batch Creation",
      description: t('landing.step1Desc') || "Farmers log raw herb origin, geo-location, and harvest batch data directly onto the platform.",
      badge: t('landing.step1Badge') || "Source",
      image: "https://images.unsplash.com/photo-1500937386664-56d1dfef3854?q=80&w=800&auto=format&fit=crop",
    },
    {
      icon: FlaskConical,
      number: "02",
      title: t('landing.step2Title') || "Verify",
      subtitle: t('landing.step2Subtitle') || "Lab & Quality Assurance",
      description: t('landing.step2Desc') || "Certified labs verify heavy metals, purity, moisture levels, and authenticity metrics.",
      badge: t('landing.step2Badge') || "Testing",
      image: "https://images.unsplash.com/photo-1532187863486-abf9dbad1b69?q=80&w=800&auto=format&fit=crop",
    },
    {
      icon: Factory,
      number: "03",
      title: t('landing.step3Title') || "Process",
      subtitle: t('landing.step3Subtitle') || "Standardized Processing",
      description: t('landing.step3Desc') || "Manufacturers process herbs into formulations with full environmental and parameter logs.",
      badge: t('landing.step3Badge') || "Manufacturing",
      image: "https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?q=80&w=800&auto=format&fit=crop",
    },
    {
      icon: Package,
      number: "04",
      title: t('landing.step4Title') || "Distribute",
      subtitle: t('landing.step4Subtitle') || "Chain of Custody",
      description: t('landing.step4Desc') || "Distributors and retailers maintain temperature, custody, and real-time location logs.",
      badge: t('landing.step4Badge') || "Logistics",
      image: "https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=800&auto=format&fit=crop",
    },
    {
      icon: Users,
      number: "05",
      title: t('landing.step5Title') || "Consumer",
      subtitle: t('landing.step5Subtitle') || "QR Code Verification",
      description: t('landing.step5Desc') || "End consumers scan a QR code on packaging to view the complete lab & journey audit trail.",
      badge: t('landing.step5Badge') || "Trust",
      image: "https://images.unsplash.com/photo-1556740758-90de374c12ad?q=80&w=800&auto=format&fit=crop",
    },
  ]

  React.useEffect(() => {
    if (!api) return

    setCurrent(api.selectedScrollSnap() + 1)

    api.on("select", () => {
      setCurrent(api.selectedScrollSnap() + 1)
    })

    api.reInit()

    const interval = setInterval(() => {
      if (!api) return
      api.scrollNext()
    }, 3500)

    return () => clearInterval(interval)
  }, [api])

  return (
    <section className="relative overflow-hidden bg-white border-t border-[#184E48]/10 py-24 lg:py-32">
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
            {t('landing.howItWorksTitle')}
          </h2>

          <p className="mx-auto mt-6 max-w-2xl text-base md:text-lg leading-relaxed text-slate-600 font-medium">
            {t('landing.howItWorksSub')}
          </p>
        </div>

        {/* Carousel Container */}
        <div className="relative max-w-[1350px] mx-auto px-4 md:px-12">
          <Carousel
            setApi={setApi}
            opts={{
              align: "start",
              loop: true,
            }}
            className="w-full"
          >
            <CarouselContent className="-ml-3 md:-ml-4">
              {steps.map((step, index) => {
                const Icon = step.icon

                return (
                  <CarouselItem
                    key={index}
                    className="pl-3 md:pl-4 basis-full sm:basis-1/2 md:basis-1/3 lg:basis-1/4"
                  >
                    <div className="group relative h-[440px] w-full rounded-3xl overflow-hidden shadow-lg shadow-[#184E48]/[0.08] border border-[#184E48]/20 hover:border-[#184E48]/60 hover:shadow-2xl hover:shadow-[#184E48]/25 transition-all duration-500 cursor-pointer flex flex-col justify-between p-6">
                      {/* Background Image */}
                      <img
                        src={step.image}
                        alt={step.title}
                        className="absolute inset-0 w-full h-full object-cover transition-transform duration-700 ease-out group-hover:scale-110"
                      />

                      {/* Gradient overlays for contrast */}
                      <div className="absolute inset-0 bg-gradient-to-b from-black/80 via-black/30 to-black/90 group-hover:from-black/85 group-hover:via-black/50 group-hover:to-black/95 transition-all duration-500 pointer-events-none" />

                     
                      <div className="absolute -right-2 -top-4 text-[95px] font-black text-white/20 group-hover:text-emerald-300/20 transition-colors duration-500 pointer-events-none select-none z-[1]">
                        {step.number}
                      </div>

                      {/* Top Bar: Title on Top & Subtle Step Number on Side */}
                      <div className="relative z-10 flex flex-col gap-2">
                        

                        {/* Main Title at Top */}
                        <div className="mt-3">
                          <h3 className="text-2xl font-bold text-white group-hover:text-emerald-300 transition-colors duration-300 tracking-tight">
                            {step.title}
                          </h3>
                          <p className="text-xs font-medium text-emerald-400/90 mt-0.5 tracking-wide">
                            {step.subtitle}
                          </p>
                        </div>
                      </div>

                      {/* Bottom Hover Details Container */}
                      <div className="relative z-10">
                        {/* Hover indicator (visible when not hovered) */}
                        <div className="flex items-center justify-between text-xs text-white/60 group-hover:opacity-0 group-hover:pointer-events-none transition-opacity duration-300">
                          <span className="font-medium tracking-wide">{t('landing.hoverForDetails')}</span>
                          <ArrowRight className="w-3.5 h-3.5" />
                        </div>

                        {/* Details content (Revealed on hover) */}
                        <div className="max-h-0 opacity-0 group-hover:max-h-56 group-hover:opacity-100 overflow-hidden transition-all duration-500 ease-out flex flex-col justify-end pt-2">
                          <p className="text-xs md:text-sm leading-relaxed text-slate-200 font-normal border-t border-white/15 pt-3">
                            {step.description}
                          </p>

                          
                        </div>
                      </div>
                    </div>
                  </CarouselItem>
                )
              })}
            </CarouselContent>
          </Carousel>

          {/* Carousel Dots */}
          <div className="flex justify-center gap-2 mt-8">
            {steps.map((_, index) => (
              <button
                key={index}
                onClick={() => api?.scrollTo(index)}
                className={`h-2 rounded-full transition-all duration-300 ${
                  current === index + 1 ? "bg-[#184E48] w-8" : "bg-[#184E48]/20 w-2 hover:bg-[#184E48]/40"
                }`}
                aria-label={`Go to slide ${index + 1}`}
              />
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}

