import type { ReactNode } from 'react';
import { HugeiconsIcon } from "@hugeicons/react";
import { CgAlignBottom } from "react-icons/cg";
import { ShieldCheck } from 'lucide-react';

interface AppShellProps {
  children: ReactNode;
}

export function AppShell({ children }: AppShellProps) {
  return (
    <div className="min-h-screen bg-slate-100">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-slate-950 text-white">
              {/* <CgAlignBottom className="h-6 w-6" aria-hidden="true" /> */}
              <img src="/logo3.svg" alt="Project Logo" className="h-6 w-6" />
            </div>
            <div>
              <h1 className="text-base font-semibold text-slate-950">AI Financial Document Auditor</h1>
              <p className="text-sm text-slate-500"><br></br></p>
            </div>
          </div>
        </div>
      </header>
      <main className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">{children}</main>
    </div>
  );
}

