import React, { useState } from 'react';
import { UserCheck, Shield, Wrench, FileCheck, CheckCircle2 } from 'lucide-react';

export default function RoleAwareOutputPanel({ alert }) {
  const [selectedRole, setSelectedRole] = useState('operator');

  const getRoleOutput = () => {
    if (selectedRole === 'operator') {
      return {
        roleTitle: 'Control Room Plant Operator',
        actionHeader: 'PHYSICAL CONTROL ROOM ACTION REQUIRED',
        badgeColor: '#FF6200',
        instructions: [
          '1. Immediately close Hydrocracker Feed Line Isolation Valve V-102.',
          '2. Issue radio command to welding team on Pump P-201: Halt all hot work instantly.',
          '3. Engage auxiliary forced ventilation fan VF-04 in Zone E.'
        ]
      };
    } else if (selectedRole === 'supervisor') {
      return {
        roleTitle: 'Refinery Shift Supervisor',
        actionHeader: 'OPERATIONAL AUTHORIZATION & WORK ORDER OVERRIDE',
        badgeColor: '#58A6FF',
        instructions: [
          '1. Authorize Emergency Maintenance Shutdown Order #SO-2026-99.',
          '2. Suspend Hot Work Permit PERMIT-2026-0440 in refinery ERP system.',
          '3. Dispatch Zone E isolation verification officer to verify spectacle blind.'
        ]
      };
    } else {
      return {
        roleTitle: 'Safety Compliance Officer',
        actionHeader: 'STATUTORY AUDIT & REGULATORY FILING IMPLICATIONS',
        badgeColor: '#2EA043',
        instructions: [
          '1. Statutory violation logged under OISD-STD-105 Clause 6.2.1 (Hot Work Interlock).',
          '2. Statutory filing logged under Factory Act 1948 Section 36 (Fumes Isolation).',
          '3. Preliminary incident report #IR-2026-0069 queued for DGMS quarterly audit.'
        ]
      };
    }
  };

  const currentRoleOutput = getRoleOutput();

  return (
    <div className="zg-card mb-[32px]">
      <div className="flex flex-wrap items-center justify-between gap-[16px] mb-[16px] border-b border-[#21262D] pb-[16px]">
        <div className="flex items-center gap-[8px]">
          <UserCheck className="w-[20px] h-[20px] text-[#58A6FF]" strokeWidth={1.5} />
          <h3 className="text-[16px] font-bold text-[#E6EDF3] uppercase tracking-[0.02em] font-mono-tech">
            ROLE-AWARE ACTION & COMPLIANCE DISPATCH
          </h3>
        </div>
        <span className="text-[11px] font-mono-tech text-[#8B949E] px-[8px] py-[4px] bg-[#0D1117] border border-[#21262D] rounded-[4px]">
          View-Customized Directives
        </span>
      </div>

      {/* Role Selection Tabs */}
      <div className="flex items-center gap-[8px] mb-[20px] font-mono-tech text-[12px]">
        <button
          onClick={() => setSelectedRole('operator')}
          className={`flex items-center gap-[6px] py-[8px] px-[16px] rounded-[4px] border transition-all ${
            selectedRole === 'operator' ? 'bg-[#FF6200] text-[#FFFFFF] border-[#FF6200] font-bold' : 'bg-[#0D1117] text-[#8B949E] border-[#21262D]'
          }`}
        >
          <Wrench className="w-[14px] h-[14px]" strokeWidth={1.5} /> Operator View
        </button>

        <button
          onClick={() => setSelectedRole('supervisor')}
          className={`flex items-center gap-[6px] py-[8px] px-[16px] rounded-[4px] border transition-all ${
            selectedRole === 'supervisor' ? 'bg-[#58A6FF] text-[#0D1117] border-[#58A6FF] font-bold' : 'bg-[#0D1117] text-[#8B949E] border-[#21262D]'
          }`}
        >
          <Shield className="w-[14px] h-[14px]" strokeWidth={1.5} /> Supervisor View
        </button>

        <button
          onClick={() => setSelectedRole('safety')}
          className={`flex items-center gap-[6px] py-[8px] px-[16px] rounded-[4px] border transition-all ${
            selectedRole === 'safety' ? 'bg-[#2EA043] text-[#0D1117] border-[#2EA043] font-bold' : 'bg-[#0D1117] text-[#8B949E] border-[#21262D]'
          }`}
        >
          <FileCheck className="w-[14px] h-[14px]" strokeWidth={1.5} /> Safety Officer View
        </button>
      </div>

      {/* Role Specific Action Card */}
      <div className="p-[20px] bg-[#0D1117] border border-[#21262D] rounded-[6px] font-mono-tech text-[12px]">
        <div className="flex items-center justify-between border-b border-[#21262D] pb-[12px] mb-[12px]">
          <span className="text-[13px] font-bold text-[#E6EDF3] uppercase tracking-[0.02em]">
            {currentRoleOutput.actionHeader}
          </span>
          <span className="px-[8px] py-[4px] rounded text-[11px] font-bold text-[#0D1117]" style={{ backgroundColor: currentRoleOutput.badgeColor }}>
            {currentRoleOutput.roleTitle}
          </span>
        </div>

        <div className="space-y-[10px]">
          {currentRoleOutput.instructions.map((inst, idx) => (
            <div key={idx} className="p-[12px] bg-[#161B22] border border-[#21262D] rounded-[4px] text-[#E6EDF3] font-sans flex items-start gap-[10px]">
              <CheckCircle2 className="w-[16px] h-[16px] text-[#58A6FF] shrink-0 mt-[2px]" strokeWidth={1.5} />
              <span>{inst}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
