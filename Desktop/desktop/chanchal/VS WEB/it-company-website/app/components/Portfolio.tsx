'use client'

import { motion } from 'framer-motion'

const pillars = [
  {
    icon: '🌍',
    title: 'Accessible Care',
    description: 'Making essential health guidance available to everyone, anytime.',
  },
  {
    icon: '🎯',
    title: 'Personalized Intelligence',
    description: 'Delivering tailored insights based on individual needs and conditions.',
  },
  {
    icon: '🛡️',
    title: 'Safe & Responsible AI',
    description: 'Building systems grounded in medical knowledge with a focus on accuracy and trust.',
  },
]

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.15, delayChildren: 0.2 },
  },
}

const itemVariants = {
  hidden: { opacity: 0, y: 30 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.5 } },
}

export default function Portfolio() {
  return (
    <section id="portfolio" className="py-24 px-6 relative overflow-hidden">
      {/* Soft divider top */}
      <div className="absolute top-0 inset-x-0 h-20 bg-linear-to-b from-accent-primary/3 via-transparent to-transparent pointer-events-none"></div>

      {/* Thin animated orbit lines - subtle neural network feel */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {/* Animated orbit circles */}
        <motion.svg
          className="absolute inset-0 w-full h-full"
          animate={{ rotate: 360 }}
          transition={{ duration: 40, repeat: Infinity, ease: "linear" }}
        >
          <circle cx="50%" cy="50%" r="20%" fill="none" stroke="rgba(251, 191, 36, 0.08)" strokeWidth="1" />
          <circle cx="50%" cy="50%" r="35%" fill="none" stroke="rgba(59, 130, 246, 0.06)" strokeWidth="1" />
          <circle cx="50%" cy="50%" r="50%" fill="none" stroke="rgba(251, 191, 36, 0.04)" strokeWidth="1" />
        </motion.svg>

        {/* Subtle grid pattern */}
        <motion.div
          animate={{ opacity: [0.15, 0.25, 0.15] }}
          transition={{ duration: 6, repeat: Infinity }}
          className="absolute inset-0 opacity-15"
          style={{
            backgroundImage: `
              linear-gradient(rgba(251, 191, 36, 0.05) 1px, transparent 1px),
              linear-gradient(90deg, rgba(251, 191, 36, 0.05) 1px, transparent 1px)
            `,
            backgroundSize: '50px 50px'
          }}
        ></motion.div>
      </div>

      {/* Minimal dark background - clean and focused */}
      <div className="absolute inset-0 bg-background pointer-events-none"></div>

      <div className="absolute inset-0 bg-linear-to-b from-background/95 via-background/98 to-background pointer-events-none"></div>

      <div className="max-w-6xl mx-auto relative z-10">
        {/* Section header */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="text-center mb-14"
        >
          <h2 className="text-4xl md:text-5xl font-bold text-foreground mb-6">Our Mission & Vision</h2>
          <p className="text-lg text-text-secondary max-w-2xl mx-auto leading-relaxed">
            We are building the future of healthcare where AI assists, not replaces - empowering every decision with intelligence.
          </p>
        </motion.div>

        {/* Cards */}
        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: '-80px' }}
          className="grid grid-cols-1 md:grid-cols-3 gap-8"
        >
          {pillars.map((pillar) => (
            <motion.div
              key={pillar.title}
              variants={itemVariants}
              whileHover={{ y: -8, transition: { duration: 0.2 } }}
              className="card group p-10 text-center"
            >
              <div className="w-16 h-16 bg-accent-primary/20 rounded-xl mx-auto mb-6 flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                <span className="text-3xl">{pillar.icon}</span>
              </div>
              <h3 className="text-xl font-bold text-foreground mb-4 group-hover:text-accent-primary transition-colors">
                {pillar.title}
              </h3>
              <p className="text-text-secondary leading-relaxed text-sm md:text-base">
                {pillar.description}
              </p>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  )
}