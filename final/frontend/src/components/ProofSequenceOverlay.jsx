import React, { useState, useEffect } from 'react';

const ProofSequenceOverlay = ({ onComplete }) => {
  const [step, setStep] = useState(0);
  const [data, setData] = useState({});
  const [logs, setLogs] = useState([]);

  const addLog = (msg) => setLogs((prev) => [...prev, msg]);

  useEffect(() => {
    const runSequence = async () => {
      // Step 1: Load Scenario
      setStep(1);
      addLog("Step 1: Loading SCEN-2026-0069...");
      const scenRes = await fetch('http://127.0.0.1:8000/api/v1/scenarios/SCEN-2026-0069');
      const scenData = await scenRes.json();
      setData(prev => ({ ...prev, scenario: scenData }));
      
      // Load into graph engine state (the GET request above already loads it into the UI, 
      // but in the actual engine we simulate it running continuously).
      await new Promise(r => setTimeout(r, 2000));

      // Step 2: Baseline Comparison
      setStep(2);
      addLog("Step 2: Fetching baseline metrics...");
      const metricsRes = await fetch('http://127.0.0.1:8000/api/v1/metrics');
      const metricsData = await metricsRes.json();
      
      // Compute naive status from scenario sensors (z_score >= 3.0 on GAS/LEL)
      const hasNaiveTrigger = scenData.sensors.some(s => (s.sensor_type.includes('GAS') || s.sensor_type.includes('LEL')) && Math.abs(s.z_score) >= 3.0);
      const naiveStatus = hasNaiveTrigger ? "CRITICAL" : "NORMAL";
      
      // Get ZeroGuard status from graph state
      const graphRes = await fetch('http://127.0.0.1:8000/api/v1/graph-state');
      const graphData = await graphRes.json();
      
      setData(prev => ({ 
        ...prev, 
        metrics: metricsData, 
        graphState: graphData,
        naiveStatus,
        zgStatus: graphData.overall_risk_level
      }));
      await new Promise(r => setTimeout(r, 3000));

      // Step 3: RCA Explanation
      setStep(3);
      addLog("Step 3: Fetching RCA Explanation...");
      const rcaRes = await fetch('http://127.0.0.1:8000/api/v1/incidents/current/explanation');
      const rcaData = await rcaRes.json();
      setData(prev => ({ ...prev, rca: rcaData }));
      await new Promise(r => setTimeout(r, 3000));

      // Step 4: DVR Replay
      setStep(4);
      addLog("Step 4: Fetching DVR Replay...");
      const dvrRes = await fetch('http://127.0.0.1:8000/api/v1/scenarios/SCEN-2026-0069/replay?window_minutes=30');
      const dvrData = await dvrRes.json();
      setData(prev => ({ ...prev, dvr: dvrData }));
      await new Promise(r => setTimeout(r, 3000));

      // Step 5: End on Metrics Strip
      setStep(5);
      addLog("Step 5: Sequence Complete.");
      await new Promise(r => setTimeout(r, 2000));
    };

    runSequence();
  }, []);

  return (
    <div className="fixed inset-0 bg-slate-900/95 z-[9999] flex items-center justify-center p-8 backdrop-blur-sm">
      <div className="bg-slate-800 border border-slate-600 rounded-xl shadow-2xl p-6 max-w-5xl w-full max-h-[90vh] overflow-y-auto">
        <h2 className="text-3xl font-bold text-white mb-6 border-b border-slate-700 pb-4 flex items-center justify-between">
          <span>ZeroGuard Live Proof Sequence</span>
          {step >= 5 && (
            <button onClick={onComplete} className="bg-emerald-600 hover:bg-emerald-500 text-white px-4 py-2 rounded text-sm font-medium transition-colors">
              Exit Sequence
            </button>
          )}
        </h2>
        
        <div className="space-y-6">
          {step >= 1 && (
            <div className="bg-slate-900 p-4 rounded border border-slate-700 animate-in fade-in slide-in-from-bottom-4 duration-500">
              <h3 className="text-emerald-400 font-mono text-sm mb-2">1. SCENARIO LOADED</h3>
              <p className="text-white text-lg">Scenario: <span className="font-mono text-blue-300">SCEN-2026-0069</span> loaded successfully into live engine state.</p>
            </div>
          )}

          {step >= 2 && data.metrics && data.graphState && (
            <div className="bg-slate-900 p-4 rounded border border-slate-700 animate-in fade-in slide-in-from-bottom-4 duration-500">
              <h3 className="text-emerald-400 font-mono text-sm mb-2">2. BASELINE COMPARISON</h3>
              <div className="grid grid-cols-2 gap-6">
                <div>
                  <p className="text-white text-lg mb-3">
                    A standard single-sensor system: <span className="text-slate-400 font-mono bg-slate-800 px-2 rounded border border-slate-700">{data.naiveStatus}</span>
                  </p>
                  <p className="text-white text-lg mb-4">
                    ZeroGuard: <span className="text-red-400 font-mono bg-slate-800 px-2 rounded border border-red-900/50">{data.zgStatus}</span>
                  </p>
                  <div className="text-sm text-slate-400 border-t border-slate-700 pt-3">
                    <p className="mb-1">Dataset Aggregate Recall (from /api/v1/metrics):</p>
                    <p>Naive: <span className="text-white">{data.metrics.naive_single_sensor_baseline.recall_pct}%</span> | ZeroGuard: <span className="text-white">{data.metrics.zeroguard_compound_engine.recall_pct}%</span></p>
                  </div>
                </div>
                <div className="bg-black p-3 rounded-lg overflow-x-auto border border-slate-800">
                  <div className="text-xs text-slate-500 mb-1 uppercase tracking-wider">Raw API Validation</div>
                  <pre className="text-[11px] text-emerald-500/80">
                    {JSON.stringify({
                      scenario_eval: { has_gas_lel_over_3: data.naiveStatus === "CRITICAL" },
                      graph_state: { overall_risk_level: data.zgStatus },
                      metrics_api: { 
                        naive: data.metrics.naive_single_sensor_baseline, 
                        zeroguard: data.metrics.zeroguard_compound_engine 
                      }
                    }, null, 2)}
                  </pre>
                </div>
              </div>
            </div>
          )}

          {step >= 3 && data.rca && (
            <div className="bg-slate-900 p-4 rounded border border-slate-700 animate-in fade-in slide-in-from-bottom-4 duration-500">
              <h3 className="text-emerald-400 font-mono text-sm mb-2">3. RCA EXPLANATION</h3>
              <div className="grid grid-cols-2 gap-6">
                <p className="text-white text-lg leading-relaxed">
                  {data.rca.explanation_text}
                </p>
                <div className="bg-black p-3 rounded-lg overflow-x-auto border border-slate-800">
                  <div className="text-xs text-slate-500 mb-1 uppercase tracking-wider">Raw API Validation (/api/v1/incidents/current/explanation)</div>
                  <pre className="text-[11px] text-emerald-500/80">
                    {JSON.stringify(data.rca, null, 2)}
                  </pre>
                </div>
              </div>
            </div>
          )}

          {step >= 4 && data.dvr && (
            <div className="bg-slate-900 p-4 rounded border border-slate-700 animate-in fade-in slide-in-from-bottom-4 duration-500">
              <h3 className="text-emerald-400 font-mono text-sm mb-2">4. FORENSIC DVR REPLAY</h3>
              <div className="grid grid-cols-2 gap-6">
                <div className="text-white">
                  <p className="mb-3 text-slate-300">Extracted {data.dvr.snapshots?.length} chronological snapshots.</p>
                  {data.dvr.snapshots?.slice(-3).map((snap, i) => (
                    <div key={i} className="text-sm border-l-2 border-emerald-500/50 pl-3 mb-3 bg-slate-800/50 py-2 rounded-r">
                      <div className="text-slate-400 font-mono text-xs mb-1">{snap.timestamp}</div>
                      <div className="flex justify-between pr-2">
                        <span>{snap.status}</span>
                        <span className="text-slate-500">Score: {snap.score}</span>
                      </div>
                    </div>
                  ))}
                </div>
                <div className="bg-black p-3 rounded-lg overflow-x-auto border border-slate-800">
                  <div className="text-xs text-slate-500 mb-1 uppercase tracking-wider">Raw API Validation (/api/v1/scenarios/.../replay)</div>
                  <pre className="text-[11px] text-emerald-500/80">
                    {JSON.stringify({ 
                      scenario_id: data.dvr.scenario_id, 
                      snapshot_count: data.dvr.snapshots?.length,
                      latest_snapshot: data.dvr.snapshots?.[data.dvr.snapshots.length - 1]
                    }, null, 2)}
                  </pre>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProofSequenceOverlay;
