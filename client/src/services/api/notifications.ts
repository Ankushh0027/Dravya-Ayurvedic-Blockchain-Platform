import api from './axios'

export interface Notification {
  id: string
  userId: string
  type: string
  title: string
  message: string
  entityType?: string
  entityId?: string
  eventKey?: string
  isRead: boolean
  priority: 'LOW' | 'NORMAL' | 'HIGH' | 'CRITICAL'
  createdAt: string
  updatedAt: string
}

export interface NotificationsResponse {
  notifications: Notification[]
  pagination: {
    total: number
    page: number
    limit: number
    totalPages: number
  }
}

export const notificationApi = {
  getNotifications: async (params?: { page?: number; limit?: number; isRead?: boolean; priority?: string }): Promise<NotificationsResponse> => {
    const { data } = await api.get<{ success: boolean, message: string, data: NotificationsResponse }>('/notifications', { params })
    return data.data
  },

  getUnreadCount: async (): Promise<{ count: number }> => {
    const { data } = await api.get<{ success: boolean, message: string, data: { count: number } }>('/notifications/unread-count')
    return data.data
  },

  markAsRead: async (id: string): Promise<Notification> => {
    const { data } = await api.patch<{ success: boolean, message: string, data: { notification: Notification } }>(`/notifications/${id}/read`)
    return data.data.notification
  },

  markAllAsRead: async (): Promise<{ count: number }> => {
    const { data } = await api.patch<{ success: boolean, message: string, data: { count: number } }>('/notifications/read-all')
    return data.data
  }
}
