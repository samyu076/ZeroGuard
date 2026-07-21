import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import JudgeFacingMetricsStrip from './components/JudgeFacingMetricsStrip';
import ZoneStatusStrip from './components/ZoneStatusStrip';
import RiskOverviewCards from './components/RiskOverviewCards';
import BaselineComparisonPanel from './components/BaselineComparisonPanel';
import IncidentReplayPanel from './components/IncidentReplayPanel';
import CounterfactualExplorerPanel from './components/CounterfactualExplorerPanel';
import RoleAwareOutputPanel from './components/RoleAwareOutputPanel';
import GraphVisualizer from './components/GraphVisualizer';
import SensorAnomalyTable from './components/SensorAnomalyTable';
import PermitTimeline from './components/PermitTimeline';
import AnomalyInjectorModal from './components/AnomalyInjectorModal';
import EvidenceExplainerModal from './components/EvidenceExplainerModal';
import ComplianceCitationPanel from './components/ComplianceCitationPanel';
import EmergencyResponseModal from './components/EmergencyResponseModal';
import ScalabilityArchitectureModal from './components/ScalabilityArchitectureModal';
import CommandPaletteModal from './components/CommandPaletteModal';
import LoginModal from './components/LoginModal';
import SettingsModal from './components/SettingsModal';
import ToastNotification from './components/ToastNotification';

import {
  fetchScenarios,
  fetchScenarioById,
  fetchGraphState,
  injectAnomaly
} from './services/api';

