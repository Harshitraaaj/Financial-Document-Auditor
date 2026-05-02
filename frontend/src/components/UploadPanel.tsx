import { ChangeEvent, FormEvent, useMemo, useState } from 'react';
import { AlertCircle, FileUp, Loader2, Upload } from 'lucide-react';
import type { DocumentType, UploadDocumentPayload } from '../types/audit';
import { Panel } from './Panel';

interface UploadPanelProps {
  isLoading: boolean;
  error: string | null;
  onUpload: (payload: UploadDocumentPayload) => Promise<void>;
}

const documentTypes: Array<{ value: DocumentType; label: string }> = [
  { value: 'invoice', label: 'Invoice' },
  { value: 'receipt', label: 'Receipt' },
  { value: 'expense_report', label: 'Expense Report' },
];

export function UploadPanel({ isLoading, error, onUpload }: UploadPanelProps) {
  const [file, setFile] = useState<File | null>(null);
  const [tenantId, setTenantId] = useState('local-tenant');
  const [submittedBy, setSubmittedBy] = useState('');
  const [costCenter, setCostCenter] = useState('');
  const [declaredDocumentType, setDeclaredDocumentType] = useState<DocumentType>('invoice');

  const fileDetail = useMemo(() => {
    if (!file) {
      return 'PDF, image, text, or spreadsheet evidence';
    }
    return `${file.name} · ${(file.size / 1024).toFixed(1)} KB`;
  }, [file]);

  function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    setFile(event.target.files?.[0] ?? null);
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!file) {
      return;
    }
    await onUpload({
      file,
      tenantId,
      submittedBy: submittedBy || 'Local Auditor',
      declaredDocumentType,
      costCenter: costCenter || undefined,
    });
  }

  return (
    <Panel title="Document Intake" description="Submit financial evidence for extraction, validation, and routing.">
      <form className="space-y-5" onSubmit={handleSubmit}>
        <label className="flex min-h-36 cursor-pointer flex-col items-center justify-center rounded-lg border border-dashed border-slate-300 bg-slate-50 px-4 py-6 text-center transition hover:border-slate-400 hover:bg-slate-100">
          <FileUp className="h-8 w-8 text-slate-500" aria-hidden="true" />
          <span className="mt-3 text-sm font-medium text-slate-900">{file ? file.name : 'Choose a document'}</span>
          <span className="mt-1 text-xs text-slate-500">{fileDetail}</span>
          <input className="sr-only" type="file" onChange={handleFileChange} />
        </label>

        <div className="grid gap-4 sm:grid-cols-2">
          <label className="space-y-1.5">
            <span className="text-sm font-medium text-slate-700">Document Type</span>
            <select
              className="w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-950 outline-none ring-blue-500 transition focus:ring-2"
              value={declaredDocumentType}
              onChange={(event) => setDeclaredDocumentType(event.target.value as DocumentType)}
            >
              {documentTypes.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>

          <label className="space-y-1.5">
            <span className="text-sm font-medium text-slate-700">Tenant</span>
            <input
              className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-950 outline-none ring-blue-500 transition focus:ring-2"
              value={tenantId}
              onChange={(event) => setTenantId(event.target.value)}
            />
          </label>

          <label className="space-y-1.5">
            <span className="text-sm font-medium text-slate-700">Submitted By</span>
            <input
              className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-950 outline-none ring-blue-500 transition focus:ring-2"
              placeholder="Local Auditor"
              value={submittedBy}
              onChange={(event) => setSubmittedBy(event.target.value)}
            />
          </label>

          <label className="space-y-1.5">
            <span className="text-sm font-medium text-slate-700">Cost Center</span>
            <input
              className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-950 outline-none ring-blue-500 transition focus:ring-2"
              placeholder="Optional"
              value={costCenter}
              onChange={(event) => setCostCenter(event.target.value)}
            />
          </label>
        </div>

        {error ? (
          <div className="flex gap-2 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-800">
            <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
            <span>{error}</span>
          </div>
        ) : null}

        <button
          className="inline-flex w-full items-center justify-center gap-2 rounded-md bg-slate-950 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-400"
          type="submit"
          disabled={!file || isLoading}
        >
          {isLoading ? <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" /> : <Upload className="h-4 w-4" aria-hidden="true" />}
          {isLoading ? 'Auditing Document' : 'Run Audit'}
        </button>
      </form>
    </Panel>
  );
}

