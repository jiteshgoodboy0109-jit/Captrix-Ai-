'use client';
import React from 'react';
import { BarChart3, PieChart } from 'lucide-react';

interface FinancialChartsProps {
  statements: any;
  ratios: any;
}

export default function FinancialCharts({ statements, ratios }: FinancialChartsProps) {
  if (!statements) return null;

  const inc = statements.income_statement || {};
  const bs = statements.balance_sheet || {};

  const rev = inc.total_revenue || 100;
  const cogs = inc.cost_of_goods_sold || 40;
  const opex = inc.operating_expenses || 30;
  const netInc = inc.net_income || 20;

  const totalAssets = bs.total_assets || 100;
  const totalLiab = bs.total_liabilities || 40;
  const totalEquity = bs.equity?.total_equity || 60;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      {/* Chart 1: Revenue & Profit Structure */}
      <div className="glass-card rounded-2xl p-5 border border-slate-200 space-y-4">
        <div className="flex items-center justify-between border-b pb-3 border-slate-100">
          <h4 className="text-sm font-bold text-slate-900 flex items-center gap-2">
            <BarChart3 className="w-4 h-4 text-brand-600" />
            Revenue & Margin Breakdown
          </h4>
          <span className="text-[10px] font-bold text-slate-400">INCOME METRICS</span>
        </div>

        <div className="space-y-3">
          <div>
            <div className="flex justify-between text-xs font-bold text-slate-700 mb-1">
              <span>Gross Revenue</span>
              <span>${(rev / 1000).toFixed(0)}k (100%)</span>
            </div>
            <div className="w-full h-3 bg-slate-100 rounded-full overflow-hidden">
              <div className="h-full bg-brand-600 rounded-full w-full"></div>
            </div>
          </div>

          <div>
            <div className="flex justify-between text-xs font-bold text-slate-700 mb-1">
              <span>Cost of Goods Sold (COGS)</span>
              <span>${(cogs / 1000).toFixed(0)}k ({((cogs / rev) * 100).toFixed(0)}%)</span>
            </div>
            <div className="w-full h-3 bg-slate-100 rounded-full overflow-hidden">
              <div
                className="h-full bg-amber-500 rounded-full"
                style={{ width: `${Math.min((cogs / rev) * 100, 100)}%` }}
              ></div>
            </div>
          </div>

          <div>
            <div className="flex justify-between text-xs font-bold text-slate-700 mb-1">
              <span>Operating Expenses (OPEX)</span>
              <span>${(opex / 1000).toFixed(0)}k ({((opex / rev) * 100).toFixed(0)}%)</span>
            </div>
            <div className="w-full h-3 bg-slate-100 rounded-full overflow-hidden">
              <div
                className="h-full bg-rose-500 rounded-full"
                style={{ width: `${Math.min((opex / rev) * 100, 100)}%` }}
              ></div>
            </div>
          </div>

          <div>
            <div className="flex justify-between text-xs font-bold text-emerald-700 mb-1">
              <span>Net Income</span>
              <span>${(netInc / 1000).toFixed(0)}k ({((netInc / rev) * 100).toFixed(1)}%)</span>
            </div>
            <div className="w-full h-3 bg-slate-100 rounded-full overflow-hidden">
              <div
                className="h-full bg-emerald-500 rounded-full"
                style={{ width: `${Math.min((netInc / rev) * 100, 100)}%` }}
              ></div>
            </div>
          </div>
        </div>
      </div>

      {/* Chart 2: Asset vs Liability Balance */}
      <div className="glass-card rounded-2xl p-5 border border-slate-200 space-y-4">
        <div className="flex items-center justify-between border-b pb-3 border-slate-100">
          <h4 className="text-sm font-bold text-slate-900 flex items-center gap-2">
            <PieChart className="w-4 h-4 text-cyan-600" />
            Capital Allocation & Solvency
          </h4>
          <span className="text-[10px] font-bold text-slate-400">BALANCE SHEET</span>
        </div>

        <div className="space-y-4">
          <div className="p-4 bg-slate-50 rounded-xl border border-slate-100 space-y-2">
            <p className="text-xs font-bold text-slate-400">Capital Structure Composition</p>
            <div className="w-full h-5 bg-slate-200 rounded-xl overflow-hidden flex">
              <div
                className="h-full bg-cyan-600"
                style={{ width: `${(totalEquity / totalAssets) * 100}%` }}
                title="Equity Share"
              ></div>
              <div
                className="h-full bg-rose-500"
                style={{ width: `${(totalLiab / totalAssets) * 100}%` }}
                title="Debt Liabilities Share"
              ></div>
            </div>

            <div className="flex justify-between text-xs font-semibold pt-1">
              <span className="flex items-center gap-1.5 text-cyan-800">
                <span className="w-2.5 h-2.5 rounded-full bg-cyan-600"></span>
                Shareholders' Equity ({((totalEquity / totalAssets) * 100).toFixed(0)}%)
              </span>
              <span className="flex items-center gap-1.5 text-rose-800">
                <span className="w-2.5 h-2.5 rounded-full bg-rose-500"></span>
                Liabilities ({((totalLiab / totalAssets) * 100).toFixed(0)}%)
              </span>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3 text-center">
            <div className="p-3 bg-brand-50 rounded-xl border border-brand-100">
              <p className="text-[11px] font-bold text-slate-500">Total Asset Base</p>
              <p className="text-base font-extrabold text-brand-900 mt-0.5">${(totalAssets / 1000).toFixed(0)}k</p>
            </div>
            <div className="p-3 bg-slate-100 rounded-xl border border-slate-200">
              <p className="text-[11px] font-bold text-slate-500">Total Obligations</p>
              <p className="text-base font-extrabold text-slate-900 mt-0.5">${(totalLiab / 1000).toFixed(0)}k</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
