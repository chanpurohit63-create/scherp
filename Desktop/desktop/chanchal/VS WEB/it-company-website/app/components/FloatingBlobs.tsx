'use client'

import { motion } from 'framer-motion'

export default function FloatingBlobs() {
  return (
    <>
      {/* Gold blob - top right */}
      <motion.div
        animate={{
          y: [0, -20, 0],
          x: [0, 10, 0],
        }}
        transition={{ duration: 8, repeat: Infinity, ease: 'easeInOut' }}
        className="blob-container absolute top-20 right-10 w-64 h-64"
      >
        <div className="blob w-full h-full rounded-full bg-accent-primary/20" style={{ filter: 'blur(40px)' }} />
      </motion.div>

      {/* Blue blob - bottom left */}
      <motion.div
        animate={{
          y: [0, 20, 0],
          x: [0, -10, 0],
        }}
        transition={{ duration: 10, repeat: Infinity, ease: 'easeInOut', delay: 2 }}
        className="blob-container absolute bottom-20 left-10 w-80 h-80"
      >
        <div className="blob w-full h-full rounded-full bg-accent-secondary/15" style={{ filter: 'blur(50px)' }} />
      </motion.div>

      {/* Orange accent blob - top left */}
      <motion.div
        animate={{
          y: [0, 15, 0],
          x: [0, -15, 0],
        }}
        transition={{ duration: 9, repeat: Infinity, ease: 'easeInOut', delay: 4 }}
        className="blob-container absolute top-1/3 left-1/4 w-72 h-72 opacity-30"
      >
        <div className="blob w-full h-full rounded-full bg-yellow-500/10" style={{ filter: 'blur(45px)' }} />
      </motion.div>
    </>
  )
}
