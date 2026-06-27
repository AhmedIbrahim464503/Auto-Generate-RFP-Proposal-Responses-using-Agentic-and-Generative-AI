'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  LayoutDashboard,
  FileText,
  Workflow,
  BookOpen,
  CheckSquare,
  BarChart3,
  Sliders,
  Settings,
  ShieldAlert,
  Activity,
  LogOut
} from 'lucide-react';

import UploadCenter from '../components/UploadCenter';
import DocumentLibrary from '../components/DocumentLibrary';
import StructureExplorer from '../components/StructureExplorer';
import RequirementExplorer from '../components/RequirementExplorer';
import DepartmentReview from '../components/DepartmentReview';
import ExecutiveDecisionDashboard from '../components/ExecutiveDecisionDashboard';
import PlanningWorkspace from '../components/PlanningWorkspace';
import KnowledgeWorkspace from '../components/KnowledgeWorkspace';
import ProposalWorkspace from '../components/ProposalWorkspace';
import NeuralNetwork3D from '../components/NeuralNetwork3D';
import WorkflowGraph from '../components/WorkflowGraph';
import WorkflowMonitor from '../components/WorkflowMonitor';

export default function LandingPage() {
  const [activeTab, setActiveTab] = useState<string>('command_center');
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [selectedDocId, setSelectedDocId] = useState<string | null>(null);
  const [notifications, setNotifications] = useState<string[]>([
    'System initialization completed successfully.',
    'Model adapters connection checked and healthy.'
  ]);

  const handleUploadSuccess = () => {
    setRefreshTrigger((prev) => prev + 1);
    setNotifications((prev) => ['New document successfully uploaded and registered.', ...prev]);
  };

  const navItems = [
    { id: 'command_center', label: 'Command Center', icon: LayoutDashboard },
    { id: 'proposal_workspace', label: 'Proposal Writer', icon: FileText, disabled: !selectedDocId },
    { id: 'workflow', label: 'Workflow Monitor', icon: Workflow, disabled: !selectedDocId },
    { id: 'knowledge', label: 'Knowledge Base', icon: BookOpen },
    { id: 'review', label: 'Review Gates', icon: CheckSquare, disabled: !selectedDocId },
    { id: 'analytics', label: 'Observability & Cost', icon: BarChart3, disabled: !selectedDocId },
    { id: 'ai_admin', label: 'AI Platform Registry', icon: Sliders },
    { id: 'settings', label: 'Settings', icon: Settings }
  ];

  return (
    <div className="flex min-h-screen bg-slate-950 text-slate-100 font-sans antialiased overflow-hidden">
      {/* Sidebar Navigation */}
      <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col shrink-0">
        {/* Title logo */}
        <div className="p-6 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded bg-violet-500 animate-pulse" />
            <h1 className="text-sm font-bold tracking-wider uppercase bg-gradient-to-r from-violet-400 to-indigo-400 bg-clip-text text-transparent">
              SPS Capture
            </h1>
          </div>
          <span className="text-[9px] font-mono text-slate-500 block mt-1.5 uppercase">
            AI Proposal Management
          </span>
        </div>

        {/* Navigation list */}
        <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                disabled={item.disabled}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-semibold tracking-wide transition-all ${
                  isActive
                    ? 'bg-violet-600 text-white shadow-md'
                    : item.disabled
                    ? 'text-slate-600 cursor-not-allowed opacity-40'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
                }`}
              >
                <Icon className="w-4 h-4 shrink-0" />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Sidebar Footer */}
        <div className="p-4 border-t border-slate-800 text-[10px] text-slate-500 font-mono space-y-1">
          <div>BU: SPS Enterprise</div>
          <div>Env: Development</div>
          <div className="text-emerald-400 font-bold flex items-center gap-1.5 mt-2">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            SECURE_CONNECTION
          </div>
        </div>
      </aside>

      {/* Main Workspace Frame */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top Header */}
        <header className="h-16 border-b border-slate-800 bg-slate-900/50 backdrop-blur-md px-8 flex justify-between items-center z-10">
          <div>
            <span className="text-[10px] font-mono text-violet-400 uppercase tracking-widest">
              Capture Console
            </span>
            <h2 className="text-sm font-bold text-white uppercase tracking-wider mt-0.5">
              {navItems.find((n) => n.id === activeTab)?.label} Workspace
            </h2>
          </div>

          <div className="flex items-center gap-4 text-xs">
            {selectedDocId && (
              <div className="px-3 py-1 bg-slate-800 border border-slate-700 rounded text-slate-300 font-mono text-[10px]">
                Active ID: {selectedDocId.slice(0, 8)}...
              </div>
            )}
            <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
          </div>
        </header>

        {/* Content Workspace Scroll Frame */}
        <main className="flex-1 overflow-y-auto p-8 relative">
          <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808003_1px,transparent_1px),linear-gradient(to_bottom,#80808003_1px,transparent_1px)] bg-[size:32px_32px] pointer-events-none" />

          <div className="max-w-6xl mx-auto space-y-8 relative z-10">
            <AnimatePresence mode="wait">
              <motion.div
                key={activeTab}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.2 }}
              >
                {/* 1. Command Center */}
                {activeTab === 'command_center' && (
                  <div className="space-y-8">
                    {/* 3D neural grid element */}
                    <NeuralNetwork3D />

                    {/* Stats Highlights Widgets */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                      <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-xl flex items-center justify-between">
                        <div>
                          <span className="text-[10px] font-mono text-slate-400 uppercase">Registered Documents</span>
                          <h3 className="text-2xl font-bold text-white mt-1">4 Active</h3>
                        </div>
                        <Activity className="w-8 h-8 text-violet-400 opacity-60" />
                      </div>
                      <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-xl flex items-center justify-between">
                        <div>
                          <span className="text-[10px] font-mono text-slate-400 uppercase">System Latency</span>
                          <h3 className="text-2xl font-bold text-white mt-1">2.4s Avg</h3>
                        </div>
                        <Workflow className="w-8 h-8 text-emerald-400 opacity-60" />
                      </div>
                      <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-xl flex items-center justify-between">
                        <div>
                          <span className="text-[10px] font-mono text-slate-400 uppercase">AI Agents Health</span>
                          <h3 className="text-2xl font-bold text-white mt-1">100% Healthy</h3>
                        </div>
                        <ShieldAlert className="w-8 h-8 text-indigo-400 opacity-60" />
                      </div>
                    </div>

                    <UploadCenter onUploadSuccess={handleUploadSuccess} />
                    <DocumentLibrary refreshTrigger={refreshTrigger} onSelectDocument={setSelectedDocId} />

                    {/* Live Notifications Feed */}
                    <div className="bg-slate-900/40 border border-slate-800 rounded-xl p-6">
                      <h4 className="text-xs font-bold text-white font-mono uppercase tracking-wider mb-4 border-b border-slate-800 pb-2">
                        Execution Event Logs Feed
                      </h4>
                      <div className="space-y-2 max-h-40 overflow-y-auto pr-2">
                        {notifications.map((n, i) => (
                          <div key={i} className="text-xs font-mono text-slate-400 py-1 border-b border-slate-900 last:border-0">
                            <span className="text-violet-400 mr-2">[{new Date().toLocaleTimeString()}]</span> {n}
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}

                {/* 2. Proposal Workspace */}
                {activeTab === 'proposal_workspace' && selectedDocId && (
                  <ProposalWorkspace documentId={selectedDocId} />
                )}

                {/* 3. Workflow Tab */}
                {activeTab === 'workflow' && selectedDocId && (
                  <div className="space-y-8">
                    <WorkflowGraph currentStep="qualification_approval_gate" executionStatus="paused" />
                    <WorkflowMonitor proposalId={selectedDocId} />
                  </div>
                )}

                {/* 4. Knowledge Base */}
                {activeTab === 'knowledge' && (
                  <KnowledgeWorkspace />
                )}

                {/* 5. Review Gates */}
                {activeTab === 'review' && selectedDocId && (
                  <div className="space-y-8">
                    <RequirementExplorer documentId={selectedDocId} />
                    <DepartmentReview documentId={selectedDocId} />
                    <ExecutiveDecisionDashboard documentId={selectedDocId} />
                    <PlanningWorkspace documentId={selectedDocId} />
                  </div>
                )}

                {/* 6. Analytics */}
                {activeTab === 'analytics' && selectedDocId && (
                  <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-6">
                    <div>
                      <h3 className="text-base font-bold text-white">Observability & Costs Breakdown</h3>
                      <p className="text-slate-400 text-xs mt-1">
                        Live visualization of token costs, node latencies, and department execution timelines.
                      </p>
                    </div>
                    {/* Recharts placeholder / styled grid */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 min-h-[300px]">
                      <div className="bg-slate-950 border border-slate-800 p-4 rounded-lg flex flex-col justify-center items-center text-center">
                        <span className="text-xs font-semibold text-slate-400">Execution Latencies per Stage</span>
                        <div className="w-full mt-4 h-32 flex items-end justify-between px-6 gap-2">
                          <div className="w-8 bg-violet-600 h-1/4 rounded-t" />
                          <div className="w-8 bg-violet-600 h-2/5 rounded-t" />
                          <div className="w-8 bg-violet-600 h-3/5 rounded-t" />
                          <div className="w-8 bg-violet-600 h-4/5 rounded-t" />
                          <div className="w-8 bg-emerald-500 h-1/5 rounded-t" />
                          <div className="w-8 bg-violet-600 h-full rounded-t" />
                        </div>
                        <div className="flex justify-between w-full px-6 text-[8px] text-slate-500 mt-2 font-mono">
                          <span>Intake</span>
                          <span>Review</span>
                          <span>Qual</span>
                          <span>Planning</span>
                          <span>Retrieval</span>
                          <span>Gen</span>
                        </div>
                      </div>

                      <div className="bg-slate-950 border border-slate-800 p-4 rounded-lg flex flex-col justify-center items-center text-center">
                        <span className="text-xs font-semibold text-slate-400">Token Cost Accumulation ($)</span>
                        <div className="w-full mt-4 h-32 flex items-center justify-center relative">
                          {/* Circle chart */}
                          <div className="w-24 h-24 rounded-full border-[8px] border-violet-600 border-r-emerald-500 border-b-indigo-400 flex items-center justify-center">
                            <span className="text-xs font-bold text-white">$0.024</span>
                          </div>
                        </div>
                        <div className="flex gap-4 text-[9px] text-slate-400 mt-2 justify-center">
                          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-violet-600" />Gemini</span>
                          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-emerald-500" />Embeddings</span>
                          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-indigo-400" />Tools</span>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* 7. AI Platform Registry */}
                {activeTab === 'ai_admin' && (
                  <div className="bg-slate-900 border border-slate-850 rounded-xl p-6 space-y-6">
                    <div>
                      <h3 className="text-base font-bold text-white">AI Platform Adaptors Configuration</h3>
                      <p className="text-slate-400 text-xs mt-1">
                        Register dynamic prompt templates, model keys, agent memory caching parameters, and content safety policies.
                      </p>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                      <div className="p-4 bg-slate-950 border border-slate-800 rounded-lg space-y-2">
                        <h4 className="text-xs font-bold text-violet-400 uppercase font-mono">Model Registries</h4>
                        <div className="text-xs text-slate-300 font-mono space-y-1">
                          <div>✓ Gemini 2.5 Flash (Active)</div>
                          <div>✓ OpenAI GPT-4o (Standby)</div>
                          <div>✓ Claude 3.5 Sonnet (Local)</div>
                        </div>
                      </div>
                      <div className="p-4 bg-slate-950 border border-slate-800 rounded-lg space-y-2">
                        <h4 className="text-xs font-bold text-violet-400 uppercase font-mono">Governance Policy</h4>
                        <div className="text-xs text-slate-300 font-mono space-y-1">
                          <div>✓ PII Redactor: ON</div>
                          <div>✓ Content Safety Audit: ON</div>
                          <div>✓ Prompt Injection Guard: ON</div>
                        </div>
                      </div>
                      <div className="p-4 bg-slate-950 border border-slate-800 rounded-lg space-y-2">
                        <h4 className="text-xs font-bold text-violet-400 uppercase font-mono">Active Tool Registers</h4>
                        <div className="text-xs text-slate-300 font-mono space-y-1">
                          <div>✓ pdf_processor: ACTIVE</div>
                          <div>✓ docx_processor: ACTIVE</div>
                          <div>✓ hybrid_searcher: ACTIVE</div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* 8. Settings */}
                {activeTab === 'settings' && (
                  <div className="bg-slate-900 border border-slate-850 rounded-xl p-6 space-y-6">
                    <div>
                      <h3 className="text-base font-bold text-white">System Settings</h3>
                      <p className="text-slate-400 text-xs mt-1">
                        Manage global parameters, API thresholds, local files directory scopes, and theme defaults.
                      </p>
                    </div>
                    <div className="space-y-4 max-w-md">
                      <div className="flex justify-between items-center border-b border-slate-850 pb-2.5">
                        <span className="text-xs text-slate-300 font-semibold">Interactive 3D Visualizer Particles</span>
                        <input type="checkbox" defaultChecked className="rounded border-slate-700 bg-slate-950 text-violet-500 focus:ring-violet-500 h-4 w-4" />
                      </div>
                      <div className="flex justify-between items-center border-b border-slate-850 pb-2.5">
                        <span className="text-xs text-slate-300 font-semibold">Enable Live Notifications WebSocket</span>
                        <input type="checkbox" defaultChecked className="rounded border-slate-700 bg-slate-950 text-violet-500 focus:ring-violet-500 h-4 w-4" />
                      </div>
                      <div className="flex justify-between items-center border-b border-slate-850 pb-2.5">
                        <span className="text-xs text-slate-300 font-semibold">Default RAG Search Score Threshold</span>
                        <input type="number" defaultValue="0.75" step="0.05" className="bg-slate-950 border border-slate-800 text-xs text-slate-300 p-1.5 rounded focus:outline-none w-20 text-center font-mono" />
                      </div>
                    </div>
                  </div>
                )}
              </motion.div>
            </AnimatePresence>
          </div>
        </main>

        {/* Footer info bar */}
        <footer className="h-10 border-t border-slate-800 bg-slate-900/50 backdrop-blur-md px-8 flex items-center justify-center text-[10px] text-slate-500 font-mono uppercase tracking-widest shrink-0">
          SPS ENTERPRISE PROPOSAL MANAGER SYSTEM CONSOLE v1.0.0
        </footer>
      </div>
    </div>
  );
}
