import React from 'react';
import { ShieldCheck, ShieldAlert, Cpu, CheckCircle2, AlertTriangle } from 'lucide-react';
import AnimatedNumber from './AnimatedNumber';

export default function RiskOverviewCards({ graphState }) {
  if (!graphState) return null;

  const {
    overall_risk_score = 0.0,
    overall_risk_level = 'NORMAL',
    confidence_score = 1.0,
    evidence_completeness = 1.0,
    active_alerts = []
  } = graphState;

  const ruleGuardAlerts = active_alerts.filter(a => a.triggered_by === 'RULE_GUARD');
  const hasRuleGuardViolation = ruleGuardAlerts.length > 0;

  const getRiskScoreColor = (score, level) => {
    if (level === 'CRITICAL' || level === 'COMPOUND_CRITICAL') return 'text-[#F85149] border-[#F85149]/40 bg-[#F85149]/10';
    if (level === 'WARNING') return 'text-[#DB6D28] border-[#DB6D28]/40 bg-[#DB6D28]/10';
    if (level === 'WATCH' || level === 'MEDIUM') return 'text-[#D29922] border-[#D29922]/40 bg-[#D29922]/10';
    return 'text-[#2EA043] border-[#2EA043]/40 bg-[#2EA043]/10';
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-[16px] mb-[32px]">
      {/* Card 1: Overall Risk Score (Stagger 1) */}
      <div className={`zg-card h-full animate-stagger-1 ${getRiskScoreColor(overall_risk_score, overall_risk_level)}`}>
        <div className="flex items-center justify-between text-[12px] font-semibold text-[#8B949E] uppercase tracking-[0.02em] mb-[8px]">
          <span>OVERALL PLANT RISK</span>
          <Cpu className="w-[20px] h-[20px] text-[#8B949E]" strokeWidth={1.5} />
        </div>
        <div className="flex items-baseline justify-between mt-[8px]">
          <span className="text-[28px] font-bold font-mono-tech leading-[1.2]">
            <AnimatedNumber value={overall_risk_score} decimals={1} />
          </span>
          <span className="text-[12px] font-semibold font-mono-tech uppercase px-[8px] py-[4px] rounded-[4px] bg-[#0D1117] border border-[#21262D]">
            {overall_risk_level}
          </span>
        </div>
        <div className="w-full bg-[#0D1117] h-[6px] rounded-[3px] mt-[16px] overflow-hidden border border-[#21262D]">
          <div
            className={`h-full rounded-[3px] transition-all duration-500 ${
              overall_risk_level === 'CRITICAL' || overall_risk_level === 'COMPOUND_CRITICAL' ? 'bg-[#F85149]' :
              overall_risk_level === 'WARNING' ? 'bg-[#DB6D28]' :
              overall_risk_level === 'WATCH' ? 'bg-[#D29922]' : 'bg-[#2EA043]'
            }`}
            style={{ width: `${Math.min(overall_risk_score, 100)}%` }}
          />
        </div>
      </div>

      {/* Card 2: Rule-Guard Status (Stagger 2) */}
      <div className="zg-card h-full animate-stagger-2">
        <div className="flex items-center justify-between text-[12px] font-semibold text-[#8B949E] uppercase tracking-[0.02em] mb-[8px]">
          <span>STATUTORY RULE GUARD</span>
          {hasRuleGuardViolation ? (
            <ShieldAlert className="w-[20px] h-[20px] text-[#F85149]" strokeWidth={1.5} />
          ) : (
            <ShieldCheck className="w-[20px] h-[20px] text-[#2EA043]" strokeWidth={1.5} />
          )}
        </div>
        <div className="flex items-baseline justify-between mt-[8px]">
          <span className="text-[20px] font-bold font-mono-tech leading-[1.2]">
            {hasRuleGuardViolation ? 'VIOLATION DETECTED' : 'ALL RULES PASSED'}
          </span>
        </div>
        <div className="text-[12px] font-mono-tech text-[#8B949E] mt-[16px]">
          {hasRuleGuardViolation ? (
            <span className="text-[#F85149] font-semibold">{ruleGuardAlerts.length} Mandatory Interlock Fired</span>
          ) : (
            <span className="text-[#2EA043]">0 Interlock Violations</span>
          )}
        </div>
      </div>

      {/* Card 3: Engine Confidence Score (Stagger 3) */}
      <div className="zg-card h-full animate-stagger-3">
        <div className="flex items-center justify-between text-[12px] font-semibold text-[#8B949E] uppercase tracking-[0.02em] mb-[8px]">
          <span>PROPAGATION CONFIDENCE</span>
          <CheckCircle2 className="w-[20px] h-[20px] text-[#58A6FF]" strokeWidth={1.5} />
        </div>
        <div className="flex items-baseline justify-between mt-[8px]">
          <span className="text-[28px] font-bold font-mono-tech text-[#58A6FF] leading-[1.2]">
            <AnimatedNumber value={confidence_score * 100} decimals={1} suffix="%" />
          </span>
          <span className="text-[12px] font-mono-tech text-[#8B949E]">PageRank α=0.15</span>
        </div>
        <div className="w-full bg-[#0D1117] h-[6px] rounded-[3px] mt-[16px] overflow-hidden border border-[#21262D]">
          <div
            className="h-full bg-[#58A6FF] rounded-[3px] transition-all duration-500"
            style={{ width: `${Math.min(confidence_score * 100, 100)}%` }}
          />
        </div>
      </div>

      {/* Card 4: Evidence Completeness (Stagger 4) */}
      <div className="zg-card h-full animate-stagger-4">
        <div className="flex items-center justify-between text-[12px] font-semibold text-[#8B949E] uppercase tracking-[0.02em] mb-[8px]">
          <span>EVIDENCE COMPLETENESS</span>
          <AlertTriangle className="w-[20px] h-[20px] text-[#8B949E]" strokeWidth={1.5} />
        </div>
        <div className="flex items-baseline justify-between mt-[8px]">
          <span className="text-[28px] font-bold font-mono-tech text-[#E6EDF3] leading-[1.2]">
            <AnimatedNumber value={evidence_completeness * 100} decimals={1} suffix="%" />
          </span>
          <span className="text-[12px] font-mono-tech text-[#8B949E]">{active_alerts.length} Active Alerts</span>
        </div>
        <div className="w-full bg-[#0D1117] h-[6px] rounded-[3px] mt-[16px] overflow-hidden border border-[#21262D]">
          <div
            className="h-full bg-[#8B949E] rounded-[3px] transition-all duration-500"
            style={{ width: `${Math.min(evidence_completeness * 100, 100)}%` }}
          />
        </div>
      </div>
    </div>
  );
}
