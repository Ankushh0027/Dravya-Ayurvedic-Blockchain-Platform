'use client'

import { useEffect, useState, useRef } from 'react'
import { cn } from '@/lib/utils'
import {
  MessageScroller,
  MessageScrollerContent,
  MessageScrollerItem,
  MessageScrollerProvider,
  MessageScrollerViewport,
} from '@/components/ui/message-scroller'

const messages = [
  { id: '1', role: 'contact', text: "Buyers keep rejecting my herbs, calling them fake." },
  { id: '2', role: 'contact', text: "I have no way to prove they're genuine." },
  { id: '3', role: 'contact', text: "Middlemen take most of the profit anyway." },
  { id: '4', role: 'contact', text: "Years of honest farming, and still no one trusts me." },
  { id: '5', role: 'contact', text: "I don't even know where my herbs end up after I sell them." },
  { id: '6', role: 'user', text: "That changes today." },
  { id: '7', role: 'user', text: "With Dravya, every batch you sell gets a digital record." },
  { id: '8', role: 'user', text: "From your farm, to the lab, to the shelf — all tracked." },
  { id: '9', role: 'contact', text: "So buyers can actually verify it's mine?" },
  { id: '10', role: 'user', text: "Exactly. Your herbs finally speak for themselves." },
]

export function ContactPreviewCard({ className, headerClassName }: { className?: string; headerClassName?: string }) {
  const [count, setCount] = useState(1)
  const [isVisible, setIsVisible] = useState(false)
  const cardRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const element = cardRef.current
    if (!element) return

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setIsVisible(true)
          } else {
            setIsVisible(false)
          }
        })
      },
      { threshold: 0.25 }
    )

    observer.observe(element)

    return () => {
      observer.disconnect()
    }
  }, [])

  useEffect(() => {
    if (!isVisible) return

    if (count < messages.length) {
      const timer = setTimeout(() => setCount((prev) => prev + 1), 1800)
      return () => clearTimeout(timer)
    } else {
      const timer = setTimeout(() => setCount(1), 3500)
      return () => clearTimeout(timer)
    }
  }, [count, isVisible])

  return (
    <div
      ref={cardRef}
      className={cn("w-full max-w-xl rounded-2xl border border-[#184E48] bg-white shadow-xl overflow-hidden", className)}
    >
      <div className={cn("flex items-center gap-3 px-4 py-3 text-white", headerClassName)}>
        <div className="w-9 h-9 rounded-full bg-white/20 flex items-center justify-center font-semibold text-sm">
          F
        </div>
        <div>
          <p className="text-sm font-semibold leading-none">Farmer</p>
          <p className="text-xs text-white/70 mt-1">Online</p>
        </div>
      </div>

      <MessageScrollerProvider defaultScrollPosition="end" autoScroll>
        <MessageScroller className="h-64">
          <MessageScrollerViewport>
            <MessageScrollerContent className="flex flex-col gap-3 p-4">
              {messages.slice(0, count).map((message) => (
                <MessageScrollerItem key={message.id} messageId={message.id} scrollAnchor={message.role === 'user'}>
                  <div className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div
                      className={`max-w-[75%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${
                        message.role === 'user'
                          ? 'bg-[#184E48] text-white rounded-br-md'
                          : 'bg-slate-100 text-slate-800 rounded-bl-md'
                      }`}
                    >
                      {message.text}
                    </div>
                  </div>
                </MessageScrollerItem>
              ))}
            </MessageScrollerContent>
          </MessageScrollerViewport>
        </MessageScroller>
      </MessageScrollerProvider>
    </div>
  )
}
