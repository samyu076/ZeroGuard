import React, { useState } from 'react';
import { Sliders, Activity, ShieldCheck, AlertTriangle, GitBranch, History } from 'lucide-react';

export default function CounterfactualExplorerPanel() {
  const [isolationTiming, setIsolationTiming] = useState('now');

  const getTrajectoryData = () => {
    if (isolationTiming === 'now') {
      return {
        label: 'Isolate Spectacle Blind / Valve V-102 Immediately (T+0m)',
        projectedRisk: 12.0,
        riskLevel: 'SAFE',
        color: '#2EA043',
        description: 'Immediate physical line break isolation prevents hydrocarbon accumulation. Zero interlock escalation.',
        resemblanceScore: '14.2% (Low Risk Similarity)'
      };
    } else if (isolationTiming === '10m') {
      return {
        label: 'Delayed Isolation in 10 Minutes (T+10m)',
        projectedRisk: 48.5,
        riskLevel: 'WATCH',
        color: '#D29922',
        description: 'Gas concentration reaches 4% LEL before isolation closes. Requires localized ventilation clearing.',
        resemblanceScore: '42.1% (Moderate Similarity to Jamnagar 2021)'
      };
    } else {
      return {
        label: 'No Isolation (Continue Hot Work Maintenance)',
        projectedRisk: 100.0,
        riskLevel: 'COMPOUND_CRITICAL',
        color: '#F85149',
        description: 'Unisolated hot welding ignites accumulated hydrocarbons at T+18m. Mandatory statutory trip engaged.',
        resemblanceScore: '68.4% (High Similarity to Visakhapatnam 2025)'
      };
    }
  };

  const currentTrajectory = getTrajectoryData();

  return (
    <div className="zg-card mb-[32px] border-[#58A6FF]/40">
      {/* Panel Header */}
      <div className="flex flex-wrap items-center justify-between gap-[16px] mb-[16px] border-b border-[#21262D] pb-[16px]">
        <div className="flex items-center gap-[8px]">
          <GitBranch className="w-[20px] h-[20px] text-[#58A6FF]" strokeWidth={1.5} />
          <h3 className="text-[16px] font-bold text-[#E6EDF3] uppercase tracking-[0.02em] font-mono-tech">
            COUNTERFACTUAL SCENARIO EXPLORER & DECISION SUPPORT
          </h3>
        </div>
        <span className="text-[11px] font-mono-tech text-[#8B949E] px-[8px] py-[4px] bg-[#0D1117] border border-[#21262D] rounded-[4px]">
          Model-Based Projections (Not Guarantees)
        </span>
      </div>

      <p className="text-[12px] text-[#8B949E] font-sans mb-[20px]">
        Evaluate predicted risk trajectories if control room operators execute isolation valve V-102 closing now vs in 10 minutes vs taking no action.
      </p>

      {/* Control Selector */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-[12px] mb-[20px] font-mono-tech text-[12px]">
        <button
          onClick={() => setIsolationTiming('now')}
          className={`p-[14px] rounded-[4px] border text-left transition-all ${
            isolationTiming === 'now' ? 'bg-[#2EA043]/15 border-[#2EA043] text-[#2EA043] font-bold' : 'bg-[#0D1117] border-[#21262D] text-[#8B949E]'
          }`}
        >
          <span className="block text-[11px] uppercase text-[#8B949E] mb-[2px]">Option A</span>
          <span className="text-[13px] font-sans block">Isolate Valve V-102 Now</span>
          <span className="text-[11px] font-mono-tech text-[#2EA043] mt-[4px] block">Projected Risk: 12.0 (SAFE)</span>
        </button>

        <button
          onClick={() => setIsolationTiming('10m')}
          className={`p-[14px] rounded-[4px] border text-left transition-all ${
            isolationTiming === '10m' ? 'bg-[#D29922]/15 border-[#D29922] text-[#D29922] font-bold' : 'bg-[#0D1117] border-[#21262D] text-[#8B949E]'
          }`}
        >
          <span className="block text-[11px] uppercase text-[#8B949E] mb-[2px]">Option B</span>
          <span className="text-[13px] font-sans block">Isolate in 10 Minutes</span>
          <span className="text-[11px] font-mono-tech text-[#D29922] mt-[4px] block">Projected Risk: 48.5 (WATCH)</span>
        </button>

        <button
          onClick={() => setIsolationTiming('none')}
          className={`p-[14px] rounded-[4px] border text-left transition-all ${
            isolationTiming === 'none' ? 'bg-[#F85149]/15 border-[#F85149] text-[#F85149] font-bold' : 'bg-[#0D1117] border-[#21262D] text-[#8B949E]'
          }`}
        >
          <span className="block text-[11px] uppercase text-[#8B949E] mb-[2px]">Option C</span>
          <span className="text-[13px] font-sans block">No Action / Continue Work</span>
          <span className="text-[11px] font-mono-tech text-[#F85149] mt-[4px] block">Projected Risk: 100.0 (CRITICAL)</span>
        </button>
      </div>

      {/* Trajectory Outcome Display */}
      <div className="p-[20px] bg-[#0D1117] border border-[#21262D] rounded-[6px] font-mono-tech text-[12px] space-y-[16px]">
        <div className="flex items-center justify-between border-b border-[#21262D] pb-[12px]">
          <div>
            <span className="text-[#8B949E] text-[11px] uppercase block">Selected Decision Path</span>
            <span className="text-[14px] font-bold text-[#E6EDF3] font-sans">{currentTrajectory.label}</span>
          </div>
          <span className="px-[12px] py-[6px] rounded-[4px] font-bold text-[12px]" style={{ color: currentTrajectory.color, backgroundColor: `${currentTrajectory.color}20`, border: `1px solid ${currentTrajectory.color}50` }}>
            {currentTrajectory.riskLevel} ({currentTrajectory.projectedRisk.toFixed(1)})
          </span>
        </div>

        <p className="text-[12px] text-[#E6EDF3] font-sans leading-[1.5]">
          {currentTrajectory.description}
        </p>

        {/* Item 3: Historical Pattern Match */}
        <div className="p-[12px] bg-[#161B22] border border-[#21262D] rounded-[4px] flex items-center justify-between">
          <div className="flex items-center gap-[8px] text-[#8B949E]">
            <History className="w-[16px] h-[16px] text-[#58A6FF]" strokeWidth={1.5} />
            <span>Historical Incident Pattern Similarity Score:</span>
          </div>
          <span className="font-bold text-[#58A6FF]">{currentTrajectory.resemblanceScore}</span>
        </div>
      </div>
    </div>
  );
}
