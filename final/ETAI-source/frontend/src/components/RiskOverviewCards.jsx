import React from 'react';
import { AlertTriangle, ShieldCheck, Zap, CheckCircle2 } from 'lucide-react';

export default function RiskOverviewCards({ graphState, isOffline }) {
  if (isOffline || !graphState) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="glass-panel p-5 rounded-2xl border border-rose-500/30">
            <span className="text-xs font-mono uppercase text-slate-500">System State</span>
            <div className="text-xl font-bold text-rose-500 mt-1 font-mono">OFFLINE</div>
            <p className="text-[10px] text-slate-500 font-mono mt-2">API Disconnected</p>
          </div>
        ))}
      </div>
    );
  }

  const overallRisk = graphState.overall_risk_score ?? 0.0;
  const confidence = graphState.confidence_score ?? 0.0;
  const completeness = graphState.evidence_completeness ?? 0.0;
  const alerts = graphState.active_alerts ?? [];

  const ruleGuardCount = alerts.filter((a) => a.triggered_by === 'rule_guard').length;
  const propagationCount = alerts.filter((a) => a.triggered_by === 'propagation').length;

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
      {/* Overall Facility Risk */}
      <div className="glass-panel p-5 rounded-2xl relative overflow-hidden glow-red">
        <div className="flex justify-between items-start">
          <div>
            <span className="text-xs font-mono uppercase text-slate-400">Facility Risk Score</span>
            <div className="text-3xl font-extrabold text-rose-500 mt-1 font-mono">
              {overallRisk.toFixed(1)} <span className="text-sm text-slate-400 font-normal">/ 100</span>
            </div>
          </div>
          <div className="p-2.5 bg-rose-500/10 rounded-xl border border-rose-500/20 text-rose-400">
            <AlertTriangle className="w-6 h-6" />
          </div>
        </div>
        <div className="mt-3 flex items-center space-x-2">
          <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-rose-950 text-rose-400 border border-rose-800">
            {overallRisk >= 80 ? 'CRITICAL LEVEL' : overallRisk >= 50 ? 'WARNING LEVEL' : 'NORMAL LEVEL'}
          </span>
          {/* Dynamically bound alert count (Resolves Medium #2) */}
          <span className="text-xs text-slate-400 font-mono">{alerts.length} Active Incident{alerts.length === 1 ? '' : 's'}</span>
        </div>
      </div>

      {/* Dual-Layer Alert Counter */}
      <div className="glass-panel p-5 rounded-2xl">
        <div className="flex justify-between items-start">
          <div>
            <span className="text-xs font-mono uppercase text-slate-400">Dual-Layer Active Alerts</span>
            <div className="flex items-baseline space-x-3 mt-1 font-mono">
              <span className="text-2xl font-bold text-amber-400">
                {ruleGuardCount} <span className="text-xs text-slate-400 font-normal">RuleGuard</span>
              </span>
              <span className="text-2xl font-bold text-cyan-400">
                {propagationCount} <span className="text-xs text-slate-400 font-normal">Propagation</span>
              </span>
            </div>
          </div>
          <div className="p-2.5 bg-amber-500/10 rounded-xl border border-amber-500/20 text-amber-400">
            <Zap className="w-6 h-6" />
          </div>
        </div>
        <p className="mt-3 text-xs text-slate-400 font-mono">Statutory & Graph emergent breakdown</p>
      </div>

      {/* Confidence Score */}
      <div className="glass-panel p-5 rounded-2xl">
        <div className="flex justify-between items-start">
          <div>
            <span className="text-xs font-mono uppercase text-slate-400">Confidence Score</span>
            <div className="text-3xl font-extrabold text-cyan-400 mt-1 font-mono">{(confidence * 100).toFixed(0)}%</div>
          </div>
          <div className="p-2.5 bg-cyan-500/10 rounded-xl border border-cyan-500/20 text-cyan-400">
            <ShieldCheck className="w-6 h-6" />
          </div>
        </div>
        <div className="mt-3 w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
          <div className="bg-cyan-400 h-full rounded-full" style={{ width: `${confidence * 100}%` }}></div>
        </div>
      </div>

      {/* Evidence Completeness */}
      <div className="glass-panel p-5 rounded-2xl">
        <div className="flex justify-between items-start">
          <div>
            <span className="text-xs font-mono uppercase text-slate-400">Evidence Completeness</span>
            <div className="text-3xl font-extrabold text-emerald-400 mt-1 font-mono">{(completeness * 100).toFixed(0)}%</div>
          </div>
          <div className="p-2.5 bg-emerald-500/10 rounded-xl border border-emerald-500/20 text-emerald-400">
            <CheckCircle2 className="w-6 h-6" />
          </div>
        </div>
        <div className="mt-3 w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
          <div className="bg-emerald-400 h-full rounded-full" style={{ width: `${completeness * 100}%` }}></div>
        </div>
      </div>
    </div>
  );
}
