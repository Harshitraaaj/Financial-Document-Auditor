import type { RoutingDecision, Severity } from '../types/audit';
import { routingTone, severityTone, titleCase } from '../lib/format';

interface BadgeProps {
  label: string;
  tone?: string;
}

export function Badge({ label, tone = 'bg-slate-100 text-slate-700 ring-slate-200' }: BadgeProps) {
  return (
    <span className={`inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset ${tone}`}>
      {label}
    </span>
  );
}

export function SeverityBadge({ severity }: { severity: Severity }) {
  return <Badge label={titleCase(severity)} tone={severityTone(severity)} />;
}

export function RoutingBadge({ decision }: { decision: RoutingDecision | null | undefined }) {
  return <Badge label={titleCase(decision)} tone={routingTone(decision)} />;
}

