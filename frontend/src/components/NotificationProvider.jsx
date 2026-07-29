import React, { createContext, useContext, useState, useCallback, useEffect, useRef } from 'react'
import { useAuth } from '../hooks/useAuth'
import { listResources, updateResource, deleteResource } from '../api'
import NotificationToast from './NotificationToast'
import { useNavigate } from 'react-router-dom'

export const NotificationContext = createContext(null)

export function NotificationProvider({ children }) {
  const { token, profile, isAuthenticated } = useAuth()
  const navigate = useNavigate()
  const [notifications, setNotifications] = useState([])
  const [unreadCount, setUnreadCount] = useState(0)
  const [toasts, setToasts] = useState([])
  const [loading, setLoading] = useState(false)
  const [total, setTotal] = useState(0)
  const [filters, setFilters] = useState({
    category: null,
    priority: null,
    is_read: null,
    is_archived: false,
    search: '',
    sort_by: 'created_on',
    order: 'desc',
  })
  const [pagination, setPagination] = useState({ skip: 0, limit: 20 })

  // Fetch notifications
  const fetchNotifications = useCallback(async (append = false) => {
    if (!token) return
    setLoading(true)
    try {
      const params = new URLSearchParams()
      params.set('skip', pagination.skip)
      params.set('limit', pagination.limit)
      if (filters.category) params.set('category', filters.category)
      if (filters.priority) params.set('priority', filters.priority)
      if (filters.is_read !== null) params.set('is_read', filters.is_read)
      if (filters.is_archived !== null) params.set('is_archived', filters.is_archived)
      if (filters.search) params.set('search', filters.search)
      params.set('sort_by', filters.sort_by)
      params.set('order', filters.order)

      const data = await listResources(token, 'notifications', params.toString())
      const items = data.notifications || []
      
      if (append) {
        setNotifications(prev => [...prev, ...items])
      } else {
        setNotifications(items)
      }
      setTotal(data.total || 0)
      setUnreadCount(data.unread_count || 0)
    } catch (e) {
      console.error('Failed to fetch notifications:', e)
    } finally {
      setLoading(false)
    }
  }, [token, pagination, filters])

  // Initial fetch
  useEffect(() => {
    if (isAuthenticated && token) {
      fetchNotifications()
    }
  }, [isAuthenticated, token, filters.category, filters.priority, filters.is_read, filters.is_archived, filters.search])

  // Handle incoming real-time notification
  const handleIncomingNotification = useCallback((notification) => {
    // Add to top of list
    setNotifications(prev => [notification, ...prev])
    setUnreadCount(prev => prev + 1)
    setTotal(prev => prev + 1)

    // Show toast
    setToasts(prev => [...prev, notification])
  }, [])

  // Dismiss toast
  const dismissToast = useCallback((id) => {
    setToasts(prev => prev.filter(t => t.id !== id))
  }, [])

  // Navigate from toast
  const handleToastNavigate = useCallback((module, recordId) => {
    const moduleRoutes = {
      homework: '/student/homework',
      'exam-results': '/student/exams',
      exams: '/student/exams',
      fees: '/student/fees',
      attendance: '/student/attendance',
      notices: '/notices',
      events: '/events',
      messages: '/student/messages',
      documents: '/student/documents',
      certificates: '/certificates',
      enrollments: '/students',
      teachers: '/teachers',
      payments: '/payments',
    }
    const route = moduleRoutes[module]
    if (route) {
      navigate(route)
    }
  }, [navigate])

  // Mark single notification as read
  const markAsRead = useCallback(async (id) => {
    try {
      await updateResource(token, 'notifications', `${id}/read`, {})
      setNotifications(prev => prev.map(n => n.id === id ? { ...n, is_read: true } : n))
      setUnreadCount(prev => Math.max(0, prev - 1))
    } catch (e) {
      console.error('Failed to mark as read:', e)
    }
  }, [token])

  // Mark all as read
  const markAllAsRead = useCallback(async () => {
    try {
      await updateResource(token, 'notifications/read-all', '', {})
      setNotifications(prev => prev.map(n => ({ ...n, is_read: true })))
      setUnreadCount(0)
    } catch (e) {
      console.error('Failed to mark all as read:', e)
    }
  }, [token])

  // Delete notification
  const deleteNotification = useCallback(async (id) => {
    try {
      await deleteResource(token, 'notifications', id)
      setNotifications(prev => prev.filter(n => n.id !== id))
      setTotal(prev => Math.max(0, prev - 1))
    } catch (e) {
      console.error('Failed to delete notification:', e)
    }
  }, [token])

  // Delete all read notifications
  const deleteAllRead = useCallback(async () => {
    try {
      await deleteResource(token, 'notifications/read', '')
      setNotifications(prev => prev.filter(n => !n.is_read))
    } catch (e) {
      console.error('Failed to delete read notifications:', e)
    }
  }, [token])

  // Archive notification
  const archiveNotification = useCallback(async (id) => {
    try {
      await updateResource(token, 'notifications', `${id}/archive`, {})
      setNotifications(prev => prev.map(n => n.id === id ? { ...n, is_archived: true } : n))
    } catch (e) {
      console.error('Failed to archive notification:', e)
    }
  }, [token])

  // Restore archived notification
  const restoreNotification = useCallback(async (id) => {
    try {
      await updateResource(token, 'notifications', `${id}/restore`, {})
      setNotifications(prev => prev.map(n => n.id === id ? { ...n, is_archived: false } : n))
    } catch (e) {
      console.error('Failed to restore notification:', e)
    }
  }, [token])

  // Pin/unpin notification
  const pinNotification = useCallback(async (id) => {
    try {
      await updateResource(token, 'notifications', `${id}/pin`, {})
      setNotifications(prev => prev.map(n => n.id === id ? { ...n, is_pinned: !n.is_pinned } : n))
    } catch (e) {
      console.error('Failed to pin notification:', e)
    }
  }, [token])

  // Load more for pagination
  const loadMore = useCallback(() => {
    setPagination(prev => ({ ...prev, skip: prev.skip + prev.limit }))
  }, [])

  // Reset pagination when filters change
  useEffect(() => {
    setPagination({ skip: 0, limit: 20 })
  }, [filters.category, filters.priority, filters.is_read, filters.search])

  const value = {
    notifications,
    unreadCount,
    total,
    loading,
    filters,
    setFilters,
    pagination,
    fetchNotifications,
    markAsRead,
    markAllAsRead,
    deleteNotification,
    deleteAllRead,
    archiveNotification,
    restoreNotification,
    pinNotification,
    loadMore,
    handleIncomingNotification,
    refresh: () => fetchNotifications(),
  }

  return (
    <NotificationContext.Provider value={value}>
      {children}
      {/* Toast notifications */}
      <div className="notification-toast-container">
        {toasts.slice(-3).map(notification => (
          <NotificationToast
            key={notification.id}
            notification={notification}
            onDismiss={dismissToast}
            onNavigate={handleToastNavigate}
          />
        ))}
      </div>
    </NotificationContext.Provider>
  )
}

export function useNotifications() {
  const context = useContext(NotificationContext)
  if (!context) {
    throw new Error('useNotifications must be used within NotificationProvider')
  }
  return context
}
