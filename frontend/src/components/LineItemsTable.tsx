import type { ExtractedInvoice } from '../types/audit';
import { formatMoney } from '../lib/format';
import { Panel } from './Panel';

interface LineItemsTableProps {
  invoice: ExtractedInvoice | null;
}

export function LineItemsTable({ invoice }: LineItemsTableProps) {
  const items = invoice?.line_items ?? [];

  return (
    <Panel title="Line Items" description="Structured table extracted from the financial document.">
      {items.length === 0 ? (
        <p className="rounded-md bg-slate-50 px-3 py-8 text-center text-sm text-slate-500">No line items extracted yet.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-200 text-sm">
            <thead>
              <tr className="text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                <th className="px-3 py-2">Description</th>
                <th className="px-3 py-2 text-right">Qty</th>
                <th className="px-3 py-2 text-right">Unit Price</th>
                <th className="px-3 py-2 text-right">Amount</th>
                <th className="px-3 py-2 text-right">Tax Rate</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {items.map((item, index) => (
                <tr className="text-slate-900" key={`${item.description}-${index}`}>
                  <td className="max-w-80 px-3 py-3 font-medium">{item.description ?? `Line ${index + 1}`}</td>
                  <td className="px-3 py-3 text-right tabular-nums">{item.quantity ?? '—'}</td>
                  <td className="px-3 py-3 text-right tabular-nums">{formatMoney(item.unit_price, invoice?.currency)}</td>
                  <td className="px-3 py-3 text-right tabular-nums">{formatMoney(item.amount, invoice?.currency)}</td>
                  <td className="px-3 py-3 text-right tabular-nums">{item.tax_rate ?? '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </Panel>
  );
}

