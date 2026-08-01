import React, { useState, useRef, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth.jsx'
import { BACKEND_URL } from '../api'
import debounce from 'lodash.debounce'

export default function GlobalSearch() {
  const auth = useAuth()
  const navigate = useNavigate()
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [show, setShow] = useState(false)
  const containerRef = useRef(null)

  useEffect(() => {
    const handleClick = (e) => {
      if (containerRef.current && !containerRef.current.contains(e.target)) {
        setShow(false)
      }
    }
    document.addEventListener('mousedown', handleClick)
    return () => document.removeEventListener('mousedown', handleClick)
  }, [])

  const performSearch = useCallback(async (q) => {
    if (!q.trim()) {
      setResults([])
      setLoading(false)
      return
    }
    setLoading(true)
    try {
      const res = await fetch(`${BACKEND_URL}/api/search?q=${encodeURIComponent(q)}`, {
        headers: { Authorization: `Bearer ${auth.token}` },
      })
      if (res.ok) {
        const data = await res.json()
        setResults(data.results || [])
      } else {
        setResults([])
      }
    } catch {
      setResults([])
    } finally {
      setLoading(false)
    }
  }, [auth.token])

  const debouncedSearch = useRef(debounce(performSearch, 300)).current

  const handleSearch = (e) => {
    const val = e.target.value
    setQuery(val)
    setShow(true)
    debouncedSearch(val)
  }

  const handleResultClick = (result) => {
    setShow(false)
    setQuery('')
    setResults([])
    if (result.url) navigate(result.url)
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Escape') {
      setShow(false)
      setQuery('')
      setResults([])
    }
  }

  return (
    <div className="global-search" ref={containerRef}>
      <div className="global-search-input-wrapper">
        <span className="global-search-icon">🔍</span>
        <input
          type="text"
          className="global-search-input"
          placeholder="Search students, teachers, classes..."
          value={query}
          onChange={handleSearch}
          onKeyDown={handleKeyDown}
          onFocus={() => query && setShow(true)}
        />
        {query && (
          <button className="global-search-clear" onClick={() => { setQuery(''); setResults([]); setShow(false) }}>×</button>
        )}
      </div>
      {show && (
        <div className="global-search-dropdown">
          {loading ? (
            <div className="global-search-loading">
              <div className="skeleton" style={{ width: '100%', height: 14, marginBottom: 8 }} />
              <div className="skeleton" style={{ width: '90%', height: 14, marginBottom: 8 }} />
              <div className="skeleton" style={{ width: '80%', height: 14 }} />
            </div>
          ) : results.length > 0 ? (
            <ul className="global-search-results">
              {results.map((r, i) => (
                <li key={i} className="global-search-result" onClick={() => handleResultClick(r)}>
                  <span className="global-search-result-icon">{r.icon || '📄'}</span>
                  <div className="global-search-result-content">
                    <div className="global-search-result-title">{r.title}</div>
                    <div className="global-search-result-meta">{r.subtitle}</div>
                  </div>
                </li>
              ))}
            </ul>
          ) : query ? (
            <div className="global-search-empty">No results found</div>
          ) : null}
        </div>
      )}
    </div>
  )
}
