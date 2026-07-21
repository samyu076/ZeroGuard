import React, { useState, useEffect } from 'react';
import { Play, Pause, SkipForward, RotateCcw, ShieldAlert, Clock, Sliders, ArrowRight } from 'lucide-react';

const REPLAY_TIMESTEPS = [
  {
    step: 0,
    timeLabel: "T+00 min",
    timestamp: "08:00:00 AM",
    description: "Shift Changeover Window — Normal Operating Baseline",
    gasZScore: 0.2,
    permitStatus: "COMPLIANT",
    maintActive: true,
    zeroguardLevel: "NORMAL",
    scadaLevel: "NORMAL",
    leadTimeMarker: null
  },
  {
    step: 1,
    timeLabel: "T+05 min",
    timestamp: "08:05:00 AM",
    description: "Hot Work Permit PERMIT-2026-0440 Issued for Feed Pump Welding",
    gasZScore: 0.5,
    permitStatus: "NON_COMPLIANT",
    maintActive: true,
    zeroguardLevel: "NORMAL",
    scadaLevel: "NORMAL",
    leadTimeMarker: null
  },
  {
    step: 2,
    timeLabel: "T+10 min",
    timestamp: "08:10:00 AM",
    description: "Concurrent Hydrocracker Equipment Maintenance Active",
    gasZScore: 1.2,
    permitStatus: "NON_COMPLIANT",
    maintActive: true,
    zeroguardLevel: "WATCH",
    scadaLevel: "NORMAL",
    leadTimeMarker: null
  },
  {
    step: 3,
    timeLabel: "T+15 min",
    timestamp: "08:15:00 AM",
    description: "Fugitive Hydrocarbon Gas Accumulation Begins (Sub-threshold Z=+1.85)",
    gasZScore: 1.85,
    permitStatus: "NON_COMPLIANT",
    maintActive: true,
    zeroguardLevel: "WARNING",
    scadaLevel: "NORMAL",
    leadTimeMarker: null
  },
  {
    step: 4,
    timeLabel: "T+18 min",
    timestamp: "08:18:00 AM",
    description: "⚡ ZEROGUARD TRIPLE-CORRELATION ENGINE FIRES MANDATORY INTERLOCK",
    gasZScore: 3.10,
    permitStatus: "NON_COMPLIANT",
    maintActive: true,
    zeroguardLevel: "COMPOUND_CRITICAL",
    scadaLevel: "NORMAL",
    leadTimeMarker: "ZeroGuard flags compound critical risk at T+18min. SCADA Baseline would not fire until T+36min (18 Minute Safety Gap Saved)."
  },
  {
    step: 5,
    timeLabel: "T+25 min",
    timestamp: "08:25:00 AM",
    description: "Gas Accumulation Escalates — ZeroGuard Interlock Dispatches Isolation Operator",
    gasZScore: 3.85,
    permitStatus: "NON_COMPLIANT",
    maintActive: true,
    zeroguardLevel: "COMPOUND_CRITICAL",
    scadaLevel: "WARNING",
    leadTimeMarker: "ZeroGuard flags compound critical risk at T+18min. SCADA Baseline would not fire until T+36min (18 Minute Safety Gap Saved)."
  },
  {
    step: 6,
    timeLabel: "T+36 min",
    timestamp: "08:36:00 AM",
    description: "⚠️ SCADA MULTI-CONDITION BASELINE FINALLY BREACHES (18 MINUTES LATE)",
    gasZScore: 4.86,
    permitStatus: "NON_COMPLIANT",
    maintActive: true,
    zeroguardLevel: "COMPOUND_CRITICAL",
    scadaLevel: "CRITICAL",
    leadTimeMarker: "SCADA Baseline threshold breach occurs 18 minutes AFTER ZeroGuard interlock."
  },
];

