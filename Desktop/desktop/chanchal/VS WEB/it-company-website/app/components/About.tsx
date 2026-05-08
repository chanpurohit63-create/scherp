'use client'

import { motion } from 'framer-motion'
import { memo } from 'react'

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.15, delayChildren: 0.2 }
  }
}

const itemVariants = {
  hidden: { opacity: 0, y: 30 },
  visible: { opacity: 1, y: 0 }
}

const ValueCard = memo(function ValueCard({ value, index }: { value: any, index: number }) {
  return (
    <motion.div
      variants={itemVariants}
      whileHover={{ y: -6, transition: { duration: 0.2 } }}
      className="card group relative p-10"
    >
      <div className="relative z-10">
        <div className="w-16 h-16 bg-accent-primary/20 rounded-xl mx-auto mb-6 flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
          <span className="text-3xl">{value.icon}</span>
        </div>
        <h3 className="text-2xl font-bold text-foreground mb-4">{value.title}</h3>
        <p className="text-text-secondary leading-relaxed text-sm md:text-base">{value.description}</p>
      </div>
    </motion.div>
  )
})

export default function About() {
  const values = [
    { icon: '🧠', title: 'Clinical Intelligence', description: 'AI trained on real medical knowledge to support accurate decision-making.' },
    { icon: '🔒', title: 'HIPAA-Level Data Security', description: 'End-to-end encryption and privacy-first architecture for patient safety.' },
    { icon: '👩‍⚕️', title: 'Doctor + AI Collaboration', description: 'Designed to assist professionals — not replace them.' },
  ]

  return (
    <section id="about" className="py-24 px-6 relative overflow-hidden">
      {/* Soft divider top */}
      <div className="absolute top-0 inset-x-0 h-20 bg-linear-to-b from-accent-primary/3 via-transparent to-transparent pointer-events-none"></div>

      {/* Subtle gradient glow - very premium */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full h-full bg-radial-gradient" style={{
          backgroundImage: 'radial-gradient(circle at 50% 50%, rgba(251, 191, 36, 0.08) 0%, rgba(59, 130, 246, 0.04) 40%, transparent 70%)'
        }}></div>
      </div>

      {/* Clean dark background */}
      <div className="absolute inset-0 bg-background pointer-events-none"></div>

      {/* Subtle gradient overlay */}
      <div className="absolute inset-0 bg-linear-to-b from-background via-background/98 to-background pointer-events-none"></div>

      <div className="max-w-6xl mx-auto relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="text-center mb-14"
        >
          <h2 className="text-4xl md:text-5xl font-bold text-foreground mb-6">About Us</h2>
          <p className="text-lg text-text-secondary max-w-2xl mx-auto leading-relaxed">
            We believe healthcare should feel accessible, supportive, and human. That's why we're building AI tools designed to assist people — not replace them. Every solution we create puts care and compassion at the center.
          </p>
        </motion.div>

        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-80px" }}
          className="grid grid-cols-1 md:grid-cols-3 gap-8"
        >
          {values.map((value, index) => (
            <ValueCard key={value.title} value={value} index={index} />
          ))}
        </motion.div>
      </div>
    </section>
  )
}