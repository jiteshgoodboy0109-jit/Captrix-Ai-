'use client';
import React, { useState } from 'react';
import { FileText, Check, FileSpreadsheet } from 'lucide-react';
import { formatCurrency, formatRawNumber, getCurrencySymbol } from '@/lib/currency';

interface StatementViewerProps {
  statements: any;
  currency?: string;
}

export default function StatementViewer({ statements, currency = 'USD' }: StatementViewerProps) {
  const inc = statements?.income_statement || {};
  const bs = statements?.balance_sheet || {};
  const cf = statements?.cash_flow || {};
  const tb = statements?.trial_balance || {};

  const hasIncome = Boolean(inc && (inc.total_revenue !== undefined || inc.revenue_from_operations !== undefined || inc.net_income !== undefined));
  const hasBalance = Boolean(bs && bs.status !== 'NOT_REPORTED_IN_SOURCE' && (bs.total_assets !== undefined || bs.total_liabilities !== undefined || bs.current_assets));
  const hasCashFlow = Boolean(cf && cf.status !== 'NOT_REPORTED_IN_SOURCE' && cf.status !== 'Missing' && (cf.operating_activities !== undefined || cf.net_cash_flow !== undefined));
  const hasTB = Boolean(tb && tb.status !== 'NOT_REPORTED_IN_SOURCE' && tb.item_count > 0);

  const initialTab: 'balance' | 'income' | 'cash_flow' | 'tb' = hasIncome ? 'income' : (hasBalance ? 'balance' : (hasTB ? 'tb' : 'income'));
  const [activeTab, setActiveTab] = useState<'balance' | 'income' | 'cash_flow' | 'tb'>(initialTab);

  const fmt = (val: number | undefined | null) => formatCurrency(val, currency);
  const fmtRaw = (val: number | undefined | null) => formatCurrency(val, currency);

  const ca = bs.current_assets || {};
  const ppe = bs.property_plant_equipment || {};
  const intangibles = bs.intangible_assets || {};

  const cl = bs.current_liabilities || {};
  const ltl = bs.long_term_liabilities || {};
  const eq = bs.equity || {};

  return (
    <div className="glass-card rounded-2xl p-6 shadow-md border border-slate-200 space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-4 border-b border-slate-200">
        <div>
          <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
            <FileText className="w-5 h-5 text-brand-600" />
            Financial Audit & Statement Engine
          </h3>
          <p className="text-xs text-slate-500">Structured accounting statements generated from parsed ledger & trial balance</p>
        </div>

        <div className="flex items-center gap-1 bg-slate-100 p-1 rounded-xl w-full sm:w-auto overflow-x-auto max-w-full scrollbar-none">
          {hasIncome && (
            <button
              onClick={() => setActiveTab('income')}
              className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all shrink-0 ${
                activeTab === 'income' ? 'bg-brand-600 text-white shadow-sm' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Income Statement
            </button>
          )}
          {hasBalance && (
            <button
              onClick={() => setActiveTab('balance')}
              className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all shrink-0 ${
                activeTab === 'balance' ? 'bg-brand-600 text-white shadow-sm' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Balance Sheet & Assets
            </button>
          )}
          {hasCashFlow && (
            <button
              onClick={() => setActiveTab('cash_flow')}
              className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all shrink-0 ${
                activeTab === 'cash_flow' ? 'bg-brand-600 text-white shadow-sm' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Cash Flow
            </button>
          )}
          {hasTB && (
            <button
              onClick={() => setActiveTab('tb')}
              className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all shrink-0 ${
                activeTab === 'tb' ? 'bg-brand-600 text-white shadow-sm' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Trial Balance
            </button>
          )}
        </div>
      </div>

      {activeTab === 'balance' && (
        <div className="border border-sky-300 rounded-xl overflow-hidden shadow-sm bg-white">
          {/* Two-Column Accounting Layout matching reference image */}
          <div className="grid grid-cols-1 md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-sky-200">
            {/* LEFT COLUMN: ASSETS */}
            <div className="flex flex-col justify-between">
              <div>
                {/* Assets Header Banner */}
                <div className="bg-sky-200/90 text-slate-900 font-extrabold text-sm uppercase tracking-wider px-5 py-3 border-b border-sky-300">
                  ASSETS
                </div>

                <div className="p-5 space-y-6 text-sm text-slate-800 font-medium">
                  {/* Current Assets */}
                  <div className="space-y-2">
                    <h4 className="font-bold text-slate-900 text-base">Current assets</h4>
                    <div className="pl-4 space-y-1.5 text-xs text-slate-700">
                      <div className="flex justify-between">
                        <span>Cash</span>
                        <span className="font-semibold">{fmt(ca.cash)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Petty cash</span>
                        <span className="font-semibold">{fmtRaw(ca.petty_cash)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Temporary Investment</span>
                        <span className="font-semibold">{fmtRaw(ca.temporary_investments)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Accounts receivable</span>
                        <span className="font-semibold">{fmtRaw(ca.accounts_receivable)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Inventory</span>
                        <span className="font-semibold">{fmtRaw(ca.inventory)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Supply</span>
                        <span className="font-semibold">{fmtRaw(ca.supplies)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Prepaid Insurance</span>
                        <span className="font-semibold">{fmtRaw(ca.prepaid_insurance)}</span>
                      </div>
                    </div>
                    <div className="flex justify-between pt-2 font-bold text-xs text-slate-900 border-t border-slate-100">
                      <span className="pl-4">Total current assets</span>
                      <span>{fmtRaw(ca.total_current_assets)}</span>
                    </div>
                  </div>

                  {/* Investment */}
                  <div className="flex justify-between font-bold text-slate-900 text-sm">
                    <span>Investment</span>
                    <span>{fmtRaw(bs.investment)}</span>
                  </div>

                  {/* Property Plant and Equipment */}
                  <div className="space-y-2">
                    <h4 className="font-bold text-slate-900 text-base">Property plant and equipment</h4>
                    <div className="pl-4 space-y-1.5 text-xs text-slate-700">
                      <div className="flex justify-between">
                        <span>Land</span>
                        <span className="font-semibold">{fmtRaw(ppe.land)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Land improvements</span>
                        <span className="font-semibold">{fmtRaw(ppe.land_improvements)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Buildings</span>
                        <span className="font-semibold">{fmtRaw(ppe.buildings)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Equipment</span>
                        <span className="font-semibold">{fmtRaw(ppe.equipment)}</span>
                      </div>
                      <div className="flex justify-between text-slate-500">
                        <span>Accumulated depreciation</span>
                        <span className="font-semibold">{fmt(ppe.accumulated_depreciation)}</span>
                      </div>
                    </div>
                    <div className="flex justify-between pt-2 font-bold text-xs text-slate-900 border-t border-slate-100">
                      <span className="pl-4">Prop, plant and equip-net</span>
                      <span>{fmtRaw(ppe.net_property_plant_equipment)}</span>
                    </div>
                  </div>

                  {/* Intangible Assets */}
                  <div className="space-y-2">
                    <h4 className="font-bold text-slate-900 text-base">Intangible assets</h4>
                    <div className="pl-4 space-y-1.5 text-xs text-slate-700">
                      <div className="flex justify-between">
                        <span>Goodwill</span>
                        <span className="font-semibold">{fmtRaw(intangibles.goodwill)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Trade names</span>
                        <span className="font-semibold">{fmtRaw(intangibles.trade_names)}</span>
                      </div>
                    </div>
                    <div className="flex justify-between pt-2 font-bold text-xs text-slate-900 border-t border-slate-100">
                      <span className="pl-4">Total intangible assets</span>
                      <span>{fmtRaw(intangibles.total_intangible_assets)}</span>
                    </div>
                  </div>

                  {/* Other Assets */}
                  <div className="flex justify-between font-bold text-slate-900 text-xs pt-1">
                    <span>Other assets</span>
                    <span>{fmtRaw(bs.other_assets)}</span>
                  </div>
                </div>
              </div>

              {/* Total Assets Bottom Footer Banner */}
              <div className="bg-sky-200/90 px-5 py-3.5 border-t border-sky-300 flex justify-between items-center font-extrabold text-base text-slate-900">
                <span>Total Assets</span>
                <span className="text-lg">{fmt(bs.total_assets)}</span>
              </div>
            </div>

            {/* RIGHT COLUMN: LIABILITIES & EQUITY */}
            <div className="flex flex-col justify-between">
              <div>
                {/* Liabilities Header Banner */}
                <div className="bg-sky-200/90 text-slate-900 font-extrabold text-sm uppercase tracking-wider px-5 py-3 border-b border-sky-300">
                  LIABILITIES
                </div>

                <div className="p-5 space-y-6 text-sm text-slate-800 font-medium">
                  {/* Current Liabilities */}
                  <div className="space-y-2">
                    <h4 className="font-bold text-slate-900 text-base">Current liabilities</h4>
                    <div className="pl-4 space-y-1.5 text-xs text-slate-700">
                      <div className="flex justify-between">
                        <span>Notes payable</span>
                        <span className="font-semibold">{fmt(cl.notes_payable)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Accounts payable</span>
                        <span className="font-semibold">{fmtRaw(cl.accounts_payable)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Wages payable</span>
                        <span className="font-semibold">{fmtRaw(cl.wages_payable)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Interest payable</span>
                        <span className="font-semibold">{fmtRaw(cl.interest_payable)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Tax payable</span>
                        <span className="font-semibold">{fmtRaw(cl.tax_payable)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Unearned revenue</span>
                        <span className="font-semibold">{fmtRaw(cl.unearned_revenue)}</span>
                      </div>
                    </div>
                    <div className="flex justify-between pt-2 font-bold text-xs text-slate-900 border-t border-slate-100">
                      <span className="pl-4">Total current liabilities</span>
                      <span>{fmtRaw(cl.total_current_liabilities)}</span>
                    </div>
                  </div>

                  {/* Long-Term Liabilities */}
                  <div className="space-y-2">
                    <h4 className="font-bold text-slate-900 text-base">Long-term liabilities</h4>
                    <div className="pl-4 space-y-1.5 text-xs text-slate-700">
                      <div className="flex justify-between">
                        <span>Notes payable</span>
                        <span className="font-semibold">{fmtRaw(ltl.notes_payable_lt)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Bonds payable</span>
                        <span className="font-semibold">{fmtRaw(ltl.bonds_payable)}</span>
                      </div>
                    </div>
                    <div className="flex justify-between pt-2 font-bold text-xs text-slate-900 border-t border-slate-100">
                      <span className="pl-4">Total long term liabilities</span>
                      <span>{fmtRaw(ltl.total_long_term_liabilities)}</span>
                    </div>
                  </div>

                  {/* Total Liabilities */}
                  <div className="flex justify-between font-extrabold text-slate-900 text-sm pt-2 border-t border-slate-200">
                    <span>Total liabilities</span>
                    <span>{fmtRaw(bs.total_liabilities)}</span>
                  </div>

                  {/* Owner's Equity Header Banner */}
                  <div className="bg-sky-200/90 text-slate-900 font-extrabold text-sm px-4 py-2 rounded-lg border border-sky-300 mt-4">
                    Owner's Equity
                  </div>

                  <div className="space-y-2 pt-1">
                    <div className="pl-4 space-y-1.5 text-xs text-slate-700">
                      <div className="flex justify-between">
                        <span>Common stock</span>
                        <span className="font-semibold">{fmtRaw(eq.common_stock)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Retained earnings</span>
                        <span className="font-semibold">{fmtRaw(eq.retained_earnings)}</span>
                      </div>
                      <div className="flex justify-between text-slate-500">
                        <span>Less: Treasury stock</span>
                        <span className="font-semibold">{fmt(eq.treasury_stock)}</span>
                      </div>
                    </div>
                    <div className="flex justify-between pt-2 font-bold text-xs text-slate-900 border-t border-slate-100">
                      <span className="pl-4">Total owner's equity</span>
                      <span>{fmtRaw(eq.total_equity)}</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Total Liabilities & Equity Bottom Footer Banner */}
              <div className="bg-sky-200/90 px-5 py-3.5 border-t border-sky-300 flex justify-between items-center font-extrabold text-base text-slate-900">
                <span>Total Liabilities & Equity</span>
                <span className="text-lg">{fmt(bs.total_liabilities_and_equity)}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'income' && (
        <div className="space-y-3">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm border-collapse">
              <thead>
                <tr className="bg-sky-200/80 text-slate-900 border-b border-sky-300 text-xs font-extrabold uppercase tracking-wider">
                  <th className="py-3 px-4">Line Item</th>
                  <th className="py-3 px-4 text-right">Amount ({currency})</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium">
                <tr className="hover:bg-slate-50/50">
                  <td className="py-2.5 px-4 font-semibold text-slate-900">Gross Product & Service Revenue</td>
                  <td className="py-2.5 px-4 text-right font-bold text-slate-900">{fmt(inc.total_revenue)}</td>
                </tr>
                <tr className="hover:bg-slate-50/50 text-slate-600">
                  <td className="py-2.5 px-4 pl-8">Cost of Goods Sold (COGS)</td>
                  <td className="py-2.5 px-4 text-right text-rose-600">{fmt(-inc.cost_of_goods_sold)}</td>
                </tr>
                <tr className="bg-brand-50/60 font-bold text-brand-900">
                  <td className="py-2.5 px-4">Gross Profit</td>
                  <td className="py-2.5 px-4 text-right">{fmt(inc.gross_profit)}</td>
                </tr>
                <tr className="hover:bg-slate-50/50 text-slate-600">
                  <td className="py-2.5 px-4 pl-8">Operating Expenses (OPEX)</td>
                  <td className="py-2.5 px-4 text-right text-rose-600">{fmt(-inc.operating_expenses)}</td>
                </tr>
                <tr className="hover:bg-slate-50/50 font-semibold text-slate-800">
                  <td className="py-2.5 px-4">EBITDA</td>
                  <td className="py-2.5 px-4 text-right">{fmt(inc.ebitda)}</td>
                </tr>
                <tr className="hover:bg-slate-50/50 text-slate-600">
                  <td className="py-2.5 px-4 pl-8">Depreciation & Amortization</td>
                  <td className="py-2.5 px-4 text-right text-rose-600">{fmt(-inc.depreciation_amortization)}</td>
                </tr>
                <tr className="hover:bg-slate-50/50 font-semibold text-slate-800">
                  <td className="py-2.5 px-4">EBIT (Operating Income)</td>
                  <td className="py-2.5 px-4 text-right">{fmt(inc.ebit)}</td>
                </tr>
                <tr className="hover:bg-slate-50/50 text-slate-600">
                  <td className="py-2.5 px-4 pl-8">Interest Expense</td>
                  <td className="py-2.5 px-4 text-right text-rose-600">{fmt(-inc.interest_expense)}</td>
                </tr>
                <tr className="hover:bg-slate-50/50 text-slate-600">
                  <td className="py-2.5 px-4 pl-8">Income Tax Expense</td>
                  <td className="py-2.5 px-4 text-right text-rose-600">{fmt(-inc.tax_expense)}</td>
                </tr>
                <tr className="bg-emerald-500 text-white font-extrabold text-base">
                  <td className="py-3 px-4 rounded-l-xl">NET INCOME</td>
                  <td className="py-3 px-4 text-right rounded-r-xl">{fmt(inc.net_income)}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      )}

      {activeTab === 'cash_flow' && (
        <div className="space-y-4">
          <div className="bg-slate-50 rounded-xl p-5 border border-slate-200 space-y-3">
            <div className="flex justify-between items-center text-sm font-semibold">
              <span className="text-slate-700">Cash Flow from Operating Activities</span>
              <span className="font-bold text-emerald-600">{fmt(cf.operating_activities)}</span>
            </div>
            <div className="flex justify-between items-center text-sm font-semibold">
              <span className="text-slate-700">Cash Flow from Investing Activities</span>
              <span className="font-bold text-rose-600">{fmt(cf.investing_activities)}</span>
            </div>
            <div className="flex justify-between items-center text-sm font-semibold">
              <span className="text-slate-700">Cash Flow from Financing Activities</span>
              <span className="font-bold text-slate-900">{fmt(cf.financing_activities)}</span>
            </div>
            <div className="pt-3 border-t border-slate-200 flex justify-between items-center font-bold text-base text-brand-900">
              <span>Net Increase / Decrease in Cash</span>
              <span>{fmt(cf.net_change_in_cash)}</span>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'tb' && (
        <div className="space-y-3">
          <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-xl flex items-center justify-between">
            <div className="flex items-center gap-2 text-emerald-800 text-xs font-bold">
              <Check className="w-4 h-4 text-emerald-600" />
              <span>Trial Balance Check: Debit & Credit Total Balanced cleanly</span>
            </div>
            <span className="text-xs font-bold text-emerald-900">Diff: ${tb.difference}</span>
          </div>

          <div className="flex justify-around bg-slate-50 p-4 rounded-xl text-center border border-slate-100">
            <div>
              <p className="text-xs font-semibold text-slate-400">Total Debit Balance</p>
              <p className="text-lg font-bold text-slate-900 mt-1">{fmt(tb.total_debit)}</p>
            </div>
            <div className="w-px bg-slate-200"></div>
            <div>
              <p className="text-xs font-semibold text-slate-400">Total Credit Balance</p>
              <p className="text-lg font-bold text-slate-900 mt-1">{fmt(tb.total_credit)}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
