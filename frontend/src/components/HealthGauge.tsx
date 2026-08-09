'use client';
import React from 'react';
import { Activity, ShieldCheck, AlertTriangle, XCircle } from 'lucide-react';

interface HealthGaugeProps {
  score: number;
  companyName: string;
  breakdown?: {
    profitability?: number;
    liquidity?: number;
    solvency?: number;
    efficiency?: number;
  };
}

export default function HealthGauge({ score, companyName, breakdown }: HealthGaugeProps) {
  const getBadgeDetails = (val: number) => {
    if (val >= 75) {
      return { 
        label: 'HEALTHY & SOLVENT', 
        color: 'text-emerald-800 bg-gradient-to-r from-emerald-50 via-teal-50 to-emerald-100 border-emerald-300 shadow-sm', 
        icon: ShieldCheck, 
        gradientId: 'gaugeGreen' 
      };
    } else if (val >= 55) {
      return { 
        label: 'MODERATE RISK', 
        color: 'text-amber-800 bg-gradient-to-r from-amber-50 via-orange-50 to-amber-100 border-amber-300 shadow-sm', 
        icon: AlertTriangle, 
        gradientId: 'gaugeAmber' 
      };
    } else {
      return { 
        label: 'CRITICAL WARNING', 
        color: 'text-rose-800 bg-gradient-to-r from-rose-50 via-pink-50 to-rose-100 border-rose-300 shadow-sm', 
        icon: XCircle, 
        gradientId: 'gaugeRose' 
      };
    }
  };

  const badge = getBadgeDetails(score);
  const Icon = badge.icon;

  // SVG Gauge calculations
  const radius = 70;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  const prof = breakdown?.profitability ?? 20.0;
  const liq = breakdown?.liquidity ?? 22.5;
  const solv = breakdown?.solvency ?? 20.0;
  const eff = breakdown?.efficiency ?? 22.5;

  return (
    <div className="glass-card rounded-2xl p-6 shadow-md border border-slate-200/80 bg-gradient-to-b from-white to-slate-50/50 flex flex-col items-center text-center">
      <div className="w-full flex items-center justify-between mb-2">
        <span className="text-[11px] font-extrabold text-slate-400 uppercase tracking-wider">Health Rating</span>
        <div className={`flex items-center gap-1.5 px-3 py-1 rounded-full border text-[11px] font-black ${badge.color}`}>
          <Icon className="w-3.5 h-3.5" />
          <span>{badge.label}</span>
        </div>
      </div>

      <div className="relative my-3 flex items-center justify-center">
        <svg className="w-44 h-44 transform -rotate-90">
          <defs>
            <linearGradient id="gaugeGreen" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#0284c7" />
              <stop offset="50%" stopColor="#06b6d4" />
              <stop offset="100%" stopColor="#10b981" />
            </linearGradient>
            <linearGradient id="gaugeAmber" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#f59e0b" />
              <stop offset="100%" stopColor="#fbbf24" />
            </linearGradient>
            <linearGradient id="gaugeRose" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#e11d48" />
              <stop offset="100%" stopColor="#f43f5e" />
            </linearGradient>
          </defs>
          <circle
            cx="88"
            cy="88"
            r={radius}
            stroke="#E2E8F0"
            strokeWidth="13"
            fill="transparent"
          />
          <circle
            cx="88"
            cy="88"
            r={radius}
            stroke={`url(#${badge.gradientId})`}
            strokeWidth="13"
            fill="transparent"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            className="transition-all duration-1000 ease-out filter drop-shadow-[0_2px_8px_rgba(16,185,129,0.3)]"
          />
        </svg>

        <div className="absolute flex flex-col items-center">
          <span className="text-4xl font-black text-slate-900 leading-none tracking-tight">{score}</span>
          <span className="text-[11px] font-bold text-slate-400 mt-1">out of 100</span>
        </div>
      </div>

      <h4 className="text-base font-extrabold text-slate-900">{companyName}</h4>
      <p className="text-xs text-slate-500 font-medium mt-0.5">Weighted accuracy index across 4 financial modules</p>

      {/* 4-Module Health Rate Sub-score Breakdown */}
      <div className="w-full mt-4 pt-3 border-t border-slate-200/80 space-y-2 text-left">
        <span className="text-[10px] font-extrabold text-slate-400 uppercase tracking-wider block text-center mb-1">
          Module Accuracy & Health Breakdown
        </span>

        {[
          { label: 'Profitability Rate', value: prof, color: 'bg-cyan-500' },
          { label: 'Liquidity Solvency', value: liq, color: 'bg-emerald-500' },
          { label: 'Debt Structure', value: solv, color: 'bg-indigo-500' },
          { label: 'Efficiency Cycle', value: eff, color: 'bg-teal-500' }
        ].map((m) => (
          <div key={m.label} className="space-y-0.5">
            <div className="flex justify-between text-[11px] font-bold text-slate-700">
              <span>{m.label}</span>
              <span>{m.value} / 25 pts</span>
            </div>
            <div className="w-full bg-slate-100 rounded-full h-1.5 overflow-hidden">
              <div 
                className={`${m.color} h-full rounded-full transition-all duration-500`}
                style={{ width: `${(m.value / 25.0) * 100}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
