import { useMemo, useState } from 'react';
import { uploadDocument, getErrorMessage } from './lib/api';
import type { PipelineResult, UploadDocumentPayload } from './types/audit';
import { AppShell } from './components/AppShell';
import { AuditSummary } from './components/AuditSummary';
import { ExtractionFields } from './components/ExtractionFields';
import { FindingsTable } from './components/FindingsTable';
import { JsonViewer } from './components/JsonViewer';
import { LineItemsTable } from './components/LineItemsTable';
import { MetadataPanel } from './components/MetadataPanel';
import { UploadPanel } from './components/UploadPanel';

export default function App() {
  const [result, setResult] = useState<PipelineResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleUpload(payload: UploadDocumentPayload) {
    setIsLoading(true);
    setError(null);
    try {
      const response = await uploadDocument(payload);
      setResult(response);
    } catch (caught) {
      setError(getErrorMessage(caught));
    } finally {
      setIsLoading(false);
    }
  }

  const invoice = result?.extraction?.invoice ?? null;
  const annotations = useMemo(() => result?.extraction?.annotations ?? {}, [result]);
  const findings = result?.validation?.findings ?? [];
  const anomalies = result?.anomaly?.flags ?? [];

  return (
    <AppShell>
      <div className="grid gap-6 lg:grid-cols-[24rem_1fr]">
        <aside className="space-y-6">
          <UploadPanel isLoading={isLoading} error={error} onUpload={handleUpload} />
          <MetadataPanel metadata={result?.metadata ?? null} preprocessing={result?.preprocessing ?? null} />
        </aside>

        <section className="space-y-6">
          <AuditSummary result={result} />
          <div className="grid gap-6 xl:grid-cols-2">
            <ExtractionFields invoice={invoice} annotations={annotations} />
            <LineItemsTable invoice={invoice} />
          </div>
          <FindingsTable findings={findings} anomalyFlags={anomalies} />
          <JsonViewer result={result} />
        </section>
      </div>
    </AppShell>
  );
}