export default function IncidentReplayPanel({ onScrollToAction }) {
  const [currentStepIdx, setCurrentStepIdx] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [speedMultiplier, setSpeedMultiplier] = useState(1);
  const [detectionMode, setDetectionMode] = useState('zeroguard'); // 'zeroguard' vs 'scada'

  const step = REPLAY_TIMESTEPS[currentStepIdx];
  const activeLevel = detectionMode === 'zeroguard' ? step.zeroguardLevel : step.scadaLevel;

  useEffect(() => {
    if (!isPlaying) return;
    const intervalTime = 3000 / speedMultiplier;
    const timer = setInterval(() => {
      setCurrentStepIdx((prev) => {
        if (prev >= REPLAY_TIMESTEPS.length - 1) {
          setIsPlaying(false);
          return prev;
        }
        return prev + 1;
      });
    }, intervalTime);
    return () => clearInterval(timer);
  }, [isPlaying, speedMultiplier]);

  return (
    <div className="zg-card mb-[32px] border-[#58A6FF]/40">
      {/* Panel Header */}
      <div className="flex flex-wrap items-center justify-between gap-[16px] mb-[16px] border-b border-[#21262D] pb-[16px]">
        <div className="flex items-center gap-[8px]">
          <Clock className="w-[20px] h-[20px] text-[#58A6FF]" strokeWidth={1.5} />
          <h3 className="text-[16px] font-bold text-[#E6EDF3] uppercase tracking-[0.02em] font-mono-tech">
            LIVE INCIDENT REPLAY MODE & BEFORE/AFTER BASELINE COMPARISON
          </h3>
        </div>
        
        {/* C1: Baseline Mode Toggle */}
        <div className="flex items-center gap-[4px] bg-[#0D1117] p-[4px] border border-[#21262D] rounded-[4px] font-mono-tech text-[11px]">
          <button
            onClick={() => setDetectionMode('zeroguard')}
            className={`px-[10px] py-[4px] rounded-[3px] font-bold ${
              detectionMode === 'zeroguard' ? 'bg-[#58A6FF] text-[#0D1117]' : 'text-[#8B949E]'
            }`}
          >
            ZeroGuard Compound Mode
          </button>
          <button
            onClick={() => setDetectionMode('scada')}
            className={`px-[10px] py-[4px] rounded-[3px] font-bold ${
              detectionMode === 'scada' ? 'bg-[#FF6200] text-[#FFFFFF]' : 'text-[#8B949E]'
            }`}
          >
            SCADA Baseline Mode
          </button>
        </div>
      </div>

      {/* Replay Timeline Controls */}
      <div className="flex flex-wrap items-center justify-between gap-[16px] mb-[20px] bg-[#0D1117] p-[16px] rounded-[6px] border border-[#21262D] font-mono-tech">
        <div className="flex items-center gap-[12px]">
          <button
            onClick={() => setIsPlaying(!isPlaying)}
            className="btn-primary py-[6px] px-[16px]"
          >
            {isPlaying ? <><Pause className="w-[14px] h-[14px]" /> Pause</> : <><Play className="w-[14px] h-[14px]" /> Replay</>}
          </button>
          <button
            onClick={() => setCurrentStepIdx(Math.min(currentStepIdx + 1, REPLAY_TIMESTEPS.length - 1))}
            disabled={currentStepIdx >= REPLAY_TIMESTEPS.length - 1}
            className="btn-secondary py-[6px] px-[12px] disabled:opacity-40"
          >
            <SkipForward className="w-[14px] h-[14px]" /> Step
          </button>
          <button
            onClick={() => setCurrentStepIdx(0)}
            className="btn-secondary py-[6px] px-[12px]"
          >
            <RotateCcw className="w-[14px] h-[14px]" /> Reset
          </button>
        </div>

        <div className="flex items-center gap-[8px] text-[12px]">
          <span className="text-[#8B949E] uppercase">Speed:</span>
          {[1, 4, 20].map((s) => (
            <button
              key={s}
              onClick={() => setSpeedMultiplier(s)}
              className={`px-[8px] py-[4px] rounded-[4px] border font-bold ${
                speedMultiplier === s ? 'bg-[#58A6FF] text-[#0D1117] border-[#58A6FF]' : 'bg-[#161B22] text-[#8B949E] border-[#21262D]'
              }`}
            >
              {s}x
            </button>
          ))}
        </div>
      </div>

      {/* C2: Minute-by-Minute Scrubbable Timeline */}
      <div className="grid grid-cols-7 gap-[8px] mb-[20px]">
        {REPLAY_TIMESTEPS.map((t, idx) => {
          const lvl = detectionMode === 'zeroguard' ? t.zeroguardLevel : t.scadaLevel;
          return (
            <button
              key={idx}
              onClick={() => setCurrentStepIdx(idx)}
              className={`p-[8px] rounded-[4px] border text-center font-mono-tech text-[11px] transition-all ${
                idx === currentStepIdx
                  ? 'bg-[#58A6FF]/20 border-[#58A6FF] text-[#E6EDF3] font-bold'
                  : idx < currentStepIdx
                  ? 'bg-[#161B22] border-[#21262D] text-[#8B949E]'
                  : 'bg-[#0D1117] border-[#21262D] text-[#4A5568]'
              }`}
            >
              <span className="block text-[10px] text-[#8B949E]">{t.timeLabel}</span>
              <span className={lvl === 'COMPOUND_CRITICAL' || lvl === 'CRITICAL' ? 'text-[#F85149] font-bold' : ''}>
                {lvl}
              </span>
            </button>
          );
        })}
      </div>

      {/* Active Timestep Details */}
      <div className="p-[20px] bg-[#0D1117] border border-[#21262D] rounded-[6px] font-mono-tech text-[12px]">
        <div className="flex items-center justify-between border-b border-[#21262D] pb-[12px] mb-[12px]">
          <div>
            <span className="text-[#58A6FF] font-bold text-[14px]">{step.timeLabel} ({step.timestamp})</span>
            <p className="text-[13px] text-[#E6EDF3] font-sans mt-[2px]">{step.description}</p>
          </div>
          <span className={activeLevel === 'COMPOUND_CRITICAL' || activeLevel === 'CRITICAL' ? 'badge-critical px-[12px] py-[6px] text-[12px]' : 'badge-safe px-[12px] py-[6px] text-[12px]'}>
            {detectionMode === 'zeroguard' ? 'ZeroGuard' : 'SCADA Baseline'}: {activeLevel}
          </span>
        </div>

        {/* C3: The "Saved from Disaster" Beat Callout */}
        {step.leadTimeMarker && (
          <div className="p-[16px] bg-[#F85149]/15 border border-[#F85149]/50 rounded-[4px] mb-[16px] text-[#F85149] font-bold flex items-center justify-between gap-[12px]">
            <div className="flex items-center gap-[10px]">
              <ShieldAlert className="w-[20px] h-[20px] shrink-0" strokeWidth={1.5} />
              <span>{step.leadTimeMarker}</span>
            </div>
            
            {/* C4: Direct Link to Recommended Operator Action */}
            <button
              onClick={onScrollToAction}
              className="btn-primary py-[4px] px-[12px] text-[11px]"
            >
              View Recommended Action <ArrowRight className="w-[12px] h-[12px]" />
            </button>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-3 gap-[16px] text-[12px]">
          <div className="p-[12px] bg-[#161B22] border border-[#21262D] rounded-[4px]">
            <span className="text-[#8B949E] block mb-[4px] uppercase">Flammable Gas SEN-LEL-681</span>
            <span className="text-[16px] font-bold text-[#E6EDF3]">Z = {step.gasZScore.toFixed(2)}</span>
          </div>

          <div className="p-[12px] bg-[#161B22] border border-[#21262D] rounded-[4px]">
            <span className="text-[#8B949E] block mb-[4px] uppercase">Hot Work Permit PERMIT-2026-0440</span>
            <span className="text-[14px] font-bold text-[#DB6D28]">{step.permitStatus}</span>
          </div>

          <div className="p-[12px] bg-[#161B22] border border-[#21262D] rounded-[4px]">
            <span className="text-[#8B949E] block mb-[4px] uppercase">Hydrocracker Maintenance</span>
            <span className="text-[14px] font-bold text-[#2EA043]">{step.maintActive ? 'ACTIVE MAINTENANCE' : 'IDLE'}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
