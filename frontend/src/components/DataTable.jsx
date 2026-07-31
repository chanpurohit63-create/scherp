import React, { useState, useMemo } from 'react'

export default function DataTable({
  columns = [],
  data = [],
  loading = false,
  pageSize = 10,
  searchable = true,
  searchPlaceholder = 'Search...',
  searchKeys = [],
  filters = [],
  emptyStateIcon = '📭',
  emptyStateTitle = 'No data found',
  emptyStateMessage = '',
  actions = null,
  rowActions = null,
}) {
  const [search, setSearch] = useState('')
  const [currentPage, setCurrentPage] = useState(1)
  const [sortColumn, setSortColumn] = useState(null)
  const [sortDirection, setSortDirection] = useState('asc')
  const [filterValues, setFilterValues] = useState({})

  // Filter data
  const filteredData = useMemo(() => {
    let result = [...data]

    // Search
    if (search && searchKeys.length > 0) {
      const lowerSearch = search.toLowerCase()
      result = result.filter(row =>
        searchKeys.some(key =>
          String(row[key] || '').toLowerCase().includes(lowerSearch)
        )
      )
    }

    // Filters
    filters.forEach(filter => {
      const value = filterValues[filter.key]
      if (value) {
        result = result.filter(row => String(row[filter.key]) === String(value))
      }
    })

    // Sort
    if (sortColumn) {
      result.sort((a, b) => {
        const aVal = a[sortColumn]
        const bVal = b[sortColumn]
        if (aVal == null) return 1
        if (bVal == null) return -1
        if (typeof aVal === 'number' && typeof bVal === 'number') {
          return sortDirection === 'asc' ? aVal - bVal : bVal - aVal
        }
        const aStr = String(aVal).toLowerCase()
        const bStr = String(bVal).toLowerCase()
        return sortDirection === 'asc' ? aStr.localeCompare(bStr) : bStr.localeCompare(aStr)
      })
    }

    return result
  }, [data, search, searchKeys, filterValues, filters, sortColumn, sortDirection])

  // Pagination
  const totalPages = Math.ceil(filteredData.length / pageSize)
  const paginatedData = filteredData.slice((currentPage - 1) * pageSize, currentPage * pageSize)

  const handleSort = (column) => {
    if (sortColumn === column) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')
    } else {
      setSortColumn(column)
      setSortDirection('asc')
    }
  }

  const handleSearch = (value) => {
    setSearch(value)
    setCurrentPage(1)
  }

  const handleFilter = (key, value) => {
    setFilterValues({ ...filterValues, [key]: value })
    setCurrentPage(1)
  }

  if (loading) {
    return (
      <div className="table-container">
        <div className="table-header">
          <h3>Loading...</h3>
        </div>
        <div className="skeleton-list" style={{ padding: 16 }}>
          {Array.from({ length: 8 }).map((_, i) => <div key={i} className="skeleton-row" />)}
        </div>
      </div>
    )
  }

  return (
    <div className="table-container">
      {/* Header with search and filters */}
      <div className="table-header">
        <h3>{filteredData.length} record{filteredData.length !== 1 ? 's' : ''}</h3>
        <div className="table-toolbar">
          {searchable && (
            <input
              className="input search-input"
              placeholder={searchPlaceholder}
              value={search}
              onChange={(e) => handleSearch(e.target.value)}
            />
          )}
          {filters.map(filter => (
            <select
              key={filter.key}
              className="input"
              style={{ width: filter.width || 140 }}
              value={filterValues[filter.key] || ''}
              onChange={(e) => handleFilter(filter.key, e.target.value)}
            >
              <option value="">{filter.label}</option>
              {filter.options.map(opt => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
          ))}
          {actions}
        </div>
      </div>

      {/* Table */}
      <div className="table-responsive">
        <table className="data-table">
          <thead>
            <tr>
              {columns.map(col => (
                <th
                  key={col.key}
                  onClick={() => col.sortable !== false && handleSort(col.key)}
                  style={{ cursor: col.sortable !== false ? 'pointer' : 'default' }}
                >
                  {col.label}
                  {col.sortable !== false && (
                    <span style={{ marginLeft: 4, opacity: 0.5 }}>
                      {sortColumn === col.key ? (sortDirection === 'asc' ? '↑' : '↓') : '↕'}
                    </span>
                  )}
                </th>
              ))}
              {rowActions && <th>Actions</th>}
            </tr>
          </thead>
          <tbody>
            {paginatedData.length === 0 ? (
              <tr>
                <td colSpan={columns.length + (rowActions ? 1 : 0)}>
                  <div className="empty-state">
                    <div className="empty-state-icon">{emptyStateIcon}</div>
                    <h3>{emptyStateTitle}</h3>
                    {emptyStateMessage && <p>{emptyStateMessage}</p>}
                  </div>
                </td>
              </tr>
            ) : paginatedData.map((row, i) => (
              <tr key={row.id || i}>
                {columns.map(col => (
                  <td key={col.key}>
                    {col.render ? col.render(row) : (row[col.key] ?? '-')}
                  </td>
                ))}
                {rowActions && (
                  <td className="cell-actions">{rowActions(row)}</td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Footer with pagination */}
      {totalPages > 1 && (
        <div className="table-footer">
          <span className="pagination-info">
            Showing {(currentPage - 1) * pageSize + 1}-{Math.min(currentPage * pageSize, filteredData.length)} of {filteredData.length}
          </span>
          <div className="pagination">
            <button onClick={() => setCurrentPage(1)} disabled={currentPage === 1}>«</button>
            <button onClick={() => setCurrentPage(currentPage - 1)} disabled={currentPage === 1}>‹</button>
            {Array.from({ length: totalPages }, (_, i) => i + 1)
              .filter(p => p === 1 || p === totalPages || Math.abs(p - currentPage) <= 2)
              .map(p => (
                <button key={p} className={currentPage === p ? 'active' : ''} onClick={() => setCurrentPage(p)}>
                  {p}
                </button>
              ))}
            <button onClick={() => setCurrentPage(currentPage + 1)} disabled={currentPage === totalPages}>›</button>
            <button onClick={() => setCurrentPage(totalPages)} disabled={currentPage === totalPages}>»</button>
          </div>
        </div>
      )}
    </div>
  )
}