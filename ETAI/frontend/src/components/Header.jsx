import React from 'react';
import { ShieldAlert, Activity, Cpu, SlidersHorizontal, FileText } from 'lucide-react';

export default function Header({ onOpenInjector, onOpenCompliance }) {
  return (
    <header className="glass-panel sticky top-0 z-40 border-b border-slate-800 px-6 py-4 flex items-center justify-between">
      <div className="flex items-center space-x-3">
        <div className="p-2 bg-cyan-500/10 border border-cyan-500/30 rounded-xl glow-cyan">
          <ShieldAlert className="w-7 h-7 text-cyan-400" />
        </div>
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-xl font-bold tracking-wider text-white">ZEROGUARD</h1>
            <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800">
              v1.0 MONOREPO
            </span>
          </div>
          <p className="text-xs text-slate-400">Compound Industrial Risk Intelligence Platform</p>
        </div>
      </div>

      <div className="flex items-center space-x-4 font-mono text-xs">
        <div className="flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-slate-900/80 border border-slate-800">
          <span className="relative flex h-2.5 w-2.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
          </span>
          <span className="text-slate-300">GRAPH-ENGINE: MOCK INTERFACE</span>
        </div>

        <button
          onClick={onOpenCompliance}
          className="flex items-center space-x-2 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition"
        >
          <FileText className="w-4 h-4 text-emerald-400" />
          <span>Statutory Citations</span>
        </button>

        <button
          onClick={onOpenInjector}
          className="flex items-center space-x-2 px-4 py-2 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-black font-semibold shadow-lg shadow-cyan-500/20 transition"
        >
          <SlidersHorizontal className="w-4 h-4" />
          <span>Inject Anomaly</span>
        </button>
      </div>
    </header>
  );
}
