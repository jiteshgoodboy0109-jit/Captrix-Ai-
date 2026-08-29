/**
 * Currency Formatting & Symbol Utility
 * Provides locale-aware monetary formatting and symbol extraction for global accounting.
 */

export const CURRENCY_SYMBOLS: Record<string, string> = {
  INR: '₹',
  USD: '$',
  EUR: '€',
  GBP: '£',
  JPY: '¥',
  CNY: '¥',
  AED: 'AED ',
  CAD: 'CA$',
  AUD: 'AU$',
  SGD: 'S$',
  CHF: 'CHF '
};

export function getCurrencySymbol(currCode: string = 'USD'): string {
  const code = (currCode || 'USD').toUpperCase().trim();
  return CURRENCY_SYMBOLS[code] || `${code} `;
}

export function formatCurrency(
  val: number | undefined | null,
  currencyCode: string = 'USD',
  maxDigits: number = 0
): string {
  if (val === undefined || val === null || isNaN(val)) return '—';
  
  const code = (currencyCode || 'USD').toUpperCase().trim();
  const isNeg = val < 0;
  const absVal = Math.abs(val);
  const symbol = getCurrencySymbol(code);

  try {
    if (code === 'INR') {
      const formatted = new Intl.NumberFormat('en-IN', {
        maximumFractionDigits: maxDigits
      }).format(absVal);
      return isNeg ? `(${symbol}${formatted})` : `${symbol}${formatted}`;
    }

    const formatted = new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: code,
      maximumFractionDigits: maxDigits
    }).format(absVal);
    
    return isNeg ? `(${formatted})` : formatted;
  } catch (e) {
    // Fallback if browser does not support specific currency ISO code
    const formatted = new Intl.NumberFormat('en-US', {
      maximumFractionDigits: maxDigits
    }).format(absVal);
    return isNeg ? `(${symbol}${formatted})` : `${symbol}${formatted}`;
  }
}

export function formatRawNumber(
  val: number | undefined | null,
  maxDigits: number = 0
): string {
  if (val === undefined || val === null || isNaN(val)) return '—';
  const isNeg = val < 0;
  const absVal = Math.abs(val);
  const formatted = new Intl.NumberFormat('en-US', { maximumFractionDigits: maxDigits }).format(absVal);
  return isNeg ? `(${formatted})` : formatted;
}
