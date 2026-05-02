import type { ExtractedInvoice, FieldAnnotation } from '../types/audit';
import { formatMoney, formatPercent } from '../lib/format';
import { Badge } from './Badge';
import { Panel } from './Panel';

interface ExtractionFieldsProps {
  invoice: ExtractedInvoice | null;
  annotations: Record<string, FieldAnnotation>;
}

const rows: Array<{ key: keyof ExtractedInvoice; label: string; money?: boolean }> = [
  { key: 'vendor_name', label: 'Vendor' },
  { key: 'invoice_number', label: 'Invoice No.' },
  { key: 'invoice_date', label: 'Invoice Date' },
  { key: 'due_date', label: 'Due Date' },
  { key: 'currency', label: 'Currency' },
  { key: 'subtotal_amount', label: 'Subtotal', money: true },
  { key: 'tax_amount', label: 'Tax', money: true },
  { key: 'total_amount', label: 'Total', money: true },
  { key: 'purchase_order', label: 'Purchase Order' },
];

export function ExtractionFields({ invoice, annotations }: ExtractionFieldsProps) {
  return (
    <Panel title="Extracted Fields" description="Key financial fields with verifier confidence and evidence hints.">
      {!invoice ? (
        <p className="rounded-md bg-slate-50 px-3 py-8 text-center text-sm text-slate-500">No extracted fields available.</p>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2">
          {rows.map((row) => {
            const value = invoice[row.key];
            const annotation = annotations[String(row.key)];
            const display = row.money ? formatMoney(value as string | number | null, invoice.currency) : String(value ?? '—');
            return (
              <div className="rounded-md border border-slate-200 p-3" key={String(row.key)}>
                <div className="flex items-start justify-between gap-3">
                  <p className="text-xs font-medium uppercase tracking-wide text-slate-500">{row.label}</p>
                  {annotation ? <Badge label={formatPercent(annotation.confidence, 0)} /> : null}
                </div>
                <p className="mt-2 break-words text-sm font-semibold text-slate-950">{display}</p>
                {annotation?.source_quote ? <p className="mt-1 truncate text-xs text-slate-500">{annotation.source_quote}</p> : null}
              </div>
            );
          })}
        </div>
      )}
    </Panel>
  );
}

