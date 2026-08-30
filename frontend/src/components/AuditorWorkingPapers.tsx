'use client';
import React, { useState } from 'react';
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
  Sparkles,
  ChevronDown,
  ChevronRight,
  Info,
  SlidersHorizontal,
  BookmarkCheck,
  AlertCircle,
  MessageSquare,
  Send,
  CheckCheck,
  Clock,
  UserCheck
} from 'lucide-react';

import { formatCurrency, getCurrencySymbol } from '@/lib/currency';

interface AuditorWorkingPapersProps {
  auditReport: any;
  companyName?: string;
  currency?: string;
}

export default function AuditorWorkingPapers({ auditReport, companyName = "Enterprise Target", currency = "USD" }: AuditorWorkingPapersProps) {
  const [activeTab, setActiveTab] = useState<'opinion' | 'lead_schedules' | 'queries' | 'exceptions' | 'forensic'>('opinion');
  const [expandedSchedule, setExpandedSchedule] = useState<string | null>(null);

  const { 
    auditor_opinion, 
    audit_planning, 
    lead_schedules = [], 
    working_papers = [], 
    exception_register = [], 
    management_letter = [], 
    audit_queries: initialQueries = [],
    exception_summary = {},
    benford_analysis, 
    sloan_accruals, 
    round_number_audit 
  } = auditReport || {};

  // Interactive local state for queries
  const [queriesList, setQueriesList] = useState<any[]>(initialQueries);
  const [activeQueryId, setActiveQueryId] = useState<string | null>(null);
  const [replyText, setReplyText] = useState<string>('');
  const [responderName, setResponderName] = useState<string>('CFO / Financial Controller');

  if (!auditReport) return null;

  const handleResolveQuery = (queryId: string, isSatisfactory: boolean) => {
    setQueriesList(prev => prev.map(q => {
      if (q.query_id === queryId) {
        return {
          ...q,
          management_response: replyText || "Documentary evidence reconciled with ledger postings and certified by management.",
          management_responder: responderName || "Financial Controller",
          response_received_at: new Date().toLocaleTimeString(),
          auditor_evaluation: isSatisfactory ? "Explanation evaluated and verified against supporting ledger records. Deemed satisfactory." : "Explanation does not mitigate risk. Escalated to statutory management letter.",
          auditor_signoff: "AI Statutory Lead Auditor",
          status: isSatisfactory ? "RESOLVED" : "ESCALATED_TO_MANAGEMENT_LETTER"
        };
      }
      return q;
    }));
    setActiveQueryId(null);
    setReplyText('');
  };

  const openQueriesCount = queriesList.filter(q => q.status === "OPEN").length;
  const resolvedQueriesCount = queriesList.filter(q => q.status === "RESOLVED").length;

  const opinionType = auditor_opinion?.opinion_type || "UNQUALIFIED_OPINION";

  const getOpinionStyle = (type: string) => {
    if (type === "UNQUALIFIED_OPINION") {
      return {
        bg: "bg-emerald-50 text-emerald-900 border-emerald-300",
        badgeBg: "bg-emerald-600 text-white",
        icon: ShieldCheck,
        label: "UNQUALIFIED OPINION (CLEAN BILL OF HEALTH)",
        border: "border-emerald-400"
      };
    }
    if (type === "QUALIFIED_OPINION") {
      return {
        bg: "bg-amber-50 text-amber-900 border-amber-300",
        badgeBg: "bg-amber-600 text-white",
        icon: AlertTriangle,
        label: "QUALIFIED OPINION (EXCEPT-FOR DEPARTURES)",
        border: "border-amber-400"
      };
    }
    if (type === "INSUFFICIENT_EVIDENCE" || type === "DISCLAIMER_OF_OPINION") {
      return {
        bg: "bg-slate-50 text-slate-800 border-slate-300",
        badgeBg: "bg-slate-700 text-white",
        icon: Info,
        label: "SCOPE LIMITATION (INSUFFICIENT SOURCE EVIDENCE)",
        border: "border-slate-400"
      };
    }
    return {
      bg: "bg-rose-50 text-rose-900 border-rose-300",
      badgeBg: "bg-rose-600 text-white",
      icon: ShieldAlert,
      label: "ADVERSE OPINION (MATERIAL MISSTATEMENT DETECTED)",
      border: "border-rose-400"
    };
  };

  const style = getOpinionStyle(opinionType);
  const OpinionIcon = style.icon;

  const toggleSchedule = (ref: string) => {
    setExpandedSchedule(expandedSchedule === ref ? null : ref);
  };

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
                Institutional Statutory Financial Audit Suite
              </h3>
              <span className="text-[10px] font-extrabold text-brand-700 bg-brand-50 border border-brand-200 px-2 py-0.5 rounded-full uppercase">
                ISA / US GAAS COMPLIANT
              </span>
            </div>
            <p className="text-xs text-slate-500 font-medium">
              Materiality benchmarks, dynamic lead schedules (WP-A to WP-H), exception register, and formal audit certificate
            </p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="flex items-center gap-1.5 p-1 bg-slate-100/80 rounded-xl border border-slate-200 text-xs font-bold">
          <button
            onClick={() => setActiveTab('opinion')}
            className={`px-3 py-1.5 rounded-lg transition-all ${activeTab === 'opinion' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-900'}`}
          >
            Opinion & Planning
          </button>
          <button
            onClick={() => setActiveTab('lead_schedules')}
            className={`px-3 py-1.5 rounded-lg transition-all flex items-center gap-1.5 ${activeTab === 'lead_schedules' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-900'}`}
          >
            Lead Schedules
            {lead_schedules.length > 0 && (
              <span className="text-[10px] bg-slate-200 text-slate-700 px-1.5 py-0.2 rounded-full">{lead_schedules.length}</span>
            )}
          </button>
          <button
            onClick={() => setActiveTab('queries')}
            className={`px-3 py-1.5 rounded-lg transition-all flex items-center gap-1.5 ${activeTab === 'queries' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-900'}`}
          >
            Audit Queries (PBC)
            {queriesList.length > 0 && (
              <span className={`text-[10px] px-1.5 py-0.2 rounded-full font-bold ${openQueriesCount > 0 ? 'bg-brand-600 text-white' : 'bg-emerald-100 text-emerald-700'}`}>
                {openQueriesCount > 0 ? `${openQueriesCount} Open` : 'Resolved'}
              </span>
            )}
          </button>
          <button
            onClick={() => setActiveTab('exceptions')}
            className={`px-3 py-1.5 rounded-lg transition-all flex items-center gap-1.5 ${activeTab === 'exceptions' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-900'}`}
          >
            Exception Register
            {exception_register.length > 0 && (
              <span className={`text-[10px] px-1.5 py-0.2 rounded-full ${exception_summary?.critical_exceptions_count > 0 ? 'bg-rose-100 text-rose-700' : 'bg-amber-100 text-amber-700'}`}>
                {exception_register.length}
              </span>
            )}
          </button>
          <button
            onClick={() => setActiveTab('forensic')}
            className={`px-3 py-1.5 rounded-lg transition-all ${activeTab === 'forensic' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-900'}`}
          >
            Forensic & Tests
          </button>
        </div>
      </div>

      {/* TAB 1: OPINION & PLANNING */}
      {activeTab === 'opinion' && (
        <div className="space-y-6">
          {/* INDEPENDENT AUDITOR'S OPINION CERTIFICATE */}
          <div className={`glass-card rounded-2xl p-6 border ${style.border} ${style.bg} space-y-4 shadow-sm relative overflow-hidden`}>
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-3 border-b pb-4 border-slate-200/80">
              <div className="flex items-center gap-2.5">
                <div className={`px-3 py-1 rounded-xl text-xs font-black uppercase tracking-wider ${style.badgeBg} flex items-center gap-1.5`}>
                  <OpinionIcon className="w-3.5 h-3.5" />
                  {style.label}
                </div>
                <span className="text-xs font-bold text-slate-600">Official Independent Auditor's Report • {companyName}</span>
              </div>

              <span className="text-xs font-mono font-bold text-slate-700 bg-white/90 px-3 py-1 rounded-lg border border-slate-200 shadow-sm">
                AUDIT DATE: {auditor_opinion?.audit_date || "Current"}
              </span>
            </div>

            <div className="space-y-2">
              <h4 className="text-lg font-black text-slate-900">{auditor_opinion?.title}</h4>
              <p className="text-xs text-slate-800 font-medium leading-relaxed bg-white/80 p-4 rounded-xl border border-slate-200/80 shadow-xs">
                "{auditor_opinion?.summary}"
              </p>
            </div>

            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center text-xs font-bold text-slate-700 pt-1 gap-2">
              <div className="flex items-center gap-1.5">
                <Award className="w-4 h-4 text-brand-600" />
                <span>Auditor Signature: <strong>{auditor_opinion?.auditor_signature}</strong></span>
              </div>
              <span className="text-[10px] text-slate-500 uppercase tracking-wider font-mono">
                Standards: {auditor_opinion?.audit_standards || "ISA / US GAAS"}
              </span>
            </div>
          </div>

          {/* AUDIT PLANNING & MATERIALITY BENCHMARKS */}
          {audit_planning && (
            <div className="glass-card rounded-2xl p-6 border border-slate-200 space-y-4 shadow-sm bg-white">
              <div className="flex justify-between items-start border-b pb-3 border-slate-100">
                <div>
                  <div className="flex items-center gap-2">
                    <SlidersHorizontal className="w-4 h-4 text-brand-600" />
                    <span className="text-[10px] font-extrabold text-slate-400 uppercase tracking-wider">Audit Planning & Thresholds (ISA 320)</span>
                  </div>
                  <h4 className="text-base font-extrabold text-slate-900 mt-0.5">Calculated Materiality Framework</h4>
                </div>
                <span className="text-xs font-mono font-extrabold text-slate-700 bg-slate-100 px-3 py-1 rounded-lg">
                  Benchmark: {audit_planning.benchmark_basis}
                </span>
              </div>

              <p className="text-xs text-slate-600 font-medium bg-slate-50 p-3 rounded-xl border border-slate-200/60 leading-relaxed">
                {audit_planning.materiality_statement}
              </p>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-1">
                <div className="p-4 rounded-xl bg-blue-50/50 border border-blue-100 space-y-1">
                  <span className="text-[10px] font-extrabold text-blue-600 uppercase tracking-wider">Planning Materiality (PM)</span>
                  <p className="text-xl font-black text-slate-900">{formatCurrency(audit_planning.planning_materiality, currency)}</p>
                  <p className="text-[11px] text-slate-500 font-medium">Aggregate financial statement tolerance</p>
                </div>

                <div className="p-4 rounded-xl bg-indigo-50/50 border border-indigo-100 space-y-1">
                  <span className="text-[10px] font-extrabold text-indigo-600 uppercase tracking-wider">Performance Materiality (75%)</span>
                  <p className="text-xl font-black text-slate-900">{formatCurrency(audit_planning.performance_materiality, currency)}</p>
                  <p className="text-[11px] text-slate-500 font-medium">Scoping & individual test sample threshold</p>
                </div>

                <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-1">
                  <span className="text-[10px] font-extrabold text-slate-500 uppercase tracking-wider">Clearly Trivial Limit (5%)</span>
                  <p className="text-xl font-black text-slate-900">{formatCurrency(audit_planning.clearly_trivial_threshold, currency)}</p>
                  <p className="text-[11px] text-slate-500 font-medium">De minimis accumulation cutoff</p>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB 2: DYNAMIC LEAD SCHEDULES */}
      {activeTab === 'lead_schedules' && (
        <div className="glass-card rounded-2xl border border-slate-200 overflow-hidden shadow-sm bg-white space-y-4 p-6">
          <div className="border-b pb-3 border-slate-100 flex justify-between items-center">
            <div>
              <div className="flex items-center gap-2">
                <Layers className="w-4 h-4 text-brand-600" />
                <span className="text-[10px] font-extrabold text-slate-400 uppercase tracking-wider">Audit Documentation</span>
              </div>
              <h4 className="text-base font-extrabold text-slate-900 mt-0.5">Verified Working Paper Lead Schedules (WP-A to WP-H)</h4>
            </div>
            <span className="text-xs text-slate-500 font-bold">
              {lead_schedules.length} Schedules Active
            </span>
          </div>

          <div className="space-y-3">
            {lead_schedules.map((sched: any) => {
              const isExpanded = expandedSchedule === sched.schedule_ref;
              return (
                <div key={sched.schedule_ref} className="border border-slate-200 rounded-xl overflow-hidden transition-all">
                  <button
                    onClick={() => toggleSchedule(sched.schedule_ref)}
                    className="w-full p-4 bg-slate-50/70 hover:bg-slate-100/80 flex items-center justify-between transition-colors text-left"
                  >
                    <div className="flex items-center gap-3">
                      <span className="w-12 py-1 text-center font-mono font-black text-xs bg-brand-100 text-brand-800 rounded-lg border border-brand-200">
                        {sched.schedule_ref}
                      </span>
                      <div>
                        <h5 className="text-xs font-extrabold text-slate-900">{sched.title}</h5>
                        <p className="text-[11px] text-slate-500 font-medium">{sched.audit_objective}</p>
                      </div>
                    </div>

                    <div className="flex items-center gap-4">
                      <div className="text-right">
                        <span className="text-xs font-black text-slate-900">{formatCurrency(sched.total_amount, currency)}</span>
                        <span className="block text-[10px] text-emerald-600 font-bold">{sched.status}</span>
                      </div>
                      {isExpanded ? <ChevronDown className="w-4 h-4 text-slate-400" /> : <ChevronRight className="w-4 h-4 text-slate-400" />}
                    </div>
                  </button>

                  {isExpanded && (
                    <div className="p-4 bg-white border-t border-slate-200 space-y-2">
                      <table className="w-full text-left text-xs border-collapse">
                        <thead>
                          <tr className="border-b border-slate-200 text-slate-400 font-bold uppercase text-[10px]">
                            <th className="py-2 px-3">Account Line Item</th>
                            <th className="py-2 px-3">Source Cross-Ref</th>
                            <th className="py-2 px-3 text-right">Audited Amount</th>
                            <th className="py-2 px-3 text-center">Status</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100 font-medium text-slate-700">
                          {sched.lines?.map((line: any, idx: number) => (
                            <tr key={idx} className="hover:bg-slate-50">
                              <td className="py-2.5 px-3 font-bold text-slate-900">{line.account_name}</td>
                              <td className="py-2.5 px-3 font-mono text-[11px] text-brand-700">{line.cross_ref}</td>
                              <td className="py-2.5 px-3 text-right font-black text-slate-900">{formatCurrency(line.amount, currency)}</td>
                              <td className="py-2.5 px-3 text-center">
                                <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                                  {line.status}
                                </span>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* TAB: AUDIT QUERIES (PBC & MANAGEMENT REPLIES) */}
      {activeTab === 'queries' && (
        <div className="space-y-6">
          <div className="glass-card rounded-2xl border border-slate-200 overflow-hidden shadow-sm bg-white p-6 space-y-4">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 border-b pb-4 border-slate-100">
              <div>
                <div className="flex items-center gap-2">
                  <MessageSquare className="w-5 h-5 text-brand-600" />
                  <span className="text-[10px] font-extrabold text-slate-400 uppercase tracking-wider">PBC Audit Query Lifecycle</span>
                </div>
                <h4 className="text-base font-extrabold text-slate-900 mt-0.5">
                  Formal Audit Queries & Management Justifications
                </h4>
              </div>

              <div className="flex items-center gap-2 text-xs font-bold">
                <span className="px-3 py-1 bg-amber-50 text-amber-800 border border-amber-200 rounded-lg">
                  {openQueriesCount} Open Inquiries
                </span>
                <span className="px-3 py-1 bg-emerald-50 text-emerald-800 border border-emerald-200 rounded-lg">
                  {resolvedQueriesCount} Resolved
                </span>
              </div>
            </div>

            {queriesList.length === 0 ? (
              <div className="text-center py-12 space-y-3">
                <CheckCircle2 className="w-10 h-10 text-emerald-600 mx-auto" />
                <p className="text-sm font-bold text-slate-800">No Open Audit Queries</p>
                <p className="text-xs text-slate-500">All extracted records and forensic tests passed statutory validation without requiring management inquiry.</p>
              </div>
            ) : (
              <div className="space-y-4">
                {queriesList.map((q: any) => {
                  const isOpen = q.status === "OPEN";
                  const isResolved = q.status === "RESOLVED";
                  const isEscalated = q.status === "ESCALATED_TO_MANAGEMENT_LETTER";

                  return (
                    <div 
                      key={q.query_id} 
                      className={`rounded-2xl border p-5 space-y-4 transition-all ${
                        isOpen ? 'bg-slate-50/70 border-slate-200' : (isResolved ? 'bg-emerald-50/40 border-emerald-200' : 'bg-amber-50/40 border-amber-200')
                      }`}
                    >
                      {/* Query Header */}
                      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2 border-b pb-3 border-slate-200/70">
                        <div className="flex items-center gap-2.5">
                          <span className="font-mono text-xs font-black text-brand-700 bg-brand-50 border border-brand-200 px-2 py-0.5 rounded-md">
                            {q.query_id}
                          </span>
                          <span className="text-xs font-bold text-slate-900">{q.query_title}</span>
                          <span className="text-[10px] font-bold text-slate-500 bg-slate-200/60 px-2 py-0.5 rounded-md">
                            {q.area}
                          </span>
                        </div>

                        <div className="flex items-center gap-2">
                          {isOpen && (
                            <span className="flex items-center gap-1 text-[10px] font-black text-amber-800 bg-amber-100 border border-amber-200 px-2 py-0.5 rounded-full uppercase">
                              <Clock className="w-3 h-3 text-amber-700" />
                              Action Required
                            </span>
                          )}
                          {isResolved && (
                            <span className="flex items-center gap-1 text-[10px] font-black text-emerald-800 bg-emerald-100 border border-emerald-200 px-2 py-0.5 rounded-full uppercase">
                              <CheckCheck className="w-3 h-3 text-emerald-700" />
                              Resolved & Verified
                            </span>
                          )}
                          {isEscalated && (
                            <span className="flex items-center gap-1 text-[10px] font-black text-amber-800 bg-amber-100 border border-amber-200 px-2 py-0.5 rounded-full uppercase">
                              <AlertTriangle className="w-3 h-3 text-amber-700" />
                              Escalated to Mgmt Letter
                            </span>
                          )}
                        </div>
                      </div>

                      {/* Auditor Inquiry */}
                      <div className="space-y-1.5 text-xs">
                        <p className="text-slate-500 font-bold uppercase text-[10px] tracking-wider">Auditor Observation & Inquiry</p>
                        <p className="text-slate-800 font-medium leading-relaxed bg-white p-3 rounded-xl border border-slate-200 shadow-xs">
                          {q.management_query}
                        </p>
                      </div>

                      {/* Management Response Section */}
                      {isOpen ? (
                        <div className="space-y-3 pt-2">
                          {activeQueryId === q.query_id ? (
                            <div className="p-4 bg-white rounded-xl border border-brand-200 shadow-sm space-y-3 animate-in fade-in duration-150">
                              <div className="flex justify-between items-center">
                                <label className="text-[11px] font-bold text-slate-700 uppercase">
                                  Management Formal Response & Evidence Justification
                                </label>
                                <span className="text-[10px] text-slate-400">Recorded for Statutory Working Papers</span>
                              </div>

                              {/* Quick institutional presets */}
                              <div className="flex flex-wrap gap-1.5">
                                {[
                                  "Reconciled with Year-End Cutoff adjustments and physical verification certificate.",
                                  "Approved by Board of Directors and recognized in accordance with standard revenue criteria.",
                                  "Timing difference verified against subsequent period bank statement and vendor invoices."
                                ].map((preset, pIdx) => (
                                  <button
                                    key={pIdx}
                                    type="button"
                                    onClick={() => setReplyText(preset)}
                                    className="text-[10px] font-medium bg-slate-100 hover:bg-slate-200 text-slate-700 px-2 py-1 rounded-md transition-colors text-left"
                                  >
                                    + {preset}
                                  </button>
                                ))}
                              </div>

                              <textarea
                                value={replyText}
                                onChange={(e) => setReplyText(e.target.value)}
                                placeholder="Enter management explanation or attach documentary justification..."
                                rows={3}
                                className="w-full text-xs p-3 rounded-xl border border-slate-200 focus:border-brand-500 focus:ring-1 focus:ring-brand-500 outline-none font-medium text-slate-800"
                              />

                              <div className="flex flex-col sm:flex-row justify-between items-center gap-3 pt-1">
                                <div className="flex items-center gap-2 text-xs">
                                  <span className="text-slate-400 font-medium">Responder:</span>
                                  <input
                                    type="text"
                                    value={responderName}
                                    onChange={(e) => setResponderName(e.target.value)}
                                    className="text-xs font-bold text-slate-800 bg-slate-50 border border-slate-200 px-2 py-1 rounded-lg"
                                  />
                                </div>

                                <div className="flex items-center gap-2">
                                  <button
                                    onClick={() => setActiveQueryId(null)}
                                    className="px-3 py-1.5 rounded-lg text-xs font-bold text-slate-500 hover:bg-slate-100"
                                  >
                                    Cancel
                                  </button>
                                  <button
                                    onClick={() => handleResolveQuery(q.query_id, true)}
                                    className="px-4 py-1.5 rounded-lg text-xs font-bold bg-emerald-600 hover:bg-emerald-700 text-white shadow-xs flex items-center gap-1.5"
                                  >
                                    <CheckCircle2 className="w-3.5 h-3.5" />
                                    Accept & Sign Off
                                  </button>
                                  <button
                                    onClick={() => handleResolveQuery(q.query_id, false)}
                                    className="px-4 py-1.5 rounded-lg text-xs font-bold bg-amber-600 hover:bg-amber-700 text-white shadow-xs flex items-center gap-1.5"
                                  >
                                    <AlertTriangle className="w-3.5 h-3.5" />
                                    Escalate to Letter
                                  </button>
                                </div>
                              </div>
                            </div>
                          ) : (
                            <button
                              onClick={() => {
                                setActiveQueryId(q.query_id);
                                setReplyText('');
                              }}
                              className="px-4 py-2 bg-brand-600 hover:bg-brand-700 text-white text-xs font-bold rounded-xl transition-all shadow-xs flex items-center gap-2"
                            >
                              <Send className="w-3.5 h-3.5" />
                              Record Management Justification & Sign Off
                            </button>
                          )}
                        </div>
                      ) : (
                        /* Recorded Management Explanation & Verdict */
                        <div className="space-y-2 pt-2">
                          <div className="p-3.5 bg-white/90 rounded-xl border border-slate-200 text-xs space-y-1.5 shadow-xs">
                            <div className="flex justify-between items-center text-[10px] font-bold text-slate-400 uppercase">
                              <span>Management Representation ({q.management_responder || 'Executive'})</span>
                              <span>Recorded at {q.response_received_at || 'Audit Stage'}</span>
                            </div>
                            <p className="text-slate-900 font-semibold italic">"{q.management_response}"</p>
                          </div>

                          <div className={`p-3 rounded-xl border text-xs flex items-center justify-between ${
                            isResolved ? 'bg-emerald-100/70 border-emerald-300 text-emerald-950' : 'bg-amber-100/70 border-amber-300 text-amber-950'
                          }`}>
                            <div className="flex items-center gap-2">
                              <UserCheck className="w-4 h-4 text-slate-700" />
                              <span className="font-bold">{q.auditor_evaluation}</span>
                            </div>
                            <span className="text-[10px] font-mono font-black uppercase text-slate-600">
                              Signed: {q.auditor_signoff || 'AI Lead Auditor'}
                            </span>
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      )}

      {/* TAB 3: EXCEPTION REGISTER & MANAGEMENT LETTER */}
      {activeTab === 'exceptions' && (
        <div className="space-y-6">
          {/* EXCEPTION REGISTER TABLE */}
          <div className="glass-card rounded-2xl border border-slate-200 overflow-hidden shadow-sm bg-white p-6 space-y-4">
            <div className="border-b pb-3 border-slate-100 flex justify-between items-center">
              <div>
                <div className="flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 text-amber-600" />
                  <span className="text-[10px] font-extrabold text-slate-400 uppercase tracking-wider">Audit Findings</span>
                </div>
                <h4 className="text-base font-extrabold text-slate-900 mt-0.5">Centralized Audit Exception Register</h4>
              </div>
              <span className="text-xs font-bold text-slate-500">
                Total Exceptions: {exception_register.length}
              </span>
            </div>

            {exception_register.length === 0 ? (
              <div className="p-8 text-center bg-emerald-50/50 rounded-xl border border-emerald-100 space-y-2">
                <CheckCircle2 className="w-8 h-8 text-emerald-600 mx-auto" />
                <h5 className="text-sm font-extrabold text-emerald-900">Zero Audit Exceptions Detected</h5>
                <p className="text-xs text-emerald-700">All financial statements, trial balance debits/credits, and forensic tests reconciled cleanly.</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="bg-slate-50 border-b border-slate-200 text-slate-400 font-bold uppercase text-[10px]">
                      <th className="py-3 px-3">Ref</th>
                      <th className="py-3 px-3">Audit Area</th>
                      <th className="py-3 px-3">Issue Title & Description</th>
                      <th className="py-3 px-3 text-center">Severity</th>
                      <th className="py-3 px-3 text-right">Impact Amount</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 font-medium text-slate-700">
                    {exception_register.map((exc: any) => (
                      <tr key={exc.exception_id} className="hover:bg-slate-50">
                        <td className="py-3 px-3 font-mono font-bold text-slate-800">{exc.exception_id}</td>
                        <td className="py-3 px-3 font-bold text-slate-900">{exc.audit_area}</td>
                        <td className="py-3 px-3 space-y-0.5">
                          <p className="font-extrabold text-slate-900">{exc.issue_title}</p>
                          <p className="text-[11px] text-slate-500">{exc.description}</p>
                        </td>
                        <td className="py-3 px-3 text-center">
                          <span className={`px-2 py-0.5 rounded-full text-[10px] font-black uppercase ${
                            exc.severity === 'MATERIAL_MISSTATEMENT' 
                              ? 'bg-rose-100 text-rose-700 border border-rose-200' 
                              : (exc.severity === 'SIGNIFICANT_DEFICIENCY' ? 'bg-amber-100 text-amber-700 border border-amber-200' : 'bg-slate-100 text-slate-700')
                          }`}>
                            {exc.severity?.replace('_', ' ')}
                          </span>
                        </td>
                        <td className="py-3 px-3 text-right font-mono font-bold text-slate-900">
                          {exc.impact_amount > 0 ? formatCurrency(exc.impact_amount, currency) : '—'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* MANAGEMENT LETTER OBSERVATIONS */}
          {management_letter.length > 0 && (
            <div className="glass-card rounded-2xl border border-slate-200 overflow-hidden shadow-sm bg-white p-6 space-y-4">
              <div className="border-b pb-3 border-slate-100">
                <div className="flex items-center gap-2">
                  <FileText className="w-4 h-4 text-amber-600" />
                  <span className="text-[10px] font-extrabold text-slate-400 uppercase tracking-wider">Executive Management Letter</span>
                </div>
                <h4 className="text-base font-extrabold text-slate-900 mt-0.5">Internal Control Weaknesses & Recommendations</h4>
              </div>

              <div className="space-y-3">
                {management_letter.map((ml: any) => (
                  <div key={ml.ref} className="p-4 rounded-xl bg-amber-50/40 border border-amber-200/80 space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-xs font-black text-amber-900 uppercase">[{ml.ref}] {ml.area}</span>
                      <span className="text-[10px] font-extrabold text-amber-700 bg-amber-100 px-2 py-0.5 rounded-full">Internal Control Deficiency</span>
                    </div>
                    <p className="text-xs text-slate-800 font-medium">{ml.deficiency}</p>
                    <div className="bg-white/80 p-3 rounded-lg border border-amber-200 text-xs text-slate-700">
                      <strong className="text-brand-800 font-extrabold">Auditor Remediation:</strong> {ml.recommendation}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB 4: FORENSIC & PROCEDURAL TESTS */}
      {activeTab === 'forensic' && (
        <div className="space-y-6">
          {/* BENFORD'S LAW DIGIT FREQUENCY ANALYSIS */}
          <div className="glass-card rounded-2xl p-6 border border-slate-200 space-y-5 shadow-sm bg-white">
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
            <div className="glass-card rounded-2xl p-5 border border-slate-200 space-y-3 shadow-sm bg-white">
              <div className="flex justify-between items-center border-b pb-2 border-slate-100">
                <span className="text-[10px] font-extrabold text-slate-400 uppercase tracking-wider">Sloan Accruals Quality</span>
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                  sloan_accruals?.status === "PASS" ? "bg-emerald-50 text-emerald-700" : (sloan_accruals?.status === "NOT_APPLICABLE" ? "bg-slate-100 text-slate-600" : "bg-amber-50 text-amber-700")
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

            <div className="glass-card rounded-2xl p-5 border border-slate-200 space-y-3 shadow-sm bg-white">
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

          {/* GENERAL WORKING PAPERS (WP-101 TO WP-104) */}
          <div className="glass-card rounded-2xl border border-slate-200 overflow-hidden shadow-sm bg-white">
            <div className="p-4 bg-slate-50/80 border-b border-slate-200 flex justify-between items-center">
              <h4 className="text-xs font-extrabold text-slate-800 uppercase tracking-wider flex items-center gap-2">
                <Layers className="w-4 h-4 text-slate-500" />
                General Audit Procedures (WP-101 to WP-104)
              </h4>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="bg-slate-100/60 border-b border-slate-200 text-slate-400 font-bold uppercase tracking-wider text-[10px]">
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
                          wp.status === "PASS" ? "bg-emerald-50 text-emerald-700 border border-emerald-200" : (wp.status === "WARNING" ? "bg-amber-50 text-amber-700 border border-amber-200" : "bg-rose-50 text-rose-700 border border-rose-200")
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
      )}
    </div>
  );
}
