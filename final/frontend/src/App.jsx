import React, { useState, useEffect } from 'react';
import { 
  Activity, ShieldAlert, Cpu, FileText, Command, User, Settings, 
  Layers, Clock, Sliders, LogIn, Lock, ArrowRight, UserCheck, Search 
} from 'lucide-react';
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
import SettingsModal from './components/SettingsModal';
import ToastNotification from './components/ToastNotification';

import {
  fetchScenarios,
  fetchScenarioById,
  fetchGraphState,
  injectAnomaly
} from './services/api';

export default function App() {
  // Login / Auth State
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [operatorId, setOperatorId] = useState('OP-REF-2026');
  const [passcode, setPasscode] = useState('••••••••');
  const [assignedZone, setAssignedZone] = useState('Zone-E-Control');

  // Dashboard state
  const [activeTab, setActiveTab] = useState('dashboard'); // 'dashboard', 'spatial-map', 'replay', 'telemetry', 'statutory'
  const [scenarios, setScenarios] = useState([]);
  const [selectedScenarioId, setSelectedScenarioId] = useState('SCEN-2026-0069');
  const [graphState, setGraphState] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isOffline, setIsOffline] = useState(false);

  const [isInjectorOpen, setIsInjectorOpen] = useState(false);
  const [isEmergencyOpen, setIsEmergencyOpen] = useState(false);
  const [isArchitectureOpen, setIsArchitectureOpen] = useState(false);
  const [isCommandPaletteOpen, setIsCommandPaletteOpen] = useState(false);
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
    if (isAuthenticated) {
      loadInitialData();
    }
  }, [isAuthenticated]);

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

  const handleLoginSubmit = (e) => {
    e.preventDefault();
    setIsAuthenticated(true);
    triggerToast({
      title: 'OPERATOR AUTHENTICATED',
      message: `Access granted for Operator ${operatorId} in ${assignedZone}.`
    });
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    setActiveTab('dashboard');
    triggerToast({
      title: 'SESSION TERMINATED',
      message: 'Operator session safely closed.'
    });
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-[#0D1117] flex items-center justify-center p-[24px] relative">
        <div className="absolute inset-0 pointer-events-none bg-[radial-gradient(circle_at_center,rgba(255,98,0,0.06)_0%,transparent_70%)]" />
        
        <div className="zg-modal-panel max-w-md w-full border-[#FF6200]/50 relative z-10 p-[32px] space-y-[24px]">
          <div className="text-center space-y-[8px]">
            <div className="inline-flex p-[12px] bg-[#FF6200]/10 border border-[#FF6200]/30 rounded-[6px]">
              <ShieldAlert className="w-[32px] h-[32px] text-[#FF6200]" strokeWidth={1.5} />
            </div>
            <h2 className="text-[20px] font-bold text-[#E6EDF3] tracking-[0.02em] font-mono-tech uppercase">
              ZERO<span className="text-[#FF6200]">GUARD</span> CONTROL SYSTEM
            </h2>
            <p className="text-[12px] text-[#8B949E] font-sans">
              Enter operator credentials to access risk intelligence console.
            </p>
          </div>

          <form onSubmit={handleLoginSubmit} className="space-y-[16px] text-[12px] font-mono-tech">
            <div>
              <label className="block text-[#8B949E] mb-[6px] uppercase tracking-[0.02em]">Operator Identification</label>
              <input
                type="text"
                required
                value={operatorId}
                onChange={(e) => setOperatorId(e.target.value)}
                className="w-full px-[12px] py-[8px] bg-[#0D1117] border border-[#21262D] rounded-[4px] text-[#E6EDF3] focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-[#8B949E] mb-[6px] uppercase tracking-[0.02em]">Refinery Keycode</label>
              <input
                type="password"
                required
                value={passcode}
                onChange={(e) => setPasscode(e.target.value)}
                className="w-full px-[12px] py-[8px] bg-[#0D1117] border border-[#21262D] rounded-[4px] text-[#E6EDF3] focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-[#8B949E] mb-[6px] uppercase tracking-[0.02em]">Assigned Control Substation</label>
              <select
                value={assignedZone}
                onChange={(e) => setAssignedZone(e.target.value)}
                className="w-full p-[8px] bg-[#0D1117] border border-[#21262D] rounded-[4px] text-[#E6EDF3] focus:outline-none"
              >
                <option value="Zone-E-Control">Zone E: Main Control Room & Substation</option>
                <option value="Zone-A-CDU">Zone A: Crude Distillation Unit</option>
                <option value="Zone-B-Pump">Zone B: Hydrocracker Pump Station</option>
                <option value="Zone-C-Tanks">Zone C: Hydrocarbon Tank Farm</option>
              </select>
            </div>

            <button
              type="submit"
              className="btn-primary w-full py-[10px] flex items-center justify-center gap-[8px]"
            >
              <LogIn className="w-[16px] h-[16px]" strokeWidth={1.5} /> Establish Secure Session
            </button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0D1117] text-[#E6EDF3] flex flex-col font-sans relative">
      <div className="ambient-hero-bg" />

      <ToastNotification
        toast={activeToast}
        onClose={() => setActiveToast(null)}
      />

      {/* Top Header Banner matching Puffin Navbar Reference Layout */}
      <header className="thick-header-banner flex items-center justify-between px-[32px] py-[16px]">
        {/* Left: Brand Logo */}
        <div className="flex items-center gap-[10px]">
          <div className="p-[6px] bg-[#FF6200]/10 border border-[#FF6200]/30 rounded-[6px]">
            <ShieldAlert className="w-[22px] h-[22px] text-[#FF6200]" strokeWidth={1.5} />
          </div>
          <span className="font-bold text-[20px] tracking-[0.03em] text-[#E6EDF3] font-mono-tech uppercase">
            ZERO<span className="text-[#FF6200]">GUARD</span>
          </span>
        </div>

        {/* Right Side Group: Right-Aligned Navigation Links + Action CTA */}
        <div className="flex items-center gap-[32px]">
          {/* Navigation Links (Right Side Layout) */}
          <nav className="hidden lg:flex items-center gap-[20px] text-[13px] font-mono-tech font-semibold">
            <button
              onClick={() => setActiveTab('dashboard')}
              className={`transition-colors py-[6px] px-[4px] relative ${
                activeTab === 'dashboard' ? 'text-[#FF6200] font-bold' : 'text-[#8B949E] hover:text-[#E6EDF3]'
              }`}
            >
              Overview
              {activeTab === 'dashboard' && (
                <span className="absolute bottom-0 left-0 right-0 h-[2px] bg-[#FF6200] rounded-full" />
              )}
            </button>
            <button
              onClick={() => setActiveTab('spatial-map')}
              className={`transition-colors py-[6px] px-[4px] relative ${
                activeTab === 'spatial-map' ? 'text-[#FF6200] font-bold' : 'text-[#8B949E] hover:text-[#E6EDF3]'
              }`}
            >
              Spatial Risk Map
              {activeTab === 'spatial-map' && (
                <span className="absolute bottom-0 left-0 right-0 h-[2px] bg-[#FF6200] rounded-full" />
              )}
            </button>
            <button
              onClick={() => setActiveTab('replay')}
              className={`transition-colors py-[6px] px-[4px] relative ${
                activeTab === 'replay' ? 'text-[#FF6200] font-bold' : 'text-[#8B949E] hover:text-[#E6EDF3]'
              }`}
            >
              Incident Replay
              {activeTab === 'replay' && (
                <span className="absolute bottom-0 left-0 right-0 h-[2px] bg-[#FF6200] rounded-full" />
              )}
            </button>
            <button
              onClick={() => setActiveTab('telemetry')}
              className={`transition-colors py-[6px] px-[4px] relative ${
                activeTab === 'telemetry' ? 'text-[#FF6200] font-bold' : 'text-[#8B949E] hover:text-[#E6EDF3]'
              }`}
            >
              Telemetry & Permits
              {activeTab === 'telemetry' && (
                <span className="absolute bottom-0 left-0 right-0 h-[2px] bg-[#FF6200] rounded-full" />
              )}
            </button>
            <button
              onClick={() => setActiveTab('statutory')}
              className={`transition-colors py-[6px] px-[4px] relative ${
                activeTab === 'statutory' ? 'text-[#FF6200] font-bold' : 'text-[#8B949E] hover:text-[#E6EDF3]'
              }`}
            >
              Statutory Compliance
              {activeTab === 'statutory' && (
                <span className="absolute bottom-0 left-0 right-0 h-[2px] bg-[#FF6200] rounded-full" />
              )}
            </button>
          </nav>

          {/* Action Dropdown & Primary CTA Button */}
          <div className="flex items-center gap-[12px]">
            {/* Scenario Selection Dropdown */}
            <div className="relative hidden md:block">
              <Search className="w-[14px] h-[14px] text-[#8B949E] absolute left-[10px] top-1/2 -translate-y-1/2" strokeWidth={1.5} />
              <select
                value={selectedScenarioId || ''}
                onChange={(e) => handleSelectScenario(e.target.value)}
                disabled={isOffline}
                className="pl-[30px] pr-[16px] py-[6px] bg-[#0D1117] border border-[#21262D] rounded-[4px] text-[11px] font-mono-tech text-[#E6EDF3] disabled:opacity-50 min-w-[180px]"
              >
                <option value="" disabled>Select Scenario...</option>
                {scenarios.map((s) => (
                  <option key={s.scenario_id} value={s.scenario_id}>
                    {s.scenario_id} [{s.ground_truth_label || 'SCENARIO'}]
                  </option>
                ))}
              </select>
            </div>

            {/* Command Palette Trigger ⌘K */}
            <button
              onClick={() => setIsCommandPaletteOpen(true)}
              className="btn-secondary py-[6px] px-[10px] flex items-center gap-[4px]"
              title="Open Command Palette (⌘K)"
            >
              <Command className="w-[13px] h-[13px] text-[#58A6FF]" strokeWidth={1.5} />
              <span className="font-mono-tech text-[11px] font-bold">⌘K</span>
            </button>

            {/* Primary Action CTA Button (Rounded like Get a Quote) */}
            <button
              onClick={() => setIsEmergencyOpen(true)}
              className="btn-primary rounded-full px-[18px] py-[8px] text-[12px] font-mono-tech flex items-center gap-[6px] shadow-lg shadow-[#FF6200]/20"
            >
              <FileText className="w-[14px] h-[14px]" strokeWidth={1.5} /> Emergency Report
            </button>

            <button
              onClick={() => setIsSettingsOpen(true)}
              className="btn-secondary py-[6px] px-[8px]"
              title="Engine Settings"
            >
              <Settings className="w-[14px] h-[14px]" strokeWidth={1.5} />
            </button>

            <button
              onClick={handleLogout}
              className="btn-secondary py-[6px] px-[10px] text-[#F85149] border-[#F85149]/30 hover:bg-[#F85149]/10"
              title="Close Session"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Persistent Judge-Facing Metrics Strip */}
      <JudgeFacingMetricsStrip overallRiskLevel={graphState?.overall_risk_level} />

      {/* Persistent Plant Zone Risk Matrix Summary Strip */}
      <ZoneStatusStrip nodes={graphState?.nodes || []} />

      {/* Main Workspace with Clean Tabbed Segregation */}
      <main className="flex-1 px-[24px] py-[32px] max-w-7xl w-full mx-auto relative z-10">
        {loading ? (
          <div className="space-y-[24px]">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-[16px]">
              <div className="h-[120px] animate-skeleton rounded-[6px]" />
              <div className="h-[120px] animate-skeleton rounded-[6px]" />
              <div className="h-[120px] animate-skeleton rounded-[6px]" />
              <div className="h-[120px] animate-skeleton rounded-[6px]" />
            </div>
            <div className="h-[400px] animate-skeleton rounded-[6px]" />
          </div>
        ) : (
          <div className="tab-content-active">
            {/* TAB 1: OVERVIEW */}
            {activeTab === 'dashboard' && (
              <div className="space-y-[24px]">
                <RiskOverviewCards graphState={graphState} />

                {/* Compound Risk Fired Interlock Banner */}
                {graphState?.active_alerts?.length > 0 && (
                  <div className="p-[20px] rounded-[6px] bg-[#F85149]/10 border border-[#F85149]/40 flex flex-wrap items-center justify-between gap-[16px] font-mono-tech">
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
                        className="btn-primary"
                      >
                        Auto-Generate Incident Report
                      </button>
                      <button
                        onClick={() => setActiveAlertForExplainer(graphState.active_alerts[0])}
                        className="btn-secondary"
                      >
                        View Causal Path
                      </button>
                    </div>
                  </div>
                )}

                {/* Baseline Comparison Summary Panel */}
                <BaselineComparisonPanel />
              </div>
            )}

            {/* TAB 2: SPATIAL RISK MAP */}
            {activeTab === 'spatial-map' && (
              <div className="space-y-[24px]">
                <GraphVisualizer
                  graphState={graphState}
                  onSelectAlert={(alert) => setActiveAlertForExplainer(alert)}
                />
              </div>
            )}

            {/* TAB 3: INCIDENT REPLAY & EXPLORER */}
            {activeTab === 'replay' && (
              <div className="space-y-[24px]">
                <IncidentReplayPanel onScrollToAction={() => setActiveTab('telemetry')} />
                <CounterfactualExplorerPanel />
              </div>
            )}

            {/* TAB 4: TELEMETRY & PERMITS */}
            {activeTab === 'telemetry' && (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-[16px]">
                <SensorAnomalyTable
                  nodes={graphState?.nodes}
                  onInjectClick={() => setIsInjectorOpen(true)}
                />
                <PermitTimeline
                  nodes={graphState?.nodes}
                />
              </div>
            )}

            {/* TAB 5: STATUTORY STANDARDS */}
            {activeTab === 'statutory' && (
              <div className="space-y-[24px]">
                <ComplianceCitationPanel onTriggerToast={triggerToast} />
              </div>
            )}
          </div>
        )}
      </main>

      {/* Modals */}
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
        onSelectCommand={(cmd) => {
          if (cmd.id.startsWith('scen-')) {
            handleSelectScenario('SCEN-2026-0069');
          } else {
            setActiveTab(cmd.id.includes('replay') ? 'replay' : 'spatial-map');
          }
        }}
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
