import React from 'react'

export default function PageHeader({ title, subtitle = '', actions = null, breadcrumbs = null, icon = null }) {
  return (
    <div className="page-header">
      <div className="page-header-left">
        {icon && <div className="page-header-icon">{icon}</div>}
        <div className="page-header-text">
          {breadcrumbs && (
            <div className="breadcrumbs">
              {breadcrumbs.map((crumb, i) => (
                <React.Fragment key={i}>
                  {i > 0 && <span className="separator">/</span>}
                  {crumb.to ? <a href={crumb.to}>{crumb.label}</a> : <span className="current">{crumb.label}</span>}
                </React.Fragment>
              ))}
            </div>
          )}
          <h1>{title}</h1>
          {subtitle && <p className="page-subtitle">{subtitle}</p>}
        </div>
      </div>
      {actions && <div className="page-header-actions">{actions}</div>}
    </div>
  )
}