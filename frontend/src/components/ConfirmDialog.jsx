import React, { useState, useCallback } from 'react'

let confirmCallback = null

export function confirm(options) {
  return new Promise((resolve) => {
    confirmCallback = { ...options, resolve }
    window.dispatchEvent(new CustomEvent('show-confirm-dialog', { detail: options }))
  })
}

export default function ConfirmDialog() {
  const [dialog, setDialog] = useState(null)

  const handleShow = useCallback((event) => {
    setDialog(event.detail)
  }, [])

  const handleConfirm = () => {
    if (dialog?.resolve) dialog.resolve(true)
    setDialog(null)
  }

  const handleCancel = () => {
    if (dialog?.resolve) dialog.resolve(false)
    setDialog(null)
  }

  React.useEffect(() => {
    window.addEventListener('show-confirm-dialog', handleShow)
    return () => window.removeEventListener('show-confirm-dialog', handleShow)
  }, [handleShow])

  if (!dialog) return null

  return (
    <div className="modal-overlay" onClick={handleCancel}>
      <div className="modal" onClick={(e) => e.stopPropagation()} style={{ maxWidth: 400 }}>
        <div className="modal-header">
          <h2>{dialog.title || 'Confirm'}</h2>
        </div>
        <div className="modal-body">
          <p style={{ color: 'var(--gray-600)', fontSize: '0.9rem' }}>{dialog.message || 'Are you sure?'}</p>
        </div>
        <div className="modal-footer">
          <button className="btn" onClick={handleCancel}>{dialog.cancelText || 'Cancel'}</button>
          <button className={`btn ${dialog.danger ? 'btn-danger' : 'btn-primary'}`} onClick={handleConfirm}>{dialog.confirmText || 'Confirm'}</button>
        </div>
      </div>
    </div>
  )
}