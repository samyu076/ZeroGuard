import React, { useState, useEffect } from 'react';
import { Search, Command, Layers, FileText, Cpu, Clock, Sliders, ShieldAlert, X } from 'lucide-react';

const PALETTE_COMMANDS = [
  { id: 'action-replay', label: 'Play Visakhapatnam Incident Replay Mode', category: 'Actions', icon: Clock },
  { id: 'action-compliance', label: 'Evaluate OISD / Factory Act / DGMS Statutory Compliance', category: 'Actions', icon: FileText },
  { id: 'action-anomaly', label: 'Inject Live Sensor Anomaly Z-Score Override', category: 'Actions', icon: Sliders },
  { id: 'action-architecture', label: 'View Enterprise Multi-Plant Scalability Architecture Roadmap', category: 'Actions', icon: Cpu },
  { id: 'scen-0069', label: 'Load SCEN-2026-0069 [COMPOUND_CRITICAL — Zone E]', category: 'Scenarios', icon: ShieldAlert },
  { id: 'scen-0030', label: 'Load SCEN-2026-0030 [WARNING — Zone B]', category: 'Scenarios', icon: ShieldAlert },
  { id: 'zone-e', label: 'Navigate to Zone E (Main Control Room & Substation)', category: 'Zones', icon: Layers },
  { id: 'zone-a', label: 'Navigate to Zone A (Crude Distillation Unit)', category: 'Zones', icon: Layers },
  { id: 'zone-b', label: 'Navigate to Zone B (Hydrocracker Feed Pump Station)', category: 'Zones', icon: Layers },
];

export default function CommandPaletteModal({ isOpen, onClose, onSelectCommand }) {
  const [query, setQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);

  const filteredCommands = PALETTE_COMMANDS.filter(cmd =>
    cmd.label.toLowerCase().includes(query.toLowerCase()) ||
    cmd.category.toLowerCase().includes(query.toLowerCase())
  );

  useEffect(() => {
    setSelectedIndex(0);
  }, [query]);

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (!isOpen) return;

      if (e.key === 'ArrowDown') {
        e.preventDefault();
        setSelectedIndex(prev => (prev + 1) % Math.max(filteredCommands.length, 1));
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        setSelectedIndex(prev => (prev - 1 + filteredCommands.length) % Math.max(filteredCommands.length, 1));
      } else if (e.key === 'Enter') {
        e.preventDefault();
        if (filteredCommands[selectedIndex]) {
          onSelectCommand(filteredCommands[selectedIndex]);
          onClose();
        }
      } else if (e.key === 'Escape') {
        onClose();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, filteredCommands, selectedIndex, onSelectCommand, onClose]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/75 backdrop-blur-sm z-50 flex items-start justify-center pt-[100px] px-[16px]">
      <div className="zg-modal-panel max-w-xl w-full relative border border-[#58A6FF]/40 shadow-2xl overflow-hidden p-0">
        {/* Search Input Bar */}
        <div className="p-[16px] border-b border-[#21262D] flex items-center gap-[12px] bg-[#0D1117]">
          <Search className="w-[18px] h-[18px] text-[#58A6FF]" strokeWidth={1.5} />
          <input
            type="text"
            autoFocus
            placeholder="Type a command, scenario ID, or plant zone (e.g. Zone E, SCEN-0069)..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full bg-transparent text-[#E6EDF3] text-[13px] font-mono-tech focus:outline-none placeholder:text-[#4A5568]"
          />
          <div className="flex items-center gap-[4px] px-[6px] py-[2px] rounded bg-[#161B22] border border-[#21262D] text-[#8B949E] text-[10px] font-mono-tech">
            <span>ESC</span>
          </div>
        </div>

        {/* Command List */}
        <div className="max-h-[340px] overflow-y-auto p-[8px] space-y-[4px]">
          {filteredCommands.length === 0 ? (
            <div className="p-[16px] text-center text-[#4A5568] font-mono-tech text-[12px]">
              No matching commands or plant zones found.
            </div>
          ) : (
            filteredCommands.map((cmd, idx) => {
              const Icon = cmd.icon;
              const isSelected = idx === selectedIndex;

              return (
                <div
                  key={cmd.id}
                  onClick={() => {
                    onSelectCommand(cmd);
                    onClose();
                  }}
                  className={`p-[10px] rounded-[4px] flex items-center justify-between gap-[12px] cursor-pointer font-mono-tech text-[12px] transition-all relative ${
                    isSelected ? 'bg-[#1C2128] text-[#E6EDF3] border-l-2 border-[#58A6FF]' : 'text-[#8B949E] hover:bg-[#161B22]'
                  }`}
                >
                  <div className="flex items-center gap-[10px]">
                    <Icon className={`w-[16px] h-[16px] ${isSelected ? 'text-[#58A6FF]' : 'text-[#8B949E]'}`} strokeWidth={1.5} />
                    <span>{cmd.label}</span>
                  </div>
                  <span className="text-[10px] uppercase text-[#4A5568] px-[6px] py-[2px] bg-[#0D1117] border border-[#21262D] rounded">
                    {cmd.category}
                  </span>
                </div>
              );
            })
          )}
        </div>

        {/* Footer info */}
        <div className="p-[10px] px-[16px] border-t border-[#21262D] bg-[#0D1117] text-[11px] font-mono-tech text-[#4A5568] flex justify-between">
          <span>Use ↑ ↓ to navigate</span>
          <span>↵ to select</span>
        </div>
      </div>
    </div>
  );
}
