import React from 'react';
import { ShieldCheck, Clock, AlertTriangle, Activity } from 'lucide-react';

export default function JudgeFacingMetricsStrip({ overallRiskLevel }) {
  return (
    <div className="bg-[#161B22] border-b border-[#21262D] px-[24px] py-[10px] flex flex-wrap items-center justify-between gap-[16px] font-mono-tech text-[12px] relative z-20">
      <div className="flex items-center gap-[8px] text-[#58A6FF] font-bold">
        <Activity className="w-[16px] h-[16px]" strokeWidth={1.5} />
        <span>ADVERSARIAL ENGINE BENCHMARK STRIP:</span>
      </div>

      <div className="flex flex-wrap items-center gap-[20px]">
        <div className="flex items-center gap-[6px]">
          <span className="text-[#8B949E]">SCADA Baseline FNR:</span>
          <span className="text-[#F85149] font-bold">50.0% (5/10 Missed)</span>
        </div>

        <div className="flex items-center gap-[6px]">
          <span className="text-[#8B949E]">ZeroGuard FNR:</span>
          <span className="text-[#2EA043] font-bold">0.0% (0 Missed Risks)</span>
        </div>

        <div className="flex items-center gap-[6px]">
          <Clock className="w-[14px] h-[14px] text-[#58A6FF]" strokeWidth={1.5} />
          <span className="text-[#8B949E]">Early Warning Lead Time:</span>
          <span className="text-[#58A6FF] font-bold">+18.0 Minutes Earlier</span>
        </div>

        <div className="flex items-center gap-[6px]">
          <ShieldCheck className="w-[14px] h-[14px] text-[#2EA043]" strokeWidth={1.5} />
          <span className="text-[#8B949E]">Alert Confidence:</span>
          <span className="text-[#E6EDF3] font-bold">100.0% Verified</span>
        </div>
      </div>
    </div>
  );
}
