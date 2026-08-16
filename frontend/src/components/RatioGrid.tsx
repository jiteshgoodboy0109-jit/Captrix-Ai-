'use client';
import React, { useState } from 'react';
import { 
  Percent, 
  Info, 
  ShieldCheck, 
  AlertTriangle, 
  XCircle, 
  BarChart3, 
  PieChart as PieIcon, 
  TrendingUp, 
  Activity, 
  Layers, 
  Target, 
  Sparkles,
  ChevronRight,
  Gauge
} from 'lucide-react';

interface RatioGridProps {
  ratios: any;
}

export default function RatioGrid({ ratios }: RatioGridProps) {
  const [activeCategory, setActiveCategory] = useState<string>('all');
  const [viewMode, setViewMode] = useState<'hybrid' | 'charts' | 'cards'>('hybrid');
  const [selectedRatio, setSelectedRatio] = useState<any | null>(null);

  if (!ratios) return null;

  const categories = [
    { key: 'all', label: 'All Categories' },
    { key: 'profitability', label: 'Profitability' },
    { key: 'liquidity', label: 'Liquidity & Cash' },
    { key: 'solvency', label: 'Solvency & Debt' },
    { key: 'efficiency', label: 'Asset Efficiency' }
  ];

  const getStatusBadge = (status: string) => {
    if (status === 'HEALTHY') {
      return { 
        label: 'HEALTHY', 
        bg: 'bg-emerald-50 text-emerald-700 border-emerald-200', 
        barBg: 'bg-gradient-to-r from-blue-600 via-cyan-500 to-emerald-400 shadow-[0_0_12px_rgba(16,185,129,0.3)]', 
        icon: ShieldCheck, 
        color: '#10b981' 
      };
    } else if (status === 'WARNING') {
      return { 
        label: 'WARNING', 
        bg: 'bg-amber-50 text-amber-700 border-amber-200', 
        barBg: 'bg-gradient-to-r from-amber-500 to-orange-400 shadow-[0_0_12px_rgba(245,158,11,0.3)]', 
        icon: AlertTriangle, 
        color: '#f59e0b' 
      };
    } else if (status === 'NOT_CALCULABLE' || status === 'N/A' || status === 'DATA_MISSING') {
      return {
        label: 'DATA MISSING',
        bg: 'bg-slate-100 text-slate-600 border-slate-200',
        barBg: 'bg-slate-300',
        icon: Info,
        color: '#64748b'
      };
    } else {
      return { 
        label: 'CRITICAL', 
        bg: 'bg-rose-50 text-rose-700 border-rose-200', 
        barBg: 'bg-gradient-to-r from-rose-600 to-pink-500 shadow-[0_0_12px_rgba(244,63,94,0.3)]', 
        icon: XCircle, 
        color: '#f43f5e' 
      };
    }
  };

  const flattenRatios = () => {
    let list: any[] = [];
    Object.keys(ratios).forEach((catKey) => {
      if (activeCategory === 'all' || activeCategory === catKey) {
        const catObj = ratios[catKey];
        if (catObj && typeof catObj === 'object') {
          Object.keys(catObj).forEach((rKey) => {
            list.push({ ...catObj[rKey], category: catKey, key: rKey });
          });
        }
      }
    });
    return list;
  };

  const ratioList = flattenRatios();

  // Helper to compute visual progress bar percentage and human-readable text
  const getRatioBenchmarkMetrics = (val: number, benchmarkStr: string, isCalculable: boolean = true, status: string = '') => {
    if (!isCalculable || status === 'NOT_CALCULABLE' || status === 'N/A') {
      return { text: 'Data Missing', widthPct: 0 };
    }
    
    if (val === null || val === undefined || isNaN(val)) {
      return { text: 'Data Missing', widthPct: 0 };
    }

    if (!benchmarkStr) {
      if (val <= 0) return { text: '0% of target', widthPct: 4 };
      return { text: '100% of target', widthPct: 100 };
    }

    // Check for range like "15% - 30%" or "4.0 - 8.0x"
    const rangeMatch = benchmarkStr.match(/([\d.]+)\s*%\s*-\s*([\d.]+)\s*%/i) || benchmarkStr.match(/([\d.]+)\s*-\s*([\d.]+)/);
    if (rangeMatch && !benchmarkStr.includes('<') && !benchmarkStr.includes('>')) {
      const min = parseFloat(rangeMatch[1]);
      const max = parseFloat(rangeMatch[2]);
      if (val >= min && val <= max) {
        return { text: '100% of target', widthPct: 100 };
      } else if (val < min) {
        const pct = min > 0 ? (val / min) * 100 : 0;
        if (val <= 0) return { text: '0% of target', widthPct: 4 };
        return { text: `${Math.round(pct)}% of target`, widthPct: Math.min(Math.max(pct, 4), 100) };
      } else {
        const pct = val > 0 ? (max / val) * 100 : 100;
        return { text: `${Math.round(pct)}% of target`, widthPct: Math.min(Math.max(pct, 4), 100) };
      }
    }

    // Check for less than target like "< 1.5" or "< 0.6"
    if (benchmarkStr.includes('<')) {
      const targetMatch = benchmarkStr.match(/[\d.]+/);
      const target = targetMatch ? parseFloat(targetMatch[0]) : 1.5;
      if (val <= target) {
        return { text: '100% of target', widthPct: 100 };
      } else {
        const pct = target > 0 ? (target / val) * 100 : 50;
        return { text: `${Math.round(pct)}% of target`, widthPct: Math.min(Math.max(pct, 4), 100) };
      }
    }

    // Greater than target like "> 30%", "> 10%", "> 1.5", "> 5%"
    const targetMatch = benchmarkStr.match(/[\d.]+/);
    const target = targetMatch ? parseFloat(targetMatch[0]) : 10;
    if (target === 0) return { text: '100% of target', widthPct: 100 };

    if (val <= 0) {
      return { text: val < 0 ? '0% of target (Negative)' : '0% of target', widthPct: 4 };
    }

    const realPct = (val / target) * 100;
    const rounded = Math.round(realPct);
    return {
      text: `${rounded}% of target`,
      widthPct: Math.min(Math.max(realPct, 4), 100)
    };
  };

  // Prepare Chart Data Sets
  const profRatios = ratios.profitability ? Object.values(ratios.profitability) : [];
  const liqRatios = ratios.liquidity ? Object.values(ratios.liquidity) : [];
  const solvRatios = ratios.solvency ? Object.values(ratios.solvency) : [];
  const effRatios = ratios.efficiency ? Object.values(ratios.efficiency) : [];

  // Count overall health summary
  const allFlattened = flattenRatios();
  const healthyCount = allFlattened.filter((r) => r.status === 'HEALTHY').length;
  const warningCount = allFlattened.filter((r) => r.status === 'WARNING').length;
  const criticalCount = allFlattened.filter((r) => r.status === 'CRITICAL').length;
  const totalCount = allFlattened.length || 1;
  const overallHealthPct = Math.round((healthyCount / totalCount) * 100);

  return (
    <div className="space-y-6">
      {/* Header & Controls */}
      <div className="glass-card rounded-2xl p-5 border border-slate-200 shadow-sm flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-xl bg-brand-50 text-brand-700 flex items-center justify-center font-bold">
              <Percent className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-base font-extrabold text-slate-900 flex items-center gap-2">
                Financial Ratio Intelligence & Graphical Analytics
              </h3>
              <p className="text-xs text-slate-500 font-medium">
                Automated ratio engine with visual performance benchmarking & AI strategic advice
              </p>
            </div>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-3 w-full md:w-auto justify-between md:justify-end">
          {/* View Mode Toggle */}
          <div className="flex items-center gap-1 bg-slate-100 p-1 rounded-xl overflow-x-auto max-w-full scrollbar-none">
            <button
              onClick={() => setViewMode('hybrid')}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5 shrink-0 ${
                viewMode === 'hybrid' ? 'bg-white text-brand-700 shadow-sm' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <Layers className="w-3.5 h-3.5" />
              <span>Combined</span>
            </button>
            <button
              onClick={() => setViewMode('charts')}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5 shrink-0 ${
                viewMode === 'charts' ? 'bg-white text-brand-700 shadow-sm' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <BarChart3 className="w-3.5 h-3.5" />
              <span>Visual Charts</span>
            </button>
            <button
              onClick={() => setViewMode('cards')}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5 shrink-0 ${
                viewMode === 'cards' ? 'bg-white text-brand-700 shadow-sm' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <Target className="w-3.5 h-3.5" />
              <span>Ratio Cards</span>
            </button>
          </div>

          {/* Category Filter */}
          <div className="flex items-center gap-1 bg-slate-100 p-1 rounded-xl overflow-x-auto max-w-full scrollbar-none">
            {categories.map((c) => (
              <button
                key={c.key}
                onClick={() => setActiveCategory(c.key)}
                className={`px-2.5 py-1 rounded-lg text-[11px] font-bold transition-all shrink-0 ${
                  activeCategory === c.key ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-900'
                }`}
              >
                {c.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Summary KPI Banner */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Ratio Health Score */}
        <div className="glass-card rounded-2xl p-4 border border-slate-200/90 bg-white shadow-[0_4px_20px_-2px_rgba(0,0,0,0.03)] flex items-center gap-3.5 transition-all hover:border-cyan-400 hover:shadow-md">
          <div className="w-11 h-11 rounded-2xl bg-cyan-50 border border-cyan-200/60 text-cyan-700 flex items-center justify-center font-bold shadow-sm shrink-0">
            <Gauge className="w-5 h-5 text-cyan-700" />
          </div>
          <div>
            <p className="text-[10px] font-extrabold text-slate-400 uppercase tracking-widest">Ratio Health Score</p>
            <p className="text-2xl font-black text-slate-900 leading-tight">{overallHealthPct}% <span className="text-xs font-bold text-emerald-600">Healthy</span></p>
          </div>
        </div>

        {/* Card 2: Optimal Ratios */}
        <div className="glass-card rounded-2xl p-4 border border-slate-200/90 bg-white shadow-[0_4px_20px_-2px_rgba(0,0,0,0.03)] flex items-center gap-3.5 transition-all hover:border-emerald-400 hover:shadow-md">
          <div className="w-11 h-11 rounded-2xl bg-emerald-50 border border-emerald-200/60 text-emerald-700 flex items-center justify-center font-bold shadow-sm shrink-0">
            <ShieldCheck className="w-5 h-5 text-emerald-700" />
          </div>
          <div>
            <p className="text-[10px] font-extrabold text-slate-400 uppercase tracking-widest">Optimal Ratios</p>
            <p className="text-2xl font-black text-slate-900 leading-tight">{healthyCount} <span className="text-xs font-bold text-emerald-700">Metrics</span></p>
          </div>
        </div>

        {/* Card 3: Moderate Warnings */}
        <div className="glass-card rounded-2xl p-4 border border-slate-200/90 bg-white shadow-[0_4px_20px_-2px_rgba(0,0,0,0.03)] flex items-center gap-3.5 transition-all hover:border-amber-400 hover:shadow-md">
          <div className="w-11 h-11 rounded-2xl bg-amber-50 border border-amber-200/60 text-amber-700 flex items-center justify-center font-bold shadow-sm shrink-0">
            <AlertTriangle className="w-5 h-5 text-amber-700" />
          </div>
          <div>
            <p className="text-[11px] font-extrabold text-slate-400 uppercase tracking-widest">Moderate Warnings</p>
            <p className="text-2xl font-black text-slate-900 leading-tight">{warningCount} <span className="text-xs font-bold text-amber-700">Metrics</span></p>
          </div>
        </div>

        {/* Card 4: Critical Action */}
        <div className="glass-card rounded-2xl p-4 border border-slate-200/90 bg-white shadow-[0_4px_20px_-2px_rgba(0,0,0,0.03)] flex items-center gap-3.5 transition-all hover:border-rose-400 hover:shadow-md">
          <div className="w-11 h-11 rounded-2xl bg-rose-50 border border-rose-200/60 text-rose-700 flex items-center justify-center font-bold shadow-sm shrink-0">
            <XCircle className="w-5 h-5 text-rose-700" />
          </div>
          <div>
            <p className="text-[11px] font-extrabold text-slate-400 uppercase tracking-widest">Critical Action</p>
            <p className="text-2xl font-black text-slate-900 leading-tight">{criticalCount} <span className="text-xs font-bold text-rose-700">Metrics</span></p>
          </div>
        </div>
      </div>

      {/* GRAPHICAL CHARTS SECTION */}
      {(viewMode === 'hybrid' || viewMode === 'charts') && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Chart 1: Profitability Margin & Return Comparison Chart */}
            {(activeCategory === 'all' || activeCategory === 'profitability') && (
              <div className="glass-card rounded-2xl p-5 border border-slate-200 space-y-4 shadow-sm">
                <div className="flex justify-between items-center border-b pb-3 border-slate-100">
                  <div className="flex items-center gap-2">
                    <TrendingUp className="w-4 h-4 text-emerald-600" />
                    <h4 className="text-sm font-bold text-slate-900">Profitability & Return Percentages</h4>
                  </div>
                  <span className="text-[10px] font-extrabold text-slate-400 bg-slate-100 px-2 py-0.5 rounded-full">
                    VS BENCHMARK
                  </span>
                </div>

                <div className="space-y-3.5">
                  {profRatios.map((item: any, i: number) => {
                    const badge = getStatusBadge(item.status);
                    const val = typeof item.value === 'number' ? item.value : parseFloat(item.value) || 0;
                    const pct = Math.min(Math.max(val, 5), 100);
                    return (
                      <div key={i} className="space-y-1">
                        <div className="flex justify-between text-xs font-bold text-slate-800">
                          <span className="flex items-center gap-1.5">
                            <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: badge.color }}></span>
                            {item.name}
                          </span>
                          <div className="flex items-center gap-2">
                            <span className="text-slate-900 font-extrabold">{val}%</span>
                            <span className="text-[10px] text-slate-400 font-normal">(Target: {item.benchmark})</span>
                          </div>
                        </div>
                        <div className="relative w-full h-3 bg-slate-100/90 rounded-full overflow-hidden p-0.5 border border-slate-200/60">
                          <div
                            className={`h-full rounded-full transition-all duration-700 ${badge.barBg}`}
                            style={{ width: `${pct}%` }}
                          ></div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Chart 2: Liquidity & Solvency Coverage Gauges */}
            {(activeCategory === 'all' || activeCategory === 'liquidity' || activeCategory === 'solvency') && (
              <div className="glass-card rounded-2xl p-5 border border-slate-200 space-y-4 shadow-sm">
                <div className="flex justify-between items-center border-b pb-3 border-slate-100">
                  <div className="flex items-center gap-2">
                    <Activity className="w-4 h-4 text-brand-600" />
                    <h4 className="text-sm font-bold text-slate-900">Liquidity & Solvency Health Meters</h4>
                  </div>
                  <span className="text-[10px] font-extrabold text-slate-400 bg-slate-100 px-2 py-0.5 rounded-full">
                    COVERAGE MULTIPLIERS
                  </span>
                </div>

                <div className="space-y-3.5">
                  {[...liqRatios, ...solvRatios].slice(0, 5).map((item: any, i: number) => {
                    const badge = getStatusBadge(item.status);
                    const val = typeof item.value === 'number' ? item.value : parseFloat(item.value) || 0;
                    const isCalculable = item.is_calculable !== false && item.status !== 'NOT_CALCULABLE';
                    const metrics = getRatioBenchmarkMetrics(val, item.benchmark, isCalculable, item.status);

                    return (
                      <div key={i} className="space-y-1">
                        <div className="flex justify-between text-xs font-bold text-slate-800">
                          <span>{item.name}</span>
                          <div className="flex items-center gap-2">
                            <span className="font-extrabold text-slate-900">
                              {val} {item.unit || 'x'}
                            </span>
                            <span className="text-[10px] text-slate-400 font-normal">Target: {item.benchmark}</span>
                          </div>
                        </div>
                        <div className="relative w-full h-3 bg-slate-100/90 rounded-full overflow-hidden p-0.5 border border-slate-200/60">
                          <div
                            className={`h-full rounded-full transition-all duration-700 ${badge.barBg}`}
                            style={{ width: `${metrics.widthPct}%` }}
                          ></div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>

          {/* Chart 3: Asset Efficiency & Operating Cycle Bar Chart */}
          {(activeCategory === 'all' || activeCategory === 'efficiency') && (
            <div className="glass-card rounded-2xl p-5 border border-slate-200 space-y-4 shadow-sm">
              <div className="flex justify-between items-center border-b pb-3 border-slate-100">
                <div className="flex items-center gap-2">
                  <BarChart3 className="w-4 h-4 text-cyan-600" />
                  <h4 className="text-sm font-bold text-slate-900">Asset Efficiency & Operational Turnover Metrics</h4>
                </div>
                <span className="text-[10px] font-extrabold text-slate-400 bg-slate-100 px-2 py-0.5 rounded-full">
                  OPERATIONAL VELOCITY
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {effRatios.map((item: any, i: number) => {
                  const badge = getStatusBadge(item.status);
                  const val = typeof item.value === 'number' ? item.value : parseFloat(item.value) || 0;
                  return (
                    <div key={i} className="p-3.5 bg-slate-50/70 rounded-xl border border-slate-100 space-y-2">
                      <div className="flex justify-between items-center">
                        <span className="text-xs font-bold text-slate-800">{item.name}</span>
                        <span className={`text-[10px] font-extrabold px-2 py-0.5 rounded-md border ${badge.bg}`}>
                          {badge.label}
                        </span>
                      </div>
                      <div className="flex items-baseline gap-2">
                        <span className="text-xl font-extrabold text-slate-900">{val}</span>
                        <span className="text-xs font-bold text-slate-500">{item.unit || 'times'}</span>
                        <span className="text-[11px] text-slate-400 ml-auto">Benchmark: {item.benchmark}</span>
                      </div>
                      <p className="text-[11px] text-slate-500 line-clamp-1">{item.interpretation}</p>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      )}

      {/* RATIO CARDS GRID SECTION */}
      {(viewMode === 'hybrid' || viewMode === 'cards') && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <Target className="w-4 h-4 text-brand-600" />
              Detailed Financial Ratio Cards & Formula Breakdown ({ratioList.length} Ratios)
            </h4>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {ratioList.map((r, idx) => {
              const badge = getStatusBadge(r.status);
              const BadgeIcon = badge.icon;
              const numericVal = typeof r.value === 'number' ? r.value : parseFloat(r.value) || 0;
              const isCalculable = r.is_calculable !== false && r.status !== 'NOT_CALCULABLE';
              const metrics = getRatioBenchmarkMetrics(numericVal, r.benchmark, isCalculable, r.status);

              return (
                <div
                  key={idx}
                  className="glass-card glass-card-hover rounded-2xl p-5 border border-slate-200 flex flex-col justify-between shadow-sm transition-all"
                >
                  <div>
                    <div className="flex justify-between items-start mb-2">
                      <span className="text-[10px] font-extrabold text-slate-400 uppercase tracking-wider bg-slate-100 px-2 py-0.5 rounded-md">
                        {r.category}
                      </span>
                      <div className={`flex items-center gap-1 px-2 py-0.5 rounded-md border text-[10px] font-bold ${badge.bg}`}>
                        <BadgeIcon className="w-3 h-3" />
                        <span>{badge.label}</span>
                      </div>
                    </div>

                    <h4 className="text-sm font-extrabold text-slate-900 mb-1">{r.name}</h4>

                    <div className="flex items-baseline gap-2 my-2">
                      <span className="text-2xl font-black text-slate-900">{r.value}</span>
                      {r.unit && <span className="text-sm font-bold text-slate-500">{r.unit}</span>}
                      <span className="text-xs font-semibold text-slate-400 ml-auto">Target: {r.benchmark}</span>
                    </div>

                    {/* Graphical Visual Progress Scale Bar */}
                    <div className="my-3 space-y-1">
                      <div className="flex justify-between text-[10px] font-bold text-slate-400">
                        <span>Benchmark Scale</span>
                        <span>{metrics.text}</span>
                      </div>
                      <div className="w-full h-2.5 bg-slate-100/90 rounded-full overflow-hidden p-0.5 border border-slate-200/60">
                        <div
                          className={`h-full rounded-full transition-all duration-500 ${badge.barBg}`}
                          style={{ width: `${metrics.widthPct}%` }}
                        ></div>
                      </div>
                    </div>

                    <div className="p-2.5 bg-slate-50/80 rounded-xl text-[11px] font-mono text-slate-600 border border-slate-100 mb-3">
                      <span className="font-bold text-slate-400">Formula: </span>{r.formula}
                    </div>
                  </div>

                  <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
                    <p className="text-slate-600 text-[11px] line-clamp-2 leading-tight">{r.interpretation}</p>
                    <button
                      onClick={() => setSelectedRatio(r)}
                      className="flex items-center gap-1 px-2.5 py-1 text-brand-700 bg-brand-50 hover:bg-brand-100 rounded-lg shrink-0 ml-2 font-bold text-[11px] transition-all"
                    >
                      <Sparkles className="w-3 h-3 text-brand-600" />
                      <span>AI Insights</span>
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* AI Explanation & Detailed Ratio Modal */}
      {selectedRatio && (
        <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-md flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl p-6 max-w-lg w-full shadow-2xl border border-slate-200 animate-in fade-in zoom-in duration-200">
            <div className="flex justify-between items-start mb-4 border-b pb-3 border-slate-100">
              <div className="flex items-center gap-2">
                <div className="w-9 h-9 rounded-xl bg-brand-50 text-brand-700 flex items-center justify-center font-bold">
                  <Sparkles className="w-5 h-5 text-brand-600" />
                </div>
                <div>
                  <span className="text-[10px] font-extrabold text-brand-600 uppercase tracking-wider">AI Executive Insights</span>
                  <h3 className="text-base font-bold text-slate-900">{selectedRatio.name}</h3>
                </div>
              </div>
              <button
                onClick={() => setSelectedRatio(null)}
                className="w-8 h-8 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-500 font-bold flex items-center justify-center text-sm transition-all"
              >
                ✕
              </button>
            </div>

            <div className="space-y-4 text-xs text-slate-700">
              <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100 grid grid-cols-2 gap-3">
                <div>
                  <p className="text-[11px] font-bold text-slate-400">Calculated Actual</p>
                  <p className="text-lg font-black text-slate-900 mt-0.5">
                    {selectedRatio.value} {selectedRatio.unit || ''}
                  </p>
                </div>
                <div>
                  <p className="text-[11px] font-bold text-slate-400">Industry Benchmark</p>
                  <p className="text-lg font-extrabold text-brand-700 mt-0.5">{selectedRatio.benchmark}</p>
                </div>
              </div>

              <div>
                <p className="text-[11px] font-extrabold text-slate-400 uppercase tracking-wider mb-1">Calculation Formula</p>
                <p className="p-2.5 bg-slate-900 text-slate-100 rounded-xl font-mono text-[11px]">
                  {selectedRatio.formula}
                </p>
              </div>

              <div>
                <p className="text-[11px] font-extrabold text-slate-400 uppercase tracking-wider mb-1">Financial Analysis</p>
                <p className="text-slate-600 leading-relaxed bg-slate-50 p-3 rounded-xl border border-slate-100">
                  {selectedRatio.interpretation}
                </p>
              </div>

              <div>
                <p className="text-[11px] font-extrabold text-brand-600 uppercase tracking-wider mb-1 flex items-center gap-1">
                  <Sparkles className="w-3.5 h-3.5" />
                  AI Executive Recommendations
                </p>
                <p className="text-slate-800 leading-relaxed bg-brand-50/70 p-3.5 rounded-2xl border border-brand-100 font-medium">
                  {selectedRatio.ai_explanation}
                </p>
              </div>
            </div>

            <button
              onClick={() => setSelectedRatio(null)}
              className="w-full mt-6 py-3 bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs rounded-xl shadow-lg transition-all"
            >
              Close AI Analysis
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

