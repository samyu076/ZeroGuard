import React from 'react';
import { Activity, ShieldAlert, Wifi, WifiOff, Search, Cpu, FileText, Command, User, Settings } from 'lucide-react';

export default function Header({
  scenarios,
  selectedScenarioId,
  onSelectScenario,
  overallRiskLevel,
  overallRiskScore,
  isOffline,
  onOpenArchitecture,
  onOpenEmergencyReport,
  onOpenCommandPalette,
  onOpenLogin,
  onOpenSettings
}) {
  const getRiskBadgeClass = (level) => {
    if (level === 'CRITICAL' || level === 'COMPOUND_CRITICAL') return 'badge-critical';
    if (level === 'WARNING') return 'badge-warning';
    if (level === 'WATCH' || level === 'MEDIUM') return 'badge-watch';
    return 'badge-safe';
  };

  return (
    <header className="bg-[#161B22] border-b border-[#21262D] px-[24px] py-[14px] flex flex-wrap items-center justify-between gap-[16px] sticky top-0 z-40">
      {/* Brand & System Mode */}
      <div className="flex items-center gap-[16px]">
        <div className="flex items-center gap-[8px]">
          {/* Safety-Orange Brand Mark */}
          <ShieldAlert className="w-[22px] h-[22px] text-[#FF6200]" strokeWidth={1.5} />
          <span className="font-semibold text-[16px] tracking-[0.02em] text-[#E6EDF3] font-mono-tech uppercase">
            ZERO<span className="text-[#FF6200]">GUARD</span> <span className="text-[#8B949E] font-normal text-[12px] uppercase">| INDUSTRIAL RISK INTELLIGENCE</span>
          </span>
        </div>
        <div className="h-[16px] w-[1px] bg-[#21262D] hidden sm:block" />
        <div className="hidden sm:flex items-center gap-[8px] text-[12px] font-mono-tech">
          {isOffline ? (
            <span className="flex items-center gap-[4px] px-[8px] py-[4px] badge-warning">
              <WifiOff className="w-[14px] h-[14px]" strokeWidth={1.5} /> SYSTEM OFFLINE
            </span>
          ) : (
            <span className="flex items-center gap-[4px] px-[8px] py-[4px] badge-safe">
              <Wifi className="w-[14px] h-[14px]" strokeWidth={1.5} /> LIVE PROPAGATION + RULE-GUARD
            </span>
          )}
        </div>
      </div>

      {/* Header Controls */}
      <div className="flex items-center gap-[10px]">
        {/* Command Palette Trigger ⌘K */}
        <button
          onClick={onOpenCommandPalette}
          className="btn-secondary text-[12px] py-[6px] px-[12px] flex items-center gap-[6px]"
          title="Open Command Palette (⌘K or Ctrl+K)"
        >
          <Command className="w-[14px] h-[14px] text-[#58A6FF]" strokeWidth={1.5} />
          <span className="font-mono-tech font-bold text-[#E6EDF3]">⌘K</span>
        </button>

        <button
          onClick={onOpenArchitecture}
          className="btn-secondary text-[12px] py-[6px] px-[12px]"
          title="View Enterprise Scalability Architecture Roadmap"
        >
          <Cpu className="w-[14px] h-[14px]" strokeWidth={1.5} /> Scalability
        </button>

        <button
          onClick={onOpenEmergencyReport}
          className="btn-secondary text-[12px] py-[6px] px-[12px] text-[#F85149] border-[#F85149]/40 hover:bg-[#F85149]/10"
          title="Auto-Generate Incident Report & Dispatch Response Team"
        >
          <FileText className="w-[14px] h-[14px]" strokeWidth={1.5} /> Incident Response
        </button>

        <button
          onClick={onOpenLogin}
          className="btn-secondary text-[12px] py-[6px] px-[10px]"
          title="Operator Login / Sign-in"
        >
          <User className="w-[14px] h-[14px]" strokeWidth={1.5} />
        </button>

        <button
          onClick={onOpenSettings}
          className="btn-secondary text-[12px] py-[6px] px-[10px]"
          title="Engine & Plant Settings"
        >
          <Settings className="w-[14px] h-[14px]" strokeWidth={1.5} />
        </button>

        {/* Scenario Dropdown */}
        <div className="relative">
          <Search className="w-[16px] h-[16px] text-[#8B949E] absolute left-[12px] top-1/2 -translate-y-1/2" strokeWidth={1.5} />
          <select
            value={selectedScenarioId || ''}
            onChange={(e) => onSelectScenario(e.target.value)}
            disabled={isOffline}
            className="pl-[36px] pr-[16px] py-[6px] bg-[#0D1117] border border-[#21262D] rounded-[4px] text-[12px] font-mono-tech text-[#E6EDF3] disabled:opacity-50 min-w-[260px]"
          >
            <option value="" disabled>Select Scenario (520 Scenarios)...</option>
            {scenarios.map((s) => (
              <option key={s.scenario_id} value={s.scenario_id}>
                {s.scenario_id} [{s.ground_truth_label || 'SCENARIO'}]
              </option>
            ))}
          </select>
        </div>

        {/* Live Risk Score Pill */}
        <div className={`px-[12px] py-[6px] text-[12px] font-semibold font-mono-tech flex items-center gap-[6px] ${getRiskBadgeClass(overallRiskLevel)}`}>
          <Activity className="w-[14px] h-[14px]" strokeWidth={1.5} />
          <span>{overallRiskLevel || 'SAFE'}</span>
          <span>({overallRiskScore !== undefined ? overallRiskScore.toFixed(1) : '0.0'})</span>
        </div>
      </div>
    </header>
  );
}
