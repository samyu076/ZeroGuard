import React from 'react';
import { Cpu, X, Server, Network, ShieldCheck, Zap } from 'lucide-react';

export default function ScalabilityArchitectureModal({ isOpen, onClose }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-[#0D1117]/90 backdrop-blur-md z-50 flex items-center justify-center p-[16px]">
      <div className="zg-modal-panel max-w-3xl w-full relative border-[#58A6FF]/40">
        <button
          onClick={onClose}
          className="absolute right-[16px] top-[16px] text-[#8B949E] hover:text-[#E6EDF3] p-[4px]"
        >
          <X className="w-[16px] h-[16px]" strokeWidth={1.5} />
        </button>

        {/* Modal Header */}
        <div className="flex items-center gap-[8px] mb-[16px] border-b border-[#21262D] pb-[16px]">
          <Cpu className="w-[22px] h-[22px] text-[#58A6FF]" strokeWidth={1.5} />
          <h3 className="text-[16px] font-bold text-[#E6EDF3] uppercase tracking-[0.02em] font-mono-tech">
            ENTERPRISE MULTI-PLANT SCALABILITY ARCHITECTURE ROADMAP
          </h3>
        </div>

        {/* B4: Softened Copy Banner */}
        <div className="p-[12px] bg-[#58A6FF]/10 border border-[#58A6FF]/40 rounded-[4px] mb-[16px] font-mono-tech text-[12px] text-[#58A6FF]">
          <strong>Schema Architecture Guarantee:</strong> Configurable across plants via external schema — zone layout, sensor types, and thresholds are data, not hardcoded logic.
        </div>

        {/* Architecture Details */}
        <div className="space-y-[16px] text-[12px] font-mono-tech">
          {/* Layer 1: SCADA Ingestion */}
          <div className="p-[16px] bg-[#0D1117] border border-[#21262D] rounded-[4px]">
            <div className="flex items-center gap-[8px] text-[#58A6FF] font-bold mb-[6px]">
              <Server className="w-[16px] h-[16px]" strokeWidth={1.5} />
              <span>1. Industrial Telemetry Ingestion (OPC-UA / Modbus TCP / MQTT)</span>
            </div>
            <p className="text-[12px] text-[#E6EDF3] font-sans leading-[1.5]">
              Replaces synthetic scenarios with high-throughput Apache Kafka / Eclipse Mosquitto MQTT brokers. Ingests raw PLC/DCS telemetry streams (Honeywell Experion, Yokogawa CENTUM, Emerson DeltaV) at 10,000 events/second per refinery zone.
            </p>
          </div>

          {/* Layer 2: Graph Scaling */}
          <div className="p-[16px] bg-[#0D1117] border border-[#21262D] rounded-[4px]">
            <div className="flex items-center gap-[8px] text-[#58A6FF] font-bold mb-[6px]">
              <Network className="w-[16px] h-[16px]" strokeWidth={1.5} />
              <span>2. Multi-Site Spatio-Temporal Graph Partitioning (Distributed PageRank)</span>
            </div>
            <p className="text-[12px] text-[#E6EDF3] font-sans leading-[1.5]">
              Partitioned spatial risk graph deployed on Apache Spark GraphX / Memgraph cluster. Plant zones (CDU, Hydrocracker, Tank Farm) run isolated graph propagation workers while cross-zone pipelines maintain inter-zone spatial coupling weights ($W_{ij}$).
            </p>
          </div>

          {/* Layer 3: Sub-50ms Interlock Latency */}
          <div className="p-[16px] bg-[#0D1117] border border-[#21262D] rounded-[4px]">
            <div className="flex items-center gap-[8px] text-[#2EA043] font-bold mb-[6px]">
              <Zap className="w-[16px] h-[16px]" strokeWidth={1.5} />
              <span>3. Edge-Compute Statutory Interlocks (&lt;50ms Response Time)</span>
            </div>
            <p className="text-[12px] text-[#E6EDF3] font-sans leading-[1.5]">
              Rule-Guard engine deployed as lightweight Rust/C++ compiled micro-services at on-site plant edge nodes. Evaluates statutory OISD, Factory Act, and DGMS rules locally to trigger physical emergency isolation trip signals in &lt;50ms, even during cloud network loss.
            </p>
          </div>

          <div className="flex justify-end pt-[8px]">
            <button
              onClick={onClose}
              className="btn-primary"
            >
              Close Architecture Spec
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
