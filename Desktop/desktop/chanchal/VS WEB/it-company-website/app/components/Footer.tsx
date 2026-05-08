'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'

export default function Footer() {
  const currentYear = new Date().getFullYear()

  const links = [
    { label: 'About', href: '#about' },
    { label: 'Services', href: '#services' },
    { label: 'Portfolio', href: '#portfolio' },
    { label: 'Contact', href: '#contact' },
  ]

  const social = [
    { icon: '𝕏', label: 'Twitter', href: '#' },
    { icon: 'in', label: 'LinkedIn', href: '#' },
    { icon: 'f', label: 'Facebook', href: '#' },
  ]

  return (
    <footer className="relative border-t border-accent-primary/15 bg-linear-to-br from-background via-dark-bg to-background">
      <div
        className="absolute inset-0 bg-cover bg-center pointer-events-none"
        style={{ backgroundImage: "url('/hero-revolving-ai.png')" }}
      ></div>
      <div className="absolute inset-0 bg-linear-to-t from-accent-primary/2 via-transparent to-transparent pointer-events-none"></div>
      <div className="absolute inset-0 bg-linear-to-b from-black/78 via-black/70 to-black/86 pointer-events-none"></div>

      <div className="max-w-7xl mx-auto px-4 py-16 relative z-10">
        {/* Newsletter Section */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="card p-8 md:p-10 mb-16 bg-linear-to-r from-accent-primary/5 to-accent-secondary/5"
        >
          <div className="flex flex-col md:flex-row items-center justify-between gap-8">
            <div>
              <h3 className="text-2xl font-bold text-foreground mb-2">Stay Updated</h3>
              <p className="text-text-secondary">Get the latest insights on IT innovation and industry trends.</p>
            </div>
            <form className="flex gap-3 w-full md:w-auto">
              <motion.input
                whileFocus={{ scale: 1.02 }}
                type="email"
                placeholder="Enter your email"
                required
                className="flex-1 md:flex-initial px-4 py-3 bg-background/50 border border-accent-primary/25 rounded-lg focus:border-accent-primary focus:outline-none focus:ring-2 focus:ring-accent-primary/20 transition-all text-foreground placeholder-foreground/50 min-h-12"
              />
              <motion.button
                type="submit"
                whileHover={{ scale: 1.02, y: -2 }}
                whileTap={{ scale: 0.98 }}
                className="btn-primary whitespace-nowrap"
              >
                Subscribe
              </motion.button>
            </form>
          </div>
        </motion.div>

        <div className="grid md:grid-cols-4 gap-12 mb-12">
          {/* Brand */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="space-y-4"
          >
            <Link href="/" className="text-2xl font-bold text-accent-primary hover:text-accent-light transition-colors flex items-center gap-2">
              <img src="/logo.svg" alt="NeuronAI Labs" width={24} height={24} className="opacity-75" />
              NeuronAI Labs
            </Link>
            <p className="text-text-secondary text-sm leading-relaxed">
              Transforming businesses through innovative IT solutions and proven expertise.
            </p>
          </motion.div>

          {/* Quick Links */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            viewport={{ once: true }}
            className="space-y-4"
          >
            <h4 className="font-semibold text-foreground text-sm uppercase tracking-wider">Quick Links</h4>
            <ul className="space-y-3">
              {links.map((link) => (
                <li key={link.label}>
                  <Link href={link.href} className="text-text-secondary hover:text-accent-primary transition-colors text-sm">
                    → {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </motion.div>

          {/* Services */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            viewport={{ once: true }}
            className="space-y-4"
          >
            <h4 className="font-semibold text-foreground text-sm uppercase tracking-wider">Services</h4>
            <ul className="space-y-3 text-sm">
              <li><Link href="#" className="text-text-secondary hover:text-accent-primary transition-colors">→ AI Solutions</Link></li>
              <li><Link href="#" className="text-text-secondary hover:text-accent-primary transition-colors">→ Cloud Computing</Link></li>
              <li><Link href="#" className="text-text-secondary hover:text-accent-primary transition-colors">→ Cybersecurity</Link></li>
              <li><Link href="#" className="text-text-secondary hover:text-accent-primary transition-colors">→ Automation</Link></li>
            </ul>
          </motion.div>

          {/* Social Links */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            viewport={{ once: true }}
            className="space-y-4"
          >
            <h4 className="font-semibold text-foreground text-sm uppercase tracking-wider">Follow Us</h4>
            <div className="flex gap-3">
              {social.map((item) => (
                <motion.a
                  key={item.label}
                  href={item.href}
                  whileHover={{ scale: 1.1, y: -3 }}
                  whileTap={{ scale: 0.95 }}
                  className="w-10 h-10 rounded-full bg-linear-to-br from-accent-primary/15 to-accent-secondary/15 border border-accent-primary/25 hover:border-accent-primary/60 flex items-center justify-center text-text-secondary hover:text-accent-primary transition-all shadow-card hover:shadow-card-hover"
                  title={item.label}
                >
                  {item.icon}
                </motion.a>
              ))}
            </div>
          </motion.div>
        </div>

        {/* Divider */}
        <div className="border-t border-accent-primary/10 my-10"></div>

        {/* Bottom section */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          viewport={{ once: true }}
          className="flex flex-col md:flex-row justify-between items-center text-sm text-text-secondary gap-6"
        >
          <div className="text-center md:text-left">
            <p>© {currentYear} NeuronAI Labs. All rights reserved.</p>
            <p className="mt-2">Kial Road</p>
          </div>
          <div className="flex gap-6 flex-wrap justify-center md:justify-end">
            <Link href="#" className="hover:text-accent-primary transition-colors">Privacy Policy</Link>
            <Link href="#" className="hover:text-accent-primary transition-colors">Terms of Service</Link>
          </div>
        </motion.div>
      </div>

      {/* Animated background orbs */}
      <div className="absolute bottom-0 right-0 w-72 h-72 bg-accent-secondary/8 rounded-full blur-3xl -z-10"></div>
    </footer>
  )
}