'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import { useState, useEffect } from 'react'

export default function Header() {
  const [scrolled, setScrolled] = useState(false)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 50)
    window.addEventListener('scroll', handleScroll, { passive: true })
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const navItems = [
    { name: 'About', href: '#about' },
    { name: 'Services', href: '#services' },
    { name: 'Vision', href: '#portfolio' },
    { name: 'Impressions', href: '#testimonials' },
    { name: 'Contact', href: '#contact' },
  ]

  return (
    <motion.header
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.5 }}
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 bg-black/60 backdrop-blur-lg border-b border-accent-secondary/20 ${
        scrolled ? 'shadow-card' : ''
      }`}
    >
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-20">
          <motion.div
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="flex items-center gap-2"
          >
            <Link 
              href="/" 
              className="flex items-center gap-2"
            >
              <motion.img 
                src="/logo.svg" 
                alt="NeuronAI Labs Logo" 
                width={32} 
                height={32}
                animate={{ rotate: 360 }}
                transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
                className="hover:opacity-80 transition-opacity duration-300"
              />
              <span className="text-2xl font-bold text-accent-primary hover:text-accent-light transition-colors duration-300">
                NeuronAI Labs
              </span>
            </Link>
          </motion.div>

          <div className="hidden md:flex items-center gap-2">
            {navItems.map((item) => (
              <motion.div key={item.name} whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                <Link
                  href={item.href}
                  className="px-4 py-2 text-foreground hover:text-accent-primary transition-colors duration-200 relative group text-sm md:text-base"
                >
                  {item.name}
                  <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-accent-primary group-hover:w-full transition-all duration-300"></span>
                </Link>
              </motion.div>
            ))}
            <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
              <Link
                href="#"
                className="px-4 py-2 rounded-full border border-accent-primary/70 bg-accent-primary/15 text-accent-primary font-semibold text-sm md:text-base transition-all duration-200 whitespace-nowrap shadow-[0_0_14px_rgba(251,191,36,0.35)] hover:shadow-[0_0_22px_rgba(251,191,36,0.5)]"
              >
                Creatae AI solution
              </Link>
            </motion.div>
          </div>

          {/* Mobile menu button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden flex flex-col gap-1 p-2"
            aria-label="Toggle menu"
          >
            <span className={`w-6 h-0.5 bg-accent-primary transition-transform duration-300 ${mobileMenuOpen ? 'rotate-45 translate-y-2' : ''}`}></span>
            <span className={`w-6 h-0.5 bg-accent-primary transition-opacity duration-300 ${mobileMenuOpen ? 'opacity-0' : ''}`}></span>
            <span className={`w-6 h-0.5 bg-accent-primary transition-transform duration-300 ${mobileMenuOpen ? '-rotate-45 -translate-y-2' : ''}`}></span>
          </button>
        </div>
      </nav>

      {/* Mobile menu dropdown */}
      <motion.div
        initial={{ opacity: 0, height: 0 }}
        animate={{ 
          opacity: mobileMenuOpen ? 1 : 0, 
          height: mobileMenuOpen ? 'auto' : 0 
        }}
        transition={{ duration: 0.3 }}
        className="md:hidden overflow-hidden bg-black/80 backdrop-blur-lg border-b border-accent-secondary/20"
      >
        <div className="px-4 py-4 space-y-3">
          {navItems.map((item) => (
            <Link
              key={item.name}
              href={item.href}
              onClick={() => setMobileMenuOpen(false)}
              className="block px-4 py-2 text-foreground hover:text-accent-primary transition-colors duration-200 text-sm"
            >
              {item.name}
            </Link>
          ))}
          <Link
            href="#"
            onClick={() => setMobileMenuOpen(false)}
            className="block px-4 py-2 rounded-full border border-accent-primary/70 bg-accent-primary/15 text-accent-primary font-semibold text-sm text-center transition-all duration-200"
          >
            Create AI solution
          </Link>
        </div>
      </motion.div>
    </motion.header>
  )
}