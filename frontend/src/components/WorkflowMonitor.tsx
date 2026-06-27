'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface Execution {
  id: string;
  workflow_name: string;
  proposal_id: string;
  status: string;
  current_node: string;
  state: any;
  error_message?: string;
  created_at: string;
  updated_at: string;
}

interface Event {
  id: string;
  event_type: string;
  payload: any;
  timestamp: string;
}

interface Metric {
  id: string;
  node_name: string;
  duration_seconds: number;
  tokens_used: number;
  cost: number;
}

interface Checkpoint {
  id: string;
  node_name: string;
  timestamp: string;
}

interface Props {
  proposalId: string;
}

const NODES = [
  { id: 'document_processing', label: 'Document Processing', desc: 'RFP Structural analysis' },
  { id: 'requirement_extraction', label: 'Requirement Extraction', desc: 'Isolating obligations' },
  { id: 'department_review', label: 'Department Review', desc: 'Feasibility assessments' },
  { id: 'qualification', label: 'Qualification', desc: 'Win probability scoring' },
  { id: 'qualification_approval_gate', label: 'HITL Gate', desc: 'Director sign-off' },
  { id: 'proposal_planning', label: 'Proposal Planning', desc: 'Generating compliance WBS' },
  { id: 'knowledge_retrieval', label: 'Knowledge Retrieval', desc: 'pgvector standard queries' },
  { id: 'proposal_generation', label: 'Proposal Generation', desc: 'Multi-agent draft writer' },
  { id: 'review_refinement', label: 'Review Refinement', desc: '14-Agent QA validation' },
  { id: 'proposal_assembly', label: 'Proposal Assembly', desc: 'Packaging deliverables' }
];

