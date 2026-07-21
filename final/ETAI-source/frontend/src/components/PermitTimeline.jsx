import React from 'react';
import { FileCheck, ShieldAlert } from 'lucide-react';

export default function PermitTimeline({ graphState }) {
  const nodes = graphState?.nodes ?? [];
  const permitNodes = nodes.filter(n => n.category === 'PERMIT');

  return (
    <div className="glass-panel p-5 rounded-2xl border border-slate-800">
      <div className="flex justify-between items-center mb-4">
        <div className="flex items-center space-x-2">
          <FileCheck className="w-5 h-5 text-amber-400" />
          <h3 className="font-bold text-white tracking-wide">Active Permit & Shift Logs</h3>
        </div>
        <span className="text-xs font-mono text-slate-400">Rulebook Aligned Generator</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 font-mono text-xs">
        {permitNodes.map((p) => {
          const isNonCompliant = p.status === 'NON_COMPLIANT';
          return (
            <div
              key={p.id}
              className={`p-4 rounded-xl border ${
                isNonCompliant ? 'bg-amber-950/20 border-amber-500/40' : 'bg-slate-900/60 border-slate-800'
              }`}
            >
              <div className="flex justify-between items-start mb-2">
                <span className="font-bold text-white">{p.name}</span>
                <span
                  className={`px-2 py-0.5 rounded text-[10px] uppercase font-bold ${
                    isNonCompliant ? 'bg-rose-950 text-rose-400 border border-rose-800' : 'bg-amber-950 text-amber-400 border border-amber-800'
                  }`}
                >
                  {p.status}
                </span>
              </div>
              <div className="text-slate-400 text-[11px] space-y-1">
                <div>Permit ID: {p.id}</div>
                <div>Zone: {p.zone_id}</div>
                <div>Contractor: {p.attributes?.contractor || 'Plant Internal'}</div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
