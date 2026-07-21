import React from 'react';
import { Activity, Clock } from 'lucide-react';

export default function SensorAnomalyTable({ graphState }) {
  const nodes = graphState?.nodes ?? [];
  const sensorNodes = nodes.filter(n => n.category === 'SENSOR');

  return (
    <div className="glass-panel p-5 rounded-2xl border border-slate-800">
      <div className="flex justify-between items-center mb-4">
        <div className="flex items-center space-x-2">
          <Activity className="w-5 h-5 text-cyan-400" />
          <h3 className="font-bold text-white tracking-wide">2-Second Aggregated Sensor Telemetry</h3>
        </div>
        <div className="flex items-center space-x-1.5 text-xs font-mono text-cyan-400">
          <Clock className="w-3.5 h-3.5" />
          <span>WINDOW: 2.0s AGGREGATION</span>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left font-mono text-xs">
          <thead>
            <tr className="border-b border-slate-800 text-slate-400 text-[11px] uppercase tracking-wider">
              <th className="pb-3">Sensor ID</th>
              <th className="pb-3">Sensor Name</th>
              <th className="pb-3">Zone</th>
              <th className="pb-3">Current Value</th>
              <th className="pb-3">2s Z-Score</th>
              <th className="pb-3">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {sensorNodes.map((s) => {
              const isAnomaly = (s.z_score ?? 0) >= 3.0;
              return (
                <tr key={s.id} className="hover:bg-slate-800/30 transition">
                  <td className="py-3 font-bold text-cyan-400">{s.id}</td>
                  <td className="py-3 text-slate-200">{s.name}</td>
                  <td className="py-3 text-slate-400">{s.zone_id}</td>
                  <td className="py-3 text-slate-200">{s.current_value ?? '--'} ppm</td>
                  <td className={`py-3 font-bold ${isAnomaly ? 'text-rose-400' : 'text-emerald-400'}`}>
                    {s.z_score ?? '0.0'}
                  </td>
                  <td className="py-3">
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        isAnomaly ? 'bg-rose-950 text-rose-400 border border-rose-800' : 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                      }`}
                    >
                      {isAnomaly ? 'ANOMALY (Z≥3.0)' : 'NORMAL'}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
