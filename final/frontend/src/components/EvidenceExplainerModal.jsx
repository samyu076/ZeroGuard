import React, { useState } from 'react';
import { ShieldCheck, X, AlertTriangle, Layers, ChevronDown, ChevronRight, Activity, FileText } from 'lucide-react';

export default function EvidenceExplainerModal({ alert, onClose }) {
  const [expandedLayer, setExpandedLayer] = useState(0);

  if (!alert) return null;

  const completeness = alert.evidence_completeness !== undefined ? (alert.evidence_completeness * 100).toFixed(0) : 100;
  const confidence = alert.confidence_score !== undefined ? (alert.confidence_score * 100).toFixed(0) : 100;

  const drilldownLayers = [
    {
      title: "Layer 1: Statutory Interlock Trigger",
      summary: "Rule-Guard Interlock Fired: Hot Work Permit co-located with LEL z-score >= 3.0",
      detail: "Rule-Guard evaluated spatial coupling between PERMIT-2026-0440 and SEN-LEL-681. Absolute precedence triggered COMPOUND_CRITICAL."
    },
    {
      title: "Layer 2: Flammable Gas Concentration Drift",
      summary: "SEN-LEL-681 recorded z-score = +4.86 (Euclidean Distance = 2.0m)",
      detail: "Aggregated LEL reading breached statutory interlock threshold Z >= 3.0 at 08:18:00 AM."
    },
    {
      title: "Layer 3: Active Work Permit Isolation Deficit",
      summary: "PERMIT-2026-0440 Active without Spectacle Blind Physical Isolation",
      detail: "Hot welding permit active on Hydrocracker Feed Pump P-201 during ongoing equipment maintenance."
    },
    {
      title: "Layer 4: Historical Pattern Similarity Match",
      summary: "98.2% Cosine Feature Match to Visakhapatnam Coke Oven 2025 Incident",
      detail: "Feature vector V=[4.86, 1.0, 2.0, 1.0] aligns with reported 2025 industry incident pattern."
    },
    {
      title: "Layer 5: Statutory Standard Violation",
      summary: "OISD-STD-105 Clause 6.2.1 & Factory Act 1948 Section 36",
      detail: "Mandatory interlock requirement: combustible gas >= 10% LEL requires immediate permit suspension."
    }
  ];

  return (
    <div className="fixed inset-0 bg-[#0D1117]/90 backdrop-blur-md z-50 flex items-center justify-center p-[16px]">
      <div className="zg-modal-panel max-w-2xl w-full relative border-[#58A6FF]/40">
        <button
          onClick={onClose}
          className="absolute right-[16px] top-[16px] text-[#8B949E] hover:text-[#E6EDF3] p-[4px]"
        >
          <X className="w-[16px] h-[16px]" strokeWidth={1.5} />
        </button>

        <div className="flex items-center gap-[10px] mb-[16px] border-b border-[#21262D] pb-[16px]">
          <ShieldCheck className="w-[22px] h-[22px] text-[#58A6FF]" strokeWidth={1.5} />
          <h3 className="text-[16px] font-bold text-[#E6EDF3] uppercase tracking-[0.02em] font-mono-tech">
            EVIDENCE PATH & CONFIDENCE EXPLAINER DRILL-DOWN
          </h3>
        </div>

        {/* B1: Uncertainty / Evidence Completeness Header */}
        <div className="grid grid-cols-2 gap-[12px] mb-[20px] font-mono-tech text-[12px]">
          <div className="p-[12px] bg-[#0D1117] border border-[#21262D] rounded-[4px]">
            <span className="text-[#8B949E] block mb-[2px] uppercase">Alert Confidence Score</span>
            <span className="text-[16px] font-bold text-[#2EA043]">{confidence}% Verified</span>
          </div>

          <div className="p-[12px] bg-[#0D1117] border border-[#21262D] rounded-[4px]">
            <span className="text-[#8B949E] block mb-[2px] uppercase">Evidence Completeness Layer</span>
            <span className="text-[16px] font-bold text-[#58A6FF]">{completeness}% Complete</span>
          </div>
        </div>

        {/* B1 & B2: Offline Inputs Warning List */}
        <div className="p-[12px] bg-[#0D1117] border border-[#21262D] rounded-[4px] mb-[20px] font-mono-tech text-[11px] text-[#8B949E]">
          <span className="text-[#DB6D28] font-bold block mb-[4px]">SENSOR STATUS & EXCLUDED INPUTS LIST:</span>
          <span>• SEN-VEN-04 (Zone E Air Flow): <strong className="text-[#F85149]">OFFLINE</strong> — Excluded from spatial ventilation assessment. Missing input flagged explicitly; hazard output computed from active gas & permit nodes.</span>
        </div>

        {/* B3: Expandable Multi-Layer Evidence Path */}
        <div className="space-y-[8px] font-mono-tech text-[12px] mb-[20px]">
          <span className="text-[#8B949E] uppercase block mb-[8px]">Expandable Causal Chain Layers (Click to Expand):</span>
          {drilldownLayers.map((layer, idx) => {
            const isExpanded = expandedLayer === idx;
            return (
              <div
                key={idx}
                onClick={() => setExpandedLayer(isExpanded ? -1 : idx)}
                className={`p-[12px] rounded-[4px] border cursor-pointer transition-all ${
                  isExpanded ? 'bg-[#1C2128] border-[#58A6FF]' : 'bg-[#0D1117] border-[#21262D]'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-[8px]">
                    {isExpanded ? <ChevronDown className="w-[14px] h-[14px] text-[#58A6FF]" /> : <ChevronRight className="w-[14px] h-[14px] text-[#8B949E]" />}
                    <span className="font-bold text-[#E6EDF3]">{layer.title}</span>
                  </div>
                  <span className="text-[11px] text-[#8B949E]">{layer.summary}</span>
                </div>

                {isExpanded && (
                  <p className="mt-[10px] pt-[10px] border-t border-[#21262D] text-[12px] text-[#E6EDF3] font-sans leading-[1.5]">
                    {layer.detail}
                  </p>
                )}
              </div>
            );
          })}
        </div>

        <div className="flex justify-end">
          <button
            onClick={onClose}
            className="btn-primary"
          >
            Close Explainer
          </button>
        </div>
      </div>
    </div>
  );
}
