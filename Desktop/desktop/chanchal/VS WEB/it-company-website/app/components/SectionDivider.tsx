'use client'

import { motion } from 'framer-motion'

export default function SectionDivider({ delay = 0 }: { delay?: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, scaleX: 0 }}
      whileInView={{ opacity: 1, scaleX: 1 }}
      transition={{ duration: 0.8, delay }}
      viewport={{ once: true }}
      className="my-8 flex items-center justify-center"
    >
      <div className="w-24 h-0.5 bg-gradient-to-r from-transparent via-accent-primary/60 to-transparent relative">
        <div className="absolute inset-0 blur-sm bg-gradient-to-r from-transparent via-accent-primary/30 to-transparent"></div>
      </div>
    </motion.div>
  )
}
