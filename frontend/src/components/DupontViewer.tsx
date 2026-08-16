'use client';
import React, { useState } from 'react';
import { 
  GitFork, 
  Layers, 
  TrendingUp, 
  Percent, 
  Activity, 
  ShieldAlert, 
  Zap, 
  Sparkles, 
  ArrowRight, 
  CheckCircle2,
  PieChart
} from 'lucide-react';

interface DupontViewerProps {
  dupontData: any;
}

export default function DupontViewer({ dupontData }: DupontViewerProps) {
  const [viewMode, setViewMode] = useState<'3step' | '5step'>('3step');

  if (!dupontData) return null;

  const { reported_roe, primary_driver, driver_summary, three_step, five_step, driver_breakdown } = dupontData;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="glass-card rounded-2xl p-5 border border-slate-200 shadow-sm flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-brand-50 text-brand-700 flex items-center justify-center font-bold">
            <GitFork className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-base font-extrabold text-slate-900">
                DuPont ROE Analytical Decomposition
              </h3>
              <span className="text-[10px] font-extrabold text-brand-700 bg-brand-50 border border-brand-200 px-2 py-0.5 rounded-full">
                3-STEP & 5-STEP TREE
              </span>
            </div>
            <p className="text-xs text-slate-500 font-medium">
              Deconstructs Return on Equity into profitability margin, asset turnover velocity, and equity multiplier leverage
            </p>
          </div>
        </div>

        <div className="flex items-center gap-1 bg-slate-100 p-1 rounded-xl">
          <button
            onClick={() => setViewMode('3step')}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
              viewMode === '3step' ? 'bg-white text-brand-700 shadow-sm' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            3-Step Model
          </button>
          <button
            onClick={() => setViewMode('5step')}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
              viewMode === '5step' ? 'bg-white text-brand-700 shadow-sm' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            5-Step Extended Model
          </button>
        </div>
      </div>

      {/* Driver Highlight Card */}
      <div className="glass-card rounded-2xl p-5 border border-brand-200 bg-gradient-to-r from-brand-50/40 via-white to-cyan-50/30 shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-brand-600" />
            <span className="text-xs font-extrabold text-brand-700 uppercase tracking-wider">Primary ROE Growth Driver</span>
          </div>
          <h4 className="text-lg font-black text-slate-900">{primary_driver}</h4>
          <p className="text-xs text-slate-600 max-w-2xl font-medium leading-relaxed">{driver_summary}</p>
        </div>

        <div className="px-5 py-3 bg-white rounded-2xl border border-slate-200 shadow-sm text-center shrink-0">
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Total Return on Equity</span>
          <p className="text-3xl font-black text-brand-900">{reported_roe}%</p>
        </div>
      </div>

      {/* DUPONT TREE DIAGRAM */}
      {viewMode === '3step' ? (
        <div className="glass-card rounded-2xl p-6 border border-slate-200 space-y-6 shadow-sm">
          <div className="flex justify-between items-center border-b pb-3 border-slate-100">
            <h4 className="text-xs font-extrabold text-slate-400 uppercase tracking-wider flex items-center gap-2">
              <Layers className="w-4 h-4 text-brand-600" />
              3-Step DuPont Equation Breakdown
            </h4>
            <span className="text-[11px] font-mono text-slate-500 bg-slate-50 px-2.5 py-1 rounded-lg border border-slate-200">
              ROE = Net Margin × Asset Turnover × Equity Multiplier
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-7 gap-3 items-center text-center">
            {/* Step 1: Net Margin */}
            <div className="md:col-span-2 p-4 bg-slate-50 rounded-2xl border border-slate-200 space-y-2">
              <span className="text-[10px] font-extrabold text-slate-400 uppercase tracking-wider">Net Profit Margin</span>
              <p className="text-2xl font-black text-slate-900">{three_step.net_profit_margin_pct}%</p>
              <p className="text-[10px] text-slate-500 font-medium">Operating profitability per $1 revenue</p>
            </div>

            <div className="md:col-span-1 text-slate-300 font-black text-xl flex justify-center">×</div>

            {/* Step 2: Asset Turnover */}
            <div className="md:col-span-2 p-4 bg-slate-50 rounded-2xl border border-slate-200 space-y-2">
              <span className="text-[10px] font-extrabold text-slate-400 uppercase tracking-wider">Asset Turnover</span>
              <p className="text-2xl font-black text-slate-900">{three_step.asset_turnover_x}x</p>
              <p className="text-[10px] text-slate-500 font-medium">Asset velocity & deployment efficiency</p>
            </div>

            <div className="md:col-span-1 text-slate-300 font-black text-xl flex justify-center">×</div>

            {/* Step 3: Equity Multiplier */}
            <div className="md:col-span-1 p-4 bg-brand-50/60 rounded-2xl border border-brand-200 space-y-2">
              <span className="text-[10px] font-extrabold text-brand-700 uppercase tracking-wider">Equity Multiplier</span>
              <p className="text-2xl font-black text-brand-900">{three_step.equity_multiplier_x}x</p>
              <p className="text-[10px] text-brand-700 font-medium">Financial leverage ratio</p>
            </div>
          </div>
        </div>
      ) : (
        <div className="glass-card rounded-2xl p-6 border border-slate-200 space-y-6 shadow-sm">
          <div className="flex justify-between items-center border-b pb-3 border-slate-100">
            <h4 className="text-xs font-extrabold text-slate-400 uppercase tracking-wider flex items-center gap-2">
              <Layers className="w-4 h-4 text-brand-600" />
              5-Step Extended DuPont Decomposition
            </h4>
            <span className="text-[11px] font-mono text-slate-500 bg-slate-50 px-2.5 py-1 rounded-lg border border-slate-200">
              ROE = Tax Burden × Interest Burden × EBIT Margin × Turnover × Leverage
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3 text-center">
            <div className="p-3.5 bg-slate-50 rounded-2xl border border-slate-200 space-y-1">
              <span className="text-[10px] font-extrabold text-slate-400 uppercase tracking-wider">Tax Burden</span>
              <p className="text-xl font-black text-slate-900">{five_step.tax_burden}</p>
              <p className="text-[10px] text-slate-400">Net Income / EBT</p>
            </div>

            <div className="p-3.5 bg-slate-50 rounded-2xl border border-slate-200 space-y-1">
              <span className="text-[10px] font-extrabold text-slate-400 uppercase tracking-wider">Interest Burden</span>
              <p className="text-xl font-black text-slate-900">{five_step.interest_burden}</p>
              <p className="text-[10px] text-slate-400">EBT / EBIT</p>
            </div>

            <div className="p-3.5 bg-slate-50 rounded-2xl border border-slate-200 space-y-1">
              <span className="text-[10px] font-extrabold text-slate-400 uppercase tracking-wider">EBIT Margin</span>
              <p className="text-xl font-black text-slate-900">{five_step.ebit_margin_pct}%</p>
              <p className="text-[10px] text-slate-400">EBIT / Revenue</p>
            </div>

            <div className="p-3.5 bg-slate-50 rounded-2xl border border-slate-200 space-y-1">
              <span className="text-[10px] font-extrabold text-slate-400 uppercase tracking-wider">Asset Turnover</span>
              <p className="text-xl font-black text-slate-900">{five_step.asset_turnover_x}x</p>
              <p className="text-[10px] text-slate-400">Revenue / Total Assets</p>
            </div>

            <div className="p-3.5 bg-brand-50/60 rounded-2xl border border-brand-200 space-y-1">
              <span className="text-[10px] font-extrabold text-brand-700 uppercase tracking-wider">Financial Leverage</span>
              <p className="text-xl font-black text-brand-900">{five_step.equity_multiplier_x}x</p>
              <p className="text-[10px] text-brand-700">Total Assets / Equity</p>
            </div>
          </div>
        </div>
      )}

      {/* Driver Breakdown Progress Bars */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="glass-card rounded-2xl p-4 border border-slate-200 space-y-2">
          <div className="flex justify-between text-xs font-bold text-slate-800">
            <span>Profitability Margin Contribution</span>
            <span className="font-extrabold text-slate-900">{driver_breakdown.profitability}%</span>
          </div>
          <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
            <div className="h-full bg-emerald-500 rounded-full" style={{ width: `${Math.min(driver_breakdown.profitability, 100)}%` }}></div>
          </div>
        </div>

        <div className="glass-card rounded-2xl p-4 border border-slate-200 space-y-2">
          <div className="flex justify-between text-xs font-bold text-slate-800">
            <span>Asset Velocity (Turnover)</span>
            <span className="font-extrabold text-slate-900">{driver_breakdown.asset_efficiency}x</span>
          </div>
          <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
            <div className="h-full bg-cyan-500 rounded-full" style={{ width: `${Math.min(driver_breakdown.asset_efficiency * 50, 100)}%` }}></div>
          </div>
        </div>

        <div className="glass-card rounded-2xl p-4 border border-slate-200 space-y-2">
          <div className="flex justify-between text-xs font-bold text-slate-800">
            <span>Equity Multiplier (Financial Leverage)</span>
            <span className="font-extrabold text-slate-900">{driver_breakdown.financial_leverage}x</span>
          </div>
          <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
            <div className="h-full bg-brand-600 rounded-full" style={{ width: `${Math.min(driver_breakdown.financial_leverage * 33, 100)}%` }}></div>
          </div>
        </div>
      </div>
    </div>
  );
}
