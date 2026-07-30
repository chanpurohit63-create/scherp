import React from 'react'
import { useParentChild } from './ParentChildContext'

export default function ChildSwitcher() {
  const { children, activeChild, activeChildId, switchChild } = useParentChild()

  if (!children || children.length === 0) return null

  return (
    <div className="child-switcher">
      <label className="child-switcher-label">👶 Child:</label>
      <select
        className="input child-switcher-select"
        value={activeChildId || ''}
        onChange={(e) => switchChild(parseInt(e.target.value))}
      >
        {children.map((c) => (
          <option key={c.student_id} value={c.student_id}>
            {c.full_name} - {c.class_name || 'No Class'}
          </option>
        ))}
      </select>
      {activeChild && (
        <span className="child-switcher-info">
          {activeChild.class_name && `${activeChild.class_name}`}
          {activeChild.section_name && ` • ${activeChild.section_name}`}
          {activeChild.admission_no && ` • ${activeChild.admission_no}`}
        </span>
      )}
    </div>
  )
}