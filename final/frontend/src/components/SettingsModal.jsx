import React, { useState } from 'react';
import { Sliders, X, Check, ShieldCheck } from 'lucide-react';

export default function SettingsModal({ isOpen, onClose, onSaveConfig }) {
  const [alpha, setAlpha] = useState(0.15);
  const [lelThreshold, setLelThreshold] = useState(3.0);
  const [enableOisd, setEnableOisd] = useState(true);
  const [enableFactoryAct, setEnableFactoryAct] = useState(true);
  const [enableDgms, setEnableDgms] = useState(true);

  if (!isOpen) return null;

  const handleSave = (e) => {
    e.preventDefault();
    if (onSaveConfig) {
      onSaveConfig({ alpha, lelThreshold, enableOisd, enableFactoryAct, enableDgms });
    }
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-[#0D1117]/90 backdrop-blur-md z-50 flex items-center justify-center p-[16px]">
      <div className="zg-modal-panel max-w-lg w-full relative border-[#58A6FF]/40">
        <button
          onClick={onClose}
          className="absolute right-[16px] top-[16px] text-[#8B949E] hover:text-[#E6EDF3] p-[4px]"
        >
          <X className="w-[16px] h-[16px]" strokeWidth={1.5} />
        </button>

        <div className="flex items-center gap-[10px] mb-[16px] border-b border-[#21262D] pb-[16px]">
          <Sliders className="w-[22px] h-[22px] text-[#58A6FF]" strokeWidth={1.5} />
          <h3 className="text-[16px] font-bold text-[#E6EDF3] uppercase tracking-[0.02em] font-mono-tech">
            ZERO GUARD ENGINE & PLANT CONFIGURATION
          </h3>
        </div>

        <form onSubmit={handleSave} className="space-y-[16px] text-[12px] font-mono-tech">
          <div>
            <div className="flex justify-between mb-[6px]">
              <label className="text-[#8B949E] uppercase">PageRank Restart Probability (α)</label>
              <span className="text-[#58A6FF] font-bold">{alpha.toFixed(2)}</span>
            </div>
            <input
              type="range"
              min="0.05"
              max="0.50"
              step="0.01"
              value={alpha}
              onChange={(e) => setAlpha(parseFloat(e.target.value))}
              className="w-full accent-[#58A6FF]"
            />
            <span className="text-[11px] text-[#4A5568] font-sans">
              Controls spatial risk propagation dampening factor across graph nodes.
            </span>
          </div>

          <div>
            <div className="flex justify-between mb-[6px]">
              <label className="text-[#8B949E] uppercase">Rule-Guard LEL Trigger Threshold (Z-Score)</label>
              <span className="text-[#F85149] font-bold">Z ≥ {lelThreshold.toFixed(1)}</span>
            </div>
            <input
              type="range"
              min="1.5"
              max="4.0"
              step="0.1"
              value={lelThreshold}
              onChange={(e) => setLelThreshold(parseFloat(e.target.value))}
              className="w-full accent-[#F85149]"
            />
          </div>

          <div>
            <label className="block text-[#8B949E] mb-[8px] uppercase">Active Statutory Standard Corpora</label>
            <div className="space-y-[8px] font-sans">
              <label className="flex items-center gap-[8px] cursor-pointer">
                <input
                  type="checkbox"
                  checked={enableOisd}
                  onChange={(e) => setEnableOisd(e.target.checked)}
                  className="accent-[#58A6FF]"
                />
                <span className="text-[#E6EDF3] font-mono-tech text-[12px]">OISD-STD-105 / 118 (Oil Industry Safety Directorate)</span>
              </label>

              <label className="flex items-center gap-[8px] cursor-pointer">
                <input
                  type="checkbox"
                  checked={enableFactoryAct}
                  onChange={(e) => setEnableFactoryAct(e.target.checked)}
                  className="accent-[#58A6FF]"
                />
                <span className="text-[#E6EDF3] font-mono-tech text-[12px]">Factory Act 1948 (Section 36 Hazardous Isolation)</span>
              </label>

              <label className="flex items-center gap-[8px] cursor-pointer">
                <input
                  type="checkbox"
                  checked={enableDgms}
                  onChange={(e) => setEnableDgms(e.target.checked)}
                  className="accent-[#58A6FF]"
                />
                <span className="text-[#E6EDF3] font-mono-tech text-[12px]">DGMS Circular No. 02 (2023) / CMR 2017 Reg 145</span>
              </label>
            </div>
          </div>

          <div className="flex justify-end gap-[12px] pt-[8px]">
            <button
              type="button"
              onClick={onClose}
              className="btn-secondary"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn-primary"
            >
              <Check className="w-[14px] h-[14px]" strokeWidth={1.5} /> Save Engine Configuration
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
