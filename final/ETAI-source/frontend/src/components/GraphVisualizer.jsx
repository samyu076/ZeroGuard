import React, { useState } from 'react';
import { ShieldAlert, Cpu, Eye, X, Activity } from 'lucide-react';

export default function GraphVisualizer({ graphState, onSelectAlert }) {
  const nodes = graphState?.nodes ?? [];
  const edges = graphState?.edges ?? [];
  const alerts = graphState?.active_alerts ?? [];

  const [selectedNode, setSelectedNode] = useState(null);

  const getCategoryColor = (cat) => {
    switch (cat) {
      case 'SENSOR': return 'bg-cyan-500/20 border-cyan-400 text-cyan-300';
      case 'PERMIT': return 'bg-amber-500/20 border-amber-400 text-amber-300';
      case 'ZONE': return 'bg-rose-500/20 border-rose-400 text-rose-300';
      case 'EQUIPMENT': return 'bg-indigo-500/20 border-indigo-400 text-indigo-300';
      default: return 'bg-slate-500/20 border-slate-400 text-slate-300';
    }
  };

  // Map 250m x 250m spatial grid to percentage layout (10% to 90%)
  const getNodePosition = (node, index) => {
    const xRaw = node.attributes?.x ?? node.attributes?.center_x ?? (50 + (index % 3) * 80);
    const yRaw = node.attributes?.y ?? node.attributes?.center_y ?? (50 + Math.floor(index / 3) * 70);
    const posX = Math.min(Math.max((xRaw / 250) * 80 + 10, 10), 90);
    const posY = Math.min(Math.max((yRaw / 250) * 75 + 12, 12), 85);
    return { posX, posY };
  };

  // Build node positions lookup map
  const nodePositions = {};
  nodes.forEach((n, idx) => {
    nodePositions[n.id] = getNodePosition(n, idx);
  });

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Interactive Spatial Graph Topology Canvas */}
      <div className="lg:col-span-2 glass-panel p-5 rounded-2xl border border-slate-800 flex flex-col justify-between min-h-[460px] relative overflow-hidden">
        <div className="flex justify-between items-center mb-2 z-10">
          <div className="flex items-center space-x-2">
            <Cpu className="w-5 h-5 text-cyan-400" />
            <h3 className="font-bold text-white tracking-wide">Refinery Unit Spatial Risk Topology</h3>
          </div>
          <span className="text-xs font-mono text-slate-400">Rendered SVG Edges & (x, y) Coordinates</span>
        </div>

        {/* Spatial Topology Rendering Surface */}
        <div className="relative w-full h-[340px] bg-slate-950/60 rounded-xl border border-slate-800/80 my-auto overflow-hidden">
          {/* SVG Canvas layer for Topology Edges */}
          <svg className="absolute inset-0 w-full h-full pointer-events-none z-0">
            {edges.map((edge, idx) => {
              const srcPos = nodePositions[edge.source];
              const tgtPos = nodePositions[edge.target];
              if (!srcPos || !tgtPos) return null;

              return (
                <g key={`edge-${idx}`}>
                  <line
                    x1={`${srcPos.posX}%`}
                    y1={`${srcPos.posY}%`}
                    x2={`${tgtPos.posX}%`}
                    y2={`${tgtPos.posY}%`}
                    stroke={edge.relation === 'MONITORS' ? '#00F0FF' : edge.relation === 'GOVERNS' ? '#FFB800' : '#6366F1'}
                    strokeWidth={edge.weight ? edge.weight * 2.5 : 2}
                    strokeDasharray={edge.relation === 'MONITORS' ? '4 2' : 'none'}
                    className="opacity-75 animate-pulse"
                  />
                  <text
                    x={`${(srcPos.posX + tgtPos.posX) / 2}%`}
                    y={`${(srcPos.posY + tgtPos.posY) / 2}%`}
                    fill="#94A3B8"
                    fontSize="9"
                    fontFamily="monospace"
                    textAnchor="middle"
                    dy="-4"
                  >
                    {edge.relation}
                  </text>
                </g>
              );
            })}
          </svg>

          {/* Node Overlay Layer */}
          {nodes.map((node, idx) => {
            const pos = nodePositions[node.id];
            const isSelected = selectedNode?.id === node.id;
            return (
              <div
                key={node.id}
                onClick={() => setSelectedNode(node)}
                style={{ left: `${pos.posX}%`, top: `${pos.posY}%` }}
                className={`absolute -translate-x-1/2 -translate-y-1/2 p-2.5 rounded-xl border transition cursor-pointer z-10 shadow-lg ${getCategoryColor(
                  node.category
                )} ${isSelected ? 'ring-2 ring-cyan-400 scale-110 shadow-cyan-500/30' : 'hover:scale-105'}`}
              >
                <div className="flex items-center space-x-1.5 text-[10px] font-mono font-bold">
                  <span className="px-1 py-0.2 rounded bg-black/50">{node.category}</span>
                  {node.z_score !== undefined && node.z_score !== null && (
                    <span className={node.z_score >= 3.0 ? 'text-rose-400 font-extrabold' : 'text-emerald-400'}>
                      Z:{node.z_score}
                    </span>
                  )}
                </div>
                <div className="text-[11px] font-bold text-white truncate max-w-[130px]">{node.name}</div>
                <div className="text-[9px] font-mono text-slate-400 truncate">ID: {node.id}</div>
              </div>
            );
          })}
        </div>

        {/* Legend & Selected Node Details Drawer */}
        <div className="flex justify-between items-center text-[11px] font-mono text-slate-400 pt-3 border-t border-slate-800 z-10">
          <div className="flex items-center space-x-4">
            <span className="flex items-center space-x-1.5"><span className="w-2.5 h-2.5 rounded-full bg-cyan-400"></span><span>Sensor</span></span>
            <span className="flex items-center space-x-1.5"><span className="w-2.5 h-2.5 rounded-full bg-amber-400"></span><span>Permit</span></span>
            <span className="flex items-center space-x-1.5"><span className="w-2.5 h-2.5 rounded-full bg-rose-400"></span><span>Zone</span></span>
            <span className="flex items-center space-x-1.5"><span className="w-2.5 h-2.5 rounded-full bg-indigo-400"></span><span>Equipment</span></span>
          </div>
          <span className="text-cyan-400 font-bold">{edges.length} Active Spatial Edges Rendered</span>
        </div>

        {/* Node Details Drawer Modal when selectedNode is set (Resolves Medium #1) */}
        {selectedNode && (
          <div className="absolute inset-x-4 bottom-4 z-30 p-4 rounded-xl glass-panel border border-cyan-500/50 shadow-2xl bg-slate-950/95 flex justify-between items-start">
            <div className="space-y-1 font-mono text-xs">
              <div className="flex items-center space-x-2">
                <span className="px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800 text-[10px] font-bold uppercase">
                  {selectedNode.category}
                </span>
                <span className="font-bold text-white text-sm">{selectedNode.name}</span>
                <span className="text-slate-400">({selectedNode.id})</span>
              </div>
              <div className="text-slate-300 text-[11px] flex space-x-4 pt-1">
                <span>Zone: <strong className="text-cyan-300">{selectedNode.zone_id}</strong></span>
                <span>Z-Score: <strong className={selectedNode.z_score >= 3.0 ? 'text-rose-400' : 'text-emerald-400'}>{selectedNode.z_score ?? 'N/A'}</strong></span>
                <span>Current Value: <strong className="text-slate-200">{selectedNode.current_value ?? 'N/A'}</strong></span>
                <span>Status: <strong className="text-amber-400">{selectedNode.status}</strong></span>
              </div>
            </div>
            <button onClick={() => setSelectedNode(null)} className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white">
              <X className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>

      {/* Active Dual-Layer Alerts Feed */}
      <div className="glass-panel p-5 rounded-2xl border border-slate-800 flex flex-col justify-between">
        <div>
          <div className="flex justify-between items-center mb-4">
            <h3 className="font-bold text-white tracking-wide flex items-center space-x-2">
              <ShieldAlert className="w-5 h-5 text-rose-500" />
              <span>Active Compound Alerts</span>
            </h3>
            <span className="text-xs font-mono text-rose-400">{alerts.length} Live</span>
          </div>

          <div className="space-y-3 max-h-[340px] overflow-y-auto pr-1">
            {alerts.map((alert) => {
              const isRuleGuard = alert.triggered_by === 'rule_guard';
              return (
                <div
                  key={alert.alert_id}
                  className={`p-3.5 rounded-xl border transition ${
                    isRuleGuard
                      ? 'bg-amber-950/30 border-amber-500/40 text-amber-200'
                      : 'bg-rose-950/30 border-rose-500/40 text-rose-200'
                  }`}
                >
                  <div className="flex items-center justify-between text-[10px] font-mono mb-1">
                    <span
                      className={`px-2 py-0.5 rounded font-bold uppercase ${
                        isRuleGuard ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30' : 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30'
                      }`}
                    >
                      {alert.triggered_by}
                    </span>
                    <span>Risk Score: {alert.risk_score}</span>
                  </div>
                  <div className="text-xs font-bold text-slate-100">{alert.title}</div>
                  <div className="mt-2 flex items-center justify-between text-[11px] font-mono text-slate-400">
                    <span>Conf: {(alert.confidence_score * 100).toFixed(0)}%</span>
                    <span>Evid: {(alert.evidence_completeness * 100).toFixed(0)}%</span>
                    <button
                      onClick={() => onSelectAlert(alert.alert_id)}
                      className="flex items-center space-x-1 text-cyan-400 hover:text-cyan-300 font-sans font-semibold text-xs"
                    >
                      <span>Explain Path</span>
                      <Eye className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        <div className="mt-4 pt-3 border-t border-slate-800 text-[11px] font-mono text-slate-400">
          Deterministic Evidence Extractor Active (Zero LLM Narration)
        </div>
      </div>
    </div>
  );
}
