'use client';
import React from 'react';
import { 
  ShieldAlert, 
  ShieldCheck, 
  AlertTriangle, 
  Activity, 
  FileSearch, 
  CheckCircle2, 
  AlertCircle,
  HelpCircle,
  TrendingUp,
  Layers
} from 'lucide-react';

interface RiskIntelligenceViewerProps {
  riskData: any;
}

export default function RiskIntelligenceViewer({ riskData }: RiskIntelligenceViewerProps) {
  if (!riskData) return null;

  const { altman_z_score, beneish_m_score, risk_recommendations } = riskData;

  const zScore = altman_z_score?.score || 0;
  const zStatus = altman_z_score?.status || 'SAFE';
  const zZone = altman_z_score?.zone || 'Safe Zone';

  const mScore = beneish_m_score?.score || -2.5;
  const mStatus = beneish_m_score?.status || 'LOW_RISK';

  const getZScoreColor = (status: string) => {
    if (status === 'SAFE') return { bg: 'bg-emerald-50 text-emerald-700 border-emerald-200', barBg: 'bg-emerald-500', icon: ShieldCheck };
    if (status === 'GREY') return { bg: 'bg-amber-50 text-amber-700 border-amber-200', barBg: 'bg-amber-500', icon: AlertTriangle };
    return { bg: 'bg-rose-50 text-rose-700 border-rose-200', barBg: 'bg-rose-600', icon: ShieldAlert };
  };

  const zStyle = getZScoreColor(zStatus);
  const ZIcon = zStyle.icon;

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="glass-card rounded-2xl p-5 border border-slate-200 shadow-sm flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-brand-50 text-brand-700 flex items-center justify-center font-bold">
            <ShieldAlert className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-base font-extrabold text-slate-900">
                Solvency Risk & Forensic Audit Intelligence
              </h3>
              <span className="text-[10px] font-extrabold text-brand-700 bg-brand-50 border border-brand-200 px-2 py-0.5 rounded-full">
                ALTMAN Z-SCORE & BENEISH M-SCORE
              </span>
            </div>
            <p className="text-xs text-slate-500 font-medium">
              Quantitative bankruptcy risk modeling & forensic accounting anomaly detection
            </p>
          </div>
        </div>
      </div>

      {/* Main Grid: Altman Z-Score & Beneish M-Score */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Card 1: Altman Z-Score Bankruptcy Risk Gauge */}
        <div className="glass-card rounded-2xl p-6 border border-slate-200 space-y-5 shadow-sm">
          <div className="flex justify-between items-start">
            <div>
              <span className="text-[10px] font-extrabold text-slate-400 uppercase tracking-wider">Altman Z-Score Model</span>
              <h4 className="text-base font-extrabold text-slate-900 mt-0.5">Insolvency & Distress Prediction</h4>
            </div>
            <div className={`flex items-center gap-1.5 px-3 py-1 rounded-xl border text-xs font-bold ${zStyle.bg}`}>
              <ZIcon className="w-4 h-4" />
              <span>{zStatus}</span>
            </div>
          </div>

          <div className="flex items-baseline gap-3 my-2">
            <span className="text-4xl font-black text-slate-900">{zScore}</span>
            <span className="text-xs font-bold text-slate-500">{zZone}</span>
          </div>

          {/* Visual Gauge Scale */}
          <div className="space-y-1">
            <div className="flex justify-between text-[10px] font-bold text-slate-400">
              <span>Distress (&lt; 1.81)</span>
              <span>Grey Zone (1.81 - 2.99)</span>
              <span>Safe Zone (&gt; 2.99)</span>
            </div>
            <div className="w-full h-3 bg-slate-100 rounded-full overflow-hidden p-0.5 border border-slate-200 flex gap-1">
              <div className="h-full bg-rose-400/30 rounded-l-full w-1/3"></div>
              <div className="h-full bg-amber-400/30 w-1/3"></div>
              <div className="h-full bg-emerald-400/30 rounded-r-full w-1/3"></div>
            </div>
          </div>

          <p className="text-xs text-slate-600 font-medium leading-relaxed bg-slate-50 p-3 rounded-xl border border-slate-100">
            {altman_z_score?.description}
          </p>

          {/* Z-Score Component Metrics */}
          {altman_z_score?.components && (
            <div className="space-y-2 pt-2 border-t border-slate-100">
              <span className="text-[10px] font-extrabold text-slate-400 uppercase tracking-wider">Model Factor Breakdown</span>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 text-center text-xs">
                <div className="p-2 bg-slate-50 rounded-xl border border-slate-100">
                  <span className="text-[9px] text-slate-400 block font-bold">X1: WC / Assets</span>
                  <span className="font-extrabold text-slate-800">{altman_z_score.components.x1_working_capital_to_assets}</span>
                </div>
                <div className="p-2 bg-slate-50 rounded-xl border border-slate-100">
                  <span className="text-[9px] text-slate-400 block font-bold">X2: RE / Assets</span>
                  <span className="font-extrabold text-slate-800">{altman_z_score.components.x2_retained_earnings_to_assets}</span>
                </div>
                <div className="p-2 bg-slate-50 rounded-xl border border-slate-100">
                  <span className="text-[9px] text-slate-400 block font-bold">X3: EBIT / Assets</span>
                  <span className="font-extrabold text-slate-800">{altman_z_score.components.x3_ebit_to_assets}</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Card 2: Beneish M-Score Forensic Accounting Check */}
        <div className="glass-card rounded-2xl p-6 border border-slate-200 space-y-5 shadow-sm">
          <div className="flex justify-between items-start">
            <div>
              <span className="text-[10px] font-extrabold text-slate-400 uppercase tracking-wider">Beneish M-Score Check</span>
              <h4 className="text-base font-extrabold text-slate-900 mt-0.5">Earnings Manipulation Risk</h4>
            </div>
            <div className={`flex items-center gap-1.5 px-3 py-1 rounded-xl border text-xs font-bold ${
              mStatus === 'LOW_RISK' ? 'bg-emerald-50 text-emerald-700 border-emerald-200' : 'bg-rose-50 text-rose-700 border-rose-200'
            }`}>
              <FileSearch className="w-4 h-4" />
              <span>{beneish_m_score?.label || 'Clean Integrity'}</span>
            </div>
          </div>

          <div className="flex items-baseline gap-3 my-2">
            <span className="text-4xl font-black text-slate-900">{mScore}</span>
            <span className="text-xs font-bold text-slate-400">Threshold: &le; -1.78</span>
          </div>

          <p className="text-xs text-slate-600 font-medium leading-relaxed bg-slate-50 p-3 rounded-xl border border-slate-100">
            {beneish_m_score?.description}
          </p>

          <div className="p-3.5 bg-brand-50/50 rounded-xl border border-brand-100 flex items-center justify-between">
            <div>
              <span className="text-[10px] font-bold text-brand-700 uppercase tracking-wider block">Total Accruals to Assets (TATA)</span>
              <span className="text-xs text-slate-600">Accruals quality ratio</span>
            </div>
            <span className="text-base font-black text-brand-900">{beneish_m_score?.tata_accruals_ratio || 0.05}</span>
          </div>
        </div>
      </div>

      {/* Risk Actions & Recommendations */}
      {risk_recommendations && risk_recommendations.length > 0 && (
        <div className="glass-card rounded-2xl p-5 border border-slate-200 space-y-3 shadow-sm">
          <h4 className="text-xs font-extrabold text-slate-400 uppercase tracking-wider flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-brand-600" />
            Risk Mitigation & Financial Resilience Action Items
          </h4>

          <div className="space-y-2">
            {risk_recommendations.map((action: string, i: number) => (
              <div key={i} className="flex items-start gap-2.5 p-3 bg-slate-50 rounded-xl border border-slate-100 text-xs font-bold text-slate-800">
                <span className="w-5 h-5 rounded-full bg-brand-100 text-brand-700 flex items-center justify-center shrink-0 font-extrabold text-[10px]">
                  {i + 1}
                </span>
                <p className="leading-snug pt-0.5">{action}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
