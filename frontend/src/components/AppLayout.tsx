'use client';
import React, { useState, Suspense } from 'react';
import { usePathname } from 'next/navigation';
import Sidebar from '@/components/Sidebar';
import { Menu, X } from 'lucide-react';

function AppLayoutContent({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);

  // Auth pages should render standalone without Sidebar or navigation clutter
  const isAuthPage = ['/login', '/register', '/forgot-password'].some(
    (path) => pathname === path || pathname?.startsWith(`${path}/`)
  );

  if (isAuthPage) {
    return (
      <div className="min-h-screen w-full bg-[#050D1A] flex items-center justify-center p-4">
        {children}
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col lg:flex-row antialiased">
      {/* Mobile Header Bar (Visible on mobile/tablet screens < 1024px) */}
      <header className="lg:hidden sticky top-0 z-40 bg-[#050D1A]/95 backdrop-blur-xl text-white px-4 py-3 border-b border-cyan-500/30 flex items-center justify-between shadow-[0_4px_25px_-5px_rgba(2,132,199,0.35)]">
        <div className="flex items-center gap-3">
          <div className="relative flex items-center justify-center shrink-0">
            <div className="absolute -inset-1 rounded-xl bg-gradient-to-r from-blue-600 via-cyan-400 to-teal-400 opacity-70 blur-sm"></div>
            <div className="relative bg-white/95 border border-white/20 rounded-xl p-1 w-9 h-9 flex items-center justify-center shadow-inner">
              <img src="/logo.png" alt="Captrix AI Agent Logo" className="w-full h-full object-contain" />
            </div>
          </div>
          <div>
            <h1 className="text-base font-black text-white leading-none tracking-tight">
              Captrix <span className="bg-gradient-to-r from-cyan-300 via-blue-400 to-indigo-300 bg-clip-text text-transparent">AI AGENT</span>
            </h1>
            <p className="text-[10px] text-cyan-400 font-extrabold tracking-wider uppercase mt-0.5">
              Financial Intelligence
            </p>
          </div>
        </div>

        <button
          onClick={() => setMobileOpen(!mobileOpen)}
          className="relative p-2.5 rounded-xl bg-gradient-to-r from-[#0E1E38] to-[#0A172C] border border-cyan-400/40 text-cyan-300 shadow-[0_0_15px_rgba(6,182,212,0.3)] hover:scale-105 transition-all duration-300 active:scale-95"
          aria-label="Toggle Mobile Navigation"
        >
          {mobileOpen ? <X className="w-5 h-5 text-cyan-300" /> : <Menu className="w-5 h-5 text-cyan-300" />}
        </button>
      </header>

      {/* Mobile Drawer Overlay */}
      {mobileOpen && (
        <div
          onClick={() => setMobileOpen(false)}
          className="fixed inset-0 z-50 bg-slate-950/70 backdrop-blur-sm lg:hidden transition-opacity"
        />
      )}

      {/* Mobile Sidebar Container */}
      <div
        className={`fixed top-0 bottom-0 left-0 z-50 transition-transform duration-300 transform lg:hidden h-full max-h-screen overflow-y-auto shadow-2xl ${
          mobileOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <Sidebar onNavigate={() => setMobileOpen(false)} />
      </div>

      {/* Desktop Permanent Sidebar */}
      <div className="hidden lg:block">
        <Sidebar />
      </div>

      {/* Main Responsive Page View Content Area */}
      <main className="flex-1 p-3.5 sm:p-6 lg:p-8 max-w-7xl mx-auto w-full overflow-x-hidden min-h-[calc(100vh-4rem)] lg:min-h-screen">
        {children}
      </main>
    </div>
  );
}

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <Suspense fallback={<div className="min-h-screen bg-[#050D1A]" />}>
      <AppLayoutContent>{children}</AppLayoutContent>
    </Suspense>
  );
}
