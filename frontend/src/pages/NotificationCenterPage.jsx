import React, { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useNotifications } from '../components/NotificationProvider'
import NotificationItem from '../components/NotificationItem'
import { useAuth } from '../hooks/useAuth'

const CATEGORIES = [
  'All', 'Academic', 'Homework', 'Attendance', 'Examinations', 'Fees',
  'Payments', 'Messages', 'Events', 'Certificates', 'Documents',
  'Security', 'System', 'Announcements',
]

const PRIORITIES = ['All', 'low', 'normal', 'high', 'critical']

export default function NotificationCenterPage() {
  const navigate = useNavigate()
  const { profile, hasRole } = useAuth()
  const {
    notifications, unreadCount, total, loading, filters, setFilters,
    markAsRead, markAllAsRead, deleteNotification, deleteAllRead,
    archiveNotification, restoreNotification, pinNotification,
    loadMore, refresh,
  } = useNotifications()

  const [activeTab, setActiveTab] = useState('all')
  const [searchText, setSearchText] = useState('')

  useEffect(() => {
    setFilters(prev => ({
      ...prev,
      is_read: activeTab === 'unread' ? false : activeTab === 'read' ? true : null,
      search: searchText,
    }))
  }, [activeTab, searchText, setFilters])

  const handleMarkRead = async (id) => {
    await markAsRead(id)
  }

  const handleDelete = async (id) => {
    if (window.confirm('Delete this notification?')) {
      await deleteNotification(id)
    }
  }

  const handleArchive = async (id) => {
    const notification = notifications.find(n => n.id === id)
    if (notification?.is_archived) {
      await restoreNotification(id)
    } else {
      await archiveNotification(id)
    }
  }

  const handlePin = async (id) => {
    await pinNotification(id)
  }

  const handleNavigate = (notification) => {
    if (notification.related_module) {
      const routes = {
        homework: profile?.role === 'Student' ? '/student/homework' : '/teacher/homework',
        'exam-results': profile?.role === 'Student' ? '/student/exams' : '/exam-results',
        exams: profile?.role === 'Student' ? '/student/exams' : '/exams',
        fees: profile?.role === 'Student' ? '/student/fees' : '/fees',
        attendance: profile?.role === 'Student' ? '/student/attendance' : '/attendance',
        notices: profile?.role === 'Student' ? '/student/notices' : '/notices',
        events: '/events',
        messages: profile?.role === 'Student' ? '/student/messages' : 
                 profile?.role === 'Teacher' ? '/teacher/messages' : '/parent/messages',
        documents: '/student/documents',
        certificates: '/certificates',
        enrollments: '/students',
        teachers: '/teachers',
        payments: '/payments',
      }
      const route = routes[notification.related_module]
      if (route) navigate(route)
    }
  }

  const getHeaderForRole = () => {
    if (hasRole(['Student'])) return 'notifications'
    if (hasRole(['Parent'])) return 'notifications'
    if (hasRole(['Teacher'])) return 'notifications'
    return 'notifications'
  }

  // Get counts for tabs
  const getFilteredCount = (tab) => {
    if (tab === 'all') return total
    if (tab === 'unread') return unreadCount
    if (tab === 'read') return total - unreadCount
    return 0
  }

  return (
    <div className="page-wrapper">
      <div className="page-header">
        <div>
          <h1>Notification Centre</h1>
          <p className="page-subtitle">
            {unreadCount > 0
              ? `You have ${unreadCount} unread notification${unreadCount > 1 ? 's' : ''}`
              : 'All caught up!'}
          </p>
        </div>
        <div className="page-header-actions">
          <button className="btn btn-outline" onClick={() => markAllAsRead()}>
            Mark all read
          </button>
          <button className="btn btn-outline" onClick={() => deleteAllRead()}>
            Delete read
          </button>
        </div>
      </div>

      {/* Search */}
      <div className="search-bar">
        <input
          type="text"
          placeholder="Search notifications..."
          value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
          className="form-input"
        />
      </div>

      {/* Tabs */}
      <div className="tabs">
        {['all', 'unread', 'read'].map(tab => (
          <button
            key={tab}
            className={`tab ${activeTab === tab ? 'active' : ''}`}
            onClick={() => setActiveTab(tab)}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
            <span className="tab-count">({getFilteredCount(tab)})</span>
          </button>
        ))}
      </div>

      {/* Category Filters */}
      <div className="category-filters">
        <div className="filter-chips">
          {CATEGORIES.map(cat => (
            <button
              key={cat}
              className={`chip ${filters.category === cat || (cat === 'All' && !filters.category) ? 'active' : ''}`}
              onClick={() => setFilters(prev => ({ ...prev, category: cat === 'All' ? null : cat }))}
            >
              {cat}
            </button>
          ))}
        </div>
        <div className="filter-chips">
          <span style={{ marginRight: 8, fontWeight: 500, fontSize: '0.85rem' }}>Priority:</span>
          {PRIORITIES.map(p => (
            <button
              key={p}
              className={`chip chip-sm ${filters.priority === p || (p === 'All' && !filters.priority) ? 'active' : ''}`}
              onClick={() => setFilters(prev => ({ ...prev, priority: p === 'All' ? null : p }))}
            >
              {p.charAt(0).toUpperCase() + p.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Notifications List */}
      <div className="notifications-list">
        {loading && notifications.length === 0 ? (
          <div className="loading-skeleton">
            {[1, 2, 3, 4, 5].map(i => (
              <div key={i} className="skeleton-item">
                <div className="skeleton-icon" />
                <div className="skeleton-content">
                  <div className="skeleton-line" style={{ width: '60%' }} />
                  <div className="skeleton-line" style={{ width: '80%' }} />
                  <div className="skeleton-line" style={{ width: '30%' }} />
                </div>
              </div>
            ))}
          </div>
        ) : notifications.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">🔔</div>
            <h3>No notifications found</h3>
            <p>You're all up to date. New notifications will appear here.</p>
          </div>
        ) : (
          <>
            {notifications.map(notification => (
              <NotificationItem
                key={notification.id}
                notification={notification}
                onMarkRead={handleMarkRead}
                onDelete={handleDelete}
                onArchive={handleArchive}
                onPin={handlePin}
                onClick={handleNavigate}
              />
            ))}
            {notifications.length < total && (
              <div className="load-more">
                <button
                  className="btn btn-outline"
                  onClick={loadMore}
                  disabled={loading}
                >
                  {loading ? 'Loading...' : 'Load more'}
                </button>
              </div>
            )}
          </>
        )}
      </div>

      {/* Notification Settings Link */}
      <div className="notification-settings-link">
        <button
          className="btn btn-outline"
          onClick={() => navigate('/notifications/settings')}
        >
          ⚙️ Notification Settings
        </button>
      </div>
    </div>
  )
}
