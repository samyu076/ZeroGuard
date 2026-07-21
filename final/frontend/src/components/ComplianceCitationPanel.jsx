import React, { useState } from 'react';
import { BookOpen, Search, ShieldCheck, ShieldAlert } from 'lucide-react';
import { checkCompliance } from '../services/api';

export default function ComplianceCitationPanel({ onTriggerToast }) {
  const [permitType, setPermitType] = useState('HOT_WORK');
  const [isolationStatus, setIsolationStatus] = useState('SPECTACLE_BLIND_INSTALLED');
  const [gasZScore, setGasZScore] = useState('0.5');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);

  const handleSearch = async (e) => {
    e?.preventDefault();
    setLoading(true);
    try {
      const res = await checkCompliance({
        permitType,
        isolationStatus,
        gasZScore: parseFloat(gasZScore)
      });
      setResults(res);
      setHasSearched(true);

      // PART C5: Trigger Toast Notification
      if (onTriggerToast) {
        onTriggerToast({
          title: 'STATUTORY COMPLIANCE CHECK EVALUATED',
          message: `Evaluated ${res.length} matching statutory citations for ${permitType}.`
        });
      }
    } catch (err) {
      if (onTriggerToast) {
        onTriggerToast({
          title: 'EVALUATION ERROR',
          message: err.message,
          type: 'error'
        });
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="zg-card mb-[32px]">
      <div className="flex items-center justify-between gap-[16px] mb-[16px] border-b border-[#21262D] pb-[16px]">
        <div className="flex items-center gap-[8px]">
          <BookOpen className="w-[20px] h-[20px] text-[#58A6FF]" strokeWidth={1.5} />
          <h3 className="text-[16px] font-bold text-[#E6EDF3] uppercase tracking-[0.02em] font-mono-tech">
            STATUTORY COMPLIANCE & REGULATORY CITATION SEARCH (OISD / FACTORY ACT)
          </h3>
        </div>
      </div>

      <form onSubmit={handleSearch} className="grid grid-cols-1 md:grid-cols-4 gap-[16px] mb-[24px] text-[12px] font-mono-tech">
        <div>
          <label className="block text-[#8B949E] mb-[6px] uppercase tracking-[0.02em]">Permit Type</label>
          <select
            value={permitType}
            onChange={(e) => setPermitType(e.target.value)}
            className="w-full p-[8px] bg-[#0D1117] border border-[#21262D] rounded-[4px] text-[#E6EDF3] focus:outline-none"
          >
            <option value="HOT_WORK">HOT_WORK</option>
            <option value="VESSEL_ENTRY">VESSEL_ENTRY</option>
            <option value="LINE_BREAK">LINE_BREAK</option>
            <option value="HEIGHT_WORK">HEIGHT_WORK</option>
          </select>
        </div>

        <div>
          <label className="block text-[#8B949E] mb-[6px] uppercase tracking-[0.02em]">Isolation Status</label>
          <select
            value={isolationStatus}
            onChange={(e) => setIsolationStatus(e.target.value)}
            className="w-full p-[8px] bg-[#0D1117] border border-[#21262D] rounded-[4px] text-[#E6EDF3] focus:outline-none"
          >
            <option value="SPECTACLE_BLIND_INSTALLED">SPECTACLE_BLIND_INSTALLED (Compliant)</option>
            <option value="VALVE_CLOSED_ONLY">VALVE_CLOSED_ONLY (Violation)</option>
          </select>
        </div>

        <div>
          <label className="block text-[#8B949E] mb-[6px] uppercase tracking-[0.02em]">Ambient Gas Z-Score</label>
          <input
            type="number"
            step="0.1"
            value={gasZScore}
            onChange={(e) => setGasZScore(e.target.value)}
            className="w-full p-[8px] bg-[#0D1117] border border-[#21262D] rounded-[4px] text-[#E6EDF3] focus:outline-none"
          />
        </div>

        <div className="flex items-end">
          <button
            type="submit"
            disabled={loading}
            className="btn-primary w-full py-[8px]"
          >
            <Search className="w-[16px] h-[16px]" strokeWidth={1.5} /> {loading ? 'Evaluating...' : 'Evaluate Compliance'}
          </button>
        </div>
      </form>

      {/* Results Display */}
      {hasSearched && (
        <div className="space-y-[16px] font-mono-tech text-[12px]">
          {loading ? (
            <div className="p-[24px] animate-skeleton rounded-[4px] text-center text-[#8B949E]">
              Evaluating statutory requirements...
            </div>
          ) : results.length === 0 ? (
            <div className="p-[16px] bg-[#0D1117] text-[#8B949E] text-center rounded-[4px] border border-[#21262D]">
              No statutory citations matched query criteria.
            </div>
          ) : (
            results.map((c) => (
              <div
                key={c.citation_id}
                className={`p-[16px] rounded-[4px] border transition-colors ${
                  c.compliance_status === 'NON_COMPLIANT'
                    ? 'bg-[#F85149]/10 border-[#F85149]/40 hover:border-[#F85149]'
                    : 'bg-[#2EA043]/10 border-[#2EA043]/40 hover:border-[#2EA043]'
                }`}
              >
                <div className="flex items-center justify-between gap-[8px] mb-[8px]">
                  <span className="font-bold text-[#E6EDF3]">
                    {c.document_id} {c.section_number}: {c.title}
                  </span>
                  <span className={c.compliance_status === 'NON_COMPLIANT' ? 'badge-critical px-[8px] py-[4px]' : 'badge-safe px-[8px] py-[4px]'}>
                    {c.compliance_status}
                  </span>
                </div>
                <p className="text-[12px] text-[#E6EDF3] font-sans mt-[4px] leading-[1.4]">
                  "{c.matched_passage}"
                </p>
                <div className="text-[12px] text-[#8B949E] mt-[8px]">
                  Relevance Score: {(c.relevance_score * 100).toFixed(0)}% | Standard: {c.standard_name}
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
