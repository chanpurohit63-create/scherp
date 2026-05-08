'use client'

import { motion } from 'framer-motion'
import { useState, useEffect } from 'react'

export default function Testimonials() {
  const testimonials = [
    {
      name: 'Sneha',
      company: 'Senior OPD',
      text: 'NeuronAI Labs is tackling some of the toughest challenges in healthcare AI - the future looks bright.',
      rating: 5,
      avatar: '👨‍💼'
    },
    {
      name: 'Dr. Ritu',
      company: 'Clinical Strategy Consultant',
      text: 'Excited to see how their AI solutions will improve patient care and clinical workflows.',
      rating: 5,
      avatar: '👩‍💼'
    },
    {
      name: 'Tech Mentor',
      company: 'Startup Growth Mentor',
      text: 'A promising startup with bold vision and cutting-edge technology.',
      rating: 5,
      avatar: '👨‍💼'
    },
  ]

  const [currentIndex, setCurrentIndex] = useState(0)

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % testimonials.length)
    }, 5000)
    return () => clearInterval(timer)
  }, [testimonials.length])

  return (
    <section id="testimonials" className="py-24 px-6 relative overflow-hidden">
      {/* Soft divider top */}
      <div className="absolute top-0 inset-x-0 h-20 bg-linear-to-b from-accent-primary/3 via-transparent to-transparent pointer-events-none"></div>

      {/* Subtle particles for premium feel */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div
          animate={{ opacity: [0.3, 0.5, 0.3] }}
          transition={{ duration: 9, repeat: Infinity }}
          className="absolute -top-40 right-20 w-96 h-96 bg-accent-secondary/10 rounded-full blur-3xl"
        />
        <motion.div
          animate={{ opacity: [0.15, 0.35, 0.15] }}
          transition={{ duration: 11, repeat: Infinity, delay: 4 }}
          className="absolute -bottom-32 -left-32 w-80 h-80 bg-accent-primary/6 rounded-full blur-3xl"
        />
      </div>

      {/* Background gradient */}
      <div className="absolute inset-0 bg-linear-to-b from-black/40 via-black/50 to-black/60 pointer-events-none"></div>
      

      <div className="max-w-3xl mx-auto relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="text-center mb-12"
        >
          <h2 className="text-4xl md:text-5xl font-bold text-foreground mb-6">What People Are Saying</h2>
          <p className="text-lg text-text-secondary">
            Insights and feedback from those who knows our vision with AI solutions in healthcare.
          </p>
        </motion.div>

        {/* Testimonials carousel */}
        <div className="relative min-h-72">
          {testimonials.map((testimonial, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{
                opacity: index === currentIndex ? 1 : 0,
                y: index === currentIndex ? 0 : 20,
              }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.6, ease: "easeInOut" }}
              className="absolute inset-0 pointer-events-none"
              style={{ pointerEvents: index === currentIndex ? 'auto' : 'none' }}
            >
              <div className="card relative h-full p-8 md:p-10">
                {/* Avatar and name */}
                <div className="flex items-center mb-6">
                  <div className="w-16 h-16 rounded-full bg-accent-primary/30 border-2 border-accent-primary/40 flex items-center justify-center text-2xl">
                    {testimonial.avatar}
                  </div>
                  <div className="ml-4">
                    <h3 className="text-lg font-bold text-foreground">{testimonial.name}</h3>
                    <p className="text-text-secondary text-sm">{testimonial.company}</p>
                  </div>
                </div>

                {/* Rating */}
                <div className="flex mb-6">
                  {[...Array(testimonial.rating)].map((_, i) => (
                    <motion.span
                      key={i}
                      initial={{ opacity: 0, y: -5 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: i * 0.1 }}
                      className="text-accent-primary text-lg"
                    >
                      ★
                    </motion.span>
                  ))}
                </div>

                {/* Quote */}
                <blockquote className="text-base text-foreground italic mb-4 leading-relaxed">
                  "{testimonial.text}"
                </blockquote>

                {/* Quote mark decoration */}
                <div className="absolute top-6 right-6 text-7xl text-accent-primary/8">"</div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Navigation dots */}
        <div className="flex justify-center mt-8 gap-3">
          {testimonials.map((_, index) => (
            <motion.button
              key={index}
              onClick={() => setCurrentIndex(index)}
              className={`transition-all duration-300 ${
                index === currentIndex
                  ? 'w-8 h-3 bg-accent-primary'
                  : 'w-3 h-3 bg-foreground/30 hover:bg-foreground/50'
              } rounded-full`}
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
            />
          ))}
        </div>

        {/* Client count */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
          viewport={{ once: true }}
          className="text-center mt-12 pt-8 border-t border-accent-primary/20"
        >
          <p className="text-foreground/70 text-sm">
            Shaping the future for better
          </p>
        </motion.div>
      </div>
    </section>
  )
}