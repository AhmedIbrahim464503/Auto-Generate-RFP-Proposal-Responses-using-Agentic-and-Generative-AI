'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface Finding {
  id: string;
  generated_section_id: string;
  agent_id: string;
  category: string;
  severity: string;
  message: string;
  evidence: string;
  created_at: string;
}

interface Score {
  id: string;
  metric_name: string;
  score: number;
  weight: number;
}

interface ReviewSession {
  id: string;
  proposal_plan_id: string;
  status: string;
  overall_score: number;
  findings: Finding[];
  scores: Score[];
  created_at: string;
}

interface Props {
  proposalId: string;
}

export default function ProposalReviewDashboard({ proposalId }: Props) {
  const [session, setSession] = useState<ReviewSession | null>(null);
  const [coverage, setCoverage] = useState<any>(null);
  const [citations, setCitations] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedSectionId, setSelectedSectionId] = useState<string | null>(null);

  useEffect(() => {
    fetchReviewData();
  }, [proposalId]);

  const fetchReviewData = async () => {
    setIsLoading(true);
    try {
      const [resSession, resCoverage, resCitations] = await Promise.all([
        fetch(`/api/v1/review/${proposalId}`).then((r) => (r.ok ? r.json() : null)),
        fetch(`/api/v1/review/coverage`).then((r) => r.json()),
        fetch(`/api/v1/review/citations`).then((r) => r.json()),
      ]);
      setSession(resSession);
      setCoverage(resCoverage);
      setCitations(resCitations);
    } catch (e) {
      console.error('Failed to load review workspace', e);
    } finally {
      setIsLoading(false);
    }
  };

  const handleStartReview = async () => {
    setIsLoading(true);
    try {
      const res = await fetch(`/api/v1/review/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ proposal_plan_id: proposalId }),
      }).then((r) => r.json());
      setSession(res);
      fetchReviewData();
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRefine = async () => {
    if (!session) return;
    setIsLoading(true);
    try {
      const res = await fetch(`/api/v1/review/refine`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: session.id }),
      }).then((r) => r.json());
      setSession(res);
      fetchReviewData();
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDecision = async (action: 'approve' | 'reject') => {
    if (!session) return;
    setIsLoading(true);
    try {
      const res = await fetch(`/api/v1/review/${action}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: session.id, actor: 'Proposal Manager', message: 'Manual HITL decision override' }),
      }).then((r) => r.json());
      setSession(res);
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 text-slate-100 shadow-2xl">
      <header className="flex flex-col md:flex-row md:items-center justify-between border-b border-slate-800 pb-4 mb-6">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-indigo-500 animate-pulse" />
            Enterprise QA & Multi-Agent Validation Console
          </h2>
          <p className="text-slate-400 text-xs mt-1">
            Automated factual verification, compliance indexing, and human refinement gates
          </p>
        </div>
        <div className="flex gap-2 mt-4 md:mt-0">
          {!session ? (
            <button
              onClick={handleStartReview}
              className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 rounded text-xs font-semibold tracking-wide transition-all"
            >
              {isLoading ? 'Executing Agents...' : 'Run QA Pipeline'}
            </button>
          ) : (
            <>
              <button
                onClick={handleRefine}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded text-xs font-semibold tracking-wide transition-all border border-slate-700"
              >
                Auto-Refine Drafts
              </button>
              <button
                onClick={() => handleDecision('approve')}
                className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 rounded text-xs font-semibold tracking-wide transition-all"
              >
                Sign Off & Approve
              </button>
              <button
                onClick={() => handleDecision('reject')}
                className="px-4 py-2 bg-rose-600 hover:bg-rose-500 rounded text-xs font-semibold tracking-wide transition-all"
              >
                Reject & Block
              </button>
            </>
          )}
        </div>
      </header>

      {session ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Quality Metrics */}
          <div className="lg:col-span-2 space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-slate-950 p-4 rounded-lg border border-slate-800 text-center">
                <h4 className="text-slate-400 text-xxs font-bold uppercase tracking-widest">Proposal Quality Index</h4>
                <p className="text-3xl font-extrabold text-white mt-2">{(session.overall_score * 100).toFixed(0)}%</p>
              </div>
              <div className="bg-slate-950 p-4 rounded-lg border border-slate-800 text-center">
                <h4 className="text-slate-400 text-xxs font-bold uppercase tracking-widest">Requirements Checked</h4>
                <p className="text-3xl font-extrabold text-white mt-2">
                  {coverage ? `${coverage.satisfied}/${coverage.total_requirements}` : '0/0'}
                </p>
              </div>
              <div className="bg-slate-950 p-4 rounded-lg border border-slate-800 text-center">
                <h4 className="text-slate-400 text-xxs font-bold uppercase tracking-widest">Status Gate</h4>
                <span className={`inline-block mt-3 px-3 py-1 rounded-full text-[10px] font-bold ${
                  session.status === 'PASS' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
                  session.status === 'BLOCKED' ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20' :
                  'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                }`}>
                  {session.status}
                </span>
              </div>
            </div>

            {/* Findings List */}
            <div className="bg-slate-950 p-4 rounded-lg border border-slate-800">
              <h3 className="text-sm font-bold border-b border-slate-800 pb-2 mb-3">Validation Findings</h3>
              <div className="space-y-3 max-h-80 overflow-y-auto pr-2">
                {session.findings && session.findings.length > 0 ? (
                  session.findings.map((f) => (
                    <div key={f.id} className="p-3 bg-slate-900 rounded border border-slate-800 flex justify-between gap-4">
                      <div>
                        <div className="flex items-center gap-2">
                          <span className={`px-1.5 py-0.5 rounded text-[8px] font-bold ${
                            f.severity === 'critical' ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30' : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                          }`}>
                            {f.severity.toUpperCase()}
                          </span>
                          <span className="font-mono text-[10px] text-indigo-400">{f.agent_id}</span>
                        </div>
                        <p className="text-xs mt-2 text-slate-300">{f.message}</p>
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="text-xs text-slate-500 italic">No quality anomalies detected by evaluation agents.</p>
                )}
              </div>
            </div>
          </div>

          {/* Sidebar - Coverage Matrix & Citations */}
          <div className="space-y-6">
            <div className="bg-slate-950 p-4 rounded-lg border border-slate-800">
              <h3 className="text-sm font-bold border-b border-slate-800 pb-2 mb-3">Requirement Coverage</h3>
              {coverage ? (
                <div className="space-y-3 text-xs">
                  <div className="flex justify-between text-slate-400">
                    <span>Coverage Rate:</span>
                    <span className="font-bold text-slate-200">{coverage.coverage_percentage.toFixed(0)}%</span>
                  </div>
                  <div>
                    <h5 className="font-semibold text-slate-400 mb-1 text-[10px] uppercase">Missing Obligations</h5>
                    {coverage.missing_obligations.length > 0 ? (
                      <ul className="space-y-1 text-rose-400 font-mono text-[10px] list-disc list-inside">
                        {coverage.missing_obligations.map((m: string, i: number) => (
                          <li key={i}>{m}</li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-[10px] text-emerald-400">✓ All mandatory constraints satisfied</p>
                    )}
                  </div>
                </div>
              ) : (
                <p className="text-xs text-slate-500 italic">Loading coverage details...</p>
              )}
            </div>

            <div className="bg-slate-950 p-4 rounded-lg border border-slate-800">
              <h3 className="text-sm font-bold border-b border-slate-800 pb-2 mb-3">Citation Inspector</h3>
              {citations ? (
                <div className="space-y-3 text-xs">
                  <div className="flex justify-between text-slate-400">
                    <span>Factual Accuracy:</span>
                    <span className="font-bold text-slate-200">{citations.citation_accuracy.toFixed(0)}%</span>
                  </div>
                  <div>
                    <h5 className="font-semibold text-slate-400 mb-1 text-[10px] uppercase">Broken References</h5>
                    {citations.broken_references.length > 0 ? (
                      <ul className="space-y-1 text-rose-400 font-mono text-[10px] list-disc list-inside">
                        {citations.broken_references.map((m: string, i: number) => (
                          <li key={i}>{m}</li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-[10px] text-emerald-400">✓ All factual claims cited correctly</p>
                    )}
                  </div>
                </div>
              ) : (
                <p className="text-xs text-slate-500 italic">Loading citation checklist...</p>
              )}
            </div>
          </div>
        </div>
      ) : (
        <div className="py-12 text-center text-slate-500 italic text-sm">
          No active review run for this proposal outline. Press "Run QA Pipeline" to evaluate drafts.
        </div>
      )}
    </div>
  );
}
