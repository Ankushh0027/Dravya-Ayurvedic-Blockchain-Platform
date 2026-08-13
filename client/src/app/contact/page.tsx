'use client'

import { LandingNavbar } from '@/features/landing/components/LandingNavbar'
import { Footer } from '@/features/landing/components/Footer'
import { FloatingLeaf } from '@/features/landing/components/FloatingLeaf'
import {
  Mail,
  Phone,
  MapPin,
  Send,
  MessageSquare,
  Sprout,
  Clock,
  Building2,
  ArrowRight,
  Award,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useState } from 'react'
import Link from 'next/link'

const contactInfo = [
  {
    icon: Mail,
    title: 'Email Us',
    detail: 'hello@dravya.in',
    sub: 'We respond within 24 hours',
  },
  {
    icon: Phone,
    title: 'Call Us',
    detail: '+91 98765 43210',
    sub: 'Mon–Sat, 9am to 6pm IST',
  },
{
  icon: MapPin,
  title: 'Campus',
  detail: 'Galgotias College, Greater Noida',
  sub: 'Uttar Pradesh — 203201',
},
  {
    icon: Clock,
    title: 'Support Hours',
    detail: 'Mon – Sat',
    sub: '9:00 AM – 6:00 PM IST',
  },
]

const roles = [
  'Herb Producer / Farmer',
  'Laboratory / Testing Agency',
  'Manufacturer / Processor',
  'Distributor / Trader',
  'Retailer / Pharmacy',
  'Investor / Partner',
  'Press / Media',
  'Other',
]

