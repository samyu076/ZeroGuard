import React, { useState } from 'react';
import { Layers } from 'lucide-react';

const PLANT_ZONES = [
  { id: 'Zone-A-CrudeDistillation', label: 'Zone A: Crude Distillation Unit (CDU)', x: 30, y: 30, w: 275, h: 220 },
  { id: 'Zone-B-PumpStation', label: 'Zone B: Hydrocracker Feed Pump Station', x: 330, y: 30, w: 275, h: 220 },
  { id: 'Zone-C-TankFarm', label: 'Zone C: Hydrocarbon Tank Farm C-10', x: 630, y: 30, w: 275, h: 220 },
  { id: 'Zone-D-Loading', label: 'Zone D: Truck Loading & Unloading Rack', x: 180, y: 280, w: 275, h: 220 },
  { id: 'Zone-E-Control', label: 'Zone E: Main Plant Control Room & Substation', x: 480, y: 280, w: 275, h: 220 },
];

const ZONE_CENTERS_MAP = {
  'Zone-A-CrudeDistillation': { cx: 45.0, cy: 120.0, r: 30.0 },
  'Zone-B-PumpStation': { cx: 110.0, cy: 140.0, r: 25.0 },
  'Zone-C-TankFarm': { cx: 220.0, cy: 80.0, r: 50.0 },
  'Zone-D-Loading': { cx: 180.0, cy: 210.0, r: 35.0 },
  'Zone-E-Control': { cx: 50.0, cy: 40.0, r: 20.0 },
  // Fallbacks from scenario datasets
  'Zone-A-BoilerRoom': { cx: 45.0, cy: 120.0, r: 30.0 },
  'Zone-C-Storage': { cx: 220.0, cy: 80.0, r: 50.0 }
};

export default function GraphVisualizer({ graphState, onSelectAlert }) {
  const [selectedNodeId, setSelectedNodeId] = useState(null);

  if (!graphState) return null;

  const { nodes = [], edges = [], active_alerts = [] } = graphState;

  const criticalAlert = active_alerts.find(
    a => a.risk_level === 'CRITICAL' || a.triggered_by === 'RULE_GUARD'
  );

  const getMatchedZoneBox = (nodeZoneId) => {
    if (!nodeZoneId) return PLANT_ZONES[0];
    const match = PLANT_ZONES.find(
      z => z.id.toLowerCase().includes(nodeZoneId.toLowerCase()) || 
           nodeZoneId.toLowerCase().includes(z.id.toLowerCase()) ||
           (z.id.includes('PumpStation') && nodeZoneId.includes('Pump')) ||
           (z.id.includes('CrudeDistillation') && nodeZoneId.includes('Boiler')) ||
           (z.id.includes('TankFarm') && nodeZoneId.includes('Storage'))
    );
    return match || PLANT_ZONES[0];
  };

  const getNodePos = (node) => {
    const rawX = node.attributes?.x ?? 100.0;
    const rawY = node.attributes?.y ?? 100.0;
    const nodeZoneId = node.zone_id || 'Zone-A-CrudeDistillation';
    const z = getMatchedZoneBox(nodeZoneId);
    
    let rawCenter = ZONE_CENTERS_MAP[nodeZoneId] || ZONE_CENTERS_MAP[z.id];
    if (!rawCenter) {
      rawCenter = { cx: 100.0, cy: 100.0, r: 40.0 };
    }

    const dx = rawX - rawCenter.cx;
    const dy = rawY - rawCenter.cy;

    // Padding parameters to stay inside zone borders cleanly
    const paddingX = 45;
    const paddingY = 55;

    const svgX = (z.x + z.w / 2) + (dx / Math.max(rawCenter.r, 1.0)) * (z.w / 2 - paddingX);
    const svgY = (z.y + z.h / 2 + 15) + (dy / Math.max(rawCenter.r, 1.0)) * (z.h / 2 - paddingY);

    return { x: svgX, y: svgY };
  };

  const getNodeColor = (node) => {
    if (node.status === 'CRITICAL' || node.status === 'NON_COMPLIANT') return '#F85149';
    if (node.status === 'WARNING' || Math.abs(node.z_score || 0) >= 2.5) return '#DB6D28';
    if (Math.abs(node.z_score || 0) >= 1.5) return '#D29922';
    return '#2EA043';
  };

  // Filter out non-renderable zone nodes to prevent diagram clashing
  const renderableNodes = nodes.filter(
    n => n.category !== 'ZONE' && n.category !== 'EQUIPMENT'
  );

  const computedNodes = renderableNodes.map(n => ({
    ...n,
    pos: getNodePos(n),
    color: getNodeColor(n)
  }));

  const layoutLabelsWithCollisionDetection = () => {
    const labels = [];
    const clusters = [];

    computedNodes.forEach(node => {
      let added = false;
      for (const cluster of clusters) {
        const first = cluster[0];
        const dist = Math.hypot(node.pos.x - first.pos.x, node.pos.y - first.pos.y);
        if (dist < 32) {
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
    return renderableNodes.filter(n => {
      if (n.zone_id === zoneId) return true;
      if (zoneId.includes('PumpStation') && (n.zone_id.includes('Pump') || n.zone_id.includes('Zone-B'))) return true;
      if (zoneId.includes('CrudeDistillation') && (n.zone_id.includes('Zone-A') || n.zone_id.includes('CDU') || n.zone_id.includes('Boiler'))) return true;
      if (zoneId.includes('TankFarm') && (n.zone_id.includes('Zone-C') || n.zone_id.includes('Storage') || n.zone_id.includes('Tanks'))) return true;
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
            <pattern id="baseGrid" width="20" height="20" patternUnits="userSpaceOnUse">
              <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#21262D" strokeWidth="0.5" />
            </pattern>
            <pattern id="schematicGrid" width="16" height="16" patternUnits="userSpaceOnUse">
              <path d="M 16 0 L 0 0 0 16" fill="none" stroke="#8B949E" strokeWidth="0.5" strokeOpacity="0.04" />
            </pattern>
          </defs>

          <rect width="940" height="530" fill="url(#baseGrid)" />

          {/* Render 5 Zones */}
          {PLANT_ZONES.map((z) => {
            const nodeCount = getZoneNodeCount(z.id);

            return (
              <g key={z.id}>
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

                <rect
                  x={z.x + 2}
                  y={z.y + 2}
                  width={z.w - 4}
                  height={z.h - 4}
                  rx={4}
                  fill="url(#schematicGrid)"
                />
                
                <text
                  x={z.x + 16}
                  y={z.y + 26}
                  fill="#8B949E"
                  fontSize={11}
                  fontWeight="600"
                  className="font-mono-tech uppercase"
                >
                  {z.label}
                </text>

                {nodeCount === 0 && (
                  <g transform={`translate(${z.x + z.w / 2}, ${z.y + z.h / 2 + 10})`}>
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

          {/* SVG Topology Edges */}
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

          {/* Render Nodes */}
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

          {/* Render Collision-Free Labels */}
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
                <circle cx={4} cy={-1} r={3.5} fill={lbl.node.color} />
                <text
                  x={12}
                  y={3}
                  fill="#E6EDF3"
                  fontSize={10}
                  fontWeight="500"
                  className="font-mono-tech"
                >
                  {lbl.nodeId}
                </text>
              </g>
            </g>
          ))}
        </svg>
      </div>
    </div>
  );
}
