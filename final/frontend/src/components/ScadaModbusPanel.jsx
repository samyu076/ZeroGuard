import React, { useState, useEffect } from 'react';
import { Cpu, Radio, RefreshCw, Activity, AlertTriangle, CheckCircle2, Send } from 'lucide-react';

const API_BASE = 'http://127.0.0.1:8000/api/v1';

const REGISTER_COLORS = {
  NORMAL: { dot: 'bg-[#2EA043]', badge: 'text-[#2EA043] border-[#2EA043]/30 bg-[#2EA043]/10', bar: 'bg-[#2EA043]' },
  ALARM:  { dot: 'bg-[#F85149] animate-pulse', badge: 'text-[#F85149] border-[#F85149]/30 bg-[#F85149]/10', bar: 'bg-[#F85149]' },
};

export default function ScadaModbusPanel() {
  const [registers, setRegisters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [writeAddr, setWriteAddr] = useState(40001);
  const [writeVal, setWriteVal] = useState('');
  const [writeResult, setWriteResult] = useState(null);
  const [plcStatus, setPlcStatus] = useState('CONNECTING');
  const [refreshing, setRefreshing] = useState(false);

  const fetchRegisters = async () => {
    setRefreshing(true);
    try {
      const res = await fetch(`${API_BASE}/scada/registers`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setRegisters(data.registers || []);
      setPlcStatus(data.plc_status || 'ONLINE');
      setError(null);
    } catch (e) {
      setError('SCADA gateway offline — polling suspended.');
      setPlcStatus('OFFLINE');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchRegisters();
    const interval = setInterval(fetchRegisters, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleWrite = async (e) => {
    e.preventDefault();
    if (!writeVal) return;
    try {
      const res = await fetch(`${API_BASE}/scada/registers/write`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ register_address: writeAddr, value: parseFloat(writeVal) }),
      });
      const data = await res.json();
      setWriteResult(data);
      fetchRegisters();
    } catch (e) {
      setWriteResult({ error: e.message });
    }
  };

  return (
    <div className="space-y-[20px]">
      {/* Panel Header */}
      <div className="zg-card">
        <div className="flex items-center justify-between mb-[16px] border-b border-[#21262D] pb-[16px]">
          <div className="flex items-center gap-[10px]">
            <Cpu className="w-[20px] h-[20px] text-[#58A6FF]" strokeWidth={1.5} />
            <h3 className="text-[15px] font-bold text-[#E6EDF3] uppercase tracking-[0.02em] font-mono-tech">
              SCADA MODBUS TCP REGISTER MAP
            </h3>
            <span className="text-[10px] font-mono-tech px-[6px] py-[2px] rounded border border-[#21262D] text-[#8B949E]">
              UNIT ID: 1 · PORT 502 · FC03/FC06
            </span>
          </div>
          <div className="flex items-center gap-[10px]">
            <span className={`flex items-center gap-[6px] text-[11px] font-mono-tech font-bold ${
              plcStatus === 'ONLINE' ? 'text-[#2EA043]' : 'text-[#F85149]'
            }`}>
              <span className={`w-[6px] h-[6px] rounded-full ${plcStatus === 'ONLINE' ? 'bg-[#2EA043] animate-pulse' : 'bg-[#F85149]'}`} />
              PLC STATUS: {plcStatus}
            </span>
            <button
              onClick={fetchRegisters}
              disabled={refreshing}
              className="btn-secondary py-[4px] px-[8px] flex items-center gap-[4px] text-[11px]"
            >
              <RefreshCw className={`w-[12px] h-[12px] ${refreshing ? 'animate-spin' : ''}`} strokeWidth={1.5} />
              Poll
            </button>
          </div>
        </div>

        {/* Register Table */}
        {loading ? (
          <div className="h-[200px] animate-skeleton rounded-[6px]" />
        ) : error ? (
          <div className="p-[16px] text-center text-[#F85149] font-mono-tech text-[12px] border border-[#F85149]/30 rounded-[4px] bg-[#F85149]/5">
            {error}
          </div>
        ) : (
          <div className="space-y-[8px]">
            {registers.map((reg) => {
              const cols = REGISTER_COLORS[reg.alarm_status] || REGISTER_COLORS.NORMAL;
              const fillPct = Math.min(100, Math.max(0, (reg.value / reg.alarm_high) * 100));
              return (
                <div
                  key={reg.register_address}
                  className={`p-[12px] rounded-[4px] bg-[#0D1117] border ${
                    reg.alarm_status === 'ALARM' ? 'border-[#F85149]/40' : 'border-[#21262D]'
                  } transition-all`}
                >
                  <div className="flex items-center justify-between mb-[6px]">
                    <div className="flex items-center gap-[8px]">
                      <span className={`w-[6px] h-[6px] rounded-full flex-shrink-0 ${cols.dot}`} />
                      <span className="text-[11px] font-mono-tech text-[#8B949E]">
                        REG {reg.register_address}
                      </span>
                      <span className="text-[11px] font-sans text-[#E6EDF3]">
                        {reg.description}
                      </span>
                    </div>
                    <div className="flex items-center gap-[8px]">
                      <span className="text-[12px] font-mono-tech font-bold text-[#E6EDF3]">
                        {reg.value.toFixed(2)} {reg.unit}
                      </span>
                      <span className="text-[11px] font-mono-tech text-[#8B949E]">
                        Z={reg.z_score.toFixed(2)}
                      </span>
                      <span className={`text-[10px] px-[6px] py-[1px] rounded border font-mono-tech ${cols.badge}`}>
                        {reg.alarm_status}
                      </span>
                    </div>
                  </div>
                  {/* Progress bar showing proximity to alarm threshold */}
                  <div className="w-full bg-[#161B22] h-[4px] rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all duration-500 ${cols.bar}`}
                      style={{ width: `${fillPct}%` }}
                    />
                  </div>
                  <div className="flex justify-between mt-[2px]">
                    <span className="text-[9px] text-[#4A5568] font-mono-tech">0</span>
                    <span className="text-[9px] text-[#4A5568] font-mono-tech">ALARM: {reg.alarm_high} {reg.unit}</span>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Modbus FC06 Write Simulator */}
      <div className="zg-card">
        <div className="flex items-center gap-[8px] mb-[16px] border-b border-[#21262D] pb-[16px]">
          <Radio className="w-[18px] h-[18px] text-[#FF6200]" strokeWidth={1.5} />
          <h4 className="text-[13px] font-bold text-[#E6EDF3] uppercase tracking-[0.02em] font-mono-tech">
            FC06 WRITE SINGLE REGISTER — PLC TELEMETRY INJECTION
          </h4>
        </div>
        <form onSubmit={handleWrite} className="grid grid-cols-1 md:grid-cols-3 gap-[12px] items-end">
          <div>
            <label className="block text-[10px] text-[#8B949E] font-mono-tech uppercase mb-[4px]">
              Register Address
            </label>
            <select
              value={writeAddr}
              onChange={(e) => setWriteAddr(parseInt(e.target.value))}
              className="w-full p-[8px] bg-[#0D1117] border border-[#21262D] rounded-[4px] text-[12px] font-mono-tech text-[#E6EDF3] focus:outline-none focus:border-[#58A6FF]"
            >
              {registers.map((r) => (
                <option key={r.register_address} value={r.register_address}>
                  {r.register_address} — {r.description.split('[')[0].trim()}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-[10px] text-[#8B949E] font-mono-tech uppercase mb-[4px]">
              New Value
            </label>
            <input
              type="number"
              step="0.01"
              placeholder="e.g. 12.5"
              value={writeVal}
              onChange={(e) => setWriteVal(e.target.value)}
              className="w-full px-[10px] py-[8px] bg-[#0D1117] border border-[#21262D] rounded-[4px] text-[12px] font-mono-tech text-[#E6EDF3] focus:outline-none focus:border-[#58A6FF]"
            />
          </div>
          <button
            type="submit"
            className="btn-primary flex items-center justify-center gap-[6px] py-[9px]"
          >
            <Send className="w-[13px] h-[13px]" strokeWidth={1.5} />
            Write Register
          </button>
        </form>

        {writeResult && (
          <div className={`mt-[12px] p-[10px] rounded-[4px] text-[11px] font-mono-tech border ${
            writeResult.error
              ? 'text-[#F85149] border-[#F85149]/30 bg-[#F85149]/5'
              : 'text-[#2EA043] border-[#2EA043]/30 bg-[#2EA043]/5'
          }`}>
            {writeResult.error
              ? `ERROR: ${writeResult.error}`
              : `WRITE SUCCESS — REG ${writeResult.record?.register_address}: ${writeResult.record?.old_value} → ${writeResult.record?.new_value} ${writeResult.record?.description?.split(' ')[0]} (Z=${writeResult.record?.z_score?.toFixed(2)})`
            }
          </div>
        )}
      </div>
    </div>
  );
}