export default function App() {
  const [scenarios, setScenarios] = useState([]);
  const [selectedScenarioId, setSelectedScenarioId] = useState('SCEN-2026-0069');
  const [graphState, setGraphState] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isOffline, setIsOffline] = useState(false);

  const [isInjectorOpen, setIsInjectorOpen] = useState(false);
  const [isEmergencyOpen, setIsEmergencyOpen] = useState(false);
  const [isArchitectureOpen, setIsArchitectureOpen] = useState(false);
  const [isCommandPaletteOpen, setIsCommandPaletteOpen] = useState(false);
  const [isLoginOpen, setIsLoginOpen] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);

  const [activeAlertForExplainer, setActiveAlertForExplainer] = useState(null);
  const [activeToast, setActiveToast] = useState(null);

  const triggerToast = (toastObj) => {
    setActiveToast(toastObj);
  };

  const loadInitialData = async () => {
    setLoading(true);
    try {
      const scenarioList = await fetchScenarios();
      setScenarios(scenarioList);
      setIsOffline(false);

      const graph = await fetchGraphState();
      setGraphState(graph);
    } catch (err) {
      console.error('Failed to connect to ZeroGuard backend API:', err);
      setIsOffline(true);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadInitialData();
  }, []);

  useEffect(() => {
    const handleGlobalKeyDown = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setIsCommandPaletteOpen(prev => !prev);
      }
    };
    window.addEventListener('keydown', handleGlobalKeyDown);
    return () => window.removeEventListener('keydown', handleGlobalKeyDown);
  }, []);

  const handleSelectScenario = async (scenarioId) => {
    setSelectedScenarioId(scenarioId);
    setLoading(true);
    try {
      await fetchScenarioById(scenarioId);
      const graph = await fetchGraphState();
      setGraphState(graph);
      setIsOffline(false);
      triggerToast({
        title: 'SCENARIO LOADED',
        message: `Active operational scenario switched to ${scenarioId}.`
      });
    } catch (err) {
      console.error(`Failed to load scenario ${scenarioId}:`, err);
      setIsOffline(true);
      triggerToast({
        title: 'SCENARIO SWITCH ERROR',
        message: err.message,
        type: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleInjectAnomaly = async (sensorId, targetZScore) => {
    try {
      const updatedGraph = await injectAnomaly(sensorId, targetZScore);
      setGraphState(updatedGraph);
      setIsOffline(false);
      triggerToast({
        title: 'ANOMALY OVERRIDE EXECUTED',
        message: `Sensor ${sensorId} override set to Z = ${targetZScore.toFixed(2)}. Re-propagated graph.`
      });
    } catch (err) {
      triggerToast({
        title: 'INJECTION ERROR',
        message: err.message,
        type: 'error'
      });
    }
  };

  const scrollToRoleAction = () => {
    const el = document.getElementById('role-action-section');
    if (el) {
      el.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <div className="min-h-screen bg-[#0D1117] text-[#E6EDF3] flex flex-col font-sans relative">
      <div className="ambient-hero-bg" />

      <ToastNotification
        toast={activeToast}
        onClose={() => setActiveToast(null)}
      />

      {/* Control Room Header Bar */}
      <Header
        scenarios={scenarios}
        selectedScenarioId={selectedScenarioId}
        onSelectScenario={handleSelectScenario}
        overallRiskLevel={graphState?.overall_risk_level || 'NORMAL'}
        overallRiskScore={graphState?.overall_risk_score || 0.0}
        isOffline={isOffline}
        onOpenArchitecture={() => setIsArchitectureOpen(true)}
        onOpenEmergencyReport={() => setIsEmergencyOpen(true)}
        onOpenCommandPalette={() => setIsCommandPaletteOpen(true)}
        onOpenLogin={() => setIsLoginOpen(true)}
        onOpenSettings={() => setIsSettingsOpen(true)}
      />

      {/* C5: Persistent Judge-Facing Metrics Strip */}
      <JudgeFacingMetricsStrip overallRiskLevel={graphState?.overall_risk_level} />

      {/* Persistent Plant Zone Risk Matrix Summary Strip */}
      <ZoneStatusStrip nodes={graphState?.nodes || []} />

      {isOffline && (
        <div className="bg-[#D29922]/15 border-b border-[#D29922]/40 text-[#D29922] px-[24px] py-[12px] text-[12px] font-mono-tech flex items-center justify-between relative z-10">
          <span>
            ⚠️ <strong>SYSTEM OFFLINE</strong>: Unable to reach ZeroGuard FastAPI backend server on port 8000. Start backend server to enable live propagation.
          </span>
          <button
            onClick={loadInitialData}
            className="btn-secondary text-[12px] py-[4px] px-[12px]"
          >
            Retry Connection
          </button>
        </div>
      )}

      {/* Main Control Room Workspace */}
      <main className="flex-1 px-[24px] py-[24px] max-w-7xl w-full mx-auto relative z-10">
        {loading ? (
          <div className="space-y-[24px] py-[24px]">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-[16px]">
              <div className="h-[120px] animate-skeleton rounded-[6px]" />
              <div className="h-[120px] animate-skeleton rounded-[6px]" />
              <div className="h-[120px] animate-skeleton rounded-[6px]" />
              <div className="h-[120px] animate-skeleton rounded-[6px]" />
            </div>
            <div className="h-[480px] animate-skeleton rounded-[6px]" />
          </div>
        ) : (
          <>
            <RiskOverviewCards graphState={graphState} />

            {graphState?.active_alerts?.length > 0 && (
              <div className="mb-[32px] p-[20px] rounded-[6px] bg-[#F85149]/10 border border-[#F85149]/40 flex flex-wrap items-center justify-between gap-[16px] font-mono-tech animate-stagger-5">
                <div>
                  <span className="font-bold text-[#F85149] text-[14px] block uppercase tracking-[0.02em]">
                    COMPOUND_CRITICAL — STATUTORY SAFETY INTERLOCK FIRED
                  </span>
                  <span className="text-[12px] text-[#E6EDF3] mt-[4px] block font-sans">
                    {graphState.active_alerts[0].title}
                  </span>
                </div>
                <div className="flex items-center gap-[12px]">
                  <button
                    onClick={() => setIsEmergencyOpen(true)}
                    className="btn-primary bg-[#F85149] border-[#F85149] text-[#0D1117] hover:bg-[#F85149]/90"
                  >
                    Auto-Generate Incident Report
                  </button>
                  <button
                    onClick={() => setActiveAlertForExplainer(graphState.active_alerts[0])}
                    className="btn-primary"
                  >
                    View Evidence Path
                  </button>
                </div>
              </div>
            )}

            {/* PART C: LIVE INCIDENT REPLAY MODE (With SCADA Baseline Toggle & Action Link) */}
            <IncidentReplayPanel onScrollToAction={scrollToRoleAction} />

            {/* PART B: COUNTERFACTUAL SCENARIO EXPLORER & HISTORICAL PATTERN MATCH */}
            <CounterfactualExplorerPanel />

            {/* C4 & PART B: ROLE-AWARE ACTION DISPATCH */}
            <div id="role-action-section">
              <RoleAwareOutputPanel alert={graphState?.active_alerts?.[0]} />
            </div>

            {/* PHASE 1: BASELINE COMPARISON BENCHMARK PANEL */}
            <BaselineComparisonPanel />

            {/* Spatial Zone Map Visualizer Overlay */}
            <GraphVisualizer
              graphState={graphState}
              onSelectAlert={(alert) => setActiveAlertForExplainer(alert)}
            />

            {/* Telemetry and Permits Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-[16px]">
              <SensorAnomalyTable
                nodes={graphState?.nodes}
                onInjectClick={() => setIsInjectorOpen(true)}
              />
              <PermitTimeline
                nodes={graphState?.nodes}
              />
            </div>

            {/* PHASE 5: STATUTORY COMPLIANCE PANEL */}
            <ComplianceCitationPanel onTriggerToast={triggerToast} />
          </>
        )}
      </main>

      <AnomalyInjectorModal
        isOpen={isInjectorOpen}
        onClose={() => setIsInjectorOpen(false)}
        sensors={(graphState?.nodes || []).filter(n => n.category === 'SENSOR')}
        onInject={handleInjectAnomaly}
      />

      <EvidenceExplainerModal
        alert={activeAlertForExplainer}
        onClose={() => setActiveAlertForExplainer(null)}
      />

      <EmergencyResponseModal
        isOpen={isEmergencyOpen}
        onClose={() => setIsEmergencyOpen(false)}
        alert={graphState?.active_alerts?.[0]}
        onTriggerToast={triggerToast}
      />

      <ScalabilityArchitectureModal
        isOpen={isArchitectureOpen}
        onClose={() => setIsArchitectureOpen(false)}
      />

      <CommandPaletteModal
        isOpen={isCommandPaletteOpen}
        onClose={() => setIsCommandPaletteOpen(false)}
        onSelectCommand={() => {}}
      />

      <LoginModal
        isOpen={isLoginOpen}
        onClose={() => setIsLoginOpen(false)}
        onLoginSuccess={(ops) => triggerToast({ title: 'OPERATOR AUTHENTICATED', message: `Logged in as ${ops.operatorId} (${ops.zone}).` })}
      />

      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        onSaveConfig={(cfg) => triggerToast({ title: 'ENGINE CONFIG SAVED', message: `Updated PageRank α=${cfg.alpha.toFixed(2)}, LEL Threshold Z=${cfg.lelThreshold.toFixed(1)}.` })}
      />

      <footer className="border-t border-[#21262D] py-[16px] px-[24px] text-center text-[12px] font-mono-tech text-[#4A5568] bg-[#0D1117] relative z-10">
        ZERO GUARD INDUSTRIAL RISK INTELLIGENCE v1.0.0 | SPATIO-TEMPORAL PAGERANK & RULE-GUARD ENGINE
      </footer>
    </div>
  );
}
