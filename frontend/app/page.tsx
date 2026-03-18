'use client'

import { useState } from 'react'
import Chat from '@/components/Chat'
import { Monitor, Code, ShoppingCart, Paintbrush, ArrowRight, CheckCircle2 } from 'lucide-react'

export default function Home() {
  const [isChatOpen, setIsChatOpen] = useState(false)

  const handleAssetShow = (assetType: string | null) => {
    if (assetType && assetType.startsWith('scroll:')) {
      const sectionId = assetType.split(':')[1]
      console.log('📜 Native Scroll command for:', sectionId)
      setIsChatOpen(true)
      
      // Use a slightly longer timeout (500ms) to ensure layout is stable
      setTimeout(() => {
        const element = document.getElementById(sectionId)
        if (element) {
          element.scrollIntoView({ behavior: 'smooth' })
          console.log('🚀 Native scrollIntoView triggered')
        }
      }, 500)
    }
  }

  return (
    <main className="min-h-screen bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white font-sans selection:bg-blue-500/30">
      
      {/* Navigation */}
      <nav className="fixed w-full z-40 top-0 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border-b border-slate-200 dark:border-slate-800">
        <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white font-bold text-xl">W</div>
            <span className="text-2xl font-bold tracking-tight">WS.</span>
          </div>
          <div className="hidden md:flex gap-8 text-sm font-medium text-slate-600 dark:text-slate-300">
            <a href="#hero" className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors">Home</a>
            <a href="#services" className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors">Services</a>
            <a href="#portfolio" className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors">Portfolio</a>
            <a href="#about" className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors">About</a>
          </div>
          <button className="bg-slate-900 dark:bg-white text-white dark:text-slate-900 px-5 py-2.5 rounded-full text-sm font-semibold hover:opacity-90 transition-opacity">
            Get a Quote
          </button>
        </div>
      </nav>

      {/* Hero Section */}
      <section id="hero" className="pt-32 pb-20 md:pt-48 md:pb-32 px-6 max-w-7xl mx-auto flex flex-col items-center text-center">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 text-sm font-medium mb-8">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-500 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-600"></span>
          </span>
          Accepting New Projects
        </div>
        <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight max-w-4xl leading-[1.1] mb-8">
          We build digital experiences that <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-violet-600">drive growth.</span>
        </h1>
        <p className="text-lg md:text-xl text-slate-600 dark:text-slate-400 max-w-2xl mb-10 leading-relaxed">
          We offer a range of web development services to help you build a stunning online presence. Our services include Custom Web Applications, Modern Landing Pages, eCommerce Solutions, and UI/UX Design. We transform your digital ideas into reality natively and blazingly fast, ensuring your site looks beautiful and ranks high on SEO.
        </p>
        <div className="flex flex-col sm:flex-row gap-4">
          <button className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-4 rounded-full font-semibold flex items-center justify-center gap-2 transition-all">
            See Our Work <ArrowRight className="w-4 h-4" />
          </button>
          <button 
            onClick={() => setIsChatOpen(true)}
            className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600 text-slate-900 dark:text-white px-8 py-4 rounded-full font-semibold transition-all"
          >
            Talk to AI Assistant
          </button>
        </div>
      </section>

      {/* Services Section */}
      <section id="services" className="py-24 bg-white dark:bg-slate-950 border-y border-slate-100 dark:border-slate-900">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">Our Services</h2>
            <p className="text-slate-600 dark:text-slate-400">
              We offer a range of web development services to help you build a stunning online presence, ensuring your site looks beautiful and ranks high on SEO.
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            <div className="bg-slate-50 dark:bg-slate-900 p-8 rounded-2xl border border-slate-100 dark:border-slate-800 hover:border-blue-500/50 transition-colors group">
              <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/50 text-blue-600 dark:text-blue-400 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <Monitor className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold mb-3">Custom Web Apps</h3>
              <p className="text-slate-600 dark:text-slate-400 text-sm leading-relaxed">Complex SaaS platforms, internal tools, and interactive dashboards built with Next.js and React.</p>
            </div>
            
            <div className="bg-slate-50 dark:bg-slate-900 p-8 rounded-2xl border border-slate-100 dark:border-slate-800 hover:border-violet-500/50 transition-colors group">
              <div className="w-12 h-12 bg-violet-100 dark:bg-violet-900/50 text-violet-600 dark:text-violet-400 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <Code className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold mb-3">Landing Pages</h3>
              <p className="text-slate-600 dark:text-slate-400 text-sm leading-relaxed">High-converting, SEO-optimized marketing sites designed to turn visitors into paying customers.</p>
            </div>
            
            <div className="bg-slate-50 dark:bg-slate-900 p-8 rounded-2xl border border-slate-100 dark:border-slate-800 hover:border-emerald-500/50 transition-colors group">
              <div className="w-12 h-12 bg-emerald-100 dark:bg-emerald-900/50 text-emerald-600 dark:text-emerald-400 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <ShoppingCart className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold mb-3">eCommerce</h3>
              <p className="text-slate-600 dark:text-slate-400 text-sm leading-relaxed">Scalable online storefronts using Shopify, Stripe integration, and custom inventory management.</p>
            </div>
            
            <div className="bg-slate-50 dark:bg-slate-900 p-8 rounded-2xl border border-slate-100 dark:border-slate-800 hover:border-amber-500/50 transition-colors group">
              <div className="w-12 h-12 bg-amber-100 dark:bg-amber-900/50 text-amber-600 dark:text-amber-400 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <Paintbrush className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold mb-3">UI/UX Design</h3>
              <p className="text-slate-600 dark:text-slate-400 text-sm leading-relaxed">User-centric interface design prioritizing accessibility, modern aesthetics, and intuitive flows.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Portfolio Section */}
      <section id="portfolio" className="py-24 px-6 max-w-7xl mx-auto">
        <div className="flex flex-col md:flex-row md:items-end justify-between mb-16 gap-6">
          <div className="max-w-2xl">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">Selected Work</h2>
            <p className="text-slate-600 dark:text-slate-400">A glimpse into some of the digital products we've shipped for startups and enterprise clients.</p>
          </div>
          <button className="text-blue-600 dark:text-blue-400 font-semibold flex items-center gap-2 hover:gap-3 transition-all shrink-0">
            View full portfolio <ArrowRight className="w-4 h-4" />
          </button>
        </div>
        
        <div className="grid md:grid-cols-2 gap-8">
          <div className="group cursor-pointer">
            <div className="aspect-[4/3] bg-gradient-to-tr from-slate-200 to-slate-100 dark:from-slate-800 dark:to-slate-700 rounded-3xl mb-6 overflow-hidden relative">
              <div className="absolute inset-0 bg-black/5 group-hover:bg-transparent transition-colors"></div>
              {/* Abstract graphic placeholder */}
              <div className="absolute inset-x-10 bottom-0 top-10 bg-white dark:bg-slate-900 rounded-t-xl shadow-2xl border border-slate-200 dark:border-slate-700 p-4">
                 <div className="w-full h-8 bg-slate-100 dark:bg-slate-800 rounded mb-4"></div>
                 <div className="w-2/3 h-32 bg-slate-100 dark:bg-slate-800 rounded"></div>
              </div>
            </div>
            <h3 className="text-2xl font-bold mb-2">FinTech Dashboard</h3>
            <p className="text-slate-600 dark:text-slate-400">Web App • Next.js • React Query</p>
          </div>
          
          <div className="group cursor-pointer">
            <div className="aspect-[4/3] bg-gradient-to-tr from-slate-200 to-slate-100 dark:from-slate-800 dark:to-slate-700 rounded-3xl mb-6 overflow-hidden relative">
              <div className="absolute inset-0 bg-black/5 group-hover:bg-transparent transition-colors"></div>
               {/* Abstract graphic placeholder */}
               <div className="absolute inset-10 bg-white dark:bg-slate-900 rounded-xl shadow-2xl border border-slate-200 dark:border-slate-700 p-6 flex flex-col items-center justify-center">
                 <div className="w-32 h-32 rounded-full border-4 border-dashed border-slate-200 dark:border-slate-700 mb-6"></div>
                 <div className="flex gap-2">
                   <div className="w-16 h-8 bg-slate-100 dark:bg-slate-800 rounded-full"></div>
                   <div className="w-16 h-8 bg-slate-100 dark:bg-slate-800 rounded-full"></div>
                 </div>
              </div>
            </div>
            <h3 className="text-2xl font-bold mb-2">AI Image Generator</h3>
            <p className="text-slate-600 dark:text-slate-400">SaaS Platform • GPU Clustering • Stripe</p>
          </div>
        </div>
      </section>

      {/* About Section */}
      <section id="about" className="py-24 bg-white dark:bg-slate-950 border-t border-slate-100 dark:border-slate-900">
        <div className="max-w-7xl mx-auto px-6 grid md:grid-cols-2 gap-16 items-center">
          <div>
            <h2 className="text-3xl md:text-4xl font-bold mb-6">Built by developers, for ambitious founders.</h2>
            <p className="text-slate-600 dark:text-slate-400 text-lg leading-relaxed mb-6">
              WS was founded with a simple objective: cut through the noise of bloated agencies and deliver exceptionally fast, beautifully designed digital products.
            </p>
            <ul className="space-y-4 mb-8">
              <li className="flex items-center gap-3">
                <CheckCircle2 className="w-5 h-5 text-blue-600" />
                <span className="font-medium">100% In-house USA team</span>
              </li>
              <li className="flex items-center gap-3">
                <CheckCircle2 className="w-5 h-5 text-blue-600" />
                <span className="font-medium">Transparent weekly pricing</span>
              </li>
              <li className="flex items-center gap-3">
                <CheckCircle2 className="w-5 h-5 text-blue-600" />
                <span className="font-medium">Direct access to senior devs</span>
              </li>
            </ul>
          </div>
          <div className="grid grid-cols-2 gap-4">
             <div className="aspect-square bg-blue-600 rounded-3xl flex items-center justify-center p-8 text-center text-white">
                <div>
                   <div className="text-5xl font-black mb-2">40+</div>
                   <div className="text-blue-100 font-medium tracking-wide">Projects Shipped</div>
                </div>
             </div>
             <div className="aspect-square bg-slate-100 dark:bg-slate-900 rounded-3xl flex items-center justify-center p-8 text-center">
                <div>
                   <div className="text-5xl font-black mb-2">0ms</div>
                   <div className="text-slate-500 dark:text-slate-400 font-medium tracking-wide">Layout Shift</div>
                </div>
             </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 bg-slate-50 dark:bg-slate-900 border-t border-slate-200 dark:border-slate-800 text-center">
        <p className="text-slate-500 font-medium">© {new Date().getFullYear()} WS Web Development. All rights reserved.</p>
      </footer>

      {/* Floating Chat Widget */}
      <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end gap-4">
        {/* Chat window */}
        {isChatOpen && (
          <div className="w-[90vw] sm:w-[400px] h-[600px] max-h-[80vh] bg-white dark:bg-slate-900 shadow-2xl rounded-3xl border border-slate-200 dark:border-slate-800 overflow-hidden flex flex-col animate-in slide-in-from-bottom-4 fade-in duration-300">
            <div className="bg-blue-600 p-4 flex items-center justify-between text-white">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center font-bold">W</div>
                <div>
                   <div className="font-bold">WS AI</div>
                   <div className="text-[10px] text-blue-100 flex items-center gap-1">
                     <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                     Always Active
                   </div>
                </div>
              </div>
              <button 
                onClick={() => setIsChatOpen(false)}
                className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                title="Minimize chat"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path></svg>
              </button>
            </div>
            
            <div className="flex-1 overflow-hidden relative">
              <Chat onAssetShow={handleAssetShow} />
            </div>
          </div>
        )}

        {/* Toggle Button */}
        <button
          onClick={() => setIsChatOpen(!isChatOpen)}
          className={`w-16 h-16 rounded-full shadow-lg flex items-center justify-center transition-all duration-300 transform hover:scale-110 active:scale-95 ${
            isChatOpen ? 'bg-slate-800 dark:bg-slate-700 text-white' : 'bg-blue-600 text-white'
          }`}
        >
          {isChatOpen ? (
            <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path></svg>
          ) : (
            <div className="relative">
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"></path></svg>
              <span className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 border-2 border-white dark:border-slate-900 rounded-full"></span>
            </div>
          )}
        </button>
      </div>
    </main>
  )
}

