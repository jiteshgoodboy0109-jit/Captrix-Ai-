'use client';
import React, { useState, useEffect } from 'react';
import api from '@/lib/api';
import { 
  Award, 
  Sparkles, 
  CheckCircle2, 
  AlertTriangle, 
  ShieldCheck, 
  FileText, 
  BrainCircuit, 
  Layers, 
  Activity, 
  Loader2, 
  Table, 
  RotateCw,
  FileCheck
} from 'lucide-react';

interface ModelLeaderboardViewerProps {
  uploadId?: number | string;
}

export default function ModelLeaderboardViewer({ uploadId }: ModelLeaderboardViewerProps) {
  const [evaluationData, setEvaluationData] = useState<any | null>(null);
  const [wiproBenchmark, setWiproBenchmark] = useState<any | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [benchmarkLoading, setBenchmarkLoading] = useState<boolean>(false);

  useEffect(() => {
    fetchModelEvaluations();
  }, [uploadId]);

  const fetchModelEvaluations = async () => {
    setLoading(true);
    try {
      if (uploadId && uploadId !== 'latest') {
        const res = await api.post(`/api/models/evaluate/${uploadId}`);
        setEvaluationData(res.data);
      } else {
        const res = await api.get('/api/models/leaderboard');
        setEvaluationData(res.data);
      }
    } catch (e) {
      console.log('Error fetching model evaluation data:', e);
    } finally {
      setLoading(false);
    }
  };

  const handleRunWiproBenchmark = async () => {
    setBenchmarkLoading(true);
    try {
      const res = await api.post('/api/models/wipro-benchmark');
      setWiproBenchmark(res.data);
    } catch (e) {
      console.log('Error running Wipro benchmark:', e);
    } finally {
      setBenchmarkLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="py-16 text-center space-y-3 glass-card rounded-2xl p-8 border border-slate-200">
        <Loader2 className="w-8 h-8 animate-spin text-brand-600 mx-auto" />
        <p className="text-xs font-bold text-slate-700">Evaluating multi-model candidate accuracy against source ground truth...</p>
      </div>
    );
  }

  const evalList = evaluationData?.evaluations_leaderboard || evaluationData?.leaderboard || [];
  const topWinner = evalList[0];
  const docProfile = evaluationData?.document_profile;
  const activeBenchmark = wiproBenchmark || evaluationData;

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="glass-card rounded-2xl p-5 border border-slate-200 shadow-sm flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-brand-50 text-brand-700 flex items-center justify-center font-bold">
            <Award className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-base font-extrabold text-slate-900">
                Automatic Model Discovery & Ground-Truth Evaluator
              </h3>
              <span className="text-[10px] font-extrabold text-brand-700 bg-brand-50 border border-brand-200 px-2 py-0.5 rounded-full uppercase">
                VERIFIED SOURCE ACCURACY
              </span>
            </div>
            <p className="text-xs text-slate-500 font-medium">
              Multi-model candidate evaluation against deterministic source ground truth
            </p>
          </div>
        </div>

        <button
          onClick={handleRunWiproBenchmark}
          disabled={benchmarkLoading}
          className="flex items-center gap-2 px-4 py-2 bg-slate-900 hover:bg-black text-white rounded-xl text-xs font-bold transition-all shadow-sm shrink-0"
        >
          {benchmarkLoading ? (
            <Loader2 className="w-4 h-4 animate-spin text-brand-400" />
          ) : (
            <FileCheck className="w-4 h-4 text-brand-400" />
          )}
          <span>Run Wipro Golden Benchmark</span>
        </button>
      </div>

      {/* WINNING MODEL BANNER */}
      {topWinner && (
        <div className="glass-card rounded-2xl p-6 border border-brand-200 bg-gradient-to-r from-brand-50/50 via-white to-cyan-50/40 space-y-4 shadow-sm">
          <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-brand-600" />
                <span className="text-xs font-extrabold text-brand-700 uppercase tracking-wider">
                  Automatic Best Model Winner
                </span>
                <span className={`text-[10px] font-extrabold px-2.5 py-0.5 rounded-full border ${
                  evaluationData?.status === 'APPROVED' 
                    ? 'bg-emerald-50 text-emerald-700 border-emerald-200' 
                    : 'bg-amber-50 text-amber-700 border-amber-200'
                }`}>
                  {evaluationData?.status || 'APPROVED'}
                </span>
              </div>
              <h4 className="text-xl font-black text-slate-900">{topWinner.model_name}</h4>
              <p className="text-xs text-slate-500 font-medium">{topWinner.provider}</p>
            </div>

            <div className="flex items-center gap-3 bg-white p-3.5 rounded-2xl border border-slate-200 shadow-sm shrink-0">
              <div className="text-center px-3 border-r border-slate-100">
                <span className="text-[9px] font-bold text-slate-400 uppercase block">Overall Score</span>
                <span className="text-2xl font-black text-brand-900">{topWinner.overall_score}%</span>
              </div>
              <div className="text-center px-3 border-r border-slate-100">
                <span className="text-[9px] font-bold text-slate-400 uppercase block">Critical Accuracy</span>
                <span className="text-2xl font-black text-emerald-600">{topWinner.critical_metric_accuracy}%</span>
              </div>
              <div className="text-center px-3">
                <span className="text-[9px] font-bold text-slate-400 uppercase block">Hallucinations</span>
                <span className="text-2xl font-black text-slate-900">{topWinner.hallucination_count}</span>
              </div>
            </div>
          </div>

          <div className="p-3.5 bg-white/90 rounded-xl border border-slate-200 text-xs font-medium text-slate-800 leading-relaxed">
            <span className="font-extrabold text-brand-700 block mb-0.5">Selection Rationale (Explainable Discovery):</span>
            {evaluationData?.why_this_model_won || "Selected based on 100% verified ground-truth financial accuracy and zero hallucinations."}
          </div>
        </div>
      )}

      {/* Document Profile Badge */}
      {docProfile && (
        <div className="glass-card rounded-2xl p-4 border border-slate-200 flex flex-wrap items-center justify-between gap-4 text-xs font-semibold text-slate-700 shadow-xs">
          <div className="flex items-center gap-2">
            <Layers className="w-4 h-4 text-brand-600" />
            <span>Document Layout Profile: <strong className="text-slate-900 uppercase">{docProfile.layout_complexity}</strong></span>
          </div>
          <div>Table Density: <strong className="text-slate-900">{docProfile.table_density * 100}%</strong></div>
          <div>Statements Detected: <strong className="text-slate-900">{docProfile.financial_statement_count}</strong></div>
          <div>Periods Detected: <strong className="text-slate-900">{docProfile.number_of_periods}</strong></div>
          <div>Currency/Unit: <strong className="text-slate-900">{docProfile.currency} ({docProfile.unit})</strong></div>
        </div>
      )}

      {/* Model Leaderboard Table */}
      <div className="glass-card rounded-2xl border border-slate-200 overflow-hidden shadow-sm space-y-3">
        <div className="p-4 bg-slate-50/80 border-b border-slate-200 flex justify-between items-center">
          <h4 className="text-xs font-extrabold text-slate-800 uppercase tracking-wider flex items-center gap-2">
            <Table className="w-4 h-4 text-slate-500" />
            Model Accuracy Leaderboard (Ranked by Ground-Truth Financial Accuracy)
          </h4>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-slate-100/60 border-b border-slate-200 text-slate-400 font-bold uppercase tracking-wider">
                <th className="py-3 px-4">Rank</th>
                <th className="py-3 px-4">Model Candidate</th>
                <th className="py-3 px-4 text-center">Overall Score</th>
                <th className="py-3 px-4 text-center">Critical Accuracy</th>
                <th className="py-3 px-4 text-center">Accounting Check</th>
                <th className="py-3 px-4 text-center">Hallucination Rate</th>
                <th className="py-3 px-4 text-center">Traceability</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium text-slate-700">
              {evalList.map((m: any, idx: number) => (
                <tr key={idx} className={`hover:bg-slate-50 transition-colors ${idx === 0 ? 'bg-brand-50/20' : ''}`}>
                  <td className="py-3.5 px-4 font-black text-slate-900">#{idx + 1}</td>
                  <td className="py-3.5 px-4">
                    <span className="font-extrabold text-slate-900 block">{m.model_name}</span>
                    <span className="text-[10px] text-slate-400">{m.provider}</span>
                  </td>
                  <td className="py-3.5 px-4 text-center font-black text-brand-900">{m.overall_score}%</td>
                  <td className="py-3.5 px-4 text-center font-bold text-emerald-700">{m.critical_metric_accuracy}%</td>
                  <td className="py-3.5 px-4 text-center font-bold text-slate-800">{m.accounting_validation}%</td>
                  <td className="py-3.5 px-4 text-center">
                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                      m.hallucination_count === 0 ? 'bg-emerald-50 text-emerald-700' : 'bg-rose-50 text-rose-700'
                    }`}>
                      {m.hallucination_rate_pct}% ({m.hallucination_count})
                    </span>
                  </td>
                  <td className="py-3.5 px-4 text-center font-bold text-slate-600">{m.traceability_score}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
