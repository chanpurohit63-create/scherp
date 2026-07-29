import React, { useState } from 'react'
import NotificationBadge from './NotificationBadge'
import NotificationDropdown from './NotificationDropdown'

export default function NotificationBell({ unreadCount, onUnreadCountChange }) {
  const [isOpen, setIsOpen] = useState(false)

  const handleToggle = () => {
    setIsOpen(!isOpen)
  }

  const handleClose = () => {
    setIsOpen(false)
  }

  return (
    <div className="notification-bell-container">
      <button
        className="notification-bell"
        onClick={handleToggle}
        title="Notifications"
        aria-label="Toggle notifications"
      >
        <span className="bell-icon">🔔</span>
        {unreadCount > 0 && (
          <NotificationBadge count={unreadCount} />
        )}
      </button>
      <NotificationDropdown
        isOpen={isOpen}
        onClose={handleClose}
        unreadCount={unreadCount}
        onUnreadCountChange={onUnreadCountChange}
      />
    </div>
  )
}
