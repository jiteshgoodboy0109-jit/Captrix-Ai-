'use client';
import React from 'react';
import { BrainCircuit, CheckCircle, AlertCircle, ArrowUpRight, Lightbulb } from 'lucide-react';

interface AIInsightsPanelProps {
  aiReport: any;
}

export default function AIInsightsPanel({ aiReport }: AIInsightsPanelProps) {
  if (!aiReport) return null;

  const strengths = aiReport.strengths || [];
  const weaknesses = aiReport.weaknesses || [];
  const recommendations = aiReport.recommendations || [];

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-brand-50 text-brand-700 flex items-center justify-center font-bold">
          <BrainCircuit className="w-5 h-5" />
        </div>
        <div>
          <h3 className="text-base font-bold text-slate-900">AI Business Insights & Executive Synthesis</h3>
          <p className="text-xs text-slate-500">Autonomous analysis of company viability, cash health, and strategic growth leverage</p>
        </div>
      </div>

      {/* Executive Summary Box */}
      <div className="glass-card rounded-2xl p-5 border border-brand-200 bg-gradient-to-r from-brand-50/40 to-cyan-50/20 space-y-2">
        <span className="text-[11px] font-extrabold text-brand-700 uppercase tracking-wider">Executive Synthesis</span>
        <p className="text-sm font-medium text-slate-800 leading-relaxed">{aiReport.executive_summary}</p>
      </div>

      {/* Strengths & Weaknesses */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Core Strengths */}
        <div className="glass-card rounded-2xl p-5 border border-emerald-200 bg-emerald-50/10 space-y-3">
          <h4 className="text-sm font-bold text-emerald-900 flex items-center gap-2">
            <CheckCircle className="w-4 h-4 text-emerald-600" />
            Competitive Strengths
          </h4>
          <ul className="space-y-2 text-xs text-slate-700">
            {strengths.map((s: string, idx: number) => (
              <li key={idx} className="flex items-start gap-2 bg-white p-3 rounded-xl border border-emerald-100 shadow-sm">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 mt-1.5 shrink-0"></span>
                <span>{s}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Vulnerabilities */}
        <div className="glass-card rounded-2xl p-5 border border-amber-200 bg-amber-50/10 space-y-3">
          <h4 className="text-sm font-bold text-amber-900 flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-amber-600" />
            Financial Vulnerabilities
          </h4>
          <ul className="space-y-2 text-xs text-slate-700">
            {weaknesses.map((w: string, idx: number) => (
              <li key={idx} className="flex items-start gap-2 bg-white p-3 rounded-xl border border-amber-100 shadow-sm">
                <span className="w-1.5 h-1.5 rounded-full bg-amber-500 mt-1.5 shrink-0"></span>
                <span>{w}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Strategic AI Recommendations */}
      <div className="glass-card rounded-2xl p-5 border border-slate-200 space-y-4">
        <h4 className="text-sm font-bold text-slate-900 flex items-center gap-2">
          <Lightbulb className="w-4 h-4 text-brand-600" />
          Prioritized Action Recommendations
        </h4>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {recommendations.map((rec: any, idx: number) => (
            <div key={idx} className="p-4 bg-slate-50 rounded-xl border border-slate-200 flex flex-col justify-between space-y-2">
              <div>
                <span className="text-[10px] font-extrabold px-2 py-0.5 rounded-full bg-brand-100 text-brand-800">
                  {rec.priority}
                </span>
                <h5 className="text-sm font-bold text-slate-900 mt-2">{rec.title}</h5>
                <p className="text-xs text-slate-600 mt-1 leading-relaxed">{rec.action}</p>
              </div>

              <div className="pt-2 border-t border-slate-200 flex items-center text-[11px] font-semibold text-brand-700 gap-1">
                <span>View Strategy</span>
                <ArrowUpRight className="w-3.5 h-3.5" />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
