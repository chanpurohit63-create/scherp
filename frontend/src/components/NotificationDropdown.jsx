import React, { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import NotificationItem from './NotificationItem'
import { useAuth } from '../hooks/useAuth'
import { listResources, updateResource, deleteResource } from '../api'

export default function NotificationDropdown({ isOpen, onClose, unreadCount, onUnreadCountChange }) {
  const navigate = useNavigate()
  const { token } = useAuth()
  const dropdownRef = useRef(null)
  const [notifications, setNotifications] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (isOpen) {
      fetchLatestNotifications()
    }
  }, [isOpen])

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        onClose()
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [onClose])

  const fetchLatestNotifications = async () => {
    setLoading(true)
    try {
      const data = await listResources(token, 'notifications', 'limit=10&sort_by=created_on&order=desc')
      setNotifications(data.notifications || [])
    } catch (e) {
      console.error('Failed to fetch notifications:', e)
    } finally {
      setLoading(false)
    }
  }

  const handleMarkRead = async (id) => {
    try {
      await updateResource(token, 'notifications', `${id}/read`, {})
      setNotifications(prev => prev.map(n => n.id === id ? { ...n, is_read: true } : n))
      if (onUnreadCountChange) {
        onUnreadCountChange(Math.max(0, unreadCount - 1))
      }
    } catch (e) {
      console.error('Failed to mark as read:', e)
    }
  }

  const handleMarkAllRead = async () => {
    try {
      await updateResource(token, 'notifications/read-all', '', {})
      setNotifications(prev => prev.map(n => ({ ...n, is_read: true })))
      if (onUnreadCountChange) {
        onUnreadCountChange(0)
      }
    } catch (e) {
      console.error('Failed to mark all as read:', e)
    }
  }

  const handleDelete = async (id) => {
    try {
      await deleteResource(token, 'notifications', id)
      setNotifications(prev => prev.filter(n => n.id !== id))
    } catch (e) {
      console.error('Failed to delete notification:', e)
    }
  }

  const handleNotificationClick = (notification) => {
    onClose()
    if (notification.related_module) {
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
      const route = moduleRoutes[notification.related_module]
      if (route) {
        navigate(route)
      }
    }
  }

  if (!isOpen) return null

  return (
    <div className="notification-dropdown" ref={dropdownRef}>
      <div className="notification-dropdown-header">
        <h3>Notifications</h3>
        <div className="notification-dropdown-actions">
          {unreadCount > 0 && (
            <button className="btn btn-xs" onClick={handleMarkAllRead}>
              Mark all read
            </button>
          )}
          <button className="btn btn-xs" onClick={() => { onClose(); navigate('/notifications') }}>
            View all
          </button>
        </div>
      </div>
      <div className="notification-dropdown-body">
        {loading ? (
          <div className="notification-dropdown-loading">Loading...</div>
        ) : notifications.length === 0 ? (
          <div className="notification-dropdown-empty">No notifications yet</div>
        ) : (
          notifications.map(notification => (
            <NotificationItem
              key={notification.id}
              notification={notification}
              onMarkRead={handleMarkRead}
              onDelete={handleDelete}
              onClick={handleNotificationClick}
            />
          ))
        )}
      </div>
    </div>
  )
}
