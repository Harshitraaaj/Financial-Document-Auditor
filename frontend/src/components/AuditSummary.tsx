import { AlertTriangle, CheckCircle2, Gauge, Route } from 'lucide-react';
import type { PipelineResult } from '../types/audit';
import { formatPercent, titleCase } from '../lib/format';
import { MetricCard } from './MetricCard';
import { Panel } from './Panel';
import { RoutingBadge } from './Badge';

interface AuditSummaryProps {
  result: PipelineResult | null;
}

export function AuditSummary({ result }: AuditSummaryProps) {
  const confidence = result?.confidence;
  const findingCount = result?.validation?.findings.length ?? 0;
  const anomalyCount = result?.anomaly?.flags.length ?? 0;

  if (!result) {
    return (
      <Panel title="Audit Summary" description="Routing and confidence will appear after processing.">
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <MetricCard label="Confidence" value="Pending" detail="No document processed" icon={<Gauge className="h-4 w-4" />} />
          <MetricCard label="Routing" value="Pending" detail="Awaiting audit result" icon={<Route className="h-4 w-4" />} />
          <MetricCard label="Findings" value="0" detail="Validation not run" icon={<AlertTriangle className="h-4 w-4" />} />
          <MetricCard label="Anomalies" value="0" detail="Baseline not evaluated" icon={<CheckCircle2 className="h-4 w-4" />} />
        </div>
      </Panel>
    );
  }

  return (
    <Panel
      title="Audit Summary"
      description={confidence?.routing_reason ?? 'Document reached preprocessing but no routing decision was produced.'}
      action={<RoutingBadge decision={confidence?.routing_decision} />}
    >
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard
          label="Confidence"
          value={formatPercent(confidence?.document_confidence, 1)}
          detail="Composite document score"
          icon={<Gauge className="h-4 w-4" />}
        />
        <MetricCard
          label="Routing"
          value={titleCase(confidence?.routing_decision)}
          detail="Threshold engine decision"
          icon={<Route className="h-4 w-4" />}
        />
        <MetricCard
          label="Findings"
          value={String(findingCount)}
          detail="Deterministic validation issues"
          icon={<AlertTriangle className="h-4 w-4" />}
        />
        <MetricCard
          label="Anomalies"
          value={String(anomalyCount)}
          detail={`Deviation ${formatPercent(result.anomaly?.deviation_score, 1)}`}
          icon={<CheckCircle2 className="h-4 w-4" />}
        />
      </div>
    </Panel>
  );
}

