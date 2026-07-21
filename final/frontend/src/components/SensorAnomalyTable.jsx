import React from 'react';
import { Activity, Sliders } from 'lucide-react';

export default function SensorAnomalyTable({ nodes, onInjectClick }) {
  const sensorNodes = (nodes || []).filter(n => n.category === 'SENSOR');

  const getStatusBadge = (zScore) => {
    const absZ = Math.abs(zScore || 0);
    if (absZ >= 3.0) return <span className="badge-critical font-mono-tech px-[8px] py-[4px] text-[12px]">CRITICAL (Z≥3.0)</span>;
    if (absZ >= 2.5) return <span className="badge-warning font-mono-tech px-[8px] py-[4px] text-[12px]">WARNING (Z≥2.5)</span>;
    if (absZ >= 1.5) return <span className="badge-watch font-mono-tech px-[8px] py-[4px] text-[12px]">WATCH (Z≥1.5)</span>;
    return <span className="badge-safe font-mono-tech px-[8px] py-[4px] text-[12px]">NORMAL</span>;
  };

  return (
    <div className="zg-card mb-[48px]">
      <div className="flex items-center justify-between gap-[16px] mb-[16px] border-b border-[#21262D] pb-[16px]">
        <div className="flex items-center gap-[8px]">
          <Activity className="w-[20px] h-[20px] text-[#58A6FF]" strokeWidth={1.5} />
          <h3 className="text-[16px] font-bold text-[#E6EDF3] uppercase tracking-[0.02em] font-mono-tech">
            LIVE PLANT TELEMETRY & SENSOR ANOMALIES
          </h3>
        </div>
        <button
          onClick={onInjectClick}
          className="btn-primary text-[12px]"
        >
          <Sliders className="w-[14px] h-[14px]" strokeWidth={1.5} /> Inject Anomaly Z-Score
        </button>
      </div>

      <div className="overflow-x-auto w-full">
        <table className="w-full text-left border-collapse text-[12px] font-mono-tech min-w-[650px]">
          <thead>
            <tr className="border-b border-[#21262D] text-[#8B949E] uppercase tracking-[0.02em]">
              <th className="py-[12px] px-[16px] min-w-[130px]">Sensor ID</th>
              <th className="py-[12px] px-[16px] min-w-[160px]">Sensor Name</th>
              <th className="py-[12px] px-[16px] min-w-[130px]">Zone</th>
              <th className="py-[12px] px-[16px] min-w-[100px]">Reading</th>
              <th className="py-[12px] px-[16px] min-w-[100px]">Z-Score</th>
              <th className="py-[12px] px-[16px] min-w-[110px]">Grid (x, y)</th>
              <th className="py-[12px] px-[16px] min-w-[130px]">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#21262D]">
            {sensorNodes.length === 0 ? (
              <tr>
                <td colSpan={7} className="py-[24px] text-center text-[#4A5568] font-mono-tech">
                  No active telemetry signals in this scenario.
                </td>
              </tr>
            ) : (
              sensorNodes.map((sensor) => (
                <tr key={sensor.id} className="hover:bg-[#1C2128] transition-colors">
                  <td className="py-[12px] px-[16px] font-semibold text-[#58A6FF] whitespace-nowrap">{sensor.id}</td>
                  <td className="py-[12px] px-[16px] text-[#E6EDF3] font-sans leading-[1.5] break-words max-w-[180px]">
                    {sensor.name}
                  </td>
                  <td className="py-[12px] px-[16px] text-[#8B949E] whitespace-nowrap">{sensor.zone_id}</td>
                  <td className="py-[12px] px-[16px] text-[#E6EDF3] font-bold whitespace-nowrap">
                    {sensor.current_value !== null ? sensor.current_value.toFixed(1) : 'N/A'}
                  </td>
                  <td className="py-[12px] px-[16px] font-bold whitespace-nowrap">
                    {sensor.z_score !== null ? (
                      <span className={Math.abs(sensor.z_score) >= 3.0 ? 'text-[#F85149]' : Math.abs(sensor.z_score) >= 2.5 ? 'text-[#DB6D28]' : Math.abs(sensor.z_score) >= 1.5 ? 'text-[#D29922]' : 'text-[#2EA043]'}>
                        {sensor.z_score >= 0 ? `+${sensor.z_score.toFixed(2)}` : sensor.z_score.toFixed(2)}
                      </span>
                    ) : '0.00'}
                  </td>
                  <td className="py-[12px] px-[16px] text-[#8B949E] whitespace-nowrap">
                    ({sensor.attributes?.x ?? 0}, {sensor.attributes?.y ?? 0})
                  </td>
                  <td className="py-[12px] px-[16px] whitespace-nowrap">
                    {getStatusBadge(sensor.z_score)}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
