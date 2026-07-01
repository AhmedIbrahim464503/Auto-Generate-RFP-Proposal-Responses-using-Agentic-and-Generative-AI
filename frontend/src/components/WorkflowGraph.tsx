'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';

interface Node {
  id: string;
  label: string;
  desc: string;
  status?: 'pending' | 'running' | 'completed' | 'paused' | 'failed';
}

interface Props {
  currentStep: string;
  executionStatus: string;
}

const FLOW_NODES: Node[] = [
  { id: 'document_processing', label: 'Document Intake', desc: 'Fits structural analyses & parsing' },
  { id: 'requirement_extraction', label: 'Requirements Extractor', desc: 'Isolating compliance obligations' },
  { id: 'department_review', label: 'Feasibility Matrix', desc: 'Financial/legal rule scoring' },
  { id: 'qualification', label: 'Decision Intelligence', desc: 'Opportunity & win probability engine' },
  { id: 'qualification_approval_gate', label: 'HITL Qualification Gate', desc: 'Director sign-off validation' },
  { id: 'proposal_planning', label: 'Proposal Planner', desc: 'Compiling outlines & milestone WBS' },
  { id: 'knowledge_retrieval', label: 'RAG Retrieval', desc: ' pgvector semantic hybrid searches' },
  { id: 'proposal_generation', label: 'Multi-Agent Writer', desc: '15 specialized drafting agents' },
  { id: 'review_refinement', label: 'QA Review & Replays', desc: '14-Agent compliance validation' },
  { id: 'proposal_assembly', label: 'Assembly & Export', desc: 'Completed packages compile' }
];

export default function WorkflowGraph({ currentStep, executionStatus }: Props) {
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const [zoomLevel, setZoomLevel] = useState(1);

  const getStatusBorderColor = (nodeId: string) => {
    const activeIndex = FLOW_NODES.findIndex((n) => n.id === currentStep);
    const selfIndex = FLOW_NODES.findIndex((n) => n.id === nodeId);

    if (selfIndex === activeIndex) {
      if (executionStatus === 'paused') return 'border-amber-500 bg-amber-500/10 shadow-[0_0_15px_rgba(245,158,11,0.25)]';
      if (executionStatus === 'failed') return 'border-rose-500 bg-rose-500/10 shadow-[0_0_15px_rgba(244,63,94,0.25)]';
      return 'border-violet-500 bg-violet-500/10 shadow-[0_0_15px_rgba(124,58,237,0.25)] animate-pulse';
    }
    if (selfIndex < activeIndex || currentStep === 'completed') {
      return 'border-emerald-500/60 bg-emerald-500/5 text-slate-300';
    }
    return 'border-slate-800 bg-slate-900/40 text-slate-500';
  };

  return (
    <div className="bg-slate-950 rounded-xl border border-slate-800/80 overflow-hidden p-6 relative">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono">
            Interactive Agent Execution Flow
          </h3>
          <p className="text-slate-400 text-xs mt-0.5">
            Select node for detail inspection and execution checkpoints rollback
          </p>
        </div>
        <div className="flex gap-2 text-xxs font-mono">
          <button
            onClick={() => setZoomLevel((z) => Math.max(0.8, z - 0.1))}
            className="px-2 py-1 bg-slate-900 hover:bg-slate-800 border border-slate-800 rounded"
          >
            Zoom Out
          </button>
          <button
            onClick={() => setZoomLevel(1)}
            className="px-2 py-1 bg-slate-900 hover:bg-slate-800 border border-slate-800 rounded"
          >
            Reset
          </button>
          <button
            onClick={() => setZoomLevel((z) => Math.min(1.2, z + 0.1))}
            className="px-2 py-1 bg-slate-900 hover:bg-slate-800 border border-slate-800 rounded"
          >
            Zoom In
          </button>
        </div>
      </div>

      {/* Graph Area */}
      <div
        className="overflow-x-auto py-8 pr-4"
        style={{ transform: `scale(${zoomLevel})`, transformOrigin: 'top left', transition: 'transform 0.2s' }}
      >
        <div className="flex items-center gap-6 min-w-[1200px]">
          {FLOW_NODES.map((node, index) => (
            <React.Fragment key={node.id}>
              {/* Node Card */}
              <button
                onClick={() => setSelectedNode(node)}
                className={`flex-1 min-w-[180px] p-3 text-left border rounded-lg transition-all focus:outline-none ${getStatusBorderColor(
                  node.id
                )}`}
              >
                <div className="flex justify-between items-center font-mono text-[9px] text-slate-500">
                  <span>Chapter {index + 1}</span>
                  {currentStep === node.id && (
                    <span className="w-1.5 h-1.5 bg-violet-400 rounded-full animate-ping" />
                  )}
                </div>
                <h4 className="text-xs font-bold text-slate-200 mt-1">{node.label}</h4>
                <p className="text-[10px] text-slate-400 mt-1.5 leading-tight truncate">{node.desc}</p>
              </button>

              {/* Edge connector line */}
              {index < FLOW_NODES.length - 1 && (
                <div className="w-6 h-0.5 bg-slate-800 shrink-0 relative">
                  <div
                    className={`absolute inset-0 bg-violet-500 transition-all ${
                      FLOW_NODES.findIndex((n) => n.id === currentStep) > index ? 'w-full' : 'w-0'
                    }`}
                  />
                </div>
              )}
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* Node Detail Drawer / Inspection */}
      {selectedNode && (
        <div className="mt-6 p-4 bg-slate-900/60 border border-slate-800 rounded-lg flex justify-between items-start gap-4">
          <div className="space-y-1">
            <span className="text-[9px] font-mono text-violet-400 uppercase tracking-widest">Node Inspection</span>
            <h4 className="text-sm font-bold text-white">{selectedNode.label}</h4>
            <p className="text-xs text-slate-300 max-w-2xl">{selectedNode.desc}</p>
          </div>
          <button
            onClick={() => setSelectedNode(null)}
            className="text-slate-400 hover:text-slate-200 text-xs font-semibold"
          >
            Close
          </button>
        </div>
      )}
    </div>
  );
}
