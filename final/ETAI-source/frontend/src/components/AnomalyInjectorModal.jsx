import React, { useState } from 'react';
import { X, SlidersHorizontal, Zap } from 'lucide-react';
import { injectAnomaly } from '../services/api';

export default function AnomalyInjectorModal({ isOpen, onClose, onAnomalyInjected }) {
  const [sensorId, setSensorId] = useState('SEN-GAS-004');
  const [zScore, setZScore] = useState(4.2);
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const updatedGraph = await injectAnomaly(sensorId, parseFloat(zScore));
      onAnomalyInjected(updatedGraph);
      onClose();
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-4">
      <div className="glass-panel w-full max-w-md rounded-2xl border border-slate-700 p-6 relative shadow-2xl">
        <button onClick={onClose} className="absolute top-4 right-4 p-2 text-slate-400 hover:text-white rounded-lg bg-slate-800">
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center space-x-3 mb-4">
          <div className="p-2.5 bg-cyan-500/10 border border-cyan-500/30 rounded-xl text-cyan-400">
            <SlidersHorizontal className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-white">Inject Sensor Anomaly</h2>
            <p className="text-xs font-mono text-slate-400">Simulate Real-time Sensor Drift & Z-Score Spikes</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4 font-mono text-xs">
          <div>
            <label className="text-slate-400 block mb-1">Target Sensor</label>
            <select
              value={sensorId}
              onChange={(e) => setSensorId(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-slate-200 focus:outline-none focus:border-cyan-400"
            >
              <option value="SEN-GAS-004">SEN-GAS-004 (LEL Gas Sensor)</option>
              <option value="SEN-TEMP-101">SEN-TEMP-101 (Hydrocracker Skin Temp)</option>
            </select>
          </div>

          <div>
            <label className="text-slate-400 block mb-1">Inject Z-Score Spike ({zScore})</label>
            <input
              type="range"
              min="0.0"
              max="8.0"
              step="0.1"
              value={zScore}
              onChange={(e) => setZScore(e.target.value)}
              className="w-full accent-cyan-400"
            />
            <div className="flex justify-between text-[10px] text-slate-500 mt-1">
              <span>0.0 (Normal)</span>
              <span>3.0 (Anomaly Threshold)</span>
              <span>8.0 (Extreme Hazard)</span>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-black font-sans font-bold flex items-center justify-center space-x-2 transition shadow-lg shadow-cyan-500/20"
          >
            <Zap className="w-4 h-4" />
            <span>{loading ? 'Injecting...' : 'Trigger Simulation Spike'}</span>
          </button>
        </form>
      </div>
    </div>
  );
}
