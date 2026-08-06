import React, { createContext, useContext, useEffect, useRef, useState, useCallback } from 'react'
import { useAuth } from '../hooks/useAuth'
import { BACKEND_URL } from '../api'

const WebSocketContext = createContext(null)

export function WebSocketProvider({ children, onNotification }) {
  const { token, isAuthenticated } = useAuth()
  const wsRef = useRef(null)
  const reconnectTimeoutRef = useRef(null)
  const connectTimeoutRef = useRef(null)
  const heartbeatIntervalRef = useRef(null)
  const reconnectAttemptsRef = useRef(0)
  const manualDisconnectRef = useRef(false)
  const maxReconnectAttempts = 10
  const [isConnected, setIsConnected] = useState(false)

  const connect = useCallback(() => {
    if (!token || !isAuthenticated) return
    if (wsRef.current && wsRef.current.readyState !== WebSocket.CLOSED && wsRef.current.readyState !== WebSocket.CLOSING) {
      return
    }

    const backendUrl = new URL(BACKEND_URL)
    backendUrl.protocol = backendUrl.protocol === 'https:' ? 'wss:' : 'ws:'
    backendUrl.pathname = '/ws'
    backendUrl.searchParams.set('token', token)
    const wsUrl = backendUrl.toString()

    try {
      const ws = new WebSocket(wsUrl)
      wsRef.current = ws
      manualDisconnectRef.current = false

      ws.onopen = () => {
        console.log('WebSocket connected')
        setIsConnected(true)
        reconnectAttemptsRef.current = 0

        // Start heartbeat
        heartbeatIntervalRef.current = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'ping' }))
          }
        }, 30000)
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          
          if (data.type === 'heartbeat' || data.type === 'pong') {
            return
          }

          if (data.type === 'notification.created' && onNotification) {
            onNotification(data.notification)
          }

          // Forward all other events
          if (onNotification) {
            onNotification(data)
          }
        } catch (e) {
          console.error('WebSocket message parse error:', e)
        }
      }

      ws.onclose = () => {
        console.log('WebSocket disconnected')
        setIsConnected(false)
        clearInterval(heartbeatIntervalRef.current)

        if (manualDisconnectRef.current) {
          return
        }

        // Auto reconnect with exponential backoff
        if (reconnectAttemptsRef.current < maxReconnectAttempts) {
          const delay = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 30000)
          reconnectTimeoutRef.current = setTimeout(() => {
            reconnectAttemptsRef.current++
            connect()
          }, delay)
        }
      }

      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
      }
    } catch (e) {
      console.error('WebSocket connection error:', e)
    }
  }, [token, isAuthenticated, onNotification])

  const disconnect = useCallback(() => {
    manualDisconnectRef.current = true
    clearTimeout(connectTimeoutRef.current)
    clearTimeout(reconnectTimeoutRef.current)
    clearInterval(heartbeatIntervalRef.current)
    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }
    setIsConnected(false)
  }, [])

  useEffect(() => {
    if (isAuthenticated && token) {
      connectTimeoutRef.current = window.setTimeout(() => {
        connect()
      }, 0)
    } else {
      disconnect()
    }

    return () => {
      disconnect()
    }
  }, [isAuthenticated, token, connect, disconnect])

  const sendMessage = useCallback((data) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data))
    }
  }, [])

  return (
    <WebSocketContext.Provider value={{ isConnected, sendMessage }}>
      {children}
    </WebSocketContext.Provider>
  )
}

export function useWebSocket() {
  const context = useContext(WebSocketContext)
  if (!context) {
    throw new Error('useWebSocket must be used within WebSocketProvider')
  }
  return context
}

