'use client'

import { motion } from 'framer-motion'

export default function Hero() {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
      {/* Base background overlay */}
      <div className="absolute inset-0 bg-linear-to-b from-background via-background/90 to-background z-0" />

      {/* Hero-only controlled glow */}
      <div className="absolute inset-0 overflow-hidden z-0 pointer-events-none">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 0.08 }}
          transition={{ duration: 1.8 }}
          className="absolute top-12 left-24 w-80 h-80 bg-accent-secondary/10 rounded-full blur-3xl"
        />
      </div>

      {/* Revolving hero image background */}
      <motion.div
        animate={{ scale: [1, 1.03, 1] }}
        transition={{ duration: 18, repeat: Infinity, ease: 'easeInOut' }}
        className="absolute inset-0 z-0 pointer-events-none bg-center bg-cover"
        style={{ backgroundImage: "url('/hero-revolving-ai.png')" }}
      />

      {/* Cinematic overlay for readability - darker and more premium */}
      <div className="absolute inset-0 z-0 bg-linear-to-b from-black/80 via-black/70 to-black/85" />

      {/* Main content — sits above canvas */}
      <div className="relative z-10 w-full max-w-4xl mx-auto text-center px-6 pt-32 pb-32">
        <motion.h1
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, delay: 0.2 }}
          className="text-5xl md:text-7xl lg:text-8xl font-bold mb-10 text-foreground leading-tight"
        >
          Healthcare For Everyone. <br className="hidden md:block" />
          <span className="text-foreground">Built with</span> <span className="text-accent-primary">AI.</span>
          <span className="text-foreground"> Driven by</span> <span className="text-accent-primary">Care.</span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, delay: 0.4 }}
          className="text-base md:text-lg text-text-secondary mb-12 leading-relaxed max-w-2xl mx-auto"
        >
          Empowering doctors, patients, and healthcare systems with intelligent solutions that put people first. Real care. Real innovation. Real impact.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.6 }}
          className="flex items-center justify-center"
        >
          <motion.button
            whileHover={{ scale: 1.05, y: -1 }}
            whileTap={{ scale: 0.98 }}
            className="btn-primary px-8"
          >
            Get Started
          </motion.button>
        </motion.div>
      </div>

      {/* Scroll indicator */}
      <motion.div
        animate={{ y: [0, 12, 0] }}
        transition={{ duration: 2, repeat: Infinity }}
        className="absolute bottom-8 left-1/2 -translate-x-1/2 z-20"
      >
        <div className="w-6 h-10 border-2 border-accent-primary rounded-full flex justify-center">
          <motion.div className="w-1 h-2 bg-accent-primary rounded-full mt-2" />
        </div>
      </motion.div>

      {/* Bottom fade */}
      <div className="absolute bottom-0 left-0 right-0 h-32 bg-linear-to-t from-background to-transparent z-10 pointer-events-none" />
    </section>
  )
}