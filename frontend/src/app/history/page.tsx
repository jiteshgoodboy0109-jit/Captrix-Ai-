'use client';
import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import api, { downloadReportFile } from '@/lib/api';
import { 
  History as HistoryIcon, 
  Search, 
  Filter, 
  Trash2, 
  FileSpreadsheet, 
  Download, 
  ExternalLink, 
  ShieldCheck,
  Loader2
} from 'lucide-react';

export default function HistoryPage() {
  const [records, setRecords] = useState<any[]>([]);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchHistory();
  }, [search, statusFilter]);

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const params: any = {};
      if (search) params.search = search;
      if (statusFilter) params.status_filter = statusFilter;
      const res = await api.get('/api/history/', { params });
      if (Array.isArray(res.data)) {
        setRecords(res.data);
      } else {
        setRecords([]);
      }
    } catch (err) {
      setRecords([]);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this financial analysis report record?')) return;
    try {
      await api.delete(`/api/history/${id}`);
      fetchHistory();
    } catch (err) {
      alert('Failed to delete history record.');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-extrabold text-slate-900 flex items-center gap-2">
            <HistoryIcon className="w-6 h-6 text-brand-600" />
            Analysis History & Saved Reports
          </h2>
          <p className="text-xs text-slate-500">Persistent log of all processed accounting workbooks & audit evaluations</p>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="glass-card rounded-2xl p-4 border border-slate-200 flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="relative flex-1 w-full">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by company name or report name..."
            className="w-full pl-10 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium text-slate-900 focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/20"
          />
        </div>

        <div className="flex items-center gap-3 w-full md:w-auto">
          <Filter className="w-4 h-4 text-slate-400" />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium text-slate-900 focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/20"
          >
            <option value="">All Statuses</option>
            <option value="COMPLETED">Completed</option>
            <option value="PROCESSING">Processing</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="glass-card rounded-2xl border border-slate-200 overflow-hidden shadow-sm">
        {loading ? (
          <div className="py-16 text-center space-y-2">
            <Loader2 className="w-8 h-8 animate-spin text-brand-600 mx-auto" />
            <p className="text-xs text-slate-500 font-medium">Fetching saved reports...</p>
          </div>
        ) : records.length === 0 ? (
          <div className="py-16 text-center space-y-3">
            <FileSpreadsheet className="w-12 h-12 text-slate-300 mx-auto" />
            <p className="text-sm font-semibold text-slate-700">No analysis history found.</p>
            <p className="text-xs text-slate-400">Upload a workbook on the Dashboard to create an automated report record.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200 text-slate-400 font-bold uppercase tracking-wider">
                  <th className="py-3 px-4">Company Name</th>
                  <th className="py-3 px-4">Upload Date</th>
                  <th className="py-3 px-4 text-center">Health Score</th>
                  <th className="py-3 px-4 text-center">Status</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium text-slate-700">
                {records.map((r) => (
                  <tr key={r.id} className="hover:bg-slate-50/60 transition-colors">
                    <td className="py-3.5 px-4 font-bold text-slate-900">
                      {r.company_name}
                      <p className="text-[11px] text-slate-400 font-normal">{r.report_name}</p>
                    </td>
                    <td className="py-3.5 px-4 text-slate-500">
                      {new Date(r.timestamp).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
                    </td>
                    <td className="py-3.5 px-4 text-center">
                      <span className="font-extrabold text-brand-700 bg-brand-50 px-2.5 py-1 rounded-full border border-brand-100">
                        {r.health_score} / 100
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-center">
                      <span className="inline-flex items-center gap-1 text-[11px] font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
                        <ShieldCheck className="w-3 h-3 text-emerald-600" />
                        {r.status}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <Link
                          href={`/analysis/${r.upload_id}`}
                          className="flex items-center gap-1 px-3 py-1.5 bg-brand-50 hover:bg-brand-100 text-brand-700 rounded-lg text-xs font-bold transition-all"
                        >
                          <ExternalLink className="w-3.5 h-3.5" />
                          <span>Open</span>
                        </Link>
                        <button
                          onClick={() => downloadReportFile(`/api/reports/pdf/${r.upload_id}`, `Financial_Audit_${r.upload_id}.pdf`)}
                          className="p-1.5 text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg"
                          title="Download PDF Report"
                        >
                          <Download className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleDelete(r.id)}
                          className="p-1.5 text-rose-500 hover:bg-rose-50 rounded-lg"
                          title="Delete Report Record"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
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
