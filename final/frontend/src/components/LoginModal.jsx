import React, { useState } from 'react';
import { ShieldCheck, Lock, User, Key, X } from 'lucide-react';

export default function LoginModal({ isOpen, onClose, onLoginSuccess }) {
  const [operatorId, setOperatorId] = useState('OP-REF-2026');
  const [password, setPassword] = useState('••••••••••••');
  const [zone, setZone] = useState('Zone-E-Control');

  if (!isOpen) return null;

  const handleSubmit = (e) => {
    e.preventDefault();
    if (onLoginSuccess) {
      onLoginSuccess({ operatorId, zone });
    }
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-[#0D1117]/90 backdrop-blur-md z-50 flex items-center justify-center p-[16px]">
      <div className="zg-modal-panel max-w-md w-full relative border-[#FF6200]/40">
        <button
          onClick={onClose}
          className="absolute right-[16px] top-[16px] text-[#8B949E] hover:text-[#E6EDF3] p-[4px]"
        >
          <X className="w-[16px] h-[16px]" strokeWidth={1.5} />
        </button>

        <div className="flex items-center gap-[10px] mb-[16px] border-b border-[#21262D] pb-[16px]">
          <ShieldCheck className="w-[24px] h-[24px] text-[#FF6200]" strokeWidth={1.5} />
          <div>
            <h3 className="text-[16px] font-bold text-[#E6EDF3] uppercase tracking-[0.02em] font-mono-tech">
              ZERO GUARD OPERATOR AUTHENTICATION
            </h3>
            <span className="text-[11px] text-[#8B949E]">Refinery Safety Control Room Access</span>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-[16px] text-[12px] font-mono-tech">
          <div>
            <label className="block text-[#8B949E] mb-[6px] uppercase tracking-[0.02em]">Licensed Operator ID</label>
            <div className="relative">
              <User className="w-[16px] h-[16px] text-[#8B949E] absolute left-[10px] top-1/2 -translate-y-1/2" strokeWidth={1.5} />
              <input
                type="text"
                value={operatorId}
                onChange={(e) => setOperatorId(e.target.value)}
                className="w-full pl-[34px] pr-[12px] py-[8px] bg-[#0D1117] border border-[#21262D] rounded-[4px] text-[#E6EDF3] focus:outline-none"
              />
            </div>
          </div>

          <div>
            <label className="block text-[#8B949E] mb-[6px] uppercase tracking-[0.02em]">Control Room Keycode</label>
            <div className="relative">
              <Key className="w-[16px] h-[16px] text-[#8B949E] absolute left-[10px] top-1/2 -translate-y-1/2" strokeWidth={1.5} />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full pl-[34px] pr-[12px] py-[8px] bg-[#0D1117] border border-[#21262D] rounded-[4px] text-[#E6EDF3] focus:outline-none"
              />
            </div>
          </div>

          <div>
            <label className="block text-[#8B949E] mb-[6px] uppercase tracking-[0.02em]">Assigned Operational Zone</label>
            <select
              value={zone}
              onChange={(e) => setZone(e.target.value)}
              className="w-full p-[8px] bg-[#0D1117] border border-[#21262D] rounded-[4px] text-[#E6EDF3] focus:outline-none"
            >
              <option value="Zone-E-Control">Zone E: Main Plant Control Room & Substation</option>
              <option value="Zone-A-CrudeDistillation">Zone A: Crude Distillation Unit (CDU)</option>
              <option value="Zone-B-PumpStation">Zone B: Hydrocracker Feed Pump Station</option>
              <option value="Zone-C-TankFarm">Zone C: Hydrocarbon Tank Farm C-10</option>
              <option value="Zone-D-Loading">Zone D: Truck Loading & Unloading Rack</option>
            </select>
          </div>

          <div className="pt-[8px]">
            <button
              type="submit"
              className="btn-primary w-full py-[10px]"
            >
              <Lock className="w-[14px] h-[14px]" strokeWidth={1.5} /> Authenticate Operator Session
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
