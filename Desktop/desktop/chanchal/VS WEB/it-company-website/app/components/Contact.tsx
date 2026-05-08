'use client'

import { motion } from 'framer-motion'
import { useState } from 'react'

export default function Contact() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    projectType: '',
    message: ''
  })
  const [submitted, setSubmitted] = useState(false)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitted(true)
    setFormData({ name: '', email: '', projectType: '', message: '' })
    setTimeout(() => setSubmitted(false), 3000)
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  const contactInfo = [
    { icon: '📍', label: 'Address', value: 'Kial Road' },
    { icon: '📞', label: 'Phone', value: '9179977737' },
    { icon: '✉️', label: 'Email', value: 'hello@neuronailabs.com' },
    { icon: '🕐', label: 'Hours', value: 'Mon-Sat, 9 AM - 7 PM IST' },
  ]

  return (
    <section id="contact" className="py-24 px-6 relative overflow-hidden">
      {/* Soft divider top */}
      <div className="absolute top-0 inset-x-0 h-20 bg-linear-to-b from-accent-primary/3 via-transparent to-transparent pointer-events-none"></div>

      {/* Full section background image */}
      <div
        className="absolute inset-0 bg-cover bg-center pointer-events-none"
        style={{ backgroundImage: "url('/hero-revolving-ai.png')" }}
      ></div>

      {/* Background gradient */}
      <div className="absolute inset-0 bg-linear-to-b from-black/76 via-black/66 to-black/82"></div>

      <div className="max-w-7xl mx-auto relative z-10">
        {/* Section header */}
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="text-center mb-14"
        >
          <h2 className="text-4xl md:text-5xl lg:text-6xl font-bold text-foreground mb-8">
            Get In Touch
          </h2>
          <p className="text-lg text-text-secondary max-w-3xl mx-auto">
            Building our own future, while empowering yours to come alive.
          </p>
        </motion.div>

        <div className="grid lg:grid-cols-2 gap-12">
          {/* Contact Form */}
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            whileInView={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="card p-10"
          >
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label htmlFor="name" className="block text-sm font-semibold text-foreground mb-3">
                  Full Name
                </label>
                <motion.input
                  whileFocus={{ scale: 1.02 }}
                  type="text"
                  id="name"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  required
                  placeholder="John Doe"
                  className="w-full px-4 py-3 bg-background/50 border border-accent-primary/25 rounded-lg focus:border-accent-primary focus:outline-none focus:ring-2 focus:ring-accent-primary/20 transition-all text-foreground placeholder-foreground/50 min-h-12"
                />
              </div>

              <div>
                <label htmlFor="email" className="block text-sm font-semibold text-foreground mb-3">
                  Email Address
                </label>
                <motion.input
                  whileFocus={{ scale: 1.02 }}
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  required
                  placeholder="john@example.com"
                  className="w-full px-4 py-3 bg-background/50 border border-accent-primary/25 rounded-lg focus:border-accent-primary focus:outline-none focus:ring-2 focus:ring-accent-primary/20 transition-all text-foreground placeholder-foreground/50 min-h-12"
                />
              </div>

              <div>
                <label htmlFor="projectType" className="block text-sm font-semibold text-foreground mb-3">
                  Project Type
                </label>
                <select
                  id="projectType"
                  name="projectType"
                  value={formData.projectType}
                  onChange={handleChange}
                  className="w-full px-4 py-3 bg-background/50 border border-accent-primary/25 rounded-lg focus:border-accent-primary focus:outline-none focus:ring-2 focus:ring-accent-primary/20 transition-all text-foreground min-h-12 appearance-none cursor-pointer"
                >
                  <option value="">Select a project type...</option>
                  <option value="web-app">Web Application</option>
                  <option value="mobile-app">Mobile App</option>
                  <option value="ecommerce">E-Commerce Platform</option>
                  <option value="consulting">Consulting & Strategy</option>
                  <option value="other">Other</option>
                </select>
              </div>

              <div>
                <label htmlFor="message" className="block text-sm font-semibold text-foreground mb-3">
                  Message
                </label>
                <motion.textarea
                  whileFocus={{ scale: 1.02 }}
                  id="message"
                  name="message"
                  value={formData.message}
                  onChange={handleChange}
                  required
                  rows={5}
                  placeholder="Tell us about your project and goals..."
                  className="w-full px-4 py-3 bg-background/50 border border-accent-primary/25 rounded-lg focus:border-accent-primary focus:outline-none focus:ring-2 focus:ring-accent-primary/20 transition-all text-foreground placeholder-foreground/50 resize-none"
                />
              </div>

              <motion.button
                type="submit"
                whileHover={{ scale: 1.02, y: -2 }}
                whileTap={{ scale: 0.98 }}
                className="btn-primary w-full justify-center min-h-12"
              >
                <span className="relative z-10">
                  {submitted ? '✓ Message Sent!' : 'Send Message'}
                </span>
              </motion.button>
            </form>
          </motion.div>

          {/* Contact Information */}
          <motion.div
            initial={{ opacity: 0, x: 50 }}
            whileInView={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            viewport={{ once: true }}
            className="space-y-8"
          >
            {/* Map centered on Indore, India */}
            <div className="card relative h-48 overflow-hidden">
              <iframe
                title="Neuron AI Labs location in Indore"
                src="https://www.google.com/maps?q=Indore,India&output=embed"
                className="absolute inset-0 h-full w-full border-0"
                loading="lazy"
                referrerPolicy="no-referrer-when-downgrade"
              />
            </div>

            {/* Contact details grid */}
            <div className="grid grid-cols-2 gap-6">
              {contactInfo.map((info, index) => (
                <motion.div
                  key={info.label}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  viewport={{ once: true }}
                  className="card p-6"
                >
                  <div className="text-2xl mb-3">{info.icon}</div>
                  <p className="text-xs font-semibold text-text-secondary mb-2">{info.label}</p>
                  <p className="text-sm text-foreground font-medium">{info.value}</p>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  )
}