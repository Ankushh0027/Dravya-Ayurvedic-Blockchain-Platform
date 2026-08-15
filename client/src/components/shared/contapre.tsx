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
import { useTranslation } from 'react-i18next'

export function ContactPreviewCard({ className, headerClassName }: { className?: string; headerClassName?: string }) {
  const { t } = useTranslation()
  const [count, setCount] = useState(1)
  const [isVisible, setIsVisible] = useState(false)
  const cardRef = useRef<HTMLDivElement>(null)

  const messages = [
    { id: '1', role: 'contact', text: t('about.chat.msg1') },
    { id: '2', role: 'contact', text: t('about.chat.msg2') },
    { id: '3', role: 'contact', text: t('about.chat.msg3') },
    { id: '4', role: 'contact', text: t('about.chat.msg4') },
    { id: '5', role: 'contact', text: t('about.chat.msg5') },
    { id: '6', role: 'user', text: t('about.chat.msg6') },
    { id: '7', role: 'user', text: t('about.chat.msg7') },
    { id: '8', role: 'user', text: t('about.chat.msg8') },
    { id: '9', role: 'contact', text: t('about.chat.msg9') },
    { id: '10', role: 'user', text: t('about.chat.msg10') },
  ]

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
  }, [count, isVisible, messages.length])

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
          <p className="text-sm font-semibold leading-none">{t('about.chat.roleFarmer')}</p>
          <p className="text-xs text-white/70 mt-1">{t('about.chat.online')}</p>
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
