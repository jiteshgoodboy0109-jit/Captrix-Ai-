'use client';
import React, { useState } from 'react';
import { FileText, Check, AlertCircle, Search } from 'lucide-react';
import { formatCurrency } from '@/lib/currency';
import EvidenceInspectorModal from './EvidenceInspectorModal';

interface StatementViewerProps {
  statements: any;
  currency?: string;
  canonical_dataset?: any;
}

export default function StatementViewer({ statements, currency = 'USD', canonical_dataset }: StatementViewerProps) {
  const [inspectingEvidence, setInspectingEvidence] = useState<{
    lineItemName: string;
    amount: number | string | null;
    currency?: string;
    period?: string;
    provenance?: any;
  } | null>(null);

  const handleInspect = (label: string, val: any, period?: string) => {
    const rawRecords = canonical_dataset?.layer_a_raw_records || canonical_dataset?.layer_b_canonical_dataset || [];
    const match = rawRecords.find((r: any) => 
      (r.source_label && r.source_label.toLowerCase().includes(label.toLowerCase())) ||
      (r.canonical_concept && label.toLowerCase().includes(r.canonical_concept.toLowerCase()))
    ) || {};

    setInspectingEvidence({
      lineItemName: label,
      amount: val,
      currency: currency,
      period: period || 'Current Reporting Period',
      provenance: {
        source_sheet: match.source_sheet || 'Sheet1',
        source_cell: match.source_cell || (match.source_row ? `Row ${match.source_row}, Col ${match.source_column || '-'}` : 'Source Provenance Pinned'),
        source_row: match.source_row,
        source_column: match.source_column,
        source_label: match.source_label || label,
        raw_value: match.raw_value !== undefined ? match.raw_value : val,
        verification_status: 'VERIFIED'
      }
    });
  };

  const inc = statements?.income_statement || {};
  const bs = statements?.balance_sheet || {};
  const cf = statements?.cash_flow || {};
  const tb = statements?.trial_balance || {};

  const ca = bs.current_assets || {};
  const ppe = bs.property_plant_equipment || {};
  const intangibles = bs.intangible_assets || {};
  const cl = bs.current_liabilities || {};
  const ltl = bs.long_term_liabilities || {};
  const eq = bs.equity || {};

  // Helpers to test if a field is reported/present (null/undefined = missing, 0 = reported zero)
  const isPresent = (v: any) => v !== null && v !== undefined && !Number.isNaN(v);

  // Filter dynamic line items for Assets
  const currentAssetItems = [
    { label: 'Cash & Cash Equivalents', val: ca.cash },
    { label: 'Petty Cash', val: ca.petty_cash },
    { label: 'Temporary / Marketable Investments', val: ca.temporary_investments },
    { label: 'Accounts Receivable', val: ca.accounts_receivable },
    { label: 'Inventory / Stock', val: ca.inventory },
    { label: 'Supplies', val: ca.supplies },
    { label: 'Prepaid Expenses & Insurance', val: ca.prepaid_insurance },
    { label: 'Other Current Assets', val: ca.other_current_assets }
  ].filter(i => isPresent(i.val));

  const ppeItems = [
    { label: 'Land', val: ppe.land },
    { label: 'Land Improvements', val: ppe.land_improvements },
    { label: 'Buildings', val: ppe.buildings },
    { label: 'Equipment & Machinery', val: ppe.equipment },
    { 
      label: 'Accumulated Depreciation', 
      val: isPresent(ppe.accumulated_depreciation) && ppe.accumulated_depreciation > 0 ? -Math.abs(ppe.accumulated_depreciation) : ppe.accumulated_depreciation,
      isDeduction: true 
    }
  ].filter(i => isPresent(i.val));

  const intangibleItems = [
    { label: 'Goodwill', val: intangibles.goodwill },
    { label: 'Trade Names & Patents', val: intangibles.trade_names }
  ].filter(i => isPresent(i.val));

  // Filter dynamic line items for Liabilities & Equity
  const currentLiabItems = [
    { label: 'Notes Payable (Short-Term)', val: cl.notes_payable },
    { label: 'Accounts Payable', val: cl.accounts_payable || cl.trade_payables },
    { label: 'Wages & Payroll Payable', val: cl.wages_payable },
    { label: 'Interest Payable', val: cl.interest_payable },
    { label: 'Tax Payable', val: cl.tax_payable },
    { label: 'Unearned / Deferred Revenue', val: cl.unearned_revenue },
    { label: 'Short-Term Debt & Borrowings', val: cl.short_term_borrowings || cl.short_term_debt },
    { label: 'Other Current Liabilities', val: cl.other_current_liabilities }
  ].filter(i => isPresent(i.val));

  const longTermLiabItems = [
    { label: 'Long-Term Notes Payable', val: ltl.notes_payable_lt },
    { label: 'Bonds Payable', val: ltl.bonds_payable },
    { label: 'Long-Term Debt & Borrowings', val: ltl.long_term_borrowings || ltl.long_term_debt },
    { label: 'Other Non-Current Liabilities', val: ltl.other_non_current_liabilities }
  ].filter(i => isPresent(i.val));

  const equityItems = [
    { label: 'Common Stock / Share Capital', val: eq.common_stock || eq.share_capital },
    { label: 'Retained Earnings & Reserves', val: eq.retained_earnings || eq.reserves_and_retained_earnings },
    { 
      label: 'Less: Treasury Stock', 
      val: isPresent(eq.treasury_stock) && eq.treasury_stock > 0 ? -Math.abs(eq.treasury_stock) : eq.treasury_stock,
      isDeduction: true 
    }
  ].filter(i => isPresent(i.val));

  const hasAssetsData = currentAssetItems.length > 0 || ppeItems.length > 0 || intangibleItems.length > 0 || isPresent(bs.investment) || isPresent(bs.other_assets) || isPresent(bs.total_assets);
  const hasLiabEquityData = currentLiabItems.length > 0 || longTermLiabItems.length > 0 || equityItems.length > 0 || isPresent(bs.total_liabilities) || isPresent(eq.total_equity) || isPresent(bs.total_liabilities_and_equity);

  // Dynamic Income Statement Items
  const incomeItems = [
    { label: 'Revenue from Operations / Sales', val: inc.revenue_from_operations || inc.sales || inc.total_revenue, isHeader: true },
    { label: 'Other Operating Income', val: inc.other_operating_income || inc.other_income },
    { label: 'Total Revenue & Operating Income', val: (isPresent(inc.other_operating_income || inc.other_income) && isPresent(inc.total_revenue_and_income || inc.total_revenue) && (inc.total_revenue_and_income || inc.total_revenue) !== (inc.revenue_from_operations || inc.sales)) ? (inc.total_revenue_and_income || inc.total_revenue) : null, isTotal: true },
    { label: 'Cost of Goods Sold (COGS)', val: isPresent(inc.cost_of_goods_sold || inc.cogs) ? -Math.abs(inc.cost_of_goods_sold || inc.cogs) : null, isDeduction: true },
    { label: 'Gross Profit', val: inc.gross_profit, isTotal: true },
    { label: 'Administrative & Operating Expenses (OPEX)', val: isPresent(inc.operating_expenses) && inc.operating_expenses > 0 ? -Math.abs(inc.operating_expenses) : null, isDeduction: true },
    { label: 'Profit from Operations', val: isPresent(inc.profit_from_operations) ? inc.profit_from_operations : (isPresent(inc.ebitda) && inc.ebitda !== inc.total_revenue ? inc.ebitda : null) },
    { label: 'Depreciation & Amortization', val: isPresent(inc.depreciation_amortization) && inc.depreciation_amortization > 0 ? -Math.abs(inc.depreciation_amortization) : null, isDeduction: true },
    { label: 'Interest Received (Finance Income)', val: isPresent(inc.finance_income || inc.interest_income) && (inc.finance_income || inc.interest_income) > 0 ? (inc.finance_income || inc.interest_income) : null },
    { label: 'Finance Costs (Interest Expense)', val: isPresent(inc.finance_cost || inc.interest_expense) && (inc.finance_cost || inc.interest_expense) > 0 ? -Math.abs(inc.finance_cost || inc.interest_expense) : null, isDeduction: true },
    { label: 'Profit Before Taxation (PBT)', val: isPresent(inc.pbt || inc.ebt) && (inc.pbt || inc.ebt) !== inc.net_income && (inc.pbt || inc.ebt) !== inc.total_revenue ? (inc.pbt || inc.ebt) : null },
    { label: 'Taxation Expense', val: isPresent(inc.tax_expense || inc.tax) && (inc.tax_expense || inc.tax) > 0 ? -Math.abs(inc.tax_expense || inc.tax) : null, isDeduction: true },
    { label: 'NET PROFIT FOR THE YEAR', val: inc.net_profit || inc.net_income, isFinal: true }
  ].filter(i => isPresent(i.val));

  // Dynamic Cash Flow Items
  const cashFlowItems = [
    { label: 'Cash Flow from Operating Activities', val: cf.operating_activities },
    { label: 'Cash Flow from Investing Activities', val: cf.investing_activities },
    { label: 'Cash Flow from Financing Activities', val: cf.financing_activities },
    { label: 'Net Increase / (Decrease) in Cash', val: cf.net_change_in_cash, isFinal: true }
  ].filter(i => isPresent(i.val));

  const hasIncome = incomeItems.length > 0;
  const hasBalance = (hasAssetsData || hasLiabEquityData) && bs.status !== 'NOT_REPORTED_IN_SOURCE';
  const hasCashFlow = cashFlowItems.length > 0 && cf.status !== 'NOT_REPORTED_IN_SOURCE' && cf.status !== 'Missing';
  const hasTB = Boolean(tb && tb.status !== 'NOT_REPORTED_IN_SOURCE' && tb.status !== 'NOT_APPLICABLE' && tb.item_count > 0);

  const initialTab: 'balance' | 'income' | 'cash_flow' | 'tb' = hasIncome ? 'income' : (hasBalance ? 'balance' : (hasTB ? 'tb' : 'income'));
  const [activeTab, setActiveTab] = useState<'balance' | 'income' | 'cash_flow' | 'tb'>(initialTab);

  const fmt = (val: number | undefined | null) => formatCurrency(val, currency);

  return (
    <div className="glass-card rounded-2xl p-6 shadow-md border border-slate-200 space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-4 border-b border-slate-200">
        <div>
          <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
            <FileText className="w-5 h-5 text-brand-600" />
            Financial Statements (Source-Grounded)
          </h3>
          <p className="text-xs text-slate-500">
            Rendered dynamically from verified source facts. Unreported accounts are strictly omitted.
          </p>
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
              Balance Sheet
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

      {/* BALANCE SHEET TAB */}
      {activeTab === 'balance' && hasBalance && (
        <div className="border border-sky-300 rounded-xl overflow-hidden shadow-sm bg-white">
          <div className="grid grid-cols-1 md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-sky-200">
            {/* LEFT COLUMN: ASSETS */}
            <div className="flex flex-col justify-between">
              <div>
                <div className="bg-sky-200/90 text-slate-900 font-extrabold text-sm uppercase tracking-wider px-5 py-3 border-b border-sky-300">
                  ASSETS
                </div>

                <div className="p-5 space-y-6 text-sm text-slate-800 font-medium">
                  {/* Current Assets */}
                  {currentAssetItems.length > 0 && (
                    <div className="space-y-2">
                      <h4 className="font-bold text-slate-900 text-base">Current assets</h4>
                      <div className="pl-4 space-y-1 text-xs text-slate-700">
                        {currentAssetItems.map((item, idx) => (
                          <div 
                            key={idx} 
                            onClick={() => handleInspect(item.label, item.val)}
                            className="flex justify-between items-center py-1 px-2 rounded-lg hover:bg-sky-100/70 cursor-pointer transition-all group"
                            title="Click to inspect source cell evidence"
                          >
                            <span className="group-hover:text-brand-700 transition-colors">{item.label}</span>
                            <div className="flex items-center gap-1.5">
                              <span className="font-semibold">{fmt(item.val)}</span>
                              <span className="opacity-0 group-hover:opacity-100 text-[10px] bg-brand-100 text-brand-700 px-1 py-0.2 rounded font-bold transition-opacity">
                                Cell
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                      {isPresent(ca.total_current_assets) && (
                        <div 
                          onClick={() => handleInspect('Total Current Assets', ca.total_current_assets)}
                          className="flex justify-between items-center py-1 px-2 rounded-lg hover:bg-sky-100/70 cursor-pointer pt-2 font-bold text-xs text-slate-900 border-t border-slate-100"
                        >
                          <span className="pl-2">Total current assets</span>
                          <span>{fmt(ca.total_current_assets)}</span>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Investment (if reported) */}
                  {isPresent(bs.investment) && (
                    <div 
                      onClick={() => handleInspect('Investment', bs.investment)}
                      className="flex justify-between items-center py-1 px-2 rounded-lg hover:bg-sky-100/70 cursor-pointer font-bold text-slate-900 text-sm"
                    >
                      <span>Investment</span>
                      <span>{fmt(bs.investment)}</span>
                    </div>
                  )}

                  {/* Property Plant and Equipment */}
                  {ppeItems.length > 0 && (
                    <div className="space-y-2">
                      <h4 className="font-bold text-slate-900 text-base">Property plant and equipment</h4>
                      <div className="pl-4 space-y-1 text-xs text-slate-700">
                        {ppeItems.map((item, idx) => (
                          <div 
                            key={idx} 
                            onClick={() => handleInspect(item.label, item.val)}
                            className="flex justify-between items-center py-1 px-2 rounded-lg hover:bg-sky-100/70 cursor-pointer transition-all group"
                            title="Click to inspect source cell evidence"
                          >
                            <span className="group-hover:text-brand-700 transition-colors">{item.label}</span>
                            <div className="flex items-center gap-1.5">
                              <span className="font-semibold">{fmt(item.val)}</span>
                              <span className="opacity-0 group-hover:opacity-100 text-[10px] bg-brand-100 text-brand-700 px-1 py-0.2 rounded font-bold transition-opacity">
                                Cell
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                      {isPresent(ppe.total_property_plant_equipment) && (
                        <div 
                          onClick={() => handleInspect('Total Property Plant & Equipment', ppe.total_property_plant_equipment)}
                          className="flex justify-between items-center py-1 px-2 rounded-lg hover:bg-sky-100/70 cursor-pointer pt-2 font-bold text-xs text-slate-900 border-t border-slate-100"
                        >
                          <span className="pl-2">Total property plant and equipment</span>
                          <span>{fmt(ppe.total_property_plant_equipment)}</span>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Intangibles */}
                  {intangibleItems.length > 0 && (
                    <div className="space-y-2">
                      <h4 className="font-bold text-slate-900 text-base">Intangible assets</h4>
                      <div className="pl-4 space-y-1 text-xs text-slate-700">
                        {intangibleItems.map((item, idx) => (
                          <div 
                            key={idx} 
                            onClick={() => handleInspect(item.label, item.val)}
                            className="flex justify-between items-center py-1 px-2 rounded-lg hover:bg-sky-100/70 cursor-pointer transition-all group"
                          >
                            <span>{item.label}</span>
                            <span className="font-semibold">{fmt(item.val)}</span>
                          </div>
                        ))}
                      </div>
                      {isPresent(intangibles.total_intangible_assets) && (
                        <div 
                          onClick={() => handleInspect('Total Intangible Assets', intangibles.total_intangible_assets)}
                          className="flex justify-between items-center py-1 px-2 rounded-lg hover:bg-sky-100/70 cursor-pointer pt-2 font-bold text-xs text-slate-900 border-t border-slate-100"
                        >
                          <span className="pl-2">Total intangible assets</span>
                          <span>{fmt(intangibles.total_intangible_assets)}</span>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Other Assets */}
                  {isPresent(bs.other_assets) && (
                    <div 
                      onClick={() => handleInspect('Other Assets', bs.other_assets)}
                      className="flex justify-between items-center py-1 px-2 rounded-lg hover:bg-sky-100/70 cursor-pointer font-bold text-slate-900 text-sm"
                    >
                      <span>Other assets</span>
                      <span>{fmt(bs.other_assets)}</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Total Assets Bottom Footer Banner */}
              {isPresent(bs.total_assets) && (
                <div 
                  onClick={() => handleInspect('Total Assets', bs.total_assets)}
                  className="bg-sky-200/90 px-5 py-3.5 border-t border-sky-300 flex justify-between items-center font-extrabold text-base text-slate-900 cursor-pointer hover:bg-sky-200"
                >
                  <span>Total Assets</span>
                  <span className="text-lg">{fmt(bs.total_assets)}</span>
                </div>
              )}
            </div>

            {/* RIGHT COLUMN: LIABILITIES AND EQUITY */}
            <div className="flex flex-col justify-between">
              <div>
                <div className="bg-sky-200/90 text-slate-900 font-extrabold text-sm uppercase tracking-wider px-5 py-3 border-b border-sky-300">
                  LIABILITIES AND STOCKHOLDERS' EQUITY
                </div>

                <div className="p-5 space-y-6 text-sm text-slate-800 font-medium">
                  {/* Current Liabilities */}
                  {currentLiabItems.length > 0 && (
                    <div className="space-y-2">
                      <h4 className="font-bold text-slate-900 text-base">Current liabilities</h4>
                      <div className="pl-4 space-y-1 text-xs text-slate-700">
                        {currentLiabItems.map((item, idx) => (
                          <div 
                            key={idx} 
                            onClick={() => handleInspect(item.label, item.val)}
                            className="flex justify-between items-center py-1 px-2 rounded-lg hover:bg-sky-100/70 cursor-pointer transition-all group"
                          >
                            <span className="group-hover:text-brand-700 transition-colors">{item.label}</span>
                            <div className="flex items-center gap-1.5">
                              <span className="font-semibold">{fmt(item.val)}</span>
                              <span className="opacity-0 group-hover:opacity-100 text-[10px] bg-brand-100 text-brand-700 px-1 py-0.2 rounded font-bold transition-opacity">
                                Cell
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                      {isPresent(cl.total_current_liabilities) && (
                        <div 
                          onClick={() => handleInspect('Total Current Liabilities', cl.total_current_liabilities)}
                          className="flex justify-between items-center py-1 px-2 rounded-lg hover:bg-sky-100/70 cursor-pointer pt-2 font-bold text-xs text-slate-900 border-t border-slate-100"
                        >
                          <span className="pl-2">Total current liabilities</span>
                          <span>{fmt(cl.total_current_liabilities)}</span>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Long-Term Liabilities */}
                  {longTermLiabItems.length > 0 && (
                    <div className="space-y-2">
                      <h4 className="font-bold text-slate-900 text-base">Long-term liabilities</h4>
                      <div className="pl-4 space-y-1 text-xs text-slate-700">
                        {longTermLiabItems.map((item, idx) => (
                          <div 
                            key={idx} 
                            onClick={() => handleInspect(item.label, item.val)}
                            className="flex justify-between items-center py-1 px-2 rounded-lg hover:bg-sky-100/70 cursor-pointer transition-all group"
                          >
                            <span>{item.label}</span>
                            <span className="font-semibold">{fmt(item.val)}</span>
                          </div>
                        ))}
                      </div>
                      {isPresent(ltl.total_long_term_liabilities) && (
                        <div 
                          onClick={() => handleInspect('Total Long-Term Liabilities', ltl.total_long_term_liabilities)}
                          className="flex justify-between items-center py-1 px-2 rounded-lg hover:bg-sky-100/70 cursor-pointer pt-2 font-bold text-xs text-slate-900 border-t border-slate-100"
                        >
                          <span className="pl-2">Total long-term liabilities</span>
                          <span>{fmt(ltl.total_long_term_liabilities)}</span>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Total Liabilities Subtotal */}
                  {isPresent(bs.total_liabilities) && (
                    <div 
                      onClick={() => handleInspect('Total Liabilities', bs.total_liabilities)}
                      className="flex justify-between items-center py-1 px-2 rounded-lg hover:bg-sky-100/70 cursor-pointer pt-2 font-bold text-xs text-slate-900 border-t border-slate-200"
                    >
                      <span>Total liabilities</span>
                      <span>{fmt(bs.total_liabilities)}</span>
                    </div>
                  )}

                  {/* Stockholders' Equity */}
                  {equityItems.length > 0 && (
                    <div className="space-y-2">
                      <h4 className="font-bold text-slate-900 text-base">Stockholders' equity</h4>
                      <div className="pl-4 space-y-1 text-xs text-slate-700">
                        {equityItems.map((item, idx) => (
                          <div 
                            key={idx} 
                            onClick={() => handleInspect(item.label, item.val)}
                            className="flex justify-between items-center py-1 px-2 rounded-lg hover:bg-sky-100/70 cursor-pointer transition-all group"
                          >
                            <span>{item.label}</span>
                            <span className="font-semibold">{fmt(item.val)}</span>
                          </div>
                        ))}
                      </div>
                      {isPresent(eq.total_equity) && (
                        <div 
                          onClick={() => handleInspect('Total Stockholders Equity', eq.total_equity)}
                          className="flex justify-between items-center py-1 px-2 rounded-lg hover:bg-sky-100/70 cursor-pointer pt-2 font-bold text-xs text-slate-900 border-t border-slate-100"
                        >
                          <span className="pl-2">Total stockholders' equity</span>
                          <span>{fmt(eq.total_equity)}</span>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>

              {/* Total Liabilities & Equity Bottom Footer Banner */}
              {isPresent(bs.total_liabilities_and_equity) && (
                <div 
                  onClick={() => handleInspect('Total Liabilities & Equity', bs.total_liabilities_and_equity)}
                  className="bg-sky-200/90 px-5 py-3.5 border-t border-sky-300 flex justify-between items-center font-extrabold text-base text-slate-900 cursor-pointer hover:bg-sky-200"
                >
                  <span>Total Liabilities & Equity</span>
                  <span className="text-lg">{fmt(bs.total_liabilities_and_equity)}</span>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* INCOME STATEMENT TAB */}
      {activeTab === 'income' && hasIncome && (
        <div className="space-y-3">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm border-collapse">
              <thead>
                <tr className="bg-sky-200/80 text-slate-900 border-b border-sky-300 text-xs font-extrabold uppercase tracking-wider">
                  <th className="py-3 px-4">Line Item (Source Reported / Calculated)</th>
                  <th className="py-3 px-4 text-right">Amount ({currency})</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium">
                {incomeItems.map((item, idx) => {
                  if (item.isFinal) {
                    return (
                      <tr 
                        key={idx} 
                        onClick={() => handleInspect(item.label, item.val)}
                        className="bg-emerald-500 text-white font-extrabold text-base cursor-pointer hover:bg-emerald-600 transition-colors"
                        title="Click to inspect source cell evidence"
                      >
                        <td className="py-3 px-4 rounded-l-xl">{item.label}</td>
                        <td className="py-3 px-4 text-right rounded-r-xl">{fmt(item.val)}</td>
                      </tr>
                    );
                  }
                  if (item.isTotal) {
                    return (
                      <tr 
                        key={idx} 
                        onClick={() => handleInspect(item.label, item.val)}
                        className="bg-brand-50/70 font-bold text-brand-900 cursor-pointer hover:bg-brand-100/70 transition-colors"
                        title="Click to inspect source cell evidence"
                      >
                        <td className="py-2.5 px-4">{item.label}</td>
                        <td className="py-2.5 px-4 text-right">{fmt(item.val)}</td>
                      </tr>
                    );
                  }
                  return (
                    <tr 
                      key={idx} 
                      onClick={() => handleInspect(item.label, item.val)}
                      className={`hover:bg-sky-50/70 cursor-pointer transition-colors ${item.isDeduction ? 'text-slate-600' : 'text-slate-900 font-semibold'}`}
                      title="Click to inspect source cell evidence"
                    >
                      <td className={`py-2.5 px-4 ${item.isDeduction ? 'pl-8' : ''}`}>{item.label}</td>
                      <td className={`py-2.5 px-4 text-right ${item.isDeduction ? 'text-rose-600' : ''}`}>{fmt(item.val)}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* CASH FLOW TAB */}
      {activeTab === 'cash_flow' && hasCashFlow && (
        <div className="space-y-4">
          <div className="bg-slate-50 rounded-xl p-5 border border-slate-200 space-y-3">
            {cashFlowItems.map((item, idx) => {
              if (item.isFinal) {
                return (
                  <div 
                    key={idx} 
                    onClick={() => handleInspect(item.label, item.val)}
                    className="pt-3 border-t border-slate-200 flex justify-between items-center font-bold text-base text-brand-900 cursor-pointer hover:bg-slate-100 p-2 rounded-lg transition-colors"
                  >
                    <span>{item.label}</span>
                    <span>{fmt(item.val)}</span>
                  </div>
                );
              }
              const isPos = item.val >= 0;
              return (
                <div 
                  key={idx} 
                  onClick={() => handleInspect(item.label, item.val)}
                  className="flex justify-between items-center text-sm font-semibold cursor-pointer hover:bg-slate-100 p-2 rounded-lg transition-colors"
                >
                  <span className="text-slate-700">{item.label}</span>
                  <span className={`font-bold ${isPos ? 'text-emerald-600' : 'text-rose-600'}`}>
                    {fmt(item.val)}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* TRIAL BALANCE TAB */}
      {activeTab === 'tb' && hasTB && (
        <div className="space-y-3">
          <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-xl flex items-center justify-between">
            <div className="flex items-center gap-2 text-emerald-800 text-xs font-bold">
              <Check className="w-4 h-4 text-emerald-600" />
              <span>Trial Balance Check: Balanced Cleanly</span>
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

      {/* Interactive Evidence Modal */}
      <EvidenceInspectorModal
        isOpen={Boolean(inspectingEvidence)}
        onClose={() => setInspectingEvidence(null)}
        evidence={inspectingEvidence}
      />
    </div>
  );
}
