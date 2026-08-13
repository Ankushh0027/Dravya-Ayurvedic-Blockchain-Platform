'use client'

import * as React from 'react'
import { cn } from '@/lib/utils'

// ─── Context ──────────────────────────────────────────────────────────────────

interface MessageScrollerContextValue {
  scrollRef: React.RefObject<HTMLDivElement | null>
  autoScroll: boolean
  defaultScrollPosition: 'start' | 'end'
}

const MessageScrollerContext = React.createContext<MessageScrollerContextValue>({
  scrollRef: { current: null },
  autoScroll: false,
  defaultScrollPosition: 'end',
})

// ─── Provider ─────────────────────────────────────────────────────────────────

interface MessageScrollerProviderProps {
  children: React.ReactNode
  autoScroll?: boolean
  defaultScrollPosition?: 'start' | 'end'
}

function MessageScrollerProvider({
  children,
  autoScroll = false,
  defaultScrollPosition = 'end',
}: MessageScrollerProviderProps) {
  const scrollRef = React.useRef<HTMLDivElement>(null)

  const value = React.useMemo(
    () => ({ scrollRef, autoScroll, defaultScrollPosition }),
    [autoScroll, defaultScrollPosition],
  )

  return (
    <MessageScrollerContext.Provider value={value}>
      {children}
    </MessageScrollerContext.Provider>
  )
}

// ─── Root Scroller ─────────────────────────────────────────────────────────────

function MessageScroller({
  className,
  children,
  ...props
}: React.ComponentProps<'div'>) {
  return (
    <div
      data-slot="message-scroller"
      className={cn('relative overflow-hidden', className)}
      {...props}
    >
      {children}
    </div>
  )
}

// ─── Viewport ─────────────────────────────────────────────────────────────────

function MessageScrollerViewport({
  className,
  children,
  ...props
}: React.ComponentProps<'div'>) {
  const { scrollRef, autoScroll, defaultScrollPosition } =
    React.useContext(MessageScrollerContext)

  // Scroll to bottom/top on mount
  React.useLayoutEffect(() => {
    const el = scrollRef.current
    if (!el) return
    if (defaultScrollPosition === 'end') {
      el.scrollTop = el.scrollHeight
    } else {
      el.scrollTop = 0
    }
  }, [defaultScrollPosition, scrollRef])

  // Auto-scroll when content changes
  React.useEffect(() => {
    if (!autoScroll) return
    const el = scrollRef.current
    if (!el) return

    const observer = new MutationObserver(() => {
      el.scrollTo({ top: el.scrollHeight, behavior: 'smooth' })
    })

    observer.observe(el, { childList: true, subtree: true })
    return () => observer.disconnect()
  }, [autoScroll, scrollRef])

  return (
    <div
      ref={scrollRef}
      data-slot="message-scroller-viewport"
      className={cn('h-full w-full overflow-y-auto', className)}
      {...props}
    >
      {children}
    </div>
  )
}

// ─── Content ──────────────────────────────────────────────────────────────────

function MessageScrollerContent({
  className,
  ...props
}: React.ComponentProps<'div'>) {
  return (
    <div
      data-slot="message-scroller-content"
      className={cn('min-w-full', className)}
      {...props}
    />
  )
}

// ─── Item ─────────────────────────────────────────────────────────────────────

interface MessageScrollerItemProps extends React.ComponentProps<'div'> {
  messageId: string
  scrollAnchor?: boolean
}

function MessageScrollerItem({
  className,
  messageId,
  scrollAnchor = false,
  ...props
}: MessageScrollerItemProps) {
  const { scrollRef, autoScroll } = React.useContext(MessageScrollerContext)

  const itemRef = React.useRef<HTMLDivElement>(null)

  React.useEffect(() => {
    if (!scrollAnchor || !autoScroll) return
    const el = scrollRef.current
    if (!el) return
    el.scrollTo({ top: el.scrollHeight, behavior: 'smooth' })
  }, [scrollAnchor, autoScroll, scrollRef])

  return (
    <div
      ref={itemRef}
      data-slot="message-scroller-item"
      data-message-id={messageId}
      className={cn('w-full', className)}
      {...props}
    />
  )
}

// ─── Exports ──────────────────────────────────────────────────────────────────

export {
  MessageScroller,
  MessageScrollerContent,
  MessageScrollerItem,
  MessageScrollerProvider,
  MessageScrollerViewport,
}
