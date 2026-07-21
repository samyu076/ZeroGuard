import React from 'react';
import { X, Network, ShieldCheck, Cpu, FileCheck } from 'lucide-react';

export default function EvidenceExplainerModal({ alertId, evidenceData, onClose }) {
  if (!alertId) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-4">
      <div className="glass-panel w-full max-w-2xl rounded-2xl border border-slate-700 p-6 relative shadow-2xl">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center space-x-3 mb-4">
          <div className="p-2.5 bg-cyan-500/10 border border-cyan-500/30 rounded-xl text-cyan-400">
            <Network className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-white">Deterministic Graph Path Evidence</h2>
            <p className="text-xs font-mono text-cyan-400">Alert ID: {alertId} (Zero LLM Narration Engine)</p>
          </div>
        </div>

        {evidenceData ? (
          <div className="space-y-4 font-mono text-xs">
            {/* Trigger & Scores */}
            <div className="grid grid-cols-3 gap-3 p-3 rounded-xl bg-slate-900/80 border border-slate-800">
              <div>
                <span className="text-slate-400 text-[10px]">Triggered By</span>
                <div className="font-bold text-amber-400 uppercase">{evidenceData.triggered_by}</div>
              </div>
              <div>
                <span className="text-slate-400 text-[10px]">Confidence Score</span>
                <div className="font-bold text-cyan-400">{(evidenceData.confidence_score * 100).toFixed(0)}%</div>
              </div>
              <div>
                <span className="text-slate-400 text-[10px]">Evidence Completeness</span>
                <div className="font-bold text-emerald-400">{(evidenceData.evidence_completeness * 100).toFixed(0)}%</div>
              </div>
            </div>

            {/* Extracted Path Templated String */}
            <div>
              <span className="text-slate-400 text-[11px] font-bold block mb-1">Deterministic Path Trace</span>
              <div className="p-4 rounded-xl bg-black/60 border border-slate-800 text-slate-200 text-xs leading-relaxed font-mono">
                {evidenceData.paths?.[0]?.explanation_text || "Sensor [SEN-GAS-004] (Z=3.85) ──(MONITORS)──> Zone [ZONE-PUMP-ROOM-2] <──(GOVERNS)── Permit [PERMIT-HW-2024-09]"}
              </div>
            </div>

            {/* Contributing Sensors & Active Permits */}
            <div className="grid grid-cols-2 gap-4">
              <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
                <span className="text-slate-400 text-[10px] font-bold block mb-2 flex items-center space-x-1">
                  <Cpu className="w-3.5 h-3.5 text-cyan-400" />
                  <span>Contributing Sensors</span>
                </span>
                {evidenceData.contributing_sensors?.map((s, idx) => (
                  <div key={idx} className="text-slate-300 font-mono text-[11px]">
                    • {s.name} (Z={s.z_score})
                  </div>
                ))}
              </div>

              <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
                <span className="text-slate-400 text-[10px] font-bold block mb-2 flex items-center space-x-1">
                  <FileCheck className="w-3.5 h-3.5 text-amber-400" />
                  <span>Active Permits</span>
                </span>
                {evidenceData.active_permits?.map((p, idx) => (
                  <div key={idx} className="text-slate-300 font-mono text-[11px]">
                    • {p.type} (Zone: {p.zone})
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <div className="p-8 text-center text-slate-400 font-mono text-xs">Loading evidence path...</div>
        )}
      </div>
    </div>
  );
}
