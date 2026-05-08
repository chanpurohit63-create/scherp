'use client'

import { useEffect, useRef } from 'react'

export default function MouseGlow() {
  const glowRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!glowRef.current) return

      const glow = glowRef.current
      glow.style.left = `${e.clientX - 100}px`
      glow.style.top = `${e.clientY - 100}px`
      glow.classList.add('active')
    }

    const handleMouseLeave = () => {
      if (glowRef.current) {
        glowRef.current.classList.remove('active')
      }
    }

    window.addEventListener('mousemove', handleMouseMove)
    document.addEventListener('mouseleave', handleMouseLeave)

    return () => {
      window.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseleave', handleMouseLeave)
    }
  }, [])

  return <div ref={glowRef} className="mouse-glow" />
}
