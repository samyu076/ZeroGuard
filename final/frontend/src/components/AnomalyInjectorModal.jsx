import React, { useState } from 'react';
import { Sliders, X, AlertTriangle } from 'lucide-react';

export default function AnomalyInjectorModal({ isOpen, onClose, sensors, onInject }) {
  const [selectedSensorId, setSelectedSensorId] = useState(sensors[0]?.id || '');
  const [targetZScore, setTargetZScore] = useState('3.85');
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedSensorId) return;
    setIsSubmitting(true);
    try {
      await onInject(selectedSensorId, parseFloat(targetZScore));
      onClose();
    } catch (err) {
      alert(`Injection error: ${err.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/75 backdrop-blur-sm z-50 flex items-center justify-center p-[16px]">
      <div className="zg-modal-panel max-w-md w-full relative border border-[#21262D]">
        <button
          onClick={onClose}
          className="absolute right-[16px] top-[16px] text-[#8B949E] hover:text-[#E6EDF3] p-[4px]"
        >
          <X className="w-[16px] h-[16px]" strokeWidth={1.5} />
        </button>

        <div className="flex items-center gap-[8px] mb-[16px] border-b border-[#21262D] pb-[16px]">
          <Sliders className="w-[20px] h-[20px] text-[#58A6FF]" strokeWidth={1.5} />
          <h3 className="text-[16px] font-bold text-[#E6EDF3] uppercase tracking-[0.02em] font-mono-tech">
            LIVE ANOMALY INJECTOR
          </h3>
        </div>

        <form onSubmit={handleSubmit} className="space-y-[16px] text-[12px] font-mono-tech">
          <div>
            <label className="block text-[#8B949E] mb-[6px] uppercase tracking-[0.02em]">Select Target Sensor</label>
            <select
              value={selectedSensorId}
              onChange={(e) => setSelectedSensorId(e.target.value)}
              className="w-full p-[8px] bg-[#0D1117] border border-[#21262D] rounded-[4px] text-[#E6EDF3] focus:outline-none"
            >
              {sensors.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.id} ({s.name}) — Zone {s.zone_id}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-[#8B949E] mb-[6px] uppercase tracking-[0.02em]">
              Target Anomaly Z-Score Override (-5.0 to +5.0)
            </label>
            <div className="flex items-center gap-[16px]">
              <input
                type="range"
                min="-5.0"
                max="5.0"
                step="0.05"
                value={targetZScore}
                onChange={(e) => setTargetZScore(e.target.value)}
                className="w-full accent-[#58A6FF]"
              />
              <span className="font-bold text-[16px] text-[#58A6FF] min-w-[50px] text-right">
                {parseFloat(targetZScore).toFixed(2)}
              </span>
            </div>
            <p className="text-[12px] text-[#8B949E] mt-[4px]">
              * Z ≥ 3.0 triggers statutory rule-guard check if co-located with active permit.
            </p>
          </div>

          <div className="p-[16px] bg-[#0D1117] border border-[#21262D] rounded-[4px] flex items-start gap-[8px] text-[#E6EDF3]">
            <AlertTriangle className="w-[16px] h-[16px] text-[#D29922] shrink-0 mt-[2px]" strokeWidth={1.5} />
            <span className="text-[12px] leading-[1.5]">
              Injecting an anomaly will immediately trigger PageRank re-propagation and evaluate statutory interlocks across active plant permits.
            </span>
          </div>

          <div className="flex items-center justify-end gap-[16px] pt-[8px]">
            <button
              type="button"
              onClick={onClose}
              className="btn-secondary"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="btn-primary"
            >
              {isSubmitting ? 'Injecting...' : 'Execute Anomaly Injection'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
