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

      {/* Full section background image */}
      <div
        className="absolute inset-0 bg-cover bg-center pointer-events-none"
        style={{ backgroundImage: "url('/hero-revolving-ai.png')" }}
      ></div>

      <div className="absolute inset-0 bg-linear-to-b from-black/64 via-black/52 to-black/68 pointer-events-none"></div>

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