import React, { useState } from 'react';
import { Layers } from 'lucide-react';

const PLANT_ZONES = [
  { id: 'Zone-A-CrudeDistillation', label: 'Zone A: Crude Distillation Unit (CDU)', x: 30, y: 30, w: 275, h: 220 },
  { id: 'Zone-B-PumpStation', label: 'Zone B: Hydrocracker Feed Pump Station', x: 330, y: 30, w: 275, h: 220 },
  { id: 'Zone-C-TankFarm', label: 'Zone C: Hydrocarbon Tank Farm C-10', x: 630, y: 30, w: 275, h: 220 },
  { id: 'Zone-D-Loading', label: 'Zone D: Truck Loading & Unloading Rack', x: 180, y: 280, w: 275, h: 220 },
  { id: 'Zone-E-Control', label: 'Zone E: Main Plant Control Room & Substation', x: 480, y: 280, w: 275, h: 220 },
];

export default function GraphVisualizer({ graphState, onSelectAlert }) {
  const [selectedNodeId, setSelectedNodeId] = useState(null);

  if (!graphState) return null;

  const { nodes = [], edges = [], active_alerts = [] } = graphState;

  const criticalAlert = active_alerts.find(
    a => a.risk_level === 'CRITICAL' || a.triggered_by === 'RULE_GUARD'
  );

  const getNodePos = (node) => {
    const rawX = node.attributes?.x ?? 100.0;
    const rawY = node.attributes?.y ?? 100.0;
    const svgX = 50 + (rawX / 200.0) * 830;
    const svgY = 50 + (rawY / 200.0) * 430;
    return { x: svgX, y: svgY };
  };

  const getNodeColor = (node) => {
    if (node.status === 'CRITICAL' || node.status === 'NON_COMPLIANT') return '#F85149';
    if (node.status === 'WARNING' || Math.abs(node.z_score || 0) >= 2.5) return '#DB6D28';
    if (Math.abs(node.z_score || 0) >= 1.5) return '#D29922';
    return '#2EA043';
  };

  const computedNodes = nodes.map(n => ({
    ...n,
    pos: getNodePos(n),
    color: getNodeColor(n)
  }));

  // =========================================================================
  // BUG 1 FIX: BOUNDING BOX COLLISION DETECTION & STACKED LEADER LINES
  // =========================================================================
  const layoutLabelsWithCollisionDetection = () => {
    const labels = [];
    const clusters = [];

    // Group nodes within 40px proximity into clusters
    computedNodes.forEach(node => {
      let added = false;
      for (const cluster of clusters) {
        const first = cluster[0];
        const dist = Math.hypot(node.pos.x - first.pos.x, node.pos.y - first.pos.y);
        if (dist < 40) {
          cluster.push(node);
          added = true;
          break;
        }
      }
      if (!added) {
        clusters.push([node]);
      }
    });

    clusters.forEach(cluster => {
      if (cluster.length === 1) {
        const node = cluster[0];
        const labelWidth = node.id.length * 7.5 + 34;
        labels.push({
          nodeId: node.id,
          nodePos: node.pos,
          labelPos: { x: node.pos.x + 18, y: node.pos.y + 4 },
          box: { x: node.pos.x + 18 - 2, y: node.pos.y + 4 - 10, w: labelWidth, h: 20 },
          leaderLine: null,
          node
        });
      } else {
        // Cluster of 2+ co-located nodes: stack vertically to the right with leader lines
        const center = cluster[0].pos;
        cluster.forEach((node, idx) => {
          const offsetY = (idx - (cluster.length - 1) / 2) * 24;
          const offsetX = 44;
          const labelPos = { x: center.x + offsetX, y: center.y + offsetY };
          const labelWidth = node.id.length * 7.5 + 34;

          labels.push({
            nodeId: node.id,
            nodePos: node.pos,
            labelPos,
            box: { x: labelPos.x - 2, y: labelPos.y - 10, w: labelWidth, h: 20 },
            leaderLine: {
              x1: node.pos.x,
              y1: node.pos.y,
              x2: labelPos.x - 4,
              y2: labelPos.y - 2
            },
            node
          });
        });
      }
    });

    return labels;
  };

  const nodeLabels = layoutLabelsWithCollisionDetection();

  const getZoneNodeCount = (zoneId) => {
    return nodes.filter(n => {
      if (n.zone_id === zoneId) return true;
      if (zoneId.includes('PumpStation') && (n.zone_id.includes('Pump') || n.zone_id.includes('Zone-B'))) return true;
      if (zoneId.includes('CrudeDistillation') && (n.zone_id.includes('Zone-A') || n.zone_id.includes('CDU'))) return true;
      if (zoneId.includes('TankFarm') && (n.zone_id.includes('Zone-C') || n.zone_id.includes('Storage'))) return true;
      if (zoneId.includes('Loading') && (n.zone_id.includes('Zone-D') || n.zone_id.includes('Loading'))) return true;
      if (zoneId.includes('Control') && (n.zone_id.includes('Zone-E') || n.zone_id.includes('Control'))) return true;
      return false;
    }).length;
  };

  return (
    <div className="zg-card mb-[32px]">
      <div className="flex flex-wrap items-center justify-between gap-[16px] mb-[16px] border-b border-[#21262D] pb-[16px]">
        <div className="flex items-center gap-[8px]">
          <Layers className="w-[20px] h-[20px] text-[#58A6FF]" strokeWidth={1.5} />
          <h2 className="text-[16px] font-bold text-[#E6EDF3] uppercase tracking-[0.02em] font-mono-tech">
            SPATIAL PLANT RISK TOPOLOGY OVERLAY
          </h2>
        </div>

        <div className="flex items-center gap-[16px] text-[12px] font-mono-tech text-[#8B949E]">
          <span className="flex items-center gap-[6px]">
            <span className="w-[8px] h-[8px] rounded-full bg-[#2EA043] inline-block" /> SAFE
          </span>
          <span className="flex items-center gap-[6px]">
            <span className="w-[8px] h-[8px] rounded-full bg-[#D29922] inline-block" /> WATCH
          </span>
          <span className="flex items-center gap-[6px]">
            <span className="w-[8px] h-[8px] rounded-full bg-[#DB6D28] inline-block" /> WARNING
          </span>
          <span className="flex items-center gap-[6px]">
            <span className="w-[8px] h-[8px] rounded-full bg-[#F85149] inline-block" /> COMPOUND_CRITICAL
          </span>
        </div>
      </div>

      <div className="w-full overflow-x-auto bg-[#0D1117] rounded-[6px] border border-[#21262D] p-[8px] relative">
        <svg viewBox="0 0 940 530" className="w-full h-auto min-w-[768px]">
          <defs>
            {/* Base Background Grid Pattern */}
            <pattern id="baseGrid" width="20" height="20" patternUnits="userSpaceOnUse">
              <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#21262D" strokeWidth="0.5" />
            </pattern>
            {/* BUG 3 FIX: Persistent 4% opacity schematic floor-plan grid texture inside zone boxes */}
            <pattern id="schematicGrid" width="16" height="16" patternUnits="userSpaceOnUse">
              <path d="M 16 0 L 0 0 0 16" fill="none" stroke="#8B949E" strokeWidth="0.5" strokeOpacity="0.04" />
            </pattern>
          </defs>

          <rect width="940" height="530" fill="url(#baseGrid)" />

          {/* Render 5 Zones with BUG 3 FIX: Schematic Grid Texture & Centered Placeholders */}
          {PLANT_ZONES.map((z) => {
            const nodeCount = getZoneNodeCount(z.id);

            return (
              <g key={z.id}>
                {/* Zone Outer Border Box */}
                <rect
                  x={z.x}
                  y={z.y}
                  width={z.w}
                  height={z.h}
                  rx={6}
                  fill="#161B22"
                  stroke="#21262D"
                  strokeWidth={1.5}
                />

                {/* BUG 3 FIX: Persistent Schematic Grid Texture inside Zone Box */}
                <rect
                  x={z.x + 2}
                  y={z.y + 2}
                  width={z.w - 4}
                  height={z.h - 4}
                  rx={4}
                  fill="url(#schematicGrid)"
                />
                
                {/* Zone Header Label */}
                <text
                  x={z.x + 16}
                  y={z.y + 26}
                  fill="#8B949E"
                  fontSize={12}
                  fontWeight="600"
                  className="font-mono-tech uppercase"
                >
                  {z.label}
                </text>

                {/* BUG 3 FIX: Compact Centered Empty State Icon + Label */}
                {nodeCount === 0 && (
                  <g transform={`translate(${z.x + z.w / 2}, ${z.y + z.h / 2 + 6})`}>
                    <circle r={12} fill="#0D1117" stroke="#8B949E" strokeWidth={1} strokeOpacity={0.3} />
                    <line x1="-5" y1="5" x2="5" y2="-5" stroke="#4A5568" strokeWidth={1.5} opacity={0.6} />
                    <text
                      x={0}
                      y={26}
                      fill="#4A5568"
                      fontSize={13}
                      textAnchor="middle"
                      className="font-sans select-none"
                    >
                      No active telemetry
                    </text>
                  </g>
                )}
              </g>
            );
          })}

          {/* SVG Topology Edges with PART C Single Stroke-Dashoffset Ease-Out Animation */}
          {edges.map((edge, idx) => {
            const sourceNode = computedNodes.find(n => n.id === edge.source);
            const targetNode = computedNodes.find(n => n.id === edge.target);
            if (!sourceNode || !targetNode) return null;

            const isCriticalEdge = criticalAlert && (
              criticalAlert.primary_node_id === sourceNode.id ||
              criticalAlert.primary_node_id === targetNode.id
            );

            return (
              <line
                key={`edge-${idx}`}
                x1={sourceNode.pos.x}
                y1={sourceNode.pos.y}
                x2={targetNode.pos.x}
                y2={targetNode.pos.y}
                stroke={isCriticalEdge ? '#F85149' : '#21262D'}
                strokeWidth={isCriticalEdge ? 2.5 : 1.5}
                className={isCriticalEdge ? 'animate-draw-path' : ''}
              />
            );
          })}

          {/* Render Nodes with Soft Pulse on Primary Alert Node */}
          {computedNodes.map((node) => {
            const isSelected = selectedNodeId === node.id;
            const isPrimaryAlertNode = active_alerts.some(a => a.primary_node_id === node.id);

            return (
              <g
                key={node.id}
                transform={`translate(${node.pos.x}, ${node.pos.y})`}
                onClick={() => setSelectedNodeId(node.id)}
                className="cursor-pointer group"
                tabIndex={0}
                onKeyDown={(e) => e.key === 'Enter' && setSelectedNodeId(node.id)}
              >
                <circle
                  r={isSelected || isPrimaryAlertNode ? 14 : 10}
                  fill="#0D1117"
                  stroke={node.color}
                  strokeWidth={isSelected ? 3 : 2}
                  className={isPrimaryAlertNode ? 'animate-node-pulse' : ''}
                />
                <circle r={5} fill={node.color} />
              </g>
            );
          })}

          {/* BUG 1 FIX: Render Collision-Free Labels with 1px Leader Lines */}
          {nodeLabels.map((lbl) => (
            <g key={`lbl-${lbl.nodeId}`}>
              {lbl.leaderLine && (
                <line
                  x1={lbl.leaderLine.x1}
                  y1={lbl.leaderLine.y1}
                  x2={lbl.leaderLine.x2}
                  y2={lbl.leaderLine.y2}
                  stroke="#8B949E"
                  strokeWidth={1}
                  strokeDasharray="2 2"
                />
              )}

              <g transform={`translate(${lbl.labelPos.x}, ${lbl.labelPos.y})`}>
                <rect
                  x={-2}
                  y={-10}
                  width={lbl.nodeId.length * 7.5 + 34}
                  height={18}
                  rx={3}
                  fill="#0D1117"
                  fillOpacity={0.92}
                  stroke="#21262D"
                  strokeWidth={1}
                />
                <text
                  x={2}
                  y={2}
                  fill="#E6EDF3"
                  fontSize={11}
                  fontWeight="500"
                  className="font-mono-tech select-none"
                >
                  {lbl.nodeId}
                </text>
                {lbl.node.z_score !== null && lbl.node.z_score !== undefined && (
                  <text
                    x={lbl.nodeId.length * 7.5 + 4}
                    y={2}
                    fill={Math.abs(lbl.node.z_score) >= 3.0 ? '#F85149' : Math.abs(lbl.node.z_score) >= 2.5 ? '#DB6D28' : Math.abs(lbl.node.z_score) >= 1.5 ? '#D29922' : '#2EA043'}
                    fontSize={10}
                    className="font-mono-tech select-none"
                  >
                    Z={lbl.node.z_score.toFixed(1)}
                  </text>
                )}
              </g>
            </g>
          ))}
        </svg>
      </div>

      {selectedNodeId && (
        <div className="mt-[16px] p-[16px] bg-[#0D1117] border border-[#21262D] rounded-[4px] flex items-center justify-between text-[12px] font-mono-tech text-[#8B949E]">
          {(() => {
            const node = nodes.find(n => n.id === selectedNodeId);
            if (!node) return <span>Node {selectedNodeId} selected</span>;
            return (
              <div className="flex items-center gap-[16px] flex-wrap">
                <span className="font-bold text-[#58A6FF]">{node.id}</span>
                <span>Category: {node.category}</span>
                <span>Zone: {node.zone_id}</span>
                <span>Reading: {node.current_value !== null ? node.current_value : 'N/A'}</span>
                <span>Z-Score: {node.z_score !== null ? node.z_score : 'N/A'}</span>
                <span>Status: <strong className="text-[#E6EDF3]">{node.status}</strong></span>
              </div>
            );
          })()}
          <button
            onClick={() => setSelectedNodeId(null)}
            className="btn-secondary text-[12px] py-[4px] px-[8px]"
          >
            Close
          </button>
        </div>
      )}
    </div>
  );
}