export default function ContactPage() {
  const [submitted, setSubmitted] = useState(false)
  const [form, setForm] = useState({
    name: '',
    email: '',
    role: '',
    message: '',
  })

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitted(true)
  }

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
          <FloatingLeaf className="w-full h-auto text-[#184E48]" rotate={-30} />
        </div>
        <div className="absolute bottom-8 right-14 w-[85px] lg:w-[115px] pointer-events-none z-0 opacity-25 mix-blend-multiply">
          <FloatingLeaf className="w-full h-auto text-[#184E48]" rotate={115} />
        </div>

        <div className="relative z-10 max-w-4xl mx-auto">
         

          {/* Heading */}
          <h1 className="text-4xl md:text-6xl lg:text-[4.75rem] font-bold tracking-tight text-[#1e293b] leading-[1.08] font-serif mb-6">
            We'd love to
            <span className="block text-[#184E48] mt-2">hear from you.</span>
          </h1>

          {/* Subtitle */}
          <p className="text-[17px] md:text-[19px] lg:text-[20px] text-slate-600 leading-relaxed font-medium max-w-xl mx-auto mb-6">
            Whether you're a farmer, lab, manufacturer, or just curious about Dravya — reach out and
            let's start a conversation.
          </p>
        </div>
      </section>

      {/* Main Contact Grid Section - White Background */}
      <section className=" max-w-7xl mx-auto px-6 w-full">
        <div className="grid lg:grid-cols-5 gap-12 items-start">

          {/* Left — Info cards */}
          <div className="lg:col-span-2 flex flex-col gap-5">
            <div>
             
              <h2 className="text-3xl font-bold text-[#1e293b] font-serif mt-1 mb-2">Let's connect</h2>
              <p className="text-slate-600 leading-relaxed text-sm font-medium">
                Our team is ready to help you get onboarded, answer questions, or explore partnership opportunities.
              </p>
            </div>

            {contactInfo.map(({ icon: Icon, title, detail, sub }) => (
              <div
                key={title}
                className="flex items-start gap-4 bg-white border border-slate-100 rounded-2xl p-5 shadow-sm hover:shadow-xl hover:shadow-[#184E48]/8 hover:border-[#184E48]/20 hover:-translate-y-0.5 transition-all duration-300"
              >
                <div className="w-11 h-11 flex-shrink-0 rounded-xl bg-[#184E48] flex items-center justify-center shadow-md shadow-[#184E48]/20">
                  <Icon className="w-5 h-5 text-white" />
                </div>
                <div>
                  <p className="text-xs text-slate-400 font-bold uppercase tracking-wide">{title}</p>
                  <p className="text-[#1e293b] font-bold text-base mt-0.5 font-serif">{detail}</p>
                  <p className="text-slate-500 text-xs mt-0.5 font-medium">{sub}</p>
                </div>
              </div>
            ))}

       
          </div>

          {/* Right — Form */}
          <div className="lg:col-span-3">
            {submitted ? (
              <div className="flex flex-col items-center justify-center text-center py-20 px-8 bg-[#E1E9E1]/30 border border-[#184E48]/20 rounded-3xl h-full shadow-sm">
                <div className="w-20 h-20 rounded-full bg-[#184E48] flex items-center justify-center mb-6 shadow-xl shadow-[#184E48]/30">
                  <img src="logo-out.png" className="rounded-full object-cover object-center text-white" />
                </div>
                <h3 className="text-3xl font-bold text-[#1e293b] font-serif mb-3">Message Sent!</h3>
                <p className="text-slate-600 max-w-sm leading-relaxed font-medium">
                  Thank you for reaching out. Our team will get back to you within 24 hours.
                </p>
                <button
                  onClick={() => { setSubmitted(false); setForm({ name: '', email: '', role: '', message: '' }) }}
                  className="mt-8 text-[#184E48] font-bold underline underline-offset-4 text-sm hover:opacity-80 transition-opacity"
                >
                  Send another message
                </button>
              </div>
            ) : (
              <form
                onSubmit={handleSubmit}
                className="bg-white border border-slate-100 rounded-3xl p-8 lg:p-10 shadow-lg shadow-slate-100 space-y-6"
              >
                <div>
                  <h3 className="text-2xl font-bold text-[#1e293b] font-serif mb-1">Send us a message</h3>
                  <p className="text-slate-500 text-sm font-medium">Fill in the form and we'll get back to you shortly.</p>
                </div>

                <div className="grid sm:grid-cols-2 gap-5">
                  <div className="flex flex-col gap-2">
                    <label className="text-sm font-bold text-slate-700" htmlFor="name">
                      Full Name <span className="text-red-400">*</span>
                    </label>
                    <input
                      id="name"
                      name="name"
                      type="text"
                      required
                      value={form.name}
                      onChange={handleChange}
                      placeholder="Your full name"
                      className="w-full px-4 py-3 rounded-xl border border-slate-200 text-sm text-slate-800 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-[#184E48]/30 focus:border-[#184E48] transition-all font-medium"
                    />
                  </div>
                  <div className="flex flex-col gap-2">
                    <label className="text-sm font-bold text-slate-700" htmlFor="email">
                      Email Address <span className="text-red-400">*</span>
                    </label>
                    <input
                      id="email"
                      name="email"
                      type="email"
                      required
                      value={form.email}
                      onChange={handleChange}
                      placeholder="you@example.com"
                      className="w-full px-4 py-3 rounded-xl border border-slate-200 text-sm text-slate-800 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-[#184E48]/30 focus:border-[#184E48] transition-all font-medium"
                    />
                  </div>
                </div>

                <div className="flex flex-col gap-2">
                  <label className="text-sm font-bold text-slate-700" htmlFor="role">
                    I am a... <span className="text-red-400">*</span>
                  </label>
                  <select
                    id="role"
                    name="role"
                    required
                    value={form.role}
                    onChange={handleChange}
                    className="w-full px-4 py-3 rounded-xl border border-slate-200 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-[#184E48]/30 focus:border-[#184E48] transition-all bg-white font-medium"
                  >
                    <option value="">Select your role</option>
                    {roles.map((r) => (
                      <option key={r} value={r}>{r}</option>
                    ))}
                  </select>
                </div>

                <div className="flex flex-col gap-2">
                  <label className="text-sm font-bold text-slate-700" htmlFor="message">
                    Message <span className="text-red-400">*</span>
                  </label>
                  <textarea
                    id="message"
                    name="message"
                    required
                    rows={5}
                    value={form.message}
                    onChange={handleChange}
                    placeholder="Tell us how we can help you..."
                    className="w-full px-4 py-3 rounded-xl border border-slate-200 text-sm text-slate-800 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-[#184E48]/30 focus:border-[#184E48] transition-all resize-none font-medium"
                  />
                </div>

                <Button
                  type="submit"
                  className="w-full bg-[#184E48] hover:bg-[#184E48]/90 text-white rounded-xl py-6 text-base font-semibold gap-2 shadow-lg shadow-[#184E48]/20 hover:shadow-[#184E48]/30 hover:-translate-y-0.5 transition-all duration-300"
                >
                  <Send className="w-4 h-4" />
                  Send Message
                </Button>

                <p className="text-center text-xs text-slate-400 font-medium">
                  By submitting, you agree to our{' '}
                  <a href="#" className="text-[#184E48] underline underline-offset-2">Privacy Policy</a>.
                </p>
              </form>
            )}
          </div>
        </div>
      </section>


     

      <Footer className="bg-[#184E48]" />
    </div>
  )
}
