import { CheckCircle2 } from 'lucide-react';
import type { Finding } from '../types/audit';
import { SeverityBadge } from './Badge';
import { Panel } from './Panel';

interface FindingsTableProps {
  findings: Finding[];
  anomalyFlags: Finding[];
}

export function FindingsTable({ findings, anomalyFlags }: FindingsTableProps) {
  const allFindings = [...findings, ...anomalyFlags];

  return (
    <Panel title="Validation Report" description="Deterministic findings, rule outcomes, and anomaly flags.">
      {allFindings.length === 0 ? (
        <div className="flex min-h-32 items-center justify-center rounded-md bg-teal-50 text-sm text-teal-800">
          <CheckCircle2 className="mr-2 h-4 w-4" aria-hidden="true" />
          No validation findings produced.
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-200 text-sm">
            <thead>
              <tr className="text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                <th className="px-3 py-2">Rule</th>
                <th className="px-3 py-2">Severity</th>
                <th className="px-3 py-2">Field</th>
                <th className="px-3 py-2">Expected</th>
                <th className="px-3 py-2">Actual</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {allFindings.map((finding) => (
                <tr key={`${finding.rule_id}-${finding.field_name ?? 'document'}`}>
                  <td className="max-w-lg px-3 py-3">
                    <p className="font-medium text-slate-950">{finding.rule_name}</p>
                    <p className="mt-1 text-xs text-slate-500">{finding.explanation}</p>
                    <p className="mt-1 font-mono text-xs text-slate-400">{finding.rule_id}</p>
                  </td>
                  <td className="px-3 py-3">
                    <SeverityBadge severity={finding.severity} />
                  </td>
                  <td className="px-3 py-3 text-slate-700">{finding.field_name ?? 'document'}</td>
                  <td className="max-w-48 break-words px-3 py-3 text-slate-700">{stringifyValue(finding.expected_value)}</td>
                  <td className="max-w-48 break-words px-3 py-3 text-slate-700">{stringifyValue(finding.actual_value)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </Panel>
  );
}

function stringifyValue(value: unknown): string {
  if (value === null || value === undefined || value === '') {
    return '—';
  }
  if (typeof value === 'object') {
    return JSON.stringify(value);
  }
  return String(value);
}

