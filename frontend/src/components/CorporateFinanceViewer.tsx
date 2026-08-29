'use client';
import React, { useState } from 'react';
import { 
  Building2, 
  TrendingUp, 
  DollarSign, 
  Clock, 
  Layers, 
  BarChart2, 
  Sliders, 
  ShieldCheck, 
  Info,
  ChevronRight,
  TrendingDown,
  Sparkles
} from 'lucide-react';

import { formatCurrency, getCurrencySymbol } from '@/lib/currency';

interface CorporateFinanceProps {
  corporateFinance: any;
  currency?: string;
}

export default function CorporateFinanceViewer({ corporateFinance, currency = 'USD' }: CorporateFinanceProps) {
  const [activeSubTab, setActiveSubTab] = useState<'valuation' | 'scenario' | 'budgeting' | 'wacc'>('valuation');

  if (!corporateFinance) return null;

  const cb = corporateFinance.capital_budgeting || {};
  const cs = corporateFinance.capital_structure || {};
  const wc = corporateFinance.working_capital_cycle || {};
  const val = corporateFinance.valuation_model || {};
  const scen = corporateFinance.scenario_analysis || {};

  const fmt = (valNum: number | undefined | null) => formatCurrency(valNum, currency);

  const fmtDays = (days: number | undefined | null) => {
    if (days === undefined || days === null || isNaN(days)) return 'Not Reported';
    return `${days.toFixed(1)} days`;
  };

  return (
    <div className="space-y-6">
      {/* Top Header & Navigation Sub-Tabs */}
      <div className="glass-card rounded-2xl p-6 border border-slate-200 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-2xl bg-brand-50 text-brand-700 flex items-center justify-center font-bold shadow-xs">
            <Building2 className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
              Corporate Finance & Intrinsic Valuation Engine
            </h3>
            <p className="text-xs text-slate-500">
              Institutional DCF valuation, scenario sensitivity forecasting, WACC capital structure, & cash conversion cycle
            </p>
          </div>
        </div>

        {/* View Switcher Sub-Tabs */}
        <div className="flex items-center gap-1.5 bg-slate-100 p-1 rounded-xl overflow-x-auto scrollbar-none">
          <button
            onClick={() => setActiveSubTab('valuation')}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all shrink-0 ${
              activeSubTab === 'valuation' ? 'bg-brand-600 text-white shadow-sm' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            DCF Valuation Model
          </button>
          <button
            onClick={() => setActiveSubTab('scenario')}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all shrink-0 ${
              activeSubTab === 'scenario' ? 'bg-brand-600 text-white shadow-sm' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Scenario Sensitivity (3-Case)
          </button>
          <button
            onClick={() => setActiveSubTab('budgeting')}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all shrink-0 ${
              activeSubTab === 'budgeting' ? 'bg-brand-600 text-white shadow-sm' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Capital Budgeting (NPV/IRR)
          </button>
          <button
            onClick={() => setActiveSubTab('wacc')}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all shrink-0 ${
              activeSubTab === 'wacc' ? 'bg-brand-600 text-white shadow-sm' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            WACC & Capital Structure
          </button>
        </div>
      </div>

      {/* Sub-Tab 1: DCF Intrinsic Valuation Model */}
      {activeSubTab === 'valuation' && (
        <div className="space-y-6">
          {val.is_calculable ? (
            <>
              {/* Top Key Metrics Banner */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="glass-card rounded-2xl p-5 border border-sky-200 bg-gradient-to-br from-sky-50/50 to-white shadow-xs">
                  <span className="text-xs font-semibold text-slate-500 block">Enterprise Value (EV)</span>
                  <span className="text-2xl font-black text-sky-950 mt-1 block">{fmt(val.enterprise_value)}</span>
                  <span className="text-[10px] text-sky-700 font-bold mt-1 block">PV of Cash Flows + Terminal Value</span>
                </div>

                <div className="glass-card rounded-2xl p-5 border border-emerald-200 bg-gradient-to-br from-emerald-50/50 to-white shadow-xs">
                  <span className="text-xs font-semibold text-slate-500 block">Implied Equity Value</span>
                  <span className="text-2xl font-black text-emerald-950 mt-1 block">{fmt(val.equity_value)}</span>
                  <span className="text-[10px] text-emerald-700 font-bold mt-1 block">EV less Net Debt (${val.parameters?.net_debt_deducted})</span>
                </div>

                <div className="glass-card rounded-2xl p-5 border border-brand-200 bg-gradient-to-br from-brand-50/50 to-white shadow-xs">
                  <span className="text-xs font-semibold text-slate-500 block">WACC Hurdle Discount Rate</span>
                  <span className="text-2xl font-black text-brand-950 mt-1 block">{val.parameters?.wacc_discount_rate}%</span>
                  <span className="text-[10px] text-brand-700 font-bold mt-1 block">Weighted Cost of Capital</span>
                </div>

                <div className="glass-card rounded-2xl p-5 border border-indigo-200 bg-gradient-to-br from-indigo-50/50 to-white shadow-xs">
                  <span className="text-xs font-semibold text-slate-500 block">Perpetual Growth Rate ($g$)</span>
                  <span className="text-2xl font-black text-indigo-950 mt-1 block">{val.parameters?.perpetual_growth_rate}%</span>
                  <span className="text-[10px] text-indigo-700 font-bold mt-1 block">Gordon Growth Terminal Curve</span>
                </div>
              </div>

              {/* 5-Year Projected FCFF Waterfall Table */}
              <div className="glass-card rounded-2xl p-6 border border-slate-200 shadow-sm space-y-4">
                <div className="flex items-center justify-between">
                  <h4 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                    <BarChart2 className="w-4 h-4 text-brand-600" />
                    5-Year Projected Free Cash Flow to Firm (FCFF)
                  </h4>
                  <span className="text-xs font-mono px-2.5 py-1 rounded-full bg-slate-100 text-slate-700 font-bold">
                    Method: {val.methodology}
                  </span>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs border-collapse">
                    <thead>
                      <tr className="bg-slate-50 text-slate-700 font-extrabold uppercase tracking-wider border-b border-slate-200">
                        <th className="py-2.5 px-4">Period</th>
                        <th className="py-2.5 px-4 text-right">Projected FCFF</th>
                        <th className="py-2.5 px-4 text-right">Discount Factor ($1/(1+WACC)^t$)</th>
                        <th className="py-2.5 px-4 text-right">Present Value (PV)</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 font-medium">
                      {val.projected_cash_flows?.map((cfItem: any, idx: number) => (
                        <tr key={idx} className="hover:bg-slate-50/60">
                          <td className="py-2.5 px-4 font-bold text-slate-900">{cfItem.year}</td>
                          <td className="py-2.5 px-4 text-right font-semibold text-brand-700">{fmt(cfItem.projected_fcf)}</td>
                          <td className="py-2.5 px-4 text-right font-mono text-slate-500">{cfItem.discount_factor}</td>
                          <td className="py-2.5 px-4 text-right font-bold text-slate-900">{fmt(cfItem.present_value)}</td>
                        </tr>
                      ))}
                      <tr className="bg-sky-50/70 font-bold border-t border-sky-200">
                        <td className="py-3 px-4 text-sky-950 font-extrabold">Sum of Discrete PV Cash Flows (Years 1-5)</td>
                        <td className="py-3 px-4"></td>
                        <td className="py-3 px-4"></td>
                        <td className="py-3 px-4 text-right text-sky-950 font-black text-sm">{fmt(val.sum_pv_discrete_cash_flows)}</td>
                      </tr>
                      <tr className="bg-emerald-50/70 font-bold border-t border-emerald-200">
                        <td className="py-3 px-4 text-emerald-950 font-extrabold">Present Value of Terminal Value (Gordon Growth)</td>
                        <td className="py-3 px-4 text-right text-emerald-800 font-mono">TV: {fmt(val.terminal_value)}</td>
                        <td className="py-3 px-4"></td>
                        <td className="py-3 px-4 text-right text-emerald-950 font-black text-sm">{fmt(val.pv_terminal_value)}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Valuation Sensitivity Table (WACC vs Perpetual Growth Rate) */}
              {val.sensitivity_matrix && val.sensitivity_matrix.length > 0 && (
                <div className="glass-card rounded-2xl p-6 border border-slate-200 shadow-sm space-y-4">
                  <div className="flex items-center justify-between">
                    <h4 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                      <Sliders className="w-4 h-4 text-indigo-600" />
                      DCF Enterprise Valuation Sensitivity Matrix
                    </h4>
                    <span className="text-xs text-slate-500">WACC vs. Perpetual Growth Rate ($g$)</span>
                  </div>

                  <div className="overflow-x-auto">
                    <table className="w-full text-center text-xs border-collapse">
                      <thead>
                        <tr className="bg-slate-100 text-slate-800 font-extrabold uppercase tracking-wider border-b border-slate-200">
                          <th className="py-2.5 px-3 text-left">WACC Discount Rate</th>
                          {val.sensitivity_matrix[0].valuations.map((v: any, i: number) => (
                            <th key={i} className="py-2.5 px-3">Growth $g = {v.growth_pct}\%$</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100 font-medium">
                        {val.sensitivity_matrix.map((row: any, rIdx: number) => (
                          <tr key={rIdx} className="hover:bg-slate-50/60">
                            <td className="py-2.5 px-3 text-left font-bold text-slate-900 bg-slate-50">{row.wacc_pct}% WACC</td>
                            {row.valuations.map((cell: any, cIdx: number) => (
                              <td key={cIdx} className="py-2.5 px-3 font-semibold text-slate-800">
                                {cell.enterprise_value ? fmt(cell.enterprise_value) : '—'}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="p-8 text-center bg-slate-50 rounded-2xl border border-dashed border-slate-300 space-y-2">
              <Info className="w-8 h-8 text-slate-400 mx-auto" />
              <h4 className="text-sm font-bold text-slate-700">DCF Valuation Not Computable</h4>
              <p className="text-xs text-slate-500 max-w-md mx-auto">
                {val.reason || "Positive operating revenue and cash flow items must be present in the uploaded workbook to construct a grounded DCF valuation model."}
              </p>
            </div>
          )}
        </div>
      )}

      {/* Sub-Tab 2: Scenario Sensitivity (3-Case Analysis) */}
      {activeSubTab === 'scenario' && (
        <div className="space-y-6">
          {scen.is_calculable ? (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {scen.scenarios?.map((s: any, idx: number) => {
                const isBear = s.case.toLowerCase().includes('bear');
                const isBull = s.case.toLowerCase().includes('bull');
                const themeClass = isBear 
                  ? 'border-rose-200 bg-gradient-to-b from-rose-50/40 to-white' 
                  : isBull 
                    ? 'border-emerald-200 bg-gradient-to-b from-emerald-50/40 to-white' 
                    : 'border-sky-200 bg-gradient-to-b from-sky-50/40 to-white';

                const badgeColor = isBear 
                  ? 'bg-rose-100 text-rose-800 border-rose-200' 
                  : isBull 
                    ? 'bg-emerald-100 text-emerald-800 border-emerald-200' 
                    : 'bg-sky-100 text-sky-800 border-sky-200';

                return (
                  <div key={idx} className={`glass-card rounded-2xl p-6 border ${themeClass} shadow-sm space-y-5 flex flex-col justify-between`}>
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <span className={`text-[11px] font-extrabold px-3 py-1 rounded-full border ${badgeColor}`}>
                          {s.probability} Probability
                        </span>
                        {isBear ? (
                          <TrendingDown className="w-5 h-5 text-rose-500" />
                        ) : (
                          <TrendingUp className={`w-5 h-5 ${isBull ? 'text-emerald-500' : 'text-sky-500'}`} />
                        )}
                      </div>

                      <div>
                        <h4 className="text-base font-extrabold text-slate-900">{s.case}</h4>
                        <p className="text-xs text-slate-500 mt-1">{s.liquidity_impact}</p>
                      </div>

                      <div className="space-y-3 pt-2 text-xs divide-y divide-slate-100">
                        <div className="flex justify-between text-slate-600 pt-2">
                          <span>Revenue Growth</span>
                          <span className={`font-bold ${s.revenue_growth_pct < 0 ? 'text-rose-600' : 'text-emerald-600'}`}>
                            {s.revenue_growth_pct > 0 ? `+${s.revenue_growth_pct}%` : `${s.revenue_growth_pct}%`}
                          </span>
                        </div>
                        <div className="flex justify-between text-slate-600 pt-2">
                          <span>Projected Revenue</span>
                          <span className="font-bold text-slate-900">{fmt(s.projected_revenue)}</span>
                        </div>
                        <div className="flex justify-between text-slate-600 pt-2">
                          <span>Target Net Margin</span>
                          <span className="font-bold text-slate-900">{s.projected_net_margin_pct}%</span>
                        </div>
                        <div className="flex justify-between text-slate-900 font-extrabold pt-3 text-sm">
                          <span>Projected Net Income</span>
                          <span className={s.projected_net_income < 0 ? 'text-rose-600' : 'text-emerald-700'}>
                            {fmt(s.projected_net_income)}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="p-8 text-center bg-slate-50 rounded-2xl border border-dashed border-slate-300">
              <p className="text-xs text-slate-500">Scenario analysis requires valid revenue in the uploaded workbook.</p>
            </div>
          )}
        </div>
      )}

      {/* Sub-Tab 3: Capital Budgeting & Cash Conversion Cycle */}
      {activeSubTab === 'budgeting' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Card: Capital Budgeting */}
          <div className="glass-card rounded-2xl p-6 border border-slate-200 shadow-sm space-y-4">
            <div className="flex items-center justify-between border-b pb-3 border-slate-100">
              <h4 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-emerald-600" />
                Capital Budgeting Feasibility (NPV / IRR)
              </h4>
              <span className={`text-[10px] font-extrabold px-2.5 py-0.5 rounded-full border ${
                cb.is_calculable ? 'bg-emerald-50 text-emerald-700 border-emerald-200' : 'bg-slate-100 text-slate-600 border-slate-200'
              }`}>
                {cb.verdict}
              </span>
            </div>

            <div className="space-y-3 text-xs">
              <div className="flex justify-between text-slate-600">
                <span>Simulated Baseline CAPEX</span>
                <span className="font-bold text-slate-900">{fmt(cb.initial_investment)}</span>
              </div>
              <div className="flex justify-between text-slate-600">
                <span>Projected Annual Operational FCF</span>
                <span className="font-bold text-slate-900">{fmt(cb.projected_annual_fcf)}</span>
              </div>
              <div className="flex justify-between text-slate-600">
                <span>Hurdle Discount Rate</span>
                <span className="font-bold text-slate-900">{cb.discount_rate}%</span>
              </div>
              <div className="p-4 bg-emerald-50/60 rounded-xl border border-emerald-100 flex justify-between items-baseline">
                <span className="font-bold text-emerald-900">Net Present Value (NPV)</span>
                <span className="text-xl font-extrabold text-emerald-700">{fmt(cb.npv)}</span>
              </div>
              <div className="flex justify-between text-slate-600">
                <span>Internal Rate of Return (IRR)</span>
                <span className="font-bold text-brand-700">{cb.irr}%</span>
              </div>
            </div>
          </div>

          {/* Card: Working Capital & Cash Conversion Cycle */}
          <div className="glass-card rounded-2xl p-6 border border-slate-200 shadow-sm space-y-4">
            <div className="flex items-center justify-between border-b pb-3 border-slate-100">
              <h4 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                <Clock className="w-4 h-4 text-cyan-600" />
                Working Capital Cycle & Cash Conversion (CCC)
              </h4>
              <span className="text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-cyan-50 text-cyan-700 border border-cyan-200">
                EFFICIENCY
              </span>
            </div>

            <div className="space-y-3 text-xs">
              <div className="flex justify-between text-slate-600">
                <span>Days Inventory Outstanding (DIO)</span>
                <span className="font-bold text-slate-900">{fmtDays(wc.days_inventory_outstanding_dio)}</span>
              </div>
              <div className="flex justify-between text-slate-600">
                <span>Days Sales Outstanding (DSO)</span>
                <span className="font-bold text-slate-900">{fmtDays(wc.days_sales_outstanding_dso)}</span>
              </div>
              <div className="flex justify-between text-slate-600">
                <span>Days Payable Outstanding (DPO)</span>
                <span className="font-bold text-rose-600">{fmtDays(wc.days_payable_outstanding_dpo)}</span>
              </div>
              <div className="p-4 bg-cyan-50/60 rounded-xl border border-cyan-100 flex justify-between items-baseline">
                <span className="font-bold text-cyan-900">Net Cash Conversion Cycle</span>
                <span className="text-xl font-extrabold text-cyan-700">{fmtDays(wc.cash_conversion_cycle)}</span>
              </div>
              <div className="flex justify-between text-slate-600">
                <span>Net Working Capital</span>
                <span className="font-bold text-slate-900">{fmt(wc.net_working_capital)}</span>
              </div>
              <p className="text-[11px] text-slate-500 italic mt-2">{wc.interpretation}</p>
            </div>
          </div>
        </div>
      )}

      {/* Sub-Tab 4: Capital Structure & WACC Breakdown */}
      {activeSubTab === 'wacc' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="glass-card rounded-2xl p-6 border border-slate-200 shadow-sm space-y-4">
            <div className="flex items-center justify-between border-b pb-3 border-slate-100">
              <h4 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                <DollarSign className="w-4 h-4 text-brand-600" />
                Weighted Average Cost of Capital (WACC)
              </h4>
              <span className="text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-brand-50 text-brand-700 border border-brand-200">
                CAPITAL PRICING
              </span>
            </div>

            <div className="space-y-3 text-xs">
              <div className="flex justify-between text-slate-600">
                <span>Pre-Tax Cost of Debt ($K_d$)</span>
                <span className="font-bold text-slate-900">{cs.cost_of_debt}%</span>
              </div>
              <div className="flex justify-between text-slate-600">
                <span>After-Tax Cost of Debt ($K_d \times (1-T)$)</span>
                <span className="font-bold text-slate-900">{cs.after_tax_cost_of_debt}%</span>
              </div>
              <div className="flex justify-between text-slate-600">
                <span>Cost of Equity ($K_e$ CAPM model)</span>
                <span className="font-bold text-slate-900">{cs.cost_of_equity}%</span>
              </div>
              <div className="p-4 bg-brand-50/60 rounded-xl border border-brand-100 flex justify-between items-baseline">
                <span className="font-bold text-brand-900">Calculated WACC</span>
                <span className="text-xl font-extrabold text-brand-700">{cs.wacc}%</span>
              </div>
            </div>
          </div>

          <div className="glass-card rounded-2xl p-6 border border-slate-200 shadow-sm space-y-4">
            <div className="flex items-center justify-between border-b pb-3 border-slate-100">
              <h4 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                <Layers className="w-4 h-4 text-indigo-600" />
                Capital Structure Composition
              </h4>
              <span className="text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-indigo-50 text-indigo-700 border border-indigo-200">
                LEVERAGE
              </span>
            </div>

            <div className="space-y-4 text-xs">
              <div className="space-y-1.5">
                <div className="flex justify-between text-slate-700 font-semibold">
                  <span>Debt Financing Ratio</span>
                  <span>{(cs.debt_ratio * 100).toFixed(1)}%</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                  <div className="bg-rose-500 h-full rounded-full" style={{ width: `${Math.min(100, cs.debt_ratio * 100)}%` }}></div>
                </div>
              </div>

              <div className="space-y-1.5">
                <div className="flex justify-between text-slate-700 font-semibold">
                  <span>Equity Financing Ratio</span>
                  <span>{(cs.equity_ratio * 100).toFixed(1)}%</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                  <div className="bg-emerald-500 h-full rounded-full" style={{ width: `${Math.min(100, cs.equity_ratio * 100)}%` }}></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
