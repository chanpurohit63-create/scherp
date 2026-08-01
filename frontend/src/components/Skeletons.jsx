import React from 'react'

export function Skeleton({ width = '100%', height = '16px', radius = 6, style = {} }) {
  return <div className="skeleton" style={{ width, height, borderRadius: radius, ...style }} aria-hidden="true" />
}

export function SkeletonText({ lines = 3, style = {} }) {
  return (
    <div style={style}>
      {Array.from({ length: lines }).map((_, i) => (
        <Skeleton key={i} width={i === lines - 1 ? '60%' : '100%'} height={14} style={{ marginBottom: i < lines - 1 ? 8 : 0 }} />
      ))}
    </div>
  )
}

export function SkeletonCard({ style = {} }) {
  return (
    <div className="card" style={{ overflow: 'hidden', padding: 0, ...style }}>
      <div style={{ padding: 20 }}>
        <Skeleton width="40%" height={18} style={{ marginBottom: 16 }} />
        <SkeletonText lines={3} />
      </div>
    </div>
  )
}

export function SkeletonTable({ rows = 6, cols = 5 }) {
  return (
    <div className="table-container">
      <div className="table-header">
        <Skeleton width={120} height={20} />
        <Skeleton width={200} height={36} radius={6} />
      </div>
      <div className="table-responsive">
        <table className="data-table">
          <thead><tr>{Array.from({ length: cols }).map((_, i) => <th key={i}><Skeleton width="80%" height={14} /></th>)}</tr></thead>
          <tbody>
            {Array.from({ length: rows }).map((_, r) => (
              <tr key={r}>{Array.from({ length: cols }).map((_, c) => <td key={c}><Skeleton width="90%" height={14} /></td>)}</tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export function SkeletonGrid({ items = 4 }) {
  return (
    <div className="stats-grid">
      {Array.from({ length: items }).map((_, i) => <SkeletonCard key={i} />)}
    </div>
  )
}

export default { Skeleton, SkeletonText, SkeletonCard, SkeletonTable, SkeletonGrid }