import React from 'react';
import { FileText, ShieldAlert, ShieldCheck } from 'lucide-react';

export default function PermitTimeline({ nodes }) {
  const permitNodes = (nodes || []).filter(n => n.category === 'PERMIT');

  return (
    <div className="zg-card mb-[32px]">
      <div className="flex items-center justify-between gap-[16px] mb-[16px] border-b border-[#21262D] pb-[16px]">
        <div className="flex items-center gap-[8px]">
          <FileText className="w-[20px] h-[20px] text-[#58A6FF]" strokeWidth={1.5} />
          <h3 className="text-[16px] font-bold text-[#E6EDF3] uppercase tracking-[0.02em] font-mono-tech">
            ACTIVE STATUTORY PERMITS & WORK ORDERS
          </h3>
        </div>
        <span className="text-[12px] font-mono-tech text-[#8B949E]">
          {permitNodes.length} Active Permits
        </span>
      </div>

      {/* BUG 2 FIX: Horizontal Scroll Container with Min-Widths and Line-Height 1.4 Text Wrapping */}
      <div className="overflow-x-auto w-full border border-[#21262D] rounded-[4px]">
        <table className="w-full text-left border-collapse text-[12px] font-mono-tech min-w-[720px]">
          <thead>
            <tr className="border-b border-[#21262D] bg-[#0D1117] text-[#8B949E] uppercase tracking-[0.02em]">
              <th className="py-[12px] px-[16px] min-w-[130px]">Permit ID</th>
              <th className="py-[12px] px-[16px] min-w-[150px]">Work Order Title</th>
              <th className="py-[12px] px-[16px] min-w-[110px]">Type</th>
              <th className="py-[12px] px-[16px] min-w-[130px]">Zone</th>
              <th className="py-[12px] px-[16px] min-w-[150px]">Contractor / Isolation</th>
              <th className="py-[12px] px-[16px] min-w-[160px]">Statutory Standard</th>
              <th className="py-[12px] px-[16px] min-w-[110px]">Compliance</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#21262D]">
            {permitNodes.length === 0 ? (
              <tr>
                <td colSpan={7} className="py-[24px] text-center text-[#4A5568] font-mono-tech">
                  No active permits governing plant zones in this scenario.
                </td>
              </tr>
            ) : (
              permitNodes.map((permit) => {
                const attrs = permit.attributes || {};
                const isNonCompliant = permit.status === 'NON_COMPLIANT';

                return (
                  <tr key={permit.id} className="zg-table-row">
                    <td className="py-[12px] px-[16px] font-semibold text-[#58A6FF] whitespace-nowrap">{permit.id}</td>
                    <td className="py-[12px] px-[16px] text-[#E6EDF3] font-sans leading-[1.4] break-words max-w-[180px]">
                      {permit.name}
                    </td>
                    <td className="py-[12px] px-[16px] font-semibold text-[#DB6D28] whitespace-nowrap">
                      {attrs.permit_type || attrs.type || 'WORK_PERMIT'}
                    </td>
                    <td className="py-[12px] px-[16px] text-[#8B949E] whitespace-nowrap">{permit.zone_id}</td>
                    <td className="py-[12px] px-[16px] text-[#8B949E] font-sans leading-[1.4] break-words max-w-[160px]">
                      {attrs.contractor || 'Plant Maintenance'}
                      <span className="block text-[11px] text-[#4A5568] font-mono-tech mt-[2px]">
                        Isolation: {attrs.isolation_status || 'STANDARD'}
                      </span>
                    </td>
                    <td className="py-[12px] px-[16px] text-[#E6EDF3] leading-[1.4] break-words max-w-[200px]">
                      <span className="text-[#E6EDF3] font-normal">
                        {attrs.statutory_citation || 'OISD-STD-105 Clause 6.2.1 & OSHA 29 CFR 1910.252'}
                      </span>
                    </td>
                    <td className="py-[12px] px-[16px] whitespace-nowrap min-w-[110px]">
                      {isNonCompliant ? (
                        <span className="badge-critical font-mono-tech px-[8px] py-[4px] text-[11px] flex items-center gap-[4px] w-fit">
                          <ShieldAlert className="w-[14px] h-[14px]" strokeWidth={1.5} /> NON-COMPLIANT
                        </span>
                      ) : (
                        <span className="badge-safe font-mono-tech px-[8px] py-[4px] text-[11px] flex items-center gap-[4px] w-fit">
                          <ShieldCheck className="w-[14px] h-[14px]" strokeWidth={1.5} /> COMPLIANT
                        </span>
                      )}
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
