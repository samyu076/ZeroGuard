import React, { useState, useEffect } from 'react';
import { Zap, ShieldAlert, CheckCircle2, Clock, Server, AlertTriangle } from 'lucide-react';

const API_BASE = 'http://127.0.0.1:8000/api/v1';

export default function EsdDispatchPanel({ graphState, onTriggerToast }) {
  const [esdLog, setEsdLog] = useState([]);
  const [isTriggering, setIsTriggering] = useState(false);
  const [lastPayload, setLastPayload] = useState(null);

  const fetchLog = async () => {
    try {
      const res = await fetch(`${API_BASE}/esd/log`);
      if (!res.ok) return;
      const data = await res.json();
      setEsdLog(data.esd_records || []);
    } catch (e) {
      // Silently skip if backend offline
    }
  };

  useEffect(() => {
    fetchLog();
  }, []);

  const handleTriggerEsd = async () => {
    const alert = graphState?.active_alerts?.[0];
    const alertTitle = alert?.title || 'Manual ESD Test Drill — Simulated COMPOUND_CRITICAL Interlock';
    const affectedZones = alert?.affected_zones || ['Zone-E'];

    setIsTriggering(true);
    try {
      const res = await fetch(`${API_BASE}/esd/trigger`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          alert_title: alertTitle,
          affected_zones: affectedZones,
        }),
      });
      const payload = await res.json();
      setLastPayload(payload);
      fetchLog();
      if (onTriggerToast) {
        onTriggerToast({
          title: 'ESD RELAY DISPATCHED',
          message: `${payload.shutdown_commands?.length || 0} valve(s) de-energized. ESD ID: ${payload.esd_id}`
        });
      }
    } catch (e) {
      if (onTriggerToast) {
        onTriggerToast({ title: 'ESD ERROR', message: e.message, type: 'error' });
      }
    } finally {
      setIsTriggering(false);
    }
  };

  const hasActiveAlert = graphState?.active_alerts?.length > 0;

  return (
    <div className="space-y-[16px]">
      {/* ESD Trigger Panel */}
      <div className={`p-[20px] rounded-[6px] border ${
        hasActiveAlert
          ? 'bg-[#F85149]/8 border-[#F85149]/50'
          : 'bg-[#0D1117] border-[#21262D]'
      }`}>
        <div className="flex items-center justify-between flex-wrap gap-[12px]">
          <div className="flex items-center gap-[10px]">
            <div className={`p-[8px] rounded-[6px] ${hasActiveAlert ? 'bg-[#F85149]/15' : 'bg-[#21262D]'}`}>
              <Zap className={`w-[20px] h-[20px] ${hasActiveAlert ? 'text-[#F85149]' : 'text-[#8B949E]'}`} strokeWidth={1.5} />
            </div>
            <div>
              <span className={`text-[13px] font-bold font-mono-tech uppercase block ${hasActiveAlert ? 'text-[#F85149]' : 'text-[#E6EDF3]'}`}>
                {hasActiveAlert ? 'ACTIVE INTERLOCK VIOLATION DETECTED' : 'ESD DRILL MODE — ALL ZONES SAFE'}
              </span>
              <span className="text-[11px] text-[#8B949E] font-sans">
                {hasActiveAlert
                  ? `${graphState.active_alerts[0].title.substring(0, 80)}...`
                  : 'Click to run a simulated ESD drill dispatch on Zone-E valves.'
                }
              </span>
            </div>
          </div>
          <button
            onClick={handleTriggerEsd}
            disabled={isTriggering}
            className={`flex items-center gap-[8px] px-[16px] py-[9px] rounded-[4px] font-mono-tech text-[12px] font-bold transition-all disabled:opacity-50 ${
              hasActiveAlert
                ? 'bg-[#F85149] text-white hover:bg-[#F85149]/80'
                : 'btn-secondary'
            }`}
          >
            <Zap className="w-[14px] h-[14px]" strokeWidth={1.5} />
            {isTriggering ? 'DISPATCHING...' : 'TRIGGER ESD RELAY'}
          </button>
        </div>
      </div>

      {/* Last ESD Payload Detail */}
      {lastPayload && (
        <div className="zg-card text-[11px] font-mono-tech space-y-[10px]">
          <div className="flex items-center gap-[8px] border-b border-[#21262D] pb-[12px]">
            <CheckCircle2 className="w-[16px] h-[16px] text-[#2EA043]" strokeWidth={1.5} />
            <span className="text-[13px] font-bold text-[#2EA043] uppercase">ESD DISPATCH CONFIRMED — {lastPayload.esd_id}</span>
          </div>
          <div className="grid grid-cols-2 gap-[8px] text-[#8B949E]">
            <div>Trigger Source: <strong className="text-[#E6EDF3]">{lastPayload.trigger_source}</strong></div>
            <div>Timestamp: <strong className="text-[#E6EDF3]">{lastPayload.timestamp}</strong></div>
            <div>Statutory Ref: <strong className="text-[#58A6FF]">{lastPayload.statutory_reference}</strong></div>
            <div>Fail-Safe Class: <strong className="text-[#E6EDF3]">{lastPayload.fail_safe_classification}</strong></div>
          </div>
          <div className="space-y-[6px] mt-[4px]">
            <span className="text-[10px] uppercase text-[#8B949E] block">Shutdown Commands:</span>
            {lastPayload.shutdown_commands?.map((cmd, i) => (
              <div key={i} className="flex items-center justify-between p-[8px] bg-[#0D1117] rounded-[4px] border border-[#F85149]/20">
                <span className="text-[#E6EDF3]">{cmd.valve_id} — {cmd.description}</span>
                <div className="flex items-center gap-[8px]">
                  <span className="text-[#8B949E]">{cmd.zone}</span>
                  <span className="text-[#F85149] font-bold">{cmd.action}</span>
                  <span className="text-[#2EA043]">{cmd.response_latency_ms}ms</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ESD History Log */}
      {esdLog.length > 0 && (
        <div className="zg-card">
          <div className="flex items-center gap-[8px] mb-[12px] border-b border-[#21262D] pb-[12px]">
            <Server className="w-[16px] h-[16px] text-[#8B949E]" strokeWidth={1.5} />
            <span className="text-[12px] font-bold font-mono-tech text-[#E6EDF3] uppercase">
              FAIL-SAFE SHUTDOWN LOG ({esdLog.length} Records)
            </span>
          </div>
          <div className="space-y-[6px] max-h-[200px] overflow-y-auto">
            {esdLog.map((record, i) => (
              <div key={i} className="flex items-center justify-between p-[8px] bg-[#0D1117] rounded-[4px] border border-[#21262D] text-[10px] font-mono-tech">
                <div className="flex items-center gap-[8px]">
                  <Clock className="w-[10px] h-[10px] text-[#8B949E]" strokeWidth={1.5} />
                  <span className="text-[#8B949E]">{record.timestamp}</span>
                  <span className="text-[#E6EDF3]">{record.esd_id}</span>
                </div>
                <span className="text-[#F85149]">{record.shutdown_commands?.length} VALVES DE-ENERGIZED</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
