'use client';
import React, { useState, useEffect } from 'react';
import { useParams, useSearchParams, useRouter } from 'next/navigation';
import api, { downloadReportFile } from '@/lib/api';
import HealthGauge from '@/components/HealthGauge';
import StatementViewer from '@/components/StatementViewer';
import RatioGrid from '@/components/RatioGrid';
import CorporateFinanceViewer from '@/components/CorporateFinanceViewer';
import AIInsightsPanel from '@/components/AIInsightsPanel';
import ChatbotDrawer from '@/components/ChatbotDrawer';
import FinancialCharts from '@/components/FinancialCharts';
import MultiPeriodViewer from '@/components/MultiPeriodViewer';
import { 
  Download, 
  FileSpreadsheet, 
  FileText, 
  BrainCircuit, 
  LineChart, 
  Building2, 
  MessageSquareText, 
  Loader2, 
  ArrowLeft,
  UploadCloud,
  ChevronDown,
  TrendingUp
} from 'lucide-react';
import Link from 'next/link';
import { syncAnalysisToFirestore } from '@/lib/firebase';

export default function AnalysisWorkspace() {
  const params = useParams();
  const searchParams = useSearchParams();
  const router = useRouter();
  const uploadId = params?.id || 'latest';

  const [data, setData] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [allWorkbooks, setAllWorkbooks] = useState<any[]>([]);
  const [activeTab, setActiveTab] = useState<string>(searchParams.get('tab') || 'overview');
  const [isSampleLoading, setIsSampleLoading] = useState(false);

  useEffect(() => {
    const currentTab = searchParams.get('tab');
    if (currentTab) {
      setActiveTab(currentTab);
    }
  }, [searchParams]);

  useEffect(() => {
    fetchAnalysisData();
    fetchAllWorkbooks();
  }, [uploadId]);

  const fetchAllWorkbooks = async () => {
    try {
      const res = await api.get('/api/history/');
      setAllWorkbooks(res.data || []);
    } catch (e) {
      console.log('Failed to fetch workbook history');
    }
  };

  const fetchAnalysisData = async () => {
    setLoading(true);
    setError(null);
    try {
      let targetId = uploadId;
      if (uploadId === 'latest') {
        const histRes = await api.get('/api/history/');
        if (histRes.data && histRes.data.length > 0) {
          targetId = histRes.data[0].upload_id;
        } else {
          setError('No uploaded financial workbook found. Please upload a file or click below to load sample data.');
          setLoading(false);
          return;
        }
      }

      const res = await api.get(`/api/analysis/${targetId}`);
      setData(res.data);
      syncAnalysisToFirestore(res.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load financial analysis data.');
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (tabKey: string) => {
    setActiveTab(tabKey);
    const targetId = data?.upload_id || uploadId;
    router.replace(`/analysis/${targetId}?tab=${tabKey}`, { scroll: false });
  };

  const handleDownloadPDF = () => {
    const targetId = data?.upload_id || uploadId;
    if (!targetId) return;
    downloadReportFile(`/api/reports/pdf/${targetId}`, `Financial_Audit_${targetId}.pdf`);
  };

  const handleDownloadExcel = () => {
    const targetId = data?.upload_id || uploadId;
    if (!targetId) return;
    downloadReportFile(`/api/reports/excel/${targetId}`, `Financial_Analysis_${targetId}.xlsx`);
  };

  if (loading) {
    return (
      <div className="py-20 text-center space-y-4">
        <Loader2 className="w-10 h-10 animate-spin text-brand-600 mx-auto" />
        <p className="text-sm font-semibold text-slate-700">Loading AI Financial Workspace & Statement Engines...</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="max-w-2xl mx-auto py-16 text-center space-y-6">
        <div className="w-16 h-16 bg-rose-50 text-rose-600 rounded-3xl flex items-center justify-center mx-auto border border-rose-100 shadow-sm">
          <UploadCloud className="w-8 h-8" />
        </div>
        <div>
          <h3 className="text-xl font-black text-slate-900">Workbook Required</h3>
          <p className="text-xs text-slate-500 mt-1">{error || 'Please upload an accounting workbook to run automated financial analysis.'}</p>
        </div>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
          <Link
            href="/dashboard?upload=true"
            className="w-full sm:w-auto px-5 py-3 bg-brand-600 hover:bg-brand-700 text-white font-bold text-xs rounded-xl transition-all shadow-md"
          >
            Upload Accounting File
          </Link>
        </div>
      </div>
    );
  }

  const { company_name, filename, statements, ratios, corporate_finance, ai_report } = data;

  return (
    <div className="space-y-6">
      {/* Workbook Switcher & Actions */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 glass-card rounded-2xl p-4 border border-slate-200 shadow-sm">
        <div className="flex items-center gap-3">
          <Link href="/dashboard" className="p-2 text-slate-400 hover:text-slate-900 hover:bg-slate-100 rounded-xl transition-all">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-lg font-black text-slate-900 tracking-tight">{data.company_name}</h2>
              <span className="text-[10px] font-bold text-brand-700 bg-brand-50 px-2.5 py-0.5 rounded-full border border-brand-200">
                AUDITED REPORT #{data.upload_id}
              </span>
            </div>
            <p className="text-xs text-slate-500 font-medium">{data.filename} • Analyzed on {new Date(data.created_at).toLocaleDateString()}</p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2.5 w-full md:w-auto">
          <Link
            href="/dashboard?upload=true"
            className="flex items-center gap-1.5 px-3.5 py-2 bg-brand-600 hover:bg-brand-700 text-white rounded-xl text-xs font-bold transition-all shadow-sm"
            title="Upload next financial workbook"
          >
            <UploadCloud className="w-4 h-4" />
            <span>Upload New File</span>
          </Link>

          <button
            onClick={handleDownloadExcel}
            className="flex items-center gap-2 px-4 py-2 bg-emerald-50 text-emerald-700 hover:bg-emerald-100 border border-emerald-200 rounded-xl text-xs font-bold transition-all shadow-sm"
          >
            <FileSpreadsheet className="w-4 h-4" />
            <span>Excel Export</span>
          </button>

          <button
            onClick={handleDownloadPDF}
            className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-brand-700 to-brand-600 hover:from-brand-800 hover:to-brand-700 text-white rounded-xl text-xs font-bold transition-all shadow-md shadow-brand-500/20"
          >
            <Download className="w-4 h-4" />
            <span>Audit PDF</span>
          </button>
        </div>
      </div>

      {/* Primary Navigation Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-200 pb-1 overflow-x-auto">
        {[
          { key: 'overview', label: 'Executive Overview', icon: BrainCircuit },
          { key: 'statements', label: 'Financial Statements', icon: FileText },
          { key: 'trends', label: 'Multi-Year Trends & CAGR', icon: TrendingUp },
          { key: 'ratios', label: 'Ratio Analysis', icon: LineChart },
          { key: 'corp_fin', label: 'Corporate Finance', icon: Building2 },
          { key: 'insights', label: 'AI Business Insights', icon: BrainCircuit },
          { key: 'chat', label: 'AI Copilot Chat', icon: MessageSquareText },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.key;
          return (
            <button
              key={tab.key}
              onClick={() => handleTabChange(tab.key)}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold whitespace-nowrap transition-all ${
                isActive
                  ? 'bg-white text-brand-700 shadow-sm border border-slate-200'
                  : 'text-slate-500 hover:text-slate-900 hover:bg-slate-100'
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? 'text-brand-600' : 'text-slate-400'}`} />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Tab Content Rendering */}
      {activeTab === 'overview' && (
        <div className="space-y-8">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div>
              <HealthGauge score={ai_report.health_score} companyName={company_name} />
            </div>

            <div className="lg:col-span-2 space-y-6">
              <div className="glass-card rounded-2xl p-6 border border-slate-200">
                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Executive Summary</h4>
                <p className="text-sm font-medium text-slate-800 leading-relaxed">{ai_report.executive_summary}</p>
              </div>

              <FinancialCharts statements={statements} ratios={ratios} />
            </div>
          </div>
        </div>
      )}

      {activeTab === 'statements' && (
        <StatementViewer statements={statements} />
      )}

      {activeTab === 'trends' && (
        <MultiPeriodViewer multiPeriod={data.multi_period} />
      )}

      {activeTab === 'ratios' && (
        <RatioGrid ratios={ratios} />
      )}

      {activeTab === 'corp_fin' && (
        <CorporateFinanceViewer corporateFinance={corporate_finance} />
      )}

      {activeTab === 'insights' && (
        <AIInsightsPanel aiReport={ai_report} />
      )}

      {activeTab === 'chat' && (
        <div className="max-w-3xl mx-auto">
          <ChatbotDrawer uploadId={data.upload_id} />
        </div>
      )}
    </div>
  );
}
