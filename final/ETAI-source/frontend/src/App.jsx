import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import RiskOverviewCards from './components/RiskOverviewCards';
import GraphVisualizer from './components/GraphVisualizer';
import SensorAnomalyTable from './components/SensorAnomalyTable';
import PermitTimeline from './components/PermitTimeline';
import EvidenceExplainerModal from './components/EvidenceExplainerModal';
import ComplianceCitationPanel from './components/ComplianceCitationPanel';
import AnomalyInjectorModal from './components/AnomalyInjectorModal';
import { fetchGraphState, fetchEvidence } from './services/api';
import { AlertTriangle, WifiOff } from 'lucide-react';

export default function App() {
  const [graphState, setGraphState] = useState(null);
  const [selectedAlertId, setSelectedAlertId] = useState(null);
  const [evidenceData, setEvidenceData] = useState(null);
  const [isComplianceOpen, setIsComplianceOpen] = useState(false);
  const [isInjectorOpen, setIsInjectorOpen] = useState(false);
  
  // Real-time connection & error state management (Resolves High #4 & High #6)
  const [isOffline, setIsOffline] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(null);

  useEffect(() => {
    // Initial fetch on mount
    loadGraph();

    // Active real-time polling every 3 seconds (Resolves High #4)
    const interval = setInterval(() => {
      loadGraph();
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  const loadGraph = async () => {
    try {
      const data = await fetchGraphState();
      setGraphState(data);
      setIsOffline(false);
      setLastUpdated(new Date().toLocaleTimeString());
    } catch (err) {
      console.error('API Connect Error:', err);
      setIsOffline(true);
      // Clear stale state on connection failure to prevent showing fake data
      setGraphState(null);
    }
  };

  const handleSelectAlert = async (alertId) => {
    setSelectedAlertId(alertId);
    setEvidenceData(null);
    try {
      const evidence = await fetchEvidence(alertId);
      setEvidenceData(evidence);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="min-h-screen bg-[#0B0F19] text-slate-100 flex flex-col">
      <Header
        onOpenInjector={() => setIsInjectorOpen(true)}
        onOpenCompliance={() => setIsComplianceOpen(true)}
      />

      {/* Prominent Offline / API Connection Error Banner (Resolves High #6) */}
      {isOffline && (
        <div className="bg-rose-600 text-white font-mono text-xs py-2 px-6 flex items-center justify-center space-x-2 shadow-lg z-50">
          <WifiOff className="w-4 h-4 animate-bounce" />
          <span className="font-bold">API GATEWAY OFFLINE — UNABLE TO CONNECT TO BACKEND SERVER (localhost:8000)</span>
        </div>
      )}

      <main className="flex-1 p-6 space-y-6 max-w-7xl w-full mx-auto">
        <RiskOverviewCards graphState={graphState} isOffline={isOffline} />
        
        {isOffline ? (
          <div className="glass-panel p-12 rounded-2xl border border-rose-500/40 text-center space-y-3">
            <div className="p-3 bg-rose-500/10 text-rose-400 rounded-xl inline-block">
              <AlertTriangle className="w-8 h-8 mx-auto" />
            </div>
            <h3 className="text-lg font-bold text-white">Graph Engine Connection Failure</h3>
            <p className="text-xs font-mono text-slate-400 max-w-md mx-auto">
              The control room cannot poll active risk metrics. Please ensure FastAPI server (`python -m uvicorn app.main:app`) is running.
            </p>
          </div>
        ) : (
          <>
            <GraphVisualizer
              graphState={graphState}
              onSelectAlert={handleSelectAlert}
            />

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <SensorAnomalyTable graphState={graphState} />
              <PermitTimeline graphState={graphState} />
            </div>
          </>
        )}
      </main>

      <footer className="border-t border-slate-800/80 py-4 px-6 flex items-center justify-between text-xs font-mono text-slate-500">
        <span>ZeroGuard Industrial Platform Monorepo • Real-Time Polling Active (3s)</span>
        <span>{lastUpdated ? `Last Sync: ${lastUpdated}` : 'Syncing...'}</span>
      </footer>

      {/* Modals & Drawers */}
      <EvidenceExplainerModal
        alertId={selectedAlertId}
        evidenceData={evidenceData}
        onClose={() => setSelectedAlertId(null)}
      />

      <ComplianceCitationPanel
        isOpen={isComplianceOpen}
        onClose={() => setIsComplianceOpen(false)}
      />

      <AnomalyInjectorModal
        isOpen={isInjectorOpen}
        onClose={() => setIsInjectorOpen(false)}
        onAnomalyInjected={(updatedGraph) => setGraphState(updatedGraph)}
      />
    </div>
  );
}
