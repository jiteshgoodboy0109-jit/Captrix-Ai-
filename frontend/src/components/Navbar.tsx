'use client';
import React from 'react';
import Link from 'next/link';
import { ShieldCheck, User, Bell, LogIn } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';

export default function Navbar() {
  const { user } = useAuth();

  return (
    <header className="h-16 border-b border-slate-200 bg-white/90 backdrop-blur-md sticky top-0 z-30 flex items-center justify-between px-6">
      <div className="flex items-center gap-3">
        <Link href="/dashboard" className="flex items-center gap-3 group">
          <div className="w-10 h-10 rounded-xl bg-white border border-slate-200 p-1 flex items-center justify-center shadow-sm group-hover:scale-105 transition-transform">
            <img src="/logo.png" alt="Captrix AI Agent Logo" className="w-full h-full object-contain" />
          </div>
          <div>
            <h1 className="text-lg font-black text-slate-900 leading-none tracking-tight group-hover:text-brand-700 transition-colors">
              Captrix <span className="text-brand-600 font-extrabold">AI AGENT</span>
            </h1>
            <p className="text-[11px] text-slate-500 mt-0.5 font-medium">Enterprise Financial Intelligence Platform</p>
          </div>
        </Link>
      </div>

      <div className="flex items-center gap-4">
        <div className="hidden md:flex items-center gap-2 bg-slate-50 px-3 py-1.5 rounded-full border border-slate-200 text-xs font-medium text-slate-600">
          <ShieldCheck className="w-4 h-4 text-emerald-600" />
          <span>SOC2 & Audit Compliant</span>
        </div>

        <button className="relative p-2 rounded-lg text-slate-500 hover:text-slate-900 hover:bg-slate-100 transition-colors" title="Notifications">
          <Bell className="w-5 h-5" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-brand-600 rounded-full"></span>
        </button>

        <div className="h-8 w-px bg-slate-200"></div>

        {user ? (
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-full bg-brand-50 border border-brand-200 flex items-center justify-center text-brand-700 font-bold text-sm">
              {user.full_name ? user.full_name.charAt(0).toUpperCase() : <User className="w-4 h-4" />}
            </div>
            <div className="hidden sm:block">
              <p className="text-sm font-semibold text-slate-900 leading-none">{user.full_name}</p>
              <p className="text-xs text-brand-700 font-medium mt-0.5">{user.role || 'Financial Analyst'}</p>
            </div>
          </div>
        ) : (
          <Link
            href="/login"
            className="flex items-center gap-2 px-3.5 py-1.5 bg-brand-600 hover:bg-brand-700 text-white text-xs font-bold rounded-xl shadow-sm transition-all"
          >
            <LogIn className="w-3.5 h-3.5" />
            <span>Sign In</span>
          </Link>
        )}
      </div>
    </header>
  );
}
