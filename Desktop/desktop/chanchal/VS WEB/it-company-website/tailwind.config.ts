import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'accent-primary': '#FFC857',
        'accent-secondary': '#5A7D9A',
        'accent-light': '#FFE97D',
        'accent-dark': '#CC9500',
        'text-secondary': '#A0A0A0',
        'dark-bg': '#121212',
        'card-dark': '#1a1a1a',
      },
      fontFamily: {
        orbitron: ['var(--font-orbitron)', 'sans-serif'],
        'roboto-mono': ['var(--font-roboto-mono)', 'monospace'],
        inter: ['var(--font-inter)', 'sans-serif'],
      },
      keyframes: {
        'fade-in': {
          'from': { opacity: '0' },
          'to': { opacity: '1' },
        },
        'scale-in': {
          'from': { opacity: '0', transform: 'scale(0.95)' },
          'to': { opacity: '1', transform: 'scale(1)' },
        },
        'slide-up': {
          'from': { opacity: '0', transform: 'translateY(10px)' },
          'to': { opacity: '1', transform: 'translateY(0)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-8px)' },
        },
      },
      animation: {
        'fade-in': 'fade-in 0.6s ease-out',
        'scale-in': 'scale-in 0.5s ease-out',
        'slide-up': 'slide-up 0.6s ease-out',
        float: 'float 2s ease-in-out infinite',
      },
      backdropFilter: {
        'none': 'none',
        'blur': 'blur(16px)',
      },
      boxShadow: {
        'card': '0 4px 15px rgba(0, 0, 0, 0.2)',
        'card-hover': '0 8px 30px rgba(0, 0, 0, 0.3)',
        'sm': '0 1px 2px rgba(0, 0, 0, 0.1)',
      },
    },
  },
  plugins: [],
}

export default config