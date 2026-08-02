'use client';
import React, { useState, useEffect, Suspense } from 'react';
import Link from 'next/link';
import { usePathname, useSearchParams, useRouter } from 'next/navigation';
import { 
  Home, 
  UploadCloud, 
  BarChart2, 
  FileSpreadsheet, 
  PieChart, 
  Briefcase, 
  Sparkles, 
  MessageSquare, 
  History, 
  MoreVertical,
  LogOut
} from 'lucide-react';
import { useAuth } from '@/context/AuthContext';

interface SidebarProps {
  onNavigate?: () => void;
}

function SidebarContent({ onNavigate }: SidebarProps) {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const router = useRouter();
  const { user, logout } = useAuth();
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  // Extract current upload_id if currently on an analysis route
  let currentAnalysisId = 'latest';
  if (pathname.startsWith('/analysis/')) {
    const parts = pathname.split('/');
    if (parts[2]) {
      currentAnalysisId = parts[2];
    }
  }

  const activeTab = searchParams ? searchParams.get('tab') || 'overview' : 'overview';
  const isUploadParam = searchParams ? searchParams.get('upload') === 'true' : false;

  const menuItems = [
    { 
      name: 'Dashboard', 
      path: '/dashboard', 
      icon: Home,
      isActive: pathname === '/dashboard' && !isUploadParam
    },
    { 
      name: 'Upload & Analyze', 
      path: '/dashboard?upload=true', 
      icon: UploadCloud,
      isActive: pathname === '/dashboard' && isUploadParam
    },
    { 
      name: 'Analysis Results', 
      path: `/analysis/${currentAnalysisId}?tab=overview`, 
      icon: BarChart2,
      isActive: pathname.startsWith('/analysis') && activeTab === 'overview'
    },
    { 
      name: 'Financial Statements', 
      path: `/analysis/${currentAnalysisId}?tab=statements`, 
      icon: FileSpreadsheet,
      isActive: pathname.startsWith('/analysis') && activeTab === 'statements'
    },
    { 
      name: 'Ratio Analysis', 
      path: `/analysis/${currentAnalysisId}?tab=ratios`, 
      icon: PieChart,
      isActive: pathname.startsWith('/analysis') && activeTab === 'ratios'
    },
    { 
      name: 'Corporate Finance', 
      path: `/analysis/${currentAnalysisId}?tab=corp_fin`, 
      icon: Briefcase,
      isActive: pathname.startsWith('/analysis') && activeTab === 'corp_fin'
    },
    { 
      name: 'AI Insights', 
      path: `/analysis/${currentAnalysisId}?tab=insights`, 
      icon: Sparkles,
      isActive: pathname.startsWith('/analysis') && activeTab === 'insights'
    },
    { 
      name: 'Chat Assistant', 
      path: `/analysis/${currentAnalysisId}?tab=chat`, 
      icon: MessageSquare,
      isActive: pathname.startsWith('/analysis') && activeTab === 'chat'
    },
    { 
      name: 'History', 
      path: '/history', 
      icon: History,
      isActive: pathname === '/history'
    },
  ];

  const handleSignOut = () => {
    logout();
    if (onNavigate) onNavigate();
    router.push('/login');
  };

  const userName = mounted && user?.full_name ? user.full_name : 'Jitesh P';

  return (
    <aside 
      suppressHydrationWarning
      className="w-64 bg-[#050D1A] text-white flex flex-col justify-between h-full lg:h-screen sticky top-0 shrink-0 border-r border-[#0D1F38] select-none"
    >
      {/* Top Section: Logo & Menu List */}
      <div className="p-4 space-y-5 overflow-y-auto scrollbar-none">
        {/* Simple Brand Header: Only Logo and App Name */}
        <div className="px-3 py-3 border-b border-[#0D1F38]">
          <Link href="/dashboard" className="flex items-center gap-3 group">
            <img src="/logo.png" alt="Captrix AI" className="h-9 w-auto object-contain shrink-0" />
            <h1 className="text-lg font-black text-white leading-none tracking-tight group-hover:text-cyan-400 transition-colors">
              Captrix <span className="text-cyan-400">AI</span>
            </h1>
          </Link>
        </div>

        {/* Menu Items List */}
        <nav className="space-y-1">
          {menuItems.map((item) => {
            const Icon = item.icon;
            return (
              <Link
                key={item.name}
                href={item.path}
                onClick={() => {
                  if (onNavigate) onNavigate();
                }}
                className={`flex items-center gap-3.5 px-4 py-2.5 rounded-xl text-sm font-medium transition-all ${
                  item.isActive
                    ? 'bg-[#0E49B5] text-white font-bold shadow-md shadow-blue-900/40'
                    : 'text-slate-300 hover:bg-[#0C1E38] hover:text-white'
                }`}
              >
                <Icon className={`w-4 h-4 shrink-0 ${item.isActive ? 'text-white' : 'text-slate-400'}`} />
                <span className="truncate">{item.name}</span>
              </Link>
            );
          })}
        </nav>
      </div>

      {/* Bottom Section: Footer User Badge */}
      <div className="p-4 border-t border-[#0D1F38] relative">
        <div className="bg-gradient-to-r from-[#0E1E38]/90 via-[#0A172C]/90 to-[#0F2342]/90 border border-cyan-500/30 hover:border-cyan-400/60 rounded-2xl p-3 flex items-center justify-between shadow-[0_8px_20px_-4px_rgba(2,132,199,0.25)] transition-all duration-300 group">
          <div className="flex items-center gap-3 min-w-0">
            <div className="relative flex items-center justify-center shrink-0">
              <div className="absolute -inset-0.5 rounded-full bg-gradient-to-r from-cyan-400 via-blue-500 to-indigo-500 opacity-70 blur-[3px] group-hover:opacity-100 transition duration-300"></div>
              <div className="relative w-10 h-10 rounded-full bg-gradient-to-tr from-blue-600 via-indigo-600 to-cyan-400 flex items-center justify-center text-white font-black text-base shadow-md border border-white/20 tracking-wider">
                {userName.charAt(0).toUpperCase()}
              </div>
            </div>
            <div className="min-w-0">
              <p className="text-sm font-extrabold text-white leading-tight truncate tracking-wide">{userName}</p>
              <div className="flex items-center gap-1 mt-1">
                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-gradient-to-r from-emerald-500/20 via-teal-500/20 to-cyan-500/20 text-emerald-300 border border-emerald-500/40 shadow-[0_0_12px_rgba(16,185,129,0.25)]">
                  <Sparkles className="w-2.5 h-2.5 text-emerald-400 animate-pulse" />
                  Premium Plan
                </span>
              </div>
            </div>
          </div>

          <div className="relative">
            <button
              onClick={() => setShowUserMenu(!showUserMenu)}
              className="p-1.5 text-slate-400 hover:text-white rounded-xl hover:bg-white/10 transition-colors"
              title="Account Settings & Sign Out"
            >
              <MoreVertical className="w-4 h-4" />
            </button>

            {showUserMenu && (
              <div className="absolute right-0 bottom-full mb-3 w-52 bg-[#0A182E]/95 backdrop-blur-xl border border-cyan-500/30 rounded-2xl shadow-2xl p-2 z-50">
                <div className="px-3 py-2 border-b border-[#162C4E]/60 mb-1">
                  <p className="text-xs font-bold text-white truncate">{userName}</p>
                  <p className="text-[10px] text-slate-400 truncate">{user?.email || 'user@captrix.ai'}</p>
                </div>
                <button
                  onClick={handleSignOut}
                  className="w-full flex items-center gap-2.5 px-3 py-2 text-xs font-bold text-rose-400 hover:bg-rose-500/10 hover:text-rose-300 rounded-xl transition-all text-left"
                >
                  <LogOut className="w-4 h-4" />
                  <span>Sign Out</span>
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </aside>
  );
}

export default function Sidebar({ onNavigate }: SidebarProps) {
  return (
    <Suspense fallback={
      <aside className="w-64 bg-[#050D1A] h-screen border-r border-[#0D1F38]" />
    }>
      <SidebarContent onNavigate={onNavigate} />
    </Suspense>
  );
}