export default function WorkflowMonitor({ proposalId }: Props) {
  const [execution, setExecution] = useState<Execution | null>(null);
  const [events, setEvents] = useState<Event[]>([]);
  const [metrics, setMetrics] = useState<Metric[]>([]);
  const [checkpoints, setCheckpoints] = useState<Checkpoint[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'graph' | 'events' | 'metrics' | 'checkpoints'>('graph');

  useEffect(() => {
    fetchWorkflowStatus();
  }, [proposalId]);

  const fetchWorkflowStatus = async () => {
    try {
      const history = await fetch('/api/v1/workflow/history').then((r) => r.json());
      // Filter for this proposal
      const activeExec = history.find((h: any) => h.proposal_id === proposalId) || history[history.length - 1];
      if (activeExec) {
        setExecution(activeExec);
        fetchSubData(activeExec.id);
      }
    } catch (e) {
      console.error('Failed fetching history', e);
    }
  };

  const fetchSubData = async (execId: string) => {
    try {
      const [resEvents, resMetrics, resCheckpoints] = await Promise.all([
        fetch(`/api/v1/workflow/${execId}/events`).then((r) => r.json()),
        fetch(`/api/v1/workflow/${execId}/metrics`).then((r) => r.json()),
        fetch(`/api/v1/workflow/${execId}/checkpoints`).then((r) => r.json())
      ]);
      setEvents(resEvents);
      setMetrics(resMetrics);
      setCheckpoints(resCheckpoints);
    } catch (e) {
      console.error(e);
    }
  };

  const handleStartWorkflow = async () => {
    setIsLoading(true);
    try {
      const res = await fetch('/api/v1/workflow/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ proposal_id: proposalId })
      }).then((r) => r.json());
      setExecution(res);
      fetchSubData(res.id);
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  const handleResume = async (action: 'approve' | 'reject') => {
    if (!execution) return;
    setIsLoading(true);
    try {
      const res = await fetch(`/api/v1/workflow/${execution.id}/resume`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action })
      }).then((r) => r.json());
      setExecution(res);
      fetchSubData(res.id);
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRollback = async (targetNode: string) => {
    if (!execution) return;
    setIsLoading(true);
    try {
      const res = await fetch(`/api/v1/workflow/${execution.id}/rollback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ target_node: targetNode })
      }).then((r) => r.json());
      setExecution(res);
      fetchSubData(res.id);
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRetry = async () => {
    if (!execution) return;
    setIsLoading(true);
    try {
      const res = await fetch(`/api/v1/workflow/${execution.id}/retry`, {
        method: 'POST'
      }).then((r) => r.json());
      setExecution(res);
      fetchSubData(res.id);
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30';
      case 'paused': return 'bg-amber-500/20 text-amber-400 border-amber-500/30';
      case 'failed': return 'bg-rose-500/20 text-rose-400 border-rose-500/30';
      default: return 'bg-indigo-500/20 text-indigo-400 border-indigo-500/30';
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 text-slate-100 shadow-2xl">
      <header className="flex flex-col md:flex-row md:items-center justify-between border-b border-slate-800 pb-4 mb-6">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-violet-500 animate-pulse" />
            LangGraph Master Lifecycle Orchestration
          </h2>
          <p className="text-slate-400 text-xs mt-1">
            Automated multi-agent proposal flow state-machine tracking, human validation gates, and rollbacks
          </p>
        </div>
        <div className="flex gap-2 mt-4 md:mt-0">
          {!execution ? (
            <button
              onClick={handleStartWorkflow}
              className="px-4 py-2 bg-violet-600 hover:bg-violet-500 rounded text-xs font-semibold tracking-wide transition-all shadow-md"
            >
              {isLoading ? 'Compiling Graph...' : 'Initiate Proposal Workflow'}
            </button>
          ) : (
            <div className="flex gap-2 items-center">
              <span className={`px-2.5 py-1 rounded text-xxs font-bold uppercase border ${getStatusColor(execution.status)}`}>
                {execution.status}
              </span>
              {execution.status === 'failed' && (
                <button
                  onClick={handleRetry}
                  className="px-3 py-1 bg-amber-600 hover:bg-amber-500 rounded text-xxs font-semibold tracking-wide transition-all"
                >
                  Retry Node
                </button>
              )}
            </div>
          )}
        </div>
      </header>

      {execution && (
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Main Visualizer Panel */}
          <div className="lg:col-span-3 space-y-6">
            {/* Tabs */}
            <div className="flex gap-2 border-b border-slate-800 pb-2">
              {(['graph', 'events', 'metrics', 'checkpoints'] as const).map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`px-4 py-1.5 rounded text-xs font-semibold uppercase tracking-wider transition-all ${
                    activeTab === tab ? 'bg-slate-800 text-violet-400' : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {tab}
                </button>
              ))}
            </div>

            {/* Tab Contents */}
            {activeTab === 'graph' && (
              <div className="bg-slate-950 p-6 rounded-lg border border-slate-800 space-y-8 min-h-[350px] flex flex-col justify-center">
                <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                  {NODES.map((node, index) => {
                    const isCurrent = execution.current_node === node.id;
                    const isActive = execution.status === 'running' && isCurrent;
                    const isCompleted = NODES.findIndex(n => n.id === execution.current_node) > index || execution.status === 'completed';
                    
                    return (
                      <div
                        key={node.id}
                        className={`relative p-3 rounded-lg border text-center transition-all ${
                          isActive ? 'bg-violet-600/10 border-violet-500 ring-1 ring-violet-500/30' :
                          isCurrent && execution.status === 'paused' ? 'bg-amber-600/10 border-amber-500' :
                          isCurrent && execution.status === 'failed' ? 'bg-rose-600/10 border-rose-500' :
                          isCompleted ? 'bg-emerald-600/10 border-emerald-500/40 text-slate-300' :
                          'bg-slate-900/60 border-slate-800 text-slate-500'
                        }`}
                      >
                        <div className="font-mono text-[9px] text-slate-500">Stage {index + 1}</div>
                        <h4 className="text-xs font-bold mt-1 text-slate-200">{node.label}</h4>
                        <p className="text-[10px] text-slate-400 mt-1.5 leading-tight">{node.desc}</p>
                        
                        {/* Status badge */}
                        {isCurrent && (
                          <span className={`absolute -top-2 -right-2 px-1.5 py-0.5 rounded text-[8px] font-extrabold uppercase animate-pulse ${
                            execution.status === 'paused' ? 'bg-amber-500 text-slate-950' :
                            execution.status === 'failed' ? 'bg-rose-500 text-white' :
                            'bg-violet-500 text-white'
                          }`}>
                            {execution.status}
                          </span>
                        )}
                      </div>
                    );
                  })}
                </div>

                {/* Error Banner */}
                {execution.error_message && (
                  <div className="p-4 bg-rose-500/10 border border-rose-500/20 rounded text-xs text-rose-400 font-mono">
                    <span className="font-bold">Error:</span> {execution.error_message}
                  </div>
                )}

                {/* HITL Gateway Interaction */}
                {execution.status === 'paused' && execution.current_node === 'qualification_approval_gate' && (
                  <div className="p-5 bg-amber-500/10 border border-amber-500/20 rounded-lg flex flex-col md:flex-row items-center justify-between gap-4">
                    <div>
                      <h4 className="text-sm font-bold text-amber-400 flex items-center gap-1.5">
                        <span className="w-2 h-2 bg-amber-500 rounded-full animate-ping" />
                        Human-in-the-Loop Gateway Approval Pending
                      </h4>
                      <p className="text-xs text-slate-300 mt-1">
                        Executive decision is required before proceeding to Phase 8 Proposal Planning outline synthesis.
                      </p>
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleResume('approve')}
                        className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 rounded text-xs font-bold"
                      >
                        Approve & Proceed
                      </button>
                      <button
                        onClick={() => handleResume('reject')}
                        className="px-4 py-2 bg-rose-600 hover:bg-rose-500 rounded text-xs font-bold"
                      >
                        Reject & Terminate
                      </button>
                    </div>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'events' && (
              <div className="bg-slate-950 p-4 rounded-lg border border-slate-800 max-h-[350px] overflow-y-auto">
                <div className="space-y-2">
                  {events.map((event) => (
                    <div key={event.id} className="p-2.5 bg-slate-900 border border-slate-800 rounded flex justify-between items-center text-xs font-mono">
                      <div>
                        <span className="text-violet-400 font-bold">{event.event_type}</span>
                        {event.payload && (
                          <span className="text-slate-400 ml-3 text-[10px]">{JSON.stringify(event.payload)}</span>
                        )}
                      </div>
                      <span className="text-slate-500 text-[10px]">
                        {new Date(event.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {activeTab === 'metrics' && (
              <div className="bg-slate-950 p-4 rounded-lg border border-slate-800 max-h-[350px] overflow-y-auto">
                <table className="w-full text-left text-xs font-mono">
                  <thead>
                    <tr className="border-b border-slate-800 text-slate-400">
                      <th className="pb-2">Node Name</th>
                      <th className="pb-2">Uptime Duration</th>
                      <th className="pb-2">Token Counts</th>
                      <th className="pb-2">Cost</th>
                    </tr>
                  </thead>
                  <tbody>
                    {metrics.map((metric) => (
                      <tr key={metric.id} className="border-b border-slate-900 hover:bg-slate-900/30">
                        <td className="py-2 text-slate-200">{metric.node_name}</td>
                        <td className="py-2 text-violet-400">{metric.duration_seconds.toFixed(2)}s</td>
                        <td className="py-2 text-slate-300">{metric.tokens_used}</td>
                        <td className="py-2 text-emerald-400">${metric.cost.toFixed(4)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {activeTab === 'checkpoints' && (
              <div className="bg-slate-950 p-4 rounded-lg border border-slate-800 max-h-[350px] overflow-y-auto space-y-2">
                {checkpoints.map((cp) => (
                  <div key={cp.id} className="p-3 bg-slate-900 border border-slate-800 rounded flex items-center justify-between text-xs">
                    <div>
                      <span className="font-bold text-slate-200 font-mono">{cp.node_name}</span>
                      <span className="text-slate-500 text-[10px] block mt-1">
                        Saved: {new Date(cp.timestamp).toLocaleString()}
                      </span>
                    </div>
                    <button
                      onClick={() => handleRollback(cp.node_name)}
                      className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 rounded text-xxs font-semibold border border-slate-700 text-violet-300 transition-all"
                    >
                      Rollback to Node
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Right Sidebar - Status, History details */}
          <div className="space-y-6">
            <div className="bg-slate-950 p-4 rounded-lg border border-slate-800">
              <h3 className="text-sm font-bold border-b border-slate-800 pb-2 mb-3">Active State Summary</h3>
              <div className="space-y-3 text-xs">
                <div className="flex justify-between text-slate-400">
                  <span>Current Step:</span>
                  <span className="font-bold text-slate-200 font-mono">{execution.current_node}</span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>Execution ID:</span>
                  <span className="font-mono text-[10px] text-slate-500">{execution.id.slice(0, 8)}...</span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>Requirements Count:</span>
                  <span className="font-bold text-slate-200">{execution.state?.requirements?.length || 0}</span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>Department Reviews:</span>
                  <span className="font-bold text-slate-200">{execution.state?.department_reviews?.length || 0}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {!execution && (
        <div className="py-16 text-center text-slate-500 italic text-sm">
          No active proposal workflow registered. Press "Initiate Proposal Workflow" to run multi-agent graph pipelines.
        </div>
      )}
    </div>
  );
}
