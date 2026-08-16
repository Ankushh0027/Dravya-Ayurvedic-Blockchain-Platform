'use client'

import { useState, useEffect } from 'react'
import { Bell, Check, Trash2, Info, AlertTriangle, ShieldAlert } from 'lucide-react'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { notificationApi, Notification } from '@/services/api/notifications'
import { formatDistanceToNow } from 'date-fns'

export function NotificationBell() {
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [unreadCount, setUnreadCount] = useState(0)
  const [isOpen, setIsOpen] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  const fetchNotifications = async () => {
    try {
      setIsLoading(true)
      const data = await notificationApi.getNotifications({ limit: 10 })
      setNotifications(data.notifications)
      
      const countData = await notificationApi.getUnreadCount()
      setUnreadCount(countData.count)
    } catch (error) {
      console.error('Failed to fetch notifications:', error)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchNotifications()
    // Optional: Add polling here if needed
  }, [])

  const handleMarkAsRead = async (id: string) => {
    try {
      await notificationApi.markAsRead(id)
      setNotifications(notifications.map(n => 
        n.id === id ? { ...n, isRead: true } : n
      ))
      setUnreadCount(prev => Math.max(0, prev - 1))
    } catch (error) {
      console.error('Failed to mark notification as read:', error)
    }
  }

  const handleMarkAllAsRead = async () => {
    try {
      await notificationApi.markAllAsRead()
      setNotifications(notifications.map(n => ({ ...n, isRead: true })))
      setUnreadCount(0)
    } catch (error) {
      console.error('Failed to mark all as read:', error)
    }
  }

  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'CRITICAL': return <ShieldAlert className="h-4 w-4 text-red-500" />
      case 'HIGH': return <AlertTriangle className="h-4 w-4 text-orange-500" />
      case 'NORMAL': return <Info className="h-4 w-4 text-blue-500" />
      default: return <Info className="h-4 w-4 text-slate-400" />
    }
  }

  return (
    <DropdownMenu open={isOpen} onOpenChange={(open) => {
      setIsOpen(open)
      if (open) fetchNotifications()
    }}>
      <DropdownMenuTrigger render={
        <Button variant="ghost" size="icon" className="relative text-slate-500 hover:text-slate-900 rounded-lg">
          <Bell className="h-5 w-5" />
          {unreadCount > 0 && (
            <span className="absolute top-1 right-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-red-500 text-[9px] font-bold text-white shadow-sm ring-2 ring-white">
              {unreadCount > 99 ? '99+' : unreadCount}
            </span>
          )}
        </Button>
      } />
      
      <DropdownMenuContent align="end" className="w-80 p-0 rounded-xl shadow-xl border border-slate-200/60 bg-white/95 backdrop-blur-xl">
        <div className="flex items-center justify-between px-4 py-3 border-b border-slate-100 bg-slate-50/50 rounded-t-xl">
          <span className="font-semibold text-slate-800 text-sm">Notifications</span>
          {unreadCount > 0 && (
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={handleMarkAllAsRead}
              className="h-8 px-2 text-xs font-medium text-slate-500 hover:text-[#184E48] hover:bg-[#184E48]/10"
            >
              Mark all as read
            </Button>
          )}
        </div>
        
        <div className="max-h-[360px] overflow-y-auto py-1">
          {isLoading && notifications.length === 0 ? (
            <div className="p-4 text-center text-sm text-slate-500">Loading...</div>
          ) : notifications.length === 0 ? (
            <div className="p-8 text-center flex flex-col items-center justify-center text-slate-500">
              <Bell className="h-8 w-8 mb-2 text-slate-300" />
              <p className="text-sm font-medium text-slate-600">No notifications yet</p>
              <p className="text-xs text-slate-400 mt-1">When you get notifications, they'll show up here.</p>
            </div>
          ) : (
            notifications.map((notification) => (
              <DropdownMenuItem 
                key={notification.id} 
                className={`flex flex-col items-start px-4 py-3 cursor-default focus:bg-slate-50 ${!notification.isRead ? 'bg-[#184E48]/5' : ''}`}
                onSelect={(e) => e.preventDefault()}
              >
                <div className="flex w-full items-start gap-3">
                  <div className="mt-0.5 flex-shrink-0">
                    {getPriorityIcon(notification.priority)}
                  </div>
                  <div className="flex-1 space-y-1">
                    <p className={`text-sm font-medium leading-none ${!notification.isRead ? 'text-slate-900' : 'text-slate-600'}`}>
                      {notification.title}
                    </p>
                    <p className="text-xs text-slate-500 line-clamp-2">
                      {notification.message}
                    </p>
                    <p className="text-[10px] font-medium text-slate-400 pt-1">
                      {formatDistanceToNow(new Date(notification.createdAt), { addSuffix: true })}
                    </p>
                  </div>
                  {!notification.isRead && (
                    <Button 
                      variant="ghost" 
                      size="icon"
                      className="h-6 w-6 rounded-full flex-shrink-0 text-slate-400 hover:text-[#184E48] hover:bg-[#184E48]/10"
                      onClick={(e) => {
                        e.stopPropagation()
                        handleMarkAsRead(notification.id)
                      }}
                      title="Mark as read"
                    >
                      <Check className="h-3.5 w-3.5" />
                    </Button>
                  )}
                </div>
              </DropdownMenuItem>
            ))
          )}
        </div>
        
        {notifications.length > 0 && (
          <div className="p-2 border-t border-slate-100 bg-slate-50/80 rounded-b-xl flex justify-center">
            <Button variant="ghost" size="sm" className="text-xs w-full text-slate-500 hover:text-slate-900">
              View all notifications
            </Button>
          </div>
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
