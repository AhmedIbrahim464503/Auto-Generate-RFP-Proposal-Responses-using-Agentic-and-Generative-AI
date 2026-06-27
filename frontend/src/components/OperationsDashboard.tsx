'use client';

import React, { useState, useEffect } from 'react';
import { Shield, Database, Cpu, Settings, RefreshCw, CheckCircle, AlertTriangle } from 'lucide-react';

interface AuditRecord {
  id: string;
  actor: string;
  action: string;
  entity: string;
  timestamp: string;
  correlationId: string;
}

interface CeleryJob {
  id: string;
  task: string;
  status: 'PENDING' | 'STARTED' | 'SUCCESS' | 'FAILURE';
  runtime: string;
}

export default function OperationsDashboard() {
  const [activeTab, setActiveTab] = useState<'security' | 'audit' | 'celery' | 'config'>('security');
  const [rateLimit, setRateLimit] = useState(100);
  const [auditLogs, setAuditLogs] = useState<AuditRecord[]>([
    { id: '1', actor: 'admin', action: 'ModelChanged', entity: 'ModelRegistry/gemini-2.5', timestamp: '12:05:10', correlationId: 'corr_83829' },
    { id: '2', actor: 'writer', action: 'ProposalUploaded', entity: 'Proposal/doc_193', timestamp: '12:08:44', correlationId: 'corr_37291' },
    { id: '3', actor: 'admin', action: 'HumanOverride', entity: 'DecisionOpportunity/qual_48', timestamp: '12:10:02', correlationId: 'corr_92812' }
  ]);
  const [celeryJobs, setCeleryJobs] = useState<CeleryJob[]>([
    { id: 'job_28', task: 'process_document_task', status: 'SUCCESS', runtime: '1.2s' },
    { id: 'job_29', task: 'index_knowledge_task', status: 'STARTED', runtime: '0.4s' },
    { id: 'job_30', task: 'generate_proposal_section_task', status: 'PENDING', runtime: '0s' }
  ]);

  const handleRefresh = () => {
    // Simulate updating logs and celery tasks
    setAuditLogs((prev) => [
      { id: String(prev.length + 1), actor: 'system', action: 'TokenFlush', entity: 'ExplainabilityRecord', timestamp: new Date().toLocaleTimeString(), correlationId: 'corr_refresh' },
      ...prev
    ]);
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden p-6 space-y-6">
      <div className="flex justify-between items-center border-b border-slate-800 pb-4">
        <div>
          <h3 className="text-base font-bold text-white uppercase tracking-wider font-mono">
            Enterprise Operations Platform
          </h3>
          <p className="text-slate-400 text-xs mt-0.5">
            Audit trailing, security rate limits, Celery background jobs, and system parameters
          </p>
        </div>
        <button
          onClick={handleRefresh}
          className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded text-xs font-semibold tracking-wide border border-slate-700"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          Refresh Console
        </button>
      </div>

      {/* Tabs */}
      <div className="flex gap-2">
        <button
          onClick={() => setActiveTab('security')}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-bold font-mono transition-all ${
            activeTab === 'security' ? 'bg-violet-600 text-white' : 'text-slate-400 hover:bg-slate-800/60'
          }`}
        >
          <Shield className="w-3.5 h-3.5" />
          Security Console
        </button>
        <button
          onClick={() => setActiveTab('audit')}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-bold font-mono transition-all ${
            activeTab === 'audit' ? 'bg-violet-600 text-white' : 'text-slate-400 hover:bg-slate-800/60'
          }`}
        >
          <Database className="w-3.5 h-3.5" />
          Audit Timeline
        </button>
        <button
          onClick={() => setActiveTab('celery')}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-bold font-mono transition-all ${
            activeTab === 'celery' ? 'bg-violet-600 text-white' : 'text-slate-400 hover:bg-slate-800/60'
          }`}
        >
          <Cpu className="w-3.5 h-3.5" />
          Celery Monitor
        </button>
        <button
          onClick={() => setActiveTab('config')}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-bold font-mono transition-all ${
            activeTab === 'config' ? 'bg-violet-600 text-white' : 'text-slate-400 hover:bg-slate-800/60'
          }`}
        >
          <Settings className="w-3.5 h-3.5" />
          Config center
        </button>
      </div>

      {/* Tab Contents */}
      <div className="pt-2">
        {activeTab === 'security' && (
          <div className="space-y-4">
            <div className="p-4 bg-slate-950 border border-slate-850 rounded-lg flex justify-between items-center">
              <div>
                <h4 className="text-xs font-bold text-white">Rate Limit Protection</h4>
                <p className="text-[10px] text-slate-400 mt-0.5">Maximum API requests allowed per client IP per minute</p>
              </div>
              <div className="flex items-center gap-2">
                <input
                  type="number"
                  value={rateLimit}
                  onChange={(e) => setRateLimit(Number(e.target.value))}
                  className="bg-slate-900 border border-slate-700 text-xs text-white p-1 rounded w-16 text-center font-mono"
                />
                <span className="text-[10px] text-slate-500 font-mono">req/min</span>
              </div>
            </div>

            <div className="p-4 bg-slate-950 border border-slate-850 rounded-lg space-y-2">
              <h4 className="text-xs font-bold text-white">RBAC Least Privilege Permissions matrix</h4>
              <div className="text-[10px] font-mono text-slate-300 space-y-1">
                <div>• Admin role: [read, write, admin, export]</div>
                <div>• Writer role: [read, write]</div>
                <div>• Guest role: [read]</div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'audit' && (
          <div className="bg-slate-950 border border-slate-850 rounded-lg p-4 space-y-3">
            <div className="flex justify-between items-center text-[10px] font-mono text-slate-500 uppercase pb-1.5 border-b border-slate-900">
              <span>Actor / Action</span>
              <span>Affected Entity</span>
              <span>Correlation ID</span>
            </div>
            <div className="space-y-2 max-h-40 overflow-y-auto pr-1">
              {auditLogs.map((log) => (
                <div key={log.id} className="flex justify-between items-center text-xs font-mono py-1 border-b border-slate-900/60 last:border-0">
                  <div className="flex items-center gap-2">
                    <span className="text-violet-400">[{log.timestamp}]</span>
                    <span className="font-bold text-slate-200">{log.actor}</span>
                    <span className="text-slate-400">({log.action})</span>
                  </div>
                  <span className="text-slate-300 truncate max-w-xs">{log.entity}</span>
                  <span className="text-slate-500">{log.correlationId}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'celery' && (
          <div className="bg-slate-950 border border-slate-850 rounded-lg p-4 space-y-3">
            <div className="flex justify-between items-center text-[10px] font-mono text-slate-500 uppercase pb-1.5 border-b border-slate-900">
              <span>Task Name</span>
              <span>Status</span>
              <span>Duration</span>
            </div>
            <div className="space-y-2">
              {celeryJobs.map((job) => (
                <div key={job.id} className="flex justify-between items-center text-xs font-mono py-1 border-b border-slate-900/60 last:border-0">
                  <span className="text-slate-300">{job.task}</span>
                  <span className="flex items-center gap-1.5">
                    {job.status === 'SUCCESS' && (
                      <span className="text-emerald-400 flex items-center gap-1 text-[10px]"><CheckCircle className="w-3 h-3" />SUCCESS</span>
                    )}
                    {job.status === 'STARTED' && (
                      <span className="text-blue-400 flex items-center gap-1 text-[10px] animate-pulse"><RefreshCw className="w-3 h-3" />STARTED</span>
                    )}
                    {job.status === 'PENDING' && (
                      <span className="text-slate-500 text-[10px]">PENDING</span>
                    )}
                  </span>
                  <span className="text-slate-400">{job.runtime}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'config' && (
          <div className="p-4 bg-slate-950 border border-slate-850 rounded-lg space-y-3">
            <div className="flex justify-between items-center border-b border-slate-900 pb-2">
              <span className="text-xs text-slate-300">Default Temperature Configuration</span>
              <input type="number" defaultValue="0.2" step="0.1" className="bg-slate-900 border border-slate-700 text-xs text-white p-1 rounded w-16 text-center font-mono" />
            </div>
            <div className="flex justify-between items-center border-b border-slate-900 pb-2">
              <span className="text-xs text-slate-300">Min Go/No-Go Feasibility Threshold</span>
              <input type="number" defaultValue="70" className="bg-slate-900 border border-slate-700 text-xs text-white p-1 rounded w-16 text-center font-mono" />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
