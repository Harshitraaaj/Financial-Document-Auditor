import { FileText } from 'lucide-react';
import type { DocumentMetadata, PreprocessingResult } from '../types/audit';
import { formatDateTime, titleCase } from '../lib/format';
import { Badge } from './Badge';
import { Panel } from './Panel';

interface MetadataPanelProps {
  metadata: DocumentMetadata | null;
  preprocessing: PreprocessingResult | null;
}

export function MetadataPanel({ metadata, preprocessing }: MetadataPanelProps) {
  if (!metadata) {
    return (
      <Panel title="Document Metadata" description="File identity and processing context.">
        <EmptyState />
      </Panel>
    );
  }

  const rows = [
    ['File Name', metadata.original_filename],
    ['Upload Time', formatDateTime(metadata.submitted_at_utc)],
    ['Declared Type', titleCase(metadata.declared_document_type)],
    ['Detected Type', titleCase(preprocessing?.true_document_type ?? metadata.true_document_type)],
    ['Status', titleCase(metadata.status)],
    ['Tenant', metadata.tenant_id],
    ['Cost Center', metadata.cost_center ?? '—'],
    ['SHA-256', metadata.sha256],
  ];

  return (
    <Panel title="Document Metadata" description="File identity and processing context." action={<Badge label={titleCase(metadata.status)} />}>
      <dl className="grid gap-3">
        {rows.map(([label, value]) => (
          <div className="grid gap-1 rounded-md bg-slate-50 px-3 py-2 sm:grid-cols-[8rem_1fr] sm:gap-3" key={label}>
            <dt className="text-xs font-medium uppercase tracking-wide text-slate-500">{label}</dt>
            <dd className="min-w-0 break-words text-sm text-slate-900">{value}</dd>
          </div>
        ))}
      </dl>
    </Panel>
  );
}

function EmptyState() {
  return (
    <div className="flex min-h-48 flex-col items-center justify-center rounded-lg border border-dashed border-slate-200 bg-slate-50 text-center">
      <FileText className="h-8 w-8 text-slate-400" aria-hidden="true" />
      <p className="mt-3 text-sm font-medium text-slate-900">No document selected</p>
      <p className="mt-1 text-sm text-slate-500">Upload a file to populate metadata.</p>
    </div>
  );
}

