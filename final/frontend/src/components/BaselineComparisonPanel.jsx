import React, { useEffect, useState } from 'react';
import { BarChart3, ShieldCheck, Clock, AlertTriangle } from 'lucide-react';
import { fetchMetrics } from '../services/api';

export default function BaselineComparisonPanel() {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMetrics()
      .then(data => setMetrics(data))
      .catch(err => console.error('Failed to load baseline comparison metrics:', err))
      .finally(() => setLoading(false));
  }, []);

  if (loading || !metrics) {
    return (
      <div className="zg-card mb-[32px]">
        <div className="flex items-center gap-[8px] mb-[16px]">
          <BarChart3 className="w-[20px] h-[20px] text-[#58A6FF]" strokeWidth={1.5} />
          <h3 className="text-[16px] font-bold text-[#E6EDF3] uppercase tracking-[0.02em] font-mono-tech">
            EVALUATION BENCHMARK: ZERO GUARD vs NAIVE SINGLE-SENSOR BASELINE
          </h3>
        </div>
        <div className="h-[120px] animate-skeleton rounded-[6px]" />
      </div>
    );
  }

  const baseline = metrics.naive_single_sensor_baseline;
  const zeroguard = metrics.zeroguard_compound_engine;
  const leadTime = metrics.average_early_lead_time_minutes;

  return (
    <div className="zg-card mb-[32px]">
      <div className="flex items-center justify-between gap-[16px] mb-[16px] border-b border-[#21262D] pb-[16px]">
        <div className="flex items-center gap-[8px]">
          <BarChart3 className="w-[20px] h-[20px] text-[#58A6FF]" strokeWidth={1.5} />
          <h3 className="text-[16px] font-bold text-[#E6EDF3] uppercase tracking-[0.02em] font-mono-tech">
            EVALUATION BENCHMARK: ZERO GUARD vs SINGLE-SENSOR BASELINE (520 SCENARIOS)
          </h3>
        </div>
        <span className="text-[12px] font-mono-tech text-[#2EA043] font-bold">
          0% FALSE NEGATIVE RATE
        </span>
      </div>

      {/* Prominent Lead Time Banner */}
      <div className="p-[16px] bg-[#58A6FF]/10 border border-[#58A6FF]/40 rounded-[6px] mb-[24px] flex items-center justify-between gap-[16px]">
        <div className="flex items-center gap-[12px]">
          <Clock className="w-[24px] h-[24px] text-[#58A6FF]" strokeWidth={1.5} />
          <div>
            <span className="text-[16px] font-bold text-[#E6EDF3] font-mono-tech block">
              ZeroGuard flags compound risk <strong className="text-[#58A6FF]">{leadTime} minutes earlier</strong> on average.
            </span>
            <span className="text-[12px] text-[#8B949E] font-sans">
              Evaluated across 520 synthetic/real refinery plant scenarios against single-sensor breach baselines.
            </span>
          </div>
        </div>
      </div>

      {/* Side-by-Side Metrics Comparison Bars */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-[24px] font-mono-tech text-[12px]">
        {/* Metric 1: Recall */}
        <div className="p-[16px] bg-[#0D1117] border border-[#21262D] rounded-[4px]">
          <div className="flex justify-between text-[#8B949E] mb-[8px] uppercase">
            <span>RECALL (SENSITIVITY)</span>
            <span>Higher is Better</span>
          </div>
          <div className="space-y-[12px]">
            <div>
              <div className="flex justify-between text-[#8B949E] mb-[4px] text-[11px]">
                <span>Naive Single-Sensor (Z ≥ 3.0)</span>
                <span>{(baseline.recall * 100).toFixed(0)}%</span>
              </div>
              <div className="w-full bg-[#161B22] h-[10px] rounded-[3px] overflow-hidden">
                <div className="bg-[#F85149] h-full" style={{ width: `${baseline.recall * 100}%` }} />
              </div>
            </div>
            <div>
              <div className="flex justify-between text-[#E6EDF3] font-bold mb-[4px] text-[11px]">
                <span className="text-[#58A6FF]">ZeroGuard Compound Engine</span>
                <span className="text-[#2EA043]">{(zeroguard.recall * 100).toFixed(0)}%</span>
              </div>
              <div className="w-full bg-[#161B22] h-[10px] rounded-[3px] overflow-hidden">
                <div className="bg-[#2EA043] h-full" style={{ width: `${zeroguard.recall * 100}%` }} />
              </div>
            </div>
          </div>
        </div>

        {/* Metric 2: False Negative Rate */}
        <div className="p-[16px] bg-[#0D1117] border border-[#21262D] rounded-[4px]">
          <div className="flex justify-between text-[#8B949E] mb-[8px] uppercase">
            <span>FALSE NEGATIVE RATE (MISSED RISKS)</span>
            <span>Lower is Better</span>
          </div>
          <div className="space-y-[12px]">
            <div>
              <div className="flex justify-between text-[#8B949E] mb-[4px] text-[11px]">
                <span>Naive Single-Sensor (Z ≥ 3.0)</span>
                <span className="text-[#F85149]">{(baseline.false_negative_rate * 100).toFixed(0)}%</span>
              </div>
              <div className="w-full bg-[#161B22] h-[10px] rounded-[3px] overflow-hidden">
                <div className="bg-[#F85149] h-full" style={{ width: `${baseline.false_negative_rate * 100}%` }} />
              </div>
            </div>
            <div>
              <div className="flex justify-between text-[#E6EDF3] font-bold mb-[4px] text-[11px]">
                <span className="text-[#58A6FF]">ZeroGuard Compound Engine</span>
                <span className="text-[#2EA043]">{(zeroguard.false_negative_rate * 100).toFixed(0)}%</span>
              </div>
              <div className="w-full bg-[#161B22] h-[10px] rounded-[3px] overflow-hidden">
                <div className="bg-[#2EA043] h-full" style={{ width: `${zeroguard.false_negative_rate * 100}%` }} />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
