import { BadgeCheck, BrainCircuit, Leaf } from "lucide-react"
import { LeafSprig } from "./LeafSprig"
import { FloatingLeaf } from "./FloatingLeaf"
export function AIVerification() {
  return (
    <section className="bg-[#F7FAF7] py-24">
      <div className="mx-auto grid max-w-6xl items-center gap-12 px-6 md:grid-cols-2">
        <div>
          <span className="inline-flex items-center gap-2 text-sm font-semibold uppercase tracking-[0.15em] text-[#1a4a2c]">
            <BrainCircuit className="h-4 w-4" />
            AI Verification
          </span>

          <h2 className="mt-4 text-4xl font-bold tracking-tight text-slate-900 md:text-5xl">
            Identify. Analyze.
            <span className="text-[#1a4a2c]"> Verify.</span>
          </h2>

          <p className="mt-5 max-w-lg text-base leading-7 text-slate-500 md:text-lg">
            Dravya uses AI-powered image analysis to identify medicinal herbs
            and verify their authenticity, quality, and origin.
          </p>

          <div className="mt-8 flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[#E1E9E1]">
              <BadgeCheck className="h-5 w-5 text-[#1a4a2c]" />
            </div>

            <div>
              <p className="text-sm font-semibold text-slate-900">
                Intelligent Herb Recognition
              </p>
              <p className="text-sm text-slate-500">
                Fast and reliable visual analysis
              </p>
            </div>
          </div>
        </div>

        <div className="flex justify-center">
          <div className="relative w-full max-w-md overflow-hidden rounded-[28px] border border-[#D5E2DB] bg-white p-3 shadow-[0_20px_50px_rgba(26,74,44,0.10)]">
            <img
              src="/tul-ki-si.jpg"
              alt="Medicinal herb"
              className="h-[420px] w-full rounded-[20px] object-cover"
            />

            <div className="absolute bottom-7 left-7 right-7 flex items-center gap-3 rounded-2xl border border-white/70 bg-white/90 p-4 shadow-lg backdrop-blur">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#E1E9E1]">
                <Leaf className="h-5 w-5 text-[#1a4a2c]" />
              </div>

              <div>
                <p className="text-sm font-semibold text-slate-900">
                  Herb Identified
                </p>
                <p className="text-xs text-slate-500">
                  AI analysis complete
                </p>
              </div>

              <BadgeCheck className="ml-auto h-5 w-5 text-[#1a4a2c]" />
            </div>
          </div>
        </div>
      </div>
      <div className="absolute bottom-[25%] left-0 w-[200px] md:w-[300px] lg:w-[400px] pointer-events-none z-0 opacity-75 mix-blend-multiply transform -translate-x-[15%]">
          <LeafSprig className="w-full h-auto text-primary" />
        </div>
        <div className="absolute bottom-[15%] right-0 w-[200px] md:w-[300px] lg:w-[400px] pointer-events-none z-0 opacity-75 mix-blend-multiply transform ">
          <LeafSprig className="w-full h-auto text-primary" flip={true} />
        </div>
        <div className="absolute bottom-[16%] left-[11%] w-[110px] md:w-[115px] lg:w-[160px] pointer-events-none z-0 opacity-50 mix-blend-multiply">
                  <FloatingLeaf className="w-full h-auto text-primary" rotate={-50} />
                </div>
                 <div className="absolute bottom-[35%] right-[11%] w-[110px] md:w-[135px] lg:w-[160px] pointer-events-none z-0 opacity-50 mix-blend-multiply">
                  <FloatingLeaf className="w-full h-auto text-primary" rotate={50} />
                </div>
                <div className="absolute bottom-[45%] left-[11%] w-[110px] md:w-[120px] lg:w-[120px] pointer-events-none z-0 opacity-50 mix-blend-multiply">
                  <FloatingLeaf className="w-full h-auto text-primary" rotate={-30  } />
                </div>
                 <div className="absolute bottom-[65%] left-[11%] w-[110px] md:w-[135px] lg:w-[140px] pointer-events-none z-0 opacity-50 mix-blend-multiply">
                  <FloatingLeaf className="w-full h-auto text-primary" rotate={-130  } />
                </div>
                <div className="absolute bottom-[55%] right-[11%] w-[110px] md:w-[135px] lg:w-[140px] pointer-events-none z-0 opacity-50 mix-blend-multiply">
                  <FloatingLeaf className="w-full h-auto text-primary" rotate={-290  } />
                </div>
      
    </section>
  )
}