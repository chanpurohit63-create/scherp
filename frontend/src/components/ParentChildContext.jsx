import React, { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { useAuth } from '../hooks/useAuth.jsx'
import { listResources } from '../api'

const ParentChildContext = createContext()

export function ParentChildProvider({ children: propChildren }) {
  const auth = useAuth()
  const [childList, setChildList] = useState([])
  const [activeChildId, setActiveChildId] = useState(null)
  const [loading, setLoading] = useState(true)

  const loadChildren = useCallback(async () => {
    if (!auth.token || auth.profile?.role !== 'Parent') {
      setLoading(false)
      return
    }
    try {
      const d = await listResources(auth.token, 'portal/parent/children')
      const kids = d?.children || []
      setChildList(kids)
      if (kids.length > 0 && !activeChildId) {
        setActiveChildId(kids[0].student_id)
      } else if (kids.length === 0) {
        setActiveChildId(null)
      }
    } catch (err) {
      console.error('Failed to load children:', err)
    } finally {
      setLoading(false)
    }
  }, [auth.token, auth.profile])

  useEffect(() => {
    loadChildren()
  }, [loadChildren])

  const activeChild = childList.find(c => c.student_id === activeChildId) || childList[0] || null

  const switchChild = (studentId) => {
    setActiveChildId(studentId)
  }

  return (
    <ParentChildContext.Provider value={{
      children: childList,
      activeChild,
      activeChildId,
      switchChild,
      loading,
      refreshChildren: loadChildren,
    }}>
      {propChildren}
    </ParentChildContext.Provider>
  )
}

export function useParentChild() {
  const ctx = useContext(ParentChildContext)
  if (!ctx) throw new Error('useParentChild must be used within ParentChildProvider')
  return ctx
}