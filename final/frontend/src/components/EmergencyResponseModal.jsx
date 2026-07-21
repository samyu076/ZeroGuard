import React, { useState } from 'react';
import { ShieldAlert, X, Send, FileText, CheckCircle2, ShieldCheck } from 'lucide-react';

export default function EmergencyResponseModal({ isOpen, onClose, alert, onTriggerToast }) {
  const [isNotified, setIsNotified] = useState(false);
  const [dispatchLog, setDispatchLog] = useState(null);

  if (!isOpen) return null;

  const timestampStr = new Date().toISOString().replace('T', ' ').substring(0, 19) + ' UTC';

  const handleNotifyResponseTeam = () => {
    const logId = `ER-2026-${Math.floor(1000 + Math.random() * 9000)}`;
    setIsNotified(true);
    setDispatchLog({
      logId,
      dispatchedAt: new Date().toLocaleTimeString(),
      status: 'DISPATCHED TO REFINERY FIRE & SAFETY SQUAD'
    });

    if (onTriggerToast) {
      onTriggerToast({
        title: 'EMERGENCY RESPONSE TEAM NOTIFIED',
        message: `Dispatched control room alert log #${logId} to refinery safety officers.`
      });
    }
  };

  const hasAlert = !!alert;

  return (
    <div className="fixed inset-0 bg-black/75 backdrop-blur-sm z-50 flex items-center justify-center p-[16px]">
      <div className={`zg-modal-panel max-w-2xl w-full relative border ${
        hasAlert ? 'border-[#F85149]/60' : 'border-[#21262D]'
      }`}>
        <button
          onClick={onClose}
          className="absolute right-[16px] top-[16px] text-[#8B949E] hover:text-[#E6EDF3] p-[4px]"
        >
          <X className="w-[16px] h-[16px]" strokeWidth={1.5} />
        </button>

        {/* Modal Header */}
        <div className="flex items-center gap-[8px] mb-[16px] border-b border-[#21262D] pb-[16px]">
          {hasAlert ? (
            <ShieldAlert className="w-[22px] h-[22px] text-[#F85149]" strokeWidth={1.5} />
          ) : (
            <ShieldCheck className="w-[22px] h-[22px] text-[#2EA043]" strokeWidth={1.5} />
          )}
          <h3 className={`text-[16px] font-bold uppercase tracking-[0.02em] font-mono-tech ${
            hasAlert ? 'text-[#F85149]' : 'text-[#E6EDF3]'
          }`}>
            AUTOMATED EMERGENCY RESPONSE ORCHESTRATOR
          </h3>
        </div>

        {/* Modal Content */}
        <div className="space-y-[16px] text-[12px] font-mono-tech">
          {hasAlert ? (
            <div className="p-[16px] bg-[#0D1117] border border-[#21262D] rounded-[4px]">
              <div className="flex justify-between text-[#8B949E] text-[11px] mb-[8px]">
                <span>INCIDENT REPORT ID: #IR-{alert.alert_id?.substring(0, 8) || '2026-0069'}</span>
                <span>TIMESTAMP: {timestampStr}</span>
              </div>

              <h4 className="font-bold text-[#E6EDF3] text-[13px] mb-[8px] font-sans">
                STATUTORY SAFETY INTERLOCK BREACH — {alert.title}
              </h4>

              <div className="grid grid-cols-2 gap-[12px] text-[11px] text-[#8B949E] border-t border-[#21262D] pt-[12px] mb-[12px]">
                <div>Zone: <strong className="text-[#E6EDF3]">{alert.affected_zones?.join(', ') || 'Zone-E-Control'}</strong></div>
                <div>Primary Node: <strong className="text-[#58A6FF]">{alert.primary_node_id}</strong></div>
                <div>Statutory Standard: <strong className="text-[#E6EDF3]">OISD-STD-105 Clause 6.2.1</strong></div>
                <div>Risk Score: <strong className="text-[#F85149]">100.0 / 100 (CRITICAL)</strong></div>
              </div>

              <p className="text-[12px] text-[#E6EDF3] font-sans leading-[1.5] p-[12px] bg-[#161B22] rounded-[4px] border border-[#21262D]">
                <strong>Automated Incident Summary:</strong> At {timestampStr}, ZeroGuard Rule-Guard detected a mandatory interlock violation in Zone E. Hot Work Permit {alert.primary_node_id} was active without physical spectacle blind isolation during a hydrocracker equipment maintenance window, while gas sensor SEN-LEL-681 recorded elevated flammable hydrocarbon z-scores (Z ≥ 3.0). Hot work permit automatically suspended by control room interlock.
              </p>
            </div>
          ) : (
            <div className="p-[16px] bg-[#0D1117] border border-[#21262D] rounded-[4px] space-y-[12px]">
              <div className="flex justify-between text-[#8B949E] text-[11px]">
                <span>INCIDENT REPORT ID: #IR-NORMAL-BASELINE</span>
                <span>TIMESTAMP: {timestampStr}</span>
              </div>

              <h4 className="font-bold text-[#2EA043] text-[13px] font-sans flex items-center gap-[6px]">
                <ShieldCheck className="w-[16px] h-[16px]" /> ALL PLANT ZONES SAFE
              </h4>

              <p className="text-[12px] text-[#E6EDF3] font-sans leading-[1.5] p-[12px] bg-[#161B22] rounded-[4px] border border-[#21262D]">
                <strong>System Summary:</strong> No active interlock violations or critical sensor anomalies detected. Spatio-temporal risk model indicates normal operating baseline parameters. Safety-officer dispatch functions are restricted to emergency drill protocols.
              </p>
            </div>
          )}

          {/* Dispatch Log Banner */}
          {isNotified && dispatchLog && (
            <div className="p-[12px] bg-[#2EA043]/15 border border-[#2EA043]/40 rounded-[4px] flex items-center justify-between text-[#2EA043]">
              <div className="flex items-center gap-[8px]">
                <CheckCircle2 className="w-[16px] h-[16px]" strokeWidth={1.5} />
                <span>LOG #{dispatchLog.logId}: {dispatchLog.status} AT {dispatchLog.dispatchedAt}</span>
              </div>
            </div>
          )}

          {/* Modal Actions */}
          <div className="flex items-center justify-between pt-[8px]">
            <button
              onClick={onClose}
              className="btn-secondary"
            >
              Close Report
            </button>
            <button
              onClick={handleNotifyResponseTeam}
              disabled={isNotified}
              className="btn-primary flex items-center gap-[6px] disabled:opacity-50"
            >
              <Send className="w-[14px] h-[14px]" strokeWidth={1.5} />
              {isNotified ? 'Response Team Dispatched' : 'Notify Refinery Response Team'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
