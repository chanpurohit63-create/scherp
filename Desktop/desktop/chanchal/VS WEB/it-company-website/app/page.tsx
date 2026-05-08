import Header from './components/Header'
import Hero from './components/Hero'
import About from './components/About'
import Services from './components/Services'
import Portfolio from './components/Portfolio'
import Testimonials from './components/Testimonials'
import Contact from './components/Contact'
import Footer from './components/Footer'
import MouseGlow from './components/MouseGlow'
import FloatingBlobs from './components/FloatingBlobs'
import SectionDivider from './components/SectionDivider'

export default function Home() {
  return (
    <div className="min-h-screen relative">
      <MouseGlow />
      <FloatingBlobs />
      <Header />
      <main>
        <Hero />
        <SectionDivider delay={0.2} />
        <About />
        <SectionDivider delay={0.2} />
        <Services />
        <SectionDivider delay={0.2} />
        <Portfolio />
        <SectionDivider delay={0.2} />
        <Testimonials />
        <SectionDivider delay={0.2} />
        <Contact />
      </main>
      <Footer />
    </div>
  )
}
