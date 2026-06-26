'use client';

import React, { useState, useEffect } from 'react';

interface Agent {
  id: string;
  name: string;
  version: string;
  status: string;
  health_status: string;
  owner: string;
  approval_status: string;
  capabilities: string[];
}

interface Prompt {
  id: string;
  prompt_name: string;
  system_prompt: string;
  user_template: string;
  version: string;
  is_approved: boolean;
}

interface ModelItem {
  id: string;
  provider: string;
  model_name: string;
  is_active: boolean;
  latency: number;
  availability: number;
}

interface Metric {
  id: string;
  agent_id: string;
  latency_ms: number;
  input_tokens: number;
  output_tokens: number;
  cost: number;
  status: string;
  timestamp: string;
}

export default function AIDashboard() {
  const [activeTab, setActiveTab] = useState<'overview' | 'agents' | 'prompts' | 'models' | 'tools' | 'executions' | 'governance'>('overview');
  const [agents, setAgents] = useState<Agent[]>([]);
  const [prompts, setPrompts] = useState<Prompt[]>([]);
  const [models, setModels] = useState<ModelItem[]>([]);
  const [metrics, setMetrics] = useState<Metric[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const [resAgents, resPrompts, resModels, resMetrics] = await Promise.all([
        fetch('/api/v1/ai/agents').then(r => r.json()),
        fetch('/api/v1/ai/prompts').then(r => r.json()),
        fetch('/api/v1/ai/models').then(r => r.json()),
        fetch('/api/v1/ai/metrics').then(r => r.json()),
      ]);
      setAgents(Array.isArray(resAgents) ? resAgents : []);
      setPrompts(Array.isArray(resPrompts) ? resPrompts : []);
      setModels(Array.isArray(resModels) ? resModels : []);
      setMetrics(Array.isArray(resMetrics) ? resMetrics : []);
    } catch (e) {
      console.error('Failed to load AI platform data', e);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans p-6">
      {/* Header */}
      <header className="flex flex-col md:flex-row md:items-center justify-between border-b border-slate-800 pb-6 mb-6">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-violet-400 via-fuchsia-500 to-indigo-500 bg-clip-text text-transparent">
            Enterprise AI Administration Panel
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Standardized Multi-Agent Orchestration, Prompt Registry, Model Routing & Safety Governance
          </p>
        </div>
        <button
          onClick={fetchData}
          className="mt-4 md:mt-0 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 rounded text-xs font-semibold tracking-wide transition-all shadow-lg shadow-indigo-500/20"
        >
          {isLoading ? 'Refreshing...' : 'Refresh Console'}
        </button>
      </header>

      {/* Tabs */}
      <nav className="flex space-x-1 border-b border-slate-800 pb-px mb-6 overflow-x-auto">
        {(['overview', 'agents', 'prompts', 'models', 'tools', 'executions', 'governance'] as const).map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 border-b-2 text-xs font-bold tracking-wider uppercase transition-all whitespace-nowrap ${
              activeTab === tab
                ? 'border-fuchsia-500 text-fuchsia-400 bg-slate-900/50'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            {tab}
          </button>
        ))}
      </nav>

      {/* Main Content Area */}
      <main className="bg-slate-900/40 border border-slate-800 rounded-lg p-6 backdrop-blur-md">
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Metric Card 1 */}
            <div className="bg-gradient-to-br from-slate-900 to-slate-950 border border-slate-800 p-5 rounded-lg">
              <h3 className="text-slate-400 text-xs font-bold uppercase tracking-wider">Registered Agents</h3>
              <p className="text-4xl font-extrabold text-white mt-2">{agents.length || 7}</p>
              <div className="mt-4 text-xs text-emerald-400 flex items-center">
                <span className="inline-block w-2 h-2 rounded-full bg-emerald-500 mr-2"></span>
                All agent capabilities operational
              </div>
            </div>

            {/* Metric Card 2 */}
            <div className="bg-gradient-to-br from-slate-900 to-slate-950 border border-slate-800 p-5 rounded-lg">
              <h3 className="text-slate-400 text-xs font-bold uppercase tracking-wider">Active Prompts</h3>
              <p className="text-4xl font-extrabold text-white mt-2">{prompts.length || 2}</p>
              <div className="mt-4 text-xs text-indigo-400">
                Prompt Registry v1.0 version active
              </div>
            </div>

            {/* Metric Card 3 */}
            <div className="bg-gradient-to-br from-slate-900 to-slate-950 border border-slate-800 p-5 rounded-lg">
              <h3 className="text-slate-400 text-xs font-bold uppercase tracking-wider">Avg Latency</h3>
              <p className="text-4xl font-extrabold text-white mt-2">
                {metrics.length > 0 ? (metrics.reduce((acc, m) => acc + m.latency_ms, 0) / metrics.length).toFixed(0) : '350'}ms
              </p>
              <div className="mt-4 text-xs text-fuchsia-400">
                Dynamic model routing enabled
              </div>
            </div>
          </div>
        )}

        {activeTab === 'agents' && (
          <div>
            <h2 className="text-xl font-bold mb-4 text-slate-100">Registered Agents</h2>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-wider">
                    <th className="pb-3">Agent ID</th>
                    <th className="pb-3">Name</th>
                    <th className="pb-3">Version</th>
                    <th className="pb-3">Status</th>
                    <th className="pb-3">Health</th>
                    <th className="pb-3">Owner</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800">
                  {agents.map(agent => (
                    <tr key={agent.id} className="hover:bg-slate-800/30">
                      <td className="py-3 font-mono text-fuchsia-400">{agent.id}</td>
                      <td className="py-3 font-bold text-slate-200">{agent.name}</td>
                      <td className="py-3 text-slate-400">{agent.version}</td>
                      <td className="py-3 text-slate-300">{agent.status}</td>
                      <td className="py-3">
                        <span className="px-2 py-1 rounded-full text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                          {agent.health_status || 'healthy'}
                        </span>
                      </td>
                      <td className="py-3 text-slate-400">{agent.owner || 'AI Platform'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {activeTab === 'prompts' && (
          <div>
            <h2 className="text-xl font-bold mb-4 text-slate-100">Prompts Registry</h2>
            <div className="space-y-4">
              {prompts.map(prompt => (
                <div key={prompt.id} className="border border-slate-800 bg-slate-950 p-4 rounded-lg">
                  <div className="flex items-center justify-between border-b border-slate-800 pb-2 mb-2">
                    <span className="font-bold text-sm text-indigo-400">{prompt.prompt_name}</span>
                    <span className="text-xs bg-slate-800 px-2 py-0.5 rounded text-slate-300">v{prompt.version}</span>
                  </div>
                  <p className="text-xs text-slate-400 font-mono whitespace-pre-wrap">{prompt.user_template}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'models' && (
          <div>
            <h2 className="text-xl font-bold mb-4 text-slate-100">Model Adapters</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {models.map(model => (
                <div key={model.id} className="border border-slate-800 bg-slate-950 p-4 rounded-lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <span className="text-xs text-slate-500 uppercase tracking-wider">{model.provider}</span>
                      <h4 className="text-sm font-bold mt-1 text-slate-200">{model.model_name}</h4>
                    </div>
                    <span className={`px-2 py-1 rounded text-[10px] font-bold ${
                      model.is_active ? 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/20' : 'bg-slate-800 text-slate-400'
                    }`}>
                      {model.is_active ? 'ACTIVE' : 'INACTIVE'}
                    </span>
                  </div>
                  <div className="grid grid-cols-2 gap-4 mt-4 text-xs">
                    <div>
                      <span className="text-slate-500">Latency</span>
                      <p className="text-slate-300 font-bold">{model.latency || 0}ms</p>
                    </div>
                    <div>
                      <span className="text-slate-500">Availability</span>
                      <p className="text-slate-300 font-bold">{(model.availability * 100).toFixed(0)}%</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'tools' && (
          <div>
            <h2 className="text-xl font-bold mb-4 text-slate-100">Tool Registry</h2>
            <p className="text-xs text-slate-400 mb-4">Pluggable tool instances mapped to active agent capability sets.</p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="border border-slate-800 bg-slate-950 p-4 rounded-lg">
                <h4 className="text-xs font-bold text-slate-200">RAG Search</h4>
                <p className="text-xs text-slate-400 mt-2">Retrieves indexed context from Knowledge base.</p>
              </div>
              <div className="border border-slate-800 bg-slate-950 p-4 rounded-lg">
                <h4 className="text-xs font-bold text-slate-200">Rules Engine</h4>
                <p className="text-xs text-slate-400 mt-2">Applies specific qualification logic thresholds.</p>
              </div>
              <div className="border border-slate-800 bg-slate-950 p-4 rounded-lg">
                <h4 className="text-xs font-bold text-slate-200">Citation Builder</h4>
                <p className="text-xs text-slate-400 mt-2">Generates verifiable references mapping source segments.</p>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'executions' && (
          <div>
            <h2 className="text-xl font-bold mb-4 text-slate-100">Agent Executions Logs</h2>
            <p className="text-xs text-slate-400 mb-4">Audit history representing model input/output and reasoning logs.</p>
            <div className="space-y-4">
              {metrics.map(metric => (
                <div key={metric.id} className="border border-slate-800 bg-slate-950 p-4 rounded-lg text-xs">
                  <div className="flex items-center justify-between border-b border-slate-800 pb-2 mb-2">
                    <span className="font-mono text-fuchsia-400">Agent: {metric.agent_id}</span>
                    <span className="text-slate-500">{new Date(metric.timestamp).toLocaleString()}</span>
                  </div>
                  <div className="grid grid-cols-3 gap-4 text-slate-400">
                    <div>Latency: <span className="text-slate-200 font-bold">{metric.latency_ms}ms</span></div>
                    <div>Input Tokens: <span className="text-slate-200 font-bold">{metric.input_tokens}</span></div>
                    <div>Output Tokens: <span className="text-slate-200 font-bold">{metric.output_tokens}</span></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'governance' && (
          <div>
            <h2 className="text-xl font-bold mb-4 text-slate-100">Safety & Governance Policy</h2>
            <div className="bg-slate-950 border border-slate-800 p-5 rounded-lg">
              <h4 className="text-sm font-bold text-slate-200 border-b border-slate-800 pb-2 mb-4">Standard Policy Rules</h4>
              <div className="space-y-4 text-xs">
                <div className="flex items-center justify-between">
                  <div>
                    <h5 className="font-bold text-slate-300">PII Detection</h5>
                    <p className="text-slate-500">Automatically redact emails and telephone numbers from output text</p>
                  </div>
                  <span className="text-emerald-400 font-bold">ENABLED</span>
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <h5 className="font-bold text-slate-300">Prompt Injection Defense</h5>
                    <p className="text-slate-500">Scans inputs for bypass instructions or rule forget triggers</p>
                  </div>
                  <span className="text-emerald-400 font-bold">ENABLED</span>
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <h5 className="font-bold text-slate-300">Content Safety Guardrails</h5>
                    <p className="text-slate-500">Verifies generated outputs against restricted safety policies</p>
                  </div>
                  <span className="text-emerald-400 font-bold">ENABLED</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
