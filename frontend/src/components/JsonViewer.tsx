import type { PipelineResult } from '../types/audit';
import { Panel } from './Panel';

interface JsonViewerProps {
  result: PipelineResult | null;
}

export function JsonViewer({ result }: JsonViewerProps) {
  const extracted = result?.extraction?.invoice ?? null;

  return (
    <Panel title="Extracted Structured JSON" description="Normalized invoice object returned by the extraction binder.">
      {extracted ? (
        <pre className="max-h-[32rem] overflow-auto rounded-md bg-slate-950 p-4 text-xs leading-6 text-slate-100">
          {JSON.stringify(extracted, null, 2)}
        </pre>
      ) : (
        <p className="rounded-md bg-slate-50 px-3 py-8 text-center text-sm text-slate-500">No extraction output available.</p>
      )}
    </Panel>
  );
}

