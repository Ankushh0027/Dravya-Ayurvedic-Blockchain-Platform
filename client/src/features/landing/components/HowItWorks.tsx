import React from "react"
import {
  Leaf,
  FlaskConical,
  Factory,
  Package,
  Users,
  ArrowRight,
} from "lucide-react"

export function HowItWorks() {
  const steps = [
    {
      icon: Leaf,
      number: "01",
      title: "Harvest",
      description: "Farmers create batches with crop and origin details.",
    },
    {
      icon: FlaskConical,
      number: "02",
      title: "Verify",
      description: "Labs and authorities verify quality and authenticity.",
    },
    {
      icon: Factory,
      number: "03",
      title: "Process",
      description: "Manufacturers process the herbs and record each stage.",
    },
    {
      icon: Package,
      number: "04",
      title: "Distribute",
      description: "Distributors and retailers maintain complete traceability.",
    },
    {
      icon: Users,
      number: "05",
      title: "Consumer",
      description: "Consumers scan a QR code to explore the complete journey.",
    },
  ]

  return (
    <section className="relative overflow-hidden bg-[#F7FAF7] py-24 md:py-32">
      
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <div className="mx-auto max-w-3xl text-center">
          <span className="mb-4 inline-flex items-center rounded-full border border-[#D5E2DB] bg-white px-4 py-1.5 text-xs font-semibold uppercase tracking-[0.18em] text-[#1a4a2c]">
            How It Works
          </span>

          <h2 className="text-4xl font-bold tracking-tight text-slate-900 md:text-5xl">
            Every Step.
            <span className="text-[#1a4a2c]"> Every Time. Verified.</span>
          </h2>

          <p className="mx-auto mt-5 max-w-2xl text-base leading-7 text-slate-500 md:text-lg">
            Dravya connects every stage of the Ayurvedic supply chain on one
            transparent platform, creating trust from harvest to consumer.
          </p>
        </div>

        <div className="relative mt-16">
          <div className="hidden lg:block absolute left-[10%] right-[10%] top-[47px] border-t border-dashed border-[#B8D0C3]" />

          <div className="grid grid-cols-1 gap-10 md:grid-cols-2 lg:grid-cols-5 lg:gap-4">
            {steps.map((step, index) => {
              const Icon = step.icon

              return (
                <div
                  key={step.title}
                  className="group relative flex flex-col items-center text-center"
                >
                  <div className="relative z-10 flex h-24 w-24 items-center justify-center rounded-2xl border border-[#D5E2DB] bg-white shadow-sm transition-all duration-300 group-hover:-translate-y-1 group-hover:shadow-lg">
                    <Icon
                      className="h-9 w-9 text-[#1a4a2c]"
                      strokeWidth={1.6}
                    />

                    <span className="absolute -right-2 -top-2 flex h-7 w-7 items-center justify-center rounded-full bg-[#1a4a2c] text-[10px] font-bold text-white">
                      {step.number}
                    </span>
                  </div>

                  <h3 className="mt-6 text-base font-bold text-slate-900">
                    {step.title}
                  </h3>

                  <p className="mt-2 max-w-[210px] text-sm leading-6 text-slate-500">
                    {step.description}
                  </p>

                  {index < steps.length - 1 && (
                    <ArrowRight
                      className="absolute -right-4 top-9 hidden h-5 w-5 text-[#A8C2B3] lg:block"
                      strokeWidth={1.8}
                    />
                  )}
                </div>
              )
            })}
          </div>
        </div>
      </div>
    </section>
  )
}

  

