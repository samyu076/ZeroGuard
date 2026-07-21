import React from 'react';

const PLANT_ZONES_LIST = [
  { id: 'Zone-A-CrudeDistillation', shortName: 'Zone A (CDU)' },
  { id: 'Zone-B-PumpStation', shortName: 'Zone B (Pump Station)' },
  { id: 'Zone-C-TankFarm', shortName: 'Zone C (Tank Farm)' },
  { id: 'Zone-D-Loading', shortName: 'Zone D (Loading Rack)' },
  { id: 'Zone-E-Control', shortName: 'Zone E (Control Room)' },
];

export default function ZoneStatusStrip({ nodes = [] }) {
  const getZoneStatus = (zoneId) => {
    const zoneNodes = nodes.filter(n => {
      if (n.zone_id === zoneId) return true;
      if (zoneId.includes('PumpStation') && (n.zone_id.includes('Pump') || n.zone_id.includes('Zone-B'))) return true;
      if (zoneId.includes('CrudeDistillation') && (n.zone_id.includes('Zone-A') || n.zone_id.includes('CDU'))) return true;
      if (zoneId.includes('TankFarm') && (n.zone_id.includes('Zone-C') || n.zone_id.includes('Storage'))) return true;
      if (zoneId.includes('Loading') && (n.zone_id.includes('Zone-D') || n.zone_id.includes('Loading'))) return true;
      if (zoneId.includes('Control') && (n.zone_id.includes('Zone-E') || n.zone_id.includes('Control'))) return true;
      return false;
    });

    if (zoneNodes.some(n => n.status === 'CRITICAL' || n.status === 'NON_COMPLIANT')) {
      return { level: 'CRITICAL', color: '#F85149', badgeClass: 'text-[#F85149] bg-[#F85149]/10 border-[#F85149]/30' };
    }
    if (zoneNodes.some(n => n.status === 'WARNING' || Math.abs(n.z_score || 0) >= 2.5)) {
      return { level: 'WARNING', color: '#DB6D28', badgeClass: 'text-[#DB6D28] bg-[#DB6D28]/10 border-[#DB6D28]/30' };
    }
    if (zoneNodes.some(n => Math.abs(n.z_score || 0) >= 1.5)) {
      return { level: 'WATCH', color: '#D29922', badgeClass: 'text-[#D29922] bg-[#D29922]/10 border-[#D29922]/30' };
    }
    return { level: 'NORMAL', color: '#2EA043', badgeClass: 'text-[#2EA043] bg-[#2EA043]/10 border-[#2EA043]/30' };
  };

  return (
    <div className="bg-[#161B22] border-b border-[#21262D] px-[24px] py-[8px] flex items-center justify-between gap-[16px] text-[12px] font-mono-tech overflow-x-auto">
      <span className="text-[#8B949E] uppercase tracking-[0.02em] shrink-0 font-semibold">
        PLANT ZONE RISK MATRIX:
      </span>
      <div className="flex items-center gap-[16px] overflow-x-auto">
        {PLANT_ZONES_LIST.map((zone) => {
          const status = getZoneStatus(zone.id);
          return (
            <div
              key={zone.id}
              className={`flex items-center gap-[6px] px-[10px] py-[4px] rounded-[4px] border ${status.badgeClass} shrink-0`}
            >
              <span
                className="w-[8px] h-[8px] rounded-full inline-block shrink-0"
                style={{ backgroundColor: status.color }}
              />
              <span className="font-bold">{zone.shortName}</span>
              <span className="opacity-75 text-[11px]">({status.level})</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
