'use client';
import React, { useState, useEffect, Suspense } from 'react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import api from '@/lib/api';
import FileUploader from '@/components/FileUploader';
import { 
  UploadCloud, 
  History as HistoryIcon, 
  TrendingUp, 
  ArrowRight, 
  Activity, 
  Clock, 
  CheckCircle2, 
  FileSpreadsheet, 
  ShieldCheck,
  ChevronRight,
  ArrowLeft
} from 'lucide-react';

function DashboardContent() {
  const searchParams = useSearchParams();
  const isUploadParam = searchParams ? searchParams.get('upload') === 'true' : false;

  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const res = await api.get('/api/history/');
      setHistory(res.data || []);
    } catch (err) {
      console.log('Failed to fetch history');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateStr: any) => {
    if (!dateStr) return 'Recently processed';
    const d = new Date(dateStr);
    return isNaN(d.getTime()) ? 'Recently processed' : d.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
  };

  const formatDateTime = (dateStr: any) => {
    if (!dateStr) return 'Recently';
    const d = new Date(dateStr);
    return isNaN(d.getTime()) ? 'Recently' : d.toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' });
  };

  // Dedicated Upload View when navigated via Upload & Analyze tab (/dashboard?upload=true)
  if (isUploadParam) {
    return (
      <div className="space-y-6 max-w-4xl mx-auto py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Link
              href="/dashboard"
              className="p-2 rounded-xl bg-white border border-slate-200 text-slate-600 hover:text-slate-900 shadow-sm transition-all hover:scale-105"
              title="Return to Dashboard Overview"
            >
              <ArrowLeft className="w-5 h-5" />
            </Link>
            <div>
              <h2 className="text-xl font-extrabold text-slate-900 flex items-center gap-2">
                <UploadCloud className="w-6 h-6 text-brand-600" />
                Upload & Analyze Financial Workbook
              </h2>
              <p className="text-xs text-slate-500 font-medium">
                Upload your accounting ledger (.xlsx, .csv) for automated audit statements & ratio analysis
              </p>
            </div>
          </div>

          <Link
            href="/dashboard"
            className="text-xs font-bold text-slate-600 hover:text-slate-900 px-3 py-1.5 rounded-xl border border-slate-200 bg-white shadow-sm transition-all"
          >
            Dashboard Overview
          </Link>
        </div>

        {/* Dedicated Upload Component View */}
        <FileUploader />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Top Banner & Quick Upload CTA */}
      <div className="glass-card rounded-2xl p-6 border border-slate-200 shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-4 bg-gradient-to-r from-white via-slate-50 to-brand-50/20">
        <div>
          <h2 className="text-xl font-black text-slate-900 flex items-center gap-2">
            Captrix <span className="text-brand-600">AI</span> Financial Intelligence
          </h2>
          <p className="text-xs text-slate-500 font-medium mt-1">
            Automated accounting workbook audit, multi-year financial statements, ratios & AI business insights.
          </p>
        </div>
        <Link
          href="/dashboard?upload=true"
          className="flex items-center gap-2 px-4 py-2.5 bg-brand-600 hover:bg-brand-700 text-white text-xs font-extrabold rounded-xl shadow-md shadow-brand-600/30 transition-all hover:scale-105 shrink-0"
        >
          <UploadCloud className="w-4 h-4" />
          <span>Upload New Workbook</span>
        </Link>
      </div>

      {/* Quick Statistics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <div className="glass-card p-5 rounded-2xl border border-slate-200 shadow-sm space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Total Audits</span>
            <div className="p-2 rounded-xl bg-brand-50 text-brand-600">
              <FileSpreadsheet className="w-5 h-5" />
            </div>
          </div>
          <div>
            <p className="text-2xl font-black text-slate-900">{history.length}</p>
            <p className="text-xs text-emerald-600 font-semibold mt-0.5 flex items-center gap-1">
              <TrendingUp className="w-3.5 h-3.5" />
              <span>Processed Workbooks</span>
            </p>
          </div>
        </div>

        <div className="glass-card p-5 rounded-2xl border border-slate-200 shadow-sm space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">AI Engine Status</span>
            <div className="p-2 rounded-xl bg-emerald-50 text-emerald-600">
              <Activity className="w-5 h-5" />
            </div>
          </div>
          <div>
            <p className="text-2xl font-black text-slate-900">Operational</p>
            <p className="text-xs text-emerald-600 font-semibold mt-0.5 flex items-center gap-1">
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>100% System Healthy</span>
            </p>
          </div>
        </div>

        <div className="glass-card p-5 rounded-2xl border border-slate-200 shadow-sm space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Compliance</span>
            <div className="p-2 rounded-xl bg-cyan-50 text-cyan-600">
              <ShieldCheck className="w-5 h-5" />
            </div>
          </div>
          <div>
            <p className="text-2xl font-black text-slate-900">SOC2 Type II</p>
            <p className="text-xs text-slate-500 font-semibold mt-0.5">Audit-Ready Engine</p>
          </div>
        </div>

        <div className="glass-card p-5 rounded-2xl border border-slate-200 shadow-sm space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Latest Activity</span>
            <div className="p-2 rounded-xl bg-indigo-50 text-indigo-600">
              <Clock className="w-5 h-5" />
            </div>
          </div>
          <div>
            <p className="text-sm font-bold text-slate-900 truncate">
              {history.length > 0 ? history[0].company_name : 'No workbooks yet'}
            </p>
            <p className="text-xs text-slate-500 font-medium mt-0.5">
              {history.length > 0 ? formatDate(history[0].created_at) : 'Awaiting upload'}
            </p>
          </div>
        </div>
      </div>

      {/* Recent Analysis History Table */}
      <div className="glass-card rounded-2xl p-6 border border-slate-200 shadow-sm space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <div className="flex items-center gap-2">
            <HistoryIcon className="w-5 h-5 text-brand-600" />
            <h3 className="text-base font-bold text-slate-900">Recent Accounting Audits</h3>
          </div>
          <Link
            href="/history"
            className="text-xs font-bold text-brand-600 hover:text-brand-700 flex items-center gap-1 transition-colors"
          >
            <span>View All History</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {loading ? (
          <div className="py-8 text-center text-slate-400 text-sm font-medium">Loading audit history...</div>
        ) : history.length === 0 ? (
          <div className="py-8 text-center text-slate-400 text-sm font-medium">
            No workbooks uploaded yet. Click "Upload New Workbook" above to begin.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm border-collapse">
              <thead>
                <tr className="border-b border-slate-200 text-xs font-bold text-slate-400 uppercase tracking-wider">
                  <th className="py-3 px-3">Company Name</th>
                  <th className="py-3 px-3">File Name</th>
                  <th className="py-3 px-3">Health Score</th>
                  <th className="py-3 px-3">Date Processed</th>
                  <th className="py-3 px-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium">
                {history.slice(0, 5).map((item) => (
                  <tr key={item.upload_id} className="hover:bg-slate-50/50 transition-colors">
                    <td className="py-3 px-3 font-bold text-slate-900">{item.company_name}</td>
                    <td className="py-3 px-3 text-slate-600">{item.filename}</td>
                    <td className="py-3 px-3">
                      <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold ${
                        item.health_score >= 75 ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-amber-50 text-amber-700 border border-amber-200'
                      }`}>
                        {item.health_score} / 100
                      </span>
                    </td>
                    <td className="py-3 px-3 text-slate-500 text-xs">{formatDateTime(item.created_at)}</td>
                    <td className="py-3 px-3 text-right">
                      <Link
                        href={`/analysis/${item.upload_id}`}
                        className="inline-flex items-center gap-1 text-xs font-bold text-brand-600 hover:text-brand-700 px-3 py-1.5 rounded-lg bg-brand-50 hover:bg-brand-100 transition-colors"
                      >
                        <span>Open Workspace</span>
                        <ChevronRight className="w-3.5 h-3.5" />
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

export default function Dashboard() {
  return (
    <Suspense fallback={<div className="py-12 text-center text-slate-400">Loading Dashboard...</div>}>
      <DashboardContent />
    </Suspense>
  );
}
