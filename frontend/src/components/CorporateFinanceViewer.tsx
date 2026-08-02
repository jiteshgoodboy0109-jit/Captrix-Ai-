'use client';
import React from 'react';
import { Building2, TrendingUp, DollarSign, Clock, Layers } from 'lucide-react';

interface CorporateFinanceProps {
  corporateFinance: any;
}

export default function CorporateFinanceViewer({ corporateFinance }: CorporateFinanceProps) {
  if (!corporateFinance) return null;

  const cb = corporateFinance.capital_budgeting || {};
  const cs = corporateFinance.capital_structure || {};
  const wc = corporateFinance.working_capital_cycle || {};

  const fmt = (val: number) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(val || 0);

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-brand-50 text-brand-700 flex items-center justify-center font-bold">
          <Building2 className="w-5 h-5" />
        </div>
        <div>
          <h3 className="text-base font-bold text-slate-900">Corporate Finance & Valuation Module</h3>
          <p className="text-xs text-slate-500">Capital budgeting simulation, WACC valuation model, & cash conversion cycle</p>
        </div>
      </div>

      {/* Capital Budgeting & WACC Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Card 1: Capital Budgeting */}
        <div className="glass-card rounded-2xl p-5 border border-slate-200 space-y-4">
          <div className="flex items-center justify-between border-b pb-3 border-slate-100">
            <h4 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-emerald-600" />
              Capital Budgeting (NPV/IRR)
            </h4>
            <span className="text-[10px] font-extrabold px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
              {cb.verdict}
            </span>
          </div>

          <div className="space-y-3 text-xs">
            <div className="flex justify-between text-slate-600">
              <span>Simulated Initial CAPEX</span>
              <span className="font-bold text-slate-900">{fmt(cb.initial_investment)}</span>
            </div>
            <div className="flex justify-between text-slate-600">
              <span>Projected Annual FCF</span>
              <span className="font-bold text-slate-900">{fmt(cb.projected_annual_fcf)}</span>
            </div>
            <div className="flex justify-between text-slate-600">
              <span>Hurdle Discount Rate</span>
              <span className="font-bold text-slate-900">{cb.discount_rate}%</span>
            </div>
            <div className="p-3 bg-emerald-50/50 rounded-xl border border-emerald-100 flex justify-between items-baseline">
              <span className="font-bold text-emerald-900">Net Present Value (NPV)</span>
              <span className="text-lg font-extrabold text-emerald-700">{fmt(cb.npv)}</span>
            </div>
            <div className="flex justify-between text-slate-600">
              <span>Internal Rate of Return (IRR)</span>
              <span className="font-bold text-brand-700">{cb.irr}%</span>
            </div>
            <div className="flex justify-between text-slate-600">
              <span>Payback Period</span>
              <span className="font-bold text-slate-900">{cb.payback_period} years</span>
            </div>
            <div className="flex justify-between text-slate-600">
              <span>Profitability Index (PI)</span>
              <span className="font-bold text-slate-900">{cb.profitability_index}x</span>
            </div>
          </div>
        </div>

        {/* Card 2: Capital Structure & WACC */}
        <div className="glass-card rounded-2xl p-5 border border-slate-200 space-y-4">
          <div className="flex items-center justify-between border-b pb-3 border-slate-100">
            <h4 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <DollarSign className="w-4 h-4 text-brand-600" />
              WACC & Cost of Capital
            </h4>
            <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-brand-50 text-brand-700 border border-brand-200">
              VALUATION
            </span>
          </div>

          <div className="space-y-3 text-xs">
            <div className="flex justify-between text-slate-600">
              <span>Cost of Debt (Pre-Tax)</span>
              <span className="font-bold text-slate-900">{cs.cost_of_debt}%</span>
            </div>
            <div className="flex justify-between text-slate-600">
              <span>After-Tax Cost of Debt ($K_d$)</span>
              <span className="font-bold text-slate-900">{cs.after_tax_cost_of_debt}%</span>
            </div>
            <div className="flex justify-between text-slate-600">
              <span>Cost of Equity ($K_e$ CAPM)</span>
              <span className="font-bold text-slate-900">{cs.cost_of_equity}%</span>
            </div>
            <div className="p-3 bg-brand-50/50 rounded-xl border border-brand-100 flex justify-between items-baseline">
              <span className="font-bold text-brand-900">Weighted Cost of Capital (WACC)</span>
              <span className="text-lg font-extrabold text-brand-700">{cs.wacc}%</span>
            </div>
            <div className="flex justify-between text-slate-600">
              <span>Debt Financing Ratio</span>
              <span className="font-bold text-slate-900">{(cs.debt_ratio * 100).toFixed(1)}%</span>
            </div>
            <div className="flex justify-between text-slate-600">
              <span>Equity Financing Ratio</span>
              <span className="font-bold text-slate-900">{(cs.equity_ratio * 100).toFixed(1)}%</span>
            </div>
          </div>
        </div>

        {/* Card 3: Working Capital & CCC Pipeline */}
        <div className="glass-card rounded-2xl p-5 border border-slate-200 space-y-4">
          <div className="flex items-center justify-between border-b pb-3 border-slate-100">
            <h4 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <Clock className="w-4 h-4 text-cyan-600" />
              Cash Conversion Cycle (CCC)
            </h4>
            <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-cyan-50 text-cyan-700 border border-cyan-200">
              EFFICIENCY
            </span>
          </div>

          <div className="space-y-3 text-xs">
            <div className="flex justify-between text-slate-600">
              <span>Days Inventory Outstanding (DIO)</span>
              <span className="font-bold text-slate-900">{wc.days_inventory_outstanding_dio} days</span>
            </div>
            <div className="flex justify-between text-slate-600">
              <span>Days Sales Outstanding (DSO)</span>
              <span className="font-bold text-slate-900">{wc.days_sales_outstanding_dso} days</span>
            </div>
            <div className="flex justify-between text-slate-600">
              <span>Days Payable Outstanding (DPO)</span>
              <span className="font-bold text-rose-600">({wc.days_payable_outstanding_dpo}) days</span>
            </div>
            <div className="p-3 bg-cyan-50/50 rounded-xl border border-cyan-100 flex justify-between items-baseline">
              <span className="font-bold text-cyan-900">Net Cash Conversion Cycle</span>
              <span className="text-lg font-extrabold text-cyan-700">{wc.cash_conversion_cycle} days</span>
            </div>
            <div className="flex justify-between text-slate-600">
              <span>Gross Operating Cycle</span>
              <span className="font-bold text-slate-900">{wc.operating_cycle} days</span>
            </div>
            <div className="flex justify-between text-slate-600">
              <span>Net Working Capital</span>
              <span className="font-bold text-slate-900">{fmt(wc.net_working_capital)}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
