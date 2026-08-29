'use client';
import React from 'react';
import { 
  FileCheck, 
  ShieldCheck, 
  AlertTriangle, 
  ShieldAlert, 
  BarChart3, 
  CheckCircle2, 
  FileText, 
  Award, 
  Activity,
  Zap,
  Layers,
  Sparkles
} from 'lucide-react';

import { formatCurrency, getCurrencySymbol } from '@/lib/currency';

interface AuditorWorkingPapersProps {
  auditReport: any;
  companyName?: string;
  currency?: string;
}

export default function AuditorWorkingPapers({ auditReport, companyName = "Enterprise Target", currency = "USD" }: AuditorWorkingPapersProps) {
  if (!auditReport) return null;

  const { auditor_opinion, benford_analysis, sloan_accruals, round_number_audit, working_papers } = auditReport;

  const opinionType = auditor_opinion?.opinion_type || "UNQUALIFIED_OPINION";

  const getOpinionStyle = (type: string) => {
    if (type === "UNQUALIFIED_OPINION") {
      return {
        bg: "bg-emerald-50 text-emerald-800 border-emerald-200",
        badgeBg: "bg-emerald-600 text-white",
        icon: ShieldCheck,
        label: "UNQUALIFIED OPINION (CLEAN)"
      };
    }
    if (type === "QUALIFIED_OPINION") {
      return {
        bg: "bg-amber-50 text-amber-800 border-amber-200",
        badgeBg: "bg-amber-600 text-white",
        icon: AlertTriangle,
        label: "QUALIFIED OPINION (EXPLANATIONS REQUIRED)"
      };
    }
    return {
      bg: "bg-rose-50 text-rose-800 border-rose-200",
      badgeBg: "bg-rose-600 text-white",
      icon: ShieldAlert,
      label: "ADVERSE AUDITOR OPINION (MISSTATEMENT RISK)"
    };
  };

  const style = getOpinionStyle(opinionType);
  const OpinionIcon = style.icon;

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="glass-card rounded-2xl p-5 border border-slate-200 shadow-sm flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-slate-900 text-white flex items-center justify-center font-bold">
            <FileCheck className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-base font-extrabold text-slate-900">
                Independent Auditor's Report & Working Papers
              </h3>
              <span className="text-[10px] font-extrabold text-slate-700 bg-slate-100 border border-slate-300 px-2 py-0.5 rounded-full uppercase">
                FORMAL FINANCIAL AUDIT
              </span>
            </div>
            <p className="text-xs text-slate-500 font-medium">
              Forensic accounting compliance, Benford's Law testing, and Sloan accrual realization audit
            </p>
          </div>
        </div>
      </div>

      {/* INDEPENDENT AUDITOR'S OPINION CERTIFICATE */}
      <div className={`glass-card rounded-2xl p-6 border ${style.bg} space-y-4 shadow-sm relative overflow-hidden`}>
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-3 border-b pb-4 border-slate-200/60">
          <div className="flex items-center gap-2.5">
            <div className={`px-3 py-1 rounded-xl text-xs font-black uppercase tracking-wider ${style.badgeBg}`}>
              {style.label}
            </div>
            <span className="text-xs font-bold text-slate-500">Official Audit Opinion • {companyName}</span>
          </div>

          <span className="text-xs font-mono font-bold text-slate-600 bg-white/80 px-3 py-1 rounded-lg border border-slate-200">
            AUDIT REF: {auditor_opinion?.audit_date || "2026-08-16"}
          </span>
        </div>

        <div className="space-y-2">
          <h4 className="text-lg font-black text-slate-900">{auditor_opinion?.title}</h4>
          <p className="text-xs text-slate-700 font-medium leading-relaxed bg-white/70 p-4 rounded-xl border border-slate-200/80">
            "{auditor_opinion?.summary}"
          </p>
        </div>

        <div className="flex justify-between items-center text-xs font-bold text-slate-600 pt-1">
          <div className="flex items-center gap-1.5">
            <Award className="w-4 h-4 text-brand-600" />
            <span>Auditor Signature: <strong>{auditor_opinion?.auditor_signature}</strong></span>
          </div>
          <span className="text-[10px] text-slate-400 uppercase tracking-wider">Automated Forensic Audit Pass</span>
        </div>
      </div>

      {/* BENFORD'S LAW DIGIT FREQUENCY ANALYSIS */}
      <div className="glass-card rounded-2xl p-6 border border-slate-200 space-y-5 shadow-sm">
        <div className="flex justify-between items-start">
          <div>
            <div className="flex items-center gap-2">
              <BarChart3 className="w-4 h-4 text-brand-600" />
              <span className="text-[10px] font-extrabold text-slate-400 uppercase tracking-wider">Forensic Benford's Law Test</span>
            </div>
            <h4 className="text-base font-extrabold text-slate-900 mt-0.5">First-Digit Logarithmic Frequency Conformity</h4>
          </div>
          <div className="text-right">
            <span className={`inline-block px-3 py-1 rounded-xl text-xs font-extrabold border ${
              benford_analysis?.conformity_status?.includes("Close") 
                ? "bg-emerald-50 text-emerald-700 border-emerald-200"
                : "bg-amber-50 text-amber-700 border-amber-200"
            }`}>
              {benford_analysis?.conformity_status}
            </span>
            <span className="block text-[10px] text-slate-400 mt-1 font-mono">
              Mean Absolute Deviation (MAD): {benford_analysis?.mean_absolute_deviation}
            </span>
          </div>
        </div>

        {/* Visual Benford Comparison Bars */}
        <div className="space-y-2">
          <div className="flex justify-between text-[10px] font-bold text-slate-400 uppercase tracking-wider">
            <span>Digit (1-9)</span>
            <span>Actual % vs Benford Ideal Curve %</span>
          </div>

          <div className="grid grid-cols-9 gap-2 text-center">
            {benford_analysis?.digit_chart_data?.map((d: any) => (
              <div key={d.digit} className="p-2 bg-slate-50 rounded-xl border border-slate-100 space-y-1">
                <span className="text-xs font-black text-slate-900 block">{d.digit}</span>
                <div className="h-16 flex items-end justify-center gap-1 bg-slate-100 rounded-lg p-1">
                  <div 
                    className="w-2.5 bg-brand-600 rounded-t-sm transition-all" 
                    style={{ height: `${Math.min(d.actual_pct * 2.5, 100)}%` }}
                    title={`Actual: ${d.actual_pct}%`}
                  ></div>
                  <div 
                    className="w-2.5 bg-slate-300 rounded-t-sm" 
                    style={{ height: `${Math.min(d.benford_ideal_pct * 2.5, 100)}%` }}
                    title={`Benford Ideal: ${d.benford_ideal_pct}%`}
                  ></div>
                </div>
                <span className="text-[9px] font-extrabold text-slate-700 block">{d.actual_pct}%</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* SLOAN ACCRUALS & ROUND NUMBER AUDIT GRID */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="glass-card rounded-2xl p-5 border border-slate-200 space-y-3 shadow-sm">
          <div className="flex justify-between items-center border-b pb-2 border-slate-100">
            <span className="text-[10px] font-extrabold text-slate-400 uppercase tracking-wider">Sloan Accruals Quality</span>
            <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
              sloan_accruals?.status === "PASS" ? "bg-emerald-50 text-emerald-700" : "bg-amber-50 text-amber-700"
            }`}>
              {sloan_accruals?.status}
            </span>
          </div>

          <div className="flex items-baseline justify-between">
            <div>
              <p className="text-xs text-slate-500 font-medium">Sloan Accruals Ratio</p>
              <p className="text-2xl font-black text-slate-900">{sloan_accruals?.sloan_ratio}</p>
            </div>
            <div className="text-right">
              <p className="text-xs text-slate-500 font-medium">Accruals Amount</p>
              <p className="text-sm font-extrabold text-slate-800">{formatCurrency(sloan_accruals?.accruals_amount, currency)}</p>
            </div>
          </div>

          <p className="text-xs text-slate-600 font-medium bg-slate-50 p-2.5 rounded-xl border border-slate-100">
            {sloan_accruals?.quality_label}
          </p>
        </div>

        <div className="glass-card rounded-2xl p-5 border border-slate-200 space-y-3 shadow-sm">
          <div className="flex justify-between items-center border-b pb-2 border-slate-100">
            <span className="text-[10px] font-extrabold text-slate-400 uppercase tracking-wider">Round Number Transaction Audit</span>
            <span className="text-[10px] font-bold text-slate-700 bg-slate-100 px-2 py-0.5 rounded-full">
              {round_number_audit?.risk_level} ANOMALY RISK
            </span>
          </div>

          <div className="flex items-baseline justify-between">
            <div>
              <p className="text-xs text-slate-500 font-medium">Round Entries Proportion</p>
              <p className="text-2xl font-black text-slate-900">{round_number_audit?.round_entries_pct}%</p>
            </div>
            <div className="text-right">
              <p className="text-xs text-slate-500 font-medium">Audit Threshold</p>
              <p className="text-sm font-extrabold text-slate-600">&lt; 20.0%</p>
            </div>
          </div>

          <p className="text-xs text-slate-600 font-medium bg-slate-50 p-2.5 rounded-xl border border-slate-100">
            Transactions audited for manual journal entry overrides and artificial number smoothing.
          </p>
        </div>
      </div>

      {/* AUDITOR WORKING PAPERS (WP) TRAIL */}
      <div className="glass-card rounded-2xl border border-slate-200 overflow-hidden shadow-sm">
        <div className="p-4 bg-slate-50/80 border-b border-slate-200 flex justify-between items-center">
          <h4 className="text-xs font-extrabold text-slate-800 uppercase tracking-wider flex items-center gap-2">
            <Layers className="w-4 h-4 text-slate-500" />
            Auditor Working Papers (WP) Trail & Checklist
          </h4>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-slate-100/60 border-b border-slate-200 text-slate-400 font-bold uppercase tracking-wider">
                <th className="py-3 px-4">WP Ref</th>
                <th className="py-3 px-4">Audit Procedure</th>
                <th className="py-3 px-4">Verification Result</th>
                <th className="py-3 px-4 text-center">Status</th>
                <th className="py-3 px-4">Auditor Notes</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium text-slate-700">
              {working_papers?.map((wp: any) => (
                <tr key={wp.wp_ref} className="hover:bg-slate-50 transition-colors">
                  <td className="py-3.5 px-4 font-mono font-bold text-brand-700 bg-brand-50/30">{wp.wp_ref}</td>
                  <td className="py-3.5 px-4 font-bold text-slate-900">{wp.procedure}</td>
                  <td className="py-3.5 px-4 font-semibold text-slate-800">{wp.result}</td>
                  <td className="py-3.5 px-4 text-center">
                    <span className={`px-2.5 py-1 rounded-full text-[10px] font-extrabold ${
                      wp.status === "PASS" ? "bg-emerald-50 text-emerald-700" : "bg-amber-50 text-amber-700"
                    }`}>
                      {wp.status}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 text-slate-500 text-[11px]">{wp.notes}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
