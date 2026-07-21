import React, { useState, useEffect } from 'react';
import { X, FileText, Search, ShieldAlert, CheckCircle } from 'lucide-react';
import { runComplianceCheck } from '../services/api';

export default function ComplianceCitationPanel({ isOpen, onClose }) {
  const [citations, setCitations] = useState([]);
  const [permitType, setPermitType] = useState('HOT_WORK');

  useEffect(() => {
    if (isOpen) {
      loadCitations(permitType);
    }
  }, [isOpen, permitType]);

  const loadCitations = async (type) => {
    try {
      const data = await runComplianceCheck(type, null);
      setCitations(data);
    } catch (err) {
      console.error(err);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-y-0 right-0 z-50 w-full max-w-md bg-[#0F172A] border-l border-slate-800 shadow-2xl p-6 flex flex-col justify-between overflow-y-auto">
      <div>
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-2">
            <FileText className="w-6 h-6 text-emerald-400" />
            <h2 className="text-lg font-bold text-white">Statutory Citations</h2>
          </div>
          <button onClick={onClose} className="p-2 text-slate-400 hover:text-white rounded-lg bg-slate-800">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Filter Selector */}
        <div className="mb-4">
          <label className="text-xs font-mono text-slate-400 block mb-1">Select Permit Context</label>
          <select
            value={permitType}
            onChange={(e) => setPermitType(e.target.value)}
            className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs font-mono text-slate-200 focus:outline-none focus:border-cyan-400"
          >
            <option value="HOT_WORK">OISD-STD-105 (Hot Work Permit System)</option>
            <option value="VESSEL_ENTRY">OISD-STD-118 / Factory Act Sec 36 (Vessel Entry)</option>
          </select>
        </div>

        {/* Citations List */}
        <div className="space-y-4">
          {citations.map((c) => (
            <div key={c.citation_id} className="p-4 rounded-xl glass-panel border border-slate-800 space-y-2">
              <div className="flex justify-between items-start">
                <span className="px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800 text-[10px] font-mono font-bold">
                  {c.document_id}
                </span>
                <span className="text-xs font-mono text-slate-400">{c.section_number}</span>
              </div>
              <div className="text-xs font-bold text-white">{c.title}</div>
              <div className="p-3 rounded-lg bg-black/50 border border-slate-800 text-[11px] font-mono text-slate-300 italic leading-relaxed">
                "{c.matched_passage}"
              </div>
              <div className="text-[10px] font-mono text-slate-400 flex justify-between pt-1">
                <span>Standard: {c.standard_name}</span>
                <span className="text-emerald-400">Match: {(c.relevance_score * 100).toFixed(0)}%</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="pt-4 border-t border-slate-800 text-[10px] font-mono text-slate-400 text-center">
        Zero Generative Citation Guarantee — Exact Match Retriever Only
      </div>
    </div>
  );
}
