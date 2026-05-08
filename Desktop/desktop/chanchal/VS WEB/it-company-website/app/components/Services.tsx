'use client'

import { motion } from 'framer-motion'

function ServiceIcon({ children }: { children: React.ReactNode }) {
  return (
    <div className="w-16 h-16 mx-auto mb-6 rounded-xl border border-accent-secondary/35 bg-accent-secondary/10 flex items-center justify-center text-3xl">
      {children}
    </div>
  )
}

const serviceVariants = {
  hidden: { opacity: 0, y: 50 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.15, duration: 0.6 }
  })
}

export default function Services() {
  const services = [
    {
      icon: '🧠',
      title: 'Mental Wellness',
      description: 'Confidential, empathetic support designed to help individuals manage stress and anxiety, with guidance toward professional care when needed.',
    },
    {
      icon: '🍎',
      title: 'Personalized Nutrition',
      description: 'A tailored nutrition solution that aligns with individual lifestyles, health conditions, and wellness goals.',
    },
    {
      icon: '💊',
      title: 'Medication Intelligence',
      description: 'Get instant insights on prescriptions, side effects, and interactions powered by AI.',
    },
    {
      icon: '📈',
      title: 'Health Tracking',
      description: 'A smart system to monitor daily health and generate insights that support long-term well-being.',
    },
    {
      icon: '📄',
      title: 'Medical Understanding',
      description: 'An intuitive way to simplify complex medical reports and information into clear, meaningful insights.',
    },
    {
      icon: '🤝',
      title: 'Care Assistant',
      description: 'An always-available assistant that helps users navigate health questions and access the right support.',
    },
  ]

  return (
    <section id="services" className="py-24 px-6 relative overflow-hidden">
      {/* Subtle particle background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div
          animate={{ opacity: [0.3, 0.5, 0.3] }}
          transition={{ duration: 8, repeat: Infinity }}
          className="absolute top-10 right-10 w-72 h-72 bg-accent-secondary/8 rounded-full blur-3xl"
        />
        <motion.div
          animate={{ opacity: [0.2, 0.4, 0.2] }}
          transition={{ duration: 10, repeat: Infinity, delay: 2 }}
          className="absolute bottom-20 left-20 w-80 h-80 bg-accent-primary/5 rounded-full blur-3xl"
        />
      </div>

      {/* Clean dark background */}
      <div className="absolute inset-0 bg-background pointer-events-none"></div>

      <div className="max-w-6xl mx-auto relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="text-center mb-14"
        >
          <h2 className="text-4xl md:text-5xl font-bold text-foreground mb-6">Our Solutions</h2>
          <p className="text-lg text-text-secondary max-w-2xl mx-auto">
            We design intelligent healthcare solutions that make quality guidance more accessible, personalized, and safe - supporting better decisions without replacing medical professionals.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
          {services.map((service, index) => (
            <motion.div
              key={service.title}
              custom={index}
              variants={serviceVariants}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true }}
              whileHover={{ y: -4 }}
              className="card group relative p-8 h-full flex flex-col"
            >
              <div className="relative z-10">
                <ServiceIcon>{service.icon}</ServiceIcon>
                <h3 className="text-xl font-bold text-foreground mb-4 group-hover:text-accent-primary transition-colors">{service.title}</h3>
                <p className="text-text-secondary text-sm leading-relaxed mb-6">{service.description}</p>
                
            <motion.div
              className="inline-flex items-center text-accent-primary text-sm font-semibold group-hover:text-accent-light transition-colors"
              whileHover={{ x: 4 }}
            >
              Learn more <span className="ml-2 group-hover:translate-x-1 transition-transform">→</span>
            </motion.div>
              
            </div>
          </motion.div>
          ))}
        </div>

        {/* Soft divider */}
        <div className="mt-16 pt-16 border-t border-accent-primary/5 relative">
          <div className="absolute inset-x-0 top-0 h-16 bg-linear-to-b from-accent-primary/5 via-transparent to-transparent pointer-events-none"></div>
        </div>
      </div>
    </section>
  )
}