import type { RoutingDecision, Severity } from '../types/audit';

export function formatPercent(value: number | null | undefined, digits = 1): string {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return 'Unavailable';
  }
  return `${(value * 100).toFixed(digits)}%`;
}

export function formatDateTime(value: string | null | undefined): string {
  if (!value) {
    return 'Unavailable';
  }
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value));
}

export function formatMoney(value: string | number | null | undefined, currency?: string | null): string {
  if (value === null || value === undefined || value === '') {
    return '—';
  }
  const numeric = Number(value);
  if (Number.isNaN(numeric)) {
    return String(value);
  }
  if (!currency) {
    return numeric.toFixed(2);
  }
  return new Intl.NumberFormat(undefined, {
    style: 'currency',
    currency,
  }).format(numeric);
}

export function titleCase(value: string | null | undefined): string {
  if (!value) {
    return 'Unavailable';
  }
  return value
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (character) => character.toUpperCase());
}

export function severityTone(severity: Severity): string {
  const tones: Record<Severity, string> = {
    info: 'bg-slate-100 text-slate-700 ring-slate-200',
    low: 'bg-blue-50 text-blue-700 ring-blue-200',
    medium: 'bg-amber-50 text-amber-800 ring-amber-200',
    high: 'bg-red-50 text-red-700 ring-red-200',
    critical: 'bg-red-100 text-red-900 ring-red-300',
  };
  return tones[severity];
}

export function routingTone(decision: RoutingDecision | null | undefined): string {
  if (decision === 'auto_approve') {
    return 'bg-teal-50 text-teal-800 ring-teal-200';
  }
  if (decision === 'human_review') {
    return 'bg-blue-50 text-blue-800 ring-blue-200';
  }
  if (decision === 'compliance_hold') {
    return 'bg-amber-50 text-amber-900 ring-amber-200';
  }
  if (decision === 'hard_reject') {
    return 'bg-red-50 text-red-800 ring-red-200';
  }
  return 'bg-slate-100 text-slate-700 ring-slate-200';
}

