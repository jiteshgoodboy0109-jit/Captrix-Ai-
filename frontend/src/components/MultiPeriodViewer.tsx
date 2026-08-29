'use client';
import React, { useState } from 'react';
import { 
  TrendingUp, 
  ArrowUpRight, 
  ArrowDownRight, 
  Calendar, 
  Table, 
  BarChart2, 
  Sparkles, 
  ShieldCheck, 
  Award,
  Layers
} from 'lucide-react';

import { formatCurrency, getCurrencySymbol } from '@/lib/currency';

interface MultiPeriodViewerProps {
  multiPeriod: any;
  currency?: string;
}

export default function MultiPeriodViewer({ multiPeriod, currency = 'USD' }: MultiPeriodViewerProps) {
  const [activeTab, setActiveTab] = useState<'income' | 'balance'>('income');

  if (!multiPeriod) return null;

  const cagr = multiPeriod.cagr_metrics || {};
  const yoy = multiPeriod.yoy_growth || {};
  const incComp = multiPeriod.comparative_income_statement || [];
  const bsComp = multiPeriod.comparative_balance_sheet || [];
  const marginTrends = multiPeriod.margin_trends || [];

  const formatDollar = (val: number | null | undefined) => formatCurrency(val, currency);

  const getGrowthBadge = (val: number | null | undefined) => {
    if (val === null || val === undefined) return <span className="text-xs font-medium text-slate-400">N/A</span>;
    const isPos = val >= 0;
    return (
      <span className={`inline-flex items-center gap-0.5 text-xs font-bold px-2 py-0.5 rounded-md border ${
        isPos ? 'bg-emerald-50 text-emerald-700 border-emerald-200' : 'bg-rose-50 text-rose-700 border-rose-200'
      }`}>
        {isPos ? <ArrowUpRight className="w-3 h-3 text-emerald-600" /> : <ArrowDownRight className="w-3 h-3 text-rose-600" />}
        <span>{isPos ? `+${val}%` : `${val}%`}</span>
      </span>
    );
  };

  return (
    <div className="space-y-6">
      {/* Top Header & Overview */}
      <div className="glass-card rounded-2xl p-5 border border-slate-200 shadow-sm flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-brand-50 text-brand-700 flex items-center justify-center font-bold">
            <TrendingUp className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-extrabold text-slate-900 flex items-center gap-2">
              Multi-Year Financial Trend & CAGR Analytics
            </h3>
            <p className="text-xs text-slate-500 font-medium">
              3-Year historical financial trajectory, YoY growth rates, compound CAGR & margin expansion
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 bg-slate-100 p-1 rounded-xl">
          <button
            onClick={() => setActiveTab('income')}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
              activeTab === 'income' ? 'bg-white text-brand-700 shadow-sm' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Income Trend Table
          </button>
          <button
            onClick={() => setActiveTab('balance')}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
              activeTab === 'balance' ? 'bg-white text-brand-700 shadow-sm' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Balance Sheet Trend
          </button>
        </div>
      </div>

      {/* KPI Cards: CAGR & YoY Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="glass-card rounded-2xl p-4 border border-brand-200 bg-brand-50/30 flex items-center justify-between">
          <div>
            <p className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">3-Yr Revenue CAGR</p>
            <p className="text-2xl font-black text-brand-900 mt-1">{cagr.revenue_cagr}%</p>
          </div>
          <div className="w-10 h-10 rounded-xl bg-brand-100 text-brand-700 flex items-center justify-center font-bold">
            <TrendingUp className="w-5 h-5" />
          </div>
        </div>

        <div className="glass-card rounded-2xl p-4 border border-emerald-200 bg-emerald-50/30 flex items-center justify-between">
          <div>
            <p className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">3-Yr Net Income CAGR</p>
            <p className="text-2xl font-black text-emerald-950 mt-1">{cagr.net_income_cagr}%</p>
          </div>
          <div className="w-10 h-10 rounded-xl bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold">
            <Award className="w-5 h-5" />
          </div>
        </div>

        <div className="glass-card rounded-2xl p-4 border border-slate-200 flex items-center justify-between">
          <div>
            <p className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Latest YoY Revenue</p>
            <p className="text-2xl font-black text-slate-900 mt-1">+{yoy.revenue_yoy}%</p>
          </div>
          <div className="w-10 h-10 rounded-xl bg-slate-100 text-slate-700 flex items-center justify-center font-bold">
            <Calendar className="w-5 h-5" />
          </div>
        </div>

        <div className="glass-card rounded-2xl p-4 border border-slate-200 flex items-center justify-between">
          <div>
            <p className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Latest YoY Net Profit</p>
            <p className="text-2xl font-black text-slate-900 mt-1">+{yoy.net_income_yoy}%</p>
          </div>
          <div className="w-10 h-10 rounded-xl bg-slate-100 text-slate-700 flex items-center justify-center font-bold">
            <BarChart2 className="w-5 h-5" />
          </div>
        </div>
      </div>

      {/* Graphical Margin & Revenue Expansion Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Visual Revenue Progression Bar Chart */}
        <div className="glass-card rounded-2xl p-5 border border-slate-200 space-y-4 shadow-sm">
          <div className="flex justify-between items-center border-b pb-3 border-slate-100">
            <h4 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <BarChart2 className="w-4 h-4 text-brand-600" />
              3-Year Revenue Progression (FY23 - FY25)
            </h4>
            <span className="text-[10px] font-extrabold text-slate-400 bg-slate-100 px-2 py-0.5 rounded-full">
              ORGANIC GROWTH
            </span>
          </div>

          <div className="space-y-4">
            {incComp.slice(0, 1).map((r: any) => {
              const maxVal = Math.max(r.fy2023, r.fy2024, r.fy2025, 1);
              return (
                <div key="rev-bars" className="grid grid-cols-3 gap-3 pt-2">
                  <div className="p-3 bg-slate-50 rounded-xl border text-center space-y-2">
                    <p className="text-[11px] font-bold text-slate-400">FY2023</p>
                    <p className="text-sm font-black text-slate-800">{formatDollar(r.fy2023)}</p>
                    <div className="w-full h-16 bg-slate-200 rounded-lg relative overflow-hidden flex items-end">
                      <div
                        className="w-full bg-slate-400 rounded-b-lg transition-all duration-700"
                        style={{ height: `${(r.fy2023 / maxVal) * 100}%` }}
                      ></div>
                    </div>
                  </div>

                  <div className="p-3 bg-slate-50 rounded-xl border text-center space-y-2">
                    <p className="text-[11px] font-bold text-slate-400">FY2024</p>
                    <p className="text-sm font-black text-slate-800">{formatDollar(r.fy2024)}</p>
                    <div className="w-full h-16 bg-slate-200 rounded-lg relative overflow-hidden flex items-end">
                      <div
                        className="w-full bg-brand-500 rounded-b-lg transition-all duration-700"
                        style={{ height: `${(r.fy2024 / maxVal) * 100}%` }}
                      ></div>
                    </div>
                  </div>

                  <div className="p-3 bg-brand-50/70 rounded-xl border border-brand-200 text-center space-y-2">
                    <p className="text-[11px] font-bold text-brand-600">FY2025 (Current)</p>
                    <p className="text-sm font-black text-brand-950">{formatDollar(r.fy2025)}</p>
                    <div className="w-full h-16 bg-brand-100 rounded-lg relative overflow-hidden flex items-end">
                      <div
                        className="w-full bg-brand-600 rounded-b-lg transition-all duration-700"
                        style={{ height: `${(r.fy2025 / maxVal) * 100}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Margin Trajectory Chart */}
        <div className="glass-card rounded-2xl p-5 border border-slate-200 space-y-4 shadow-sm">
          <div className="flex justify-between items-center border-b pb-3 border-slate-100">
            <h4 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-emerald-600" />
              Margin & ROE Evolution Over Time
            </h4>
            <span className="text-[10px] font-extrabold text-slate-400 bg-slate-100 px-2 py-0.5 rounded-full">
              PROFITABILITY DYNAMICS
            </span>
          </div>

          <div className="space-y-3">
            {marginTrends.map((m: any, idx: number) => (
              <div key={idx} className="p-3 bg-slate-50/80 rounded-xl border border-slate-100 flex items-center justify-between">
                <div>
                  <span className="text-xs font-black text-slate-900">{m.period}</span>
                  <p className="text-[11px] text-slate-500 font-medium">Gross Margin: {m.gross_margin}%</p>
                </div>
                <div className="flex items-center gap-3 text-right">
                  <div>
                    <p className="text-[10px] font-bold text-slate-400">Current Ratio (CRT)</p>
                    <p className="text-xs font-extrabold text-cyan-700">
                      {m.crt !== null && m.crt !== undefined ? m.crt : (m.current_ratio !== null && m.current_ratio !== undefined ? m.current_ratio : 'N/A')}
                    </p>
                  </div>
                  <div>
                    <p className="text-[10px] font-bold text-slate-400">Net Profit Margin</p>
                    <p className="text-xs font-extrabold text-emerald-700">{m.net_margin}%</p>
                  </div>
                  <div>
                    <p className="text-[10px] font-bold text-slate-400">Return on Equity</p>
                    <p className="text-xs font-extrabold text-brand-700">{m.roe}%</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Side-by-Side Comparative Table */}
      <div className="glass-card rounded-2xl border border-slate-200 overflow-hidden shadow-sm">
        <div className="p-4 bg-slate-50/80 border-b border-slate-200 flex justify-between items-center">
          <h4 className="text-xs font-extrabold text-slate-800 uppercase tracking-wider flex items-center gap-2">
            <Table className="w-4 h-4 text-slate-500" />
            Side-by-Side 3-Year Comparative Financial Statements
          </h4>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-slate-100/60 border-b border-slate-200 text-slate-400 font-bold uppercase tracking-wider">
                <th className="py-3 px-4">Financial Metric</th>
                <th className="py-3 px-4 text-right">FY2023</th>
                <th className="py-3 px-4 text-right">FY2024</th>
                <th className="py-3 px-4 text-right">FY2025 (Current)</th>
                <th className="py-3 px-4 text-center">Latest YoY Growth</th>
                <th className="py-3 px-4 text-center">3-Year CAGR</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium text-slate-700">
              {(activeTab === 'income' ? incComp : bsComp).map((row: any, i: number) => (
                <tr key={i} className="hover:bg-slate-50/80 transition-colors">
                  <td className="py-3.5 px-4 font-bold text-slate-900">{row.metric}</td>
                  <td className="py-3.5 px-4 text-right font-mono text-slate-600">
                    {row.metric.includes('Current Ratio') ? (row.fy2023 !== null && row.fy2023 !== undefined ? row.fy2023 : 'N/A') : formatDollar(row.fy2023)}
                  </td>
                  <td className="py-3.5 px-4 text-right font-mono text-slate-600">
                    {row.metric.includes('Current Ratio') ? (row.fy2024 !== null && row.fy2024 !== undefined ? row.fy2024 : 'N/A') : formatDollar(row.fy2024)}
                  </td>
                  <td className="py-3.5 px-4 text-right font-mono font-bold text-slate-900">
                    {row.metric.includes('Current Ratio') ? (row.fy2025 !== null && row.fy2025 !== undefined ? row.fy2025 : 'N/A') : formatDollar(row.fy2025)}
                  </td>
                  <td className="py-3.5 px-4 text-center">{getGrowthBadge(row.yoy_24_25)}</td>
                  <td className="py-3.5 px-4 text-center font-bold text-brand-700 bg-brand-50/30">
                    {row.cagr_3yr}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* AI Multi-Year Executive Commentary Banner */}
      <div className="glass-card rounded-2xl p-5 border border-brand-200 bg-brand-50/40 space-y-2 shadow-sm">
        <div className="flex items-center gap-2 text-brand-700 font-bold text-xs">
          <Sparkles className="w-4 h-4 text-brand-600" />
          <span>AI Multi-Year Strategic Trajectory Commentary</span>
        </div>
        <p className="text-xs text-slate-800 leading-relaxed font-medium">
          {multiPeriod.ai_trajectory}
        </p>
      </div>

      {/* 3-YEAR PREDICTIVE AI FORECASTING SECTION */}
      {multiPeriod.three_year_forecast && (
        <div className="glass-card rounded-2xl p-5 border border-cyan-200 bg-gradient-to-r from-cyan-50/30 via-white to-brand-50/20 space-y-4 shadow-sm">
          <div className="flex justify-between items-center border-b pb-3 border-cyan-100">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-cyan-600" />
              <h4 className="text-sm font-bold text-slate-900">3-Year AI Predictive Financial Forecast (Y+1, Y+2, Y+3)</h4>
            </div>
            <span className="text-[10px] font-extrabold text-cyan-700 bg-cyan-50 px-2.5 py-0.5 rounded-full border border-cyan-200">
              GROWTH BASELINE: {multiPeriod.three_year_forecast.growth_rate_used_pct}% p.a.
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {multiPeriod.three_year_forecast.projections?.map((proj: any, idx: number) => (
              <div key={idx} className="p-4 bg-white rounded-2xl border border-slate-200 space-y-2.5 shadow-xs">
                <div className="flex justify-between items-center">
                  <span className="text-xs font-black text-slate-900">{proj.period}</span>
                  <span className="text-[9px] font-bold text-cyan-700 bg-cyan-50 px-2 py-0.5 rounded-md border border-cyan-100">
                    {proj.confidence_range}
                  </span>
                </div>
                <div className="space-y-1.5 pt-1">
                  <div className="flex justify-between text-xs">
                    <span className="text-slate-500 font-medium">Projected Revenue:</span>
                    <span className="font-extrabold text-slate-900">{formatDollar(proj.projected_revenue)}</span>
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="text-slate-500 font-medium">Projected Net Income:</span>
                    <span className="font-extrabold text-emerald-700">{formatDollar(proj.projected_net_income)}</span>
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="text-slate-500 font-medium">Projected Total Assets:</span>
                    <span className="font-bold text-slate-700">{formatDollar(proj.projected_assets)}</span>
                  </div>
                  <div className="flex justify-between text-xs border-t border-slate-100 pt-1">
                    <span className="text-slate-500 font-medium">Projected Current Ratio (CRT):</span>
                    <span className="font-extrabold text-cyan-700">
                      {proj.projected_current_ratio !== null && proj.projected_current_ratio !== undefined ? proj.projected_current_ratio : (proj.crt !== null && proj.crt !== undefined ? proj.crt : 'N/A')}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
