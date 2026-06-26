"use client";

import React, { useState, useEffect } from "react";

interface ScoringBreakdown {
  dimension: string;
  raw_score: number;
  weight: number;
  weighted_score: number;
  details?: any;
}

interface ExecutiveComment {
  id: string;
  author: string;
  comment_text: string;
  timestamp: string;
}

interface QualificationResponse {
  id: string;
  opportunity_id: string;
  status: string;
  recommendation: string;
  final_decision?: string;
  decision_by?: string;
  decision_timestamp?: string;
  executive_summary?: string;
  confidence: number;
  reasoning?: string;
  evidence: string[];
  positive_factors: string[];
  negative_factors: string[];
  blocking_issues: string[];
  mitigating_factors: string[];
  recommended_actions: string[];
  escalation_requirements: string[];
  outstanding_clarifications: string[];
  next_steps: string[];
  business_impact?: string;
  opportunity_score: number;
  estimated_win_probability: number;
  win_probability_explanation?: string;
  scoring_breakdowns: ScoringBreakdown[];
  comments: ExecutiveComment[];
}

interface HistoryItem {
  id: string;
  action: string;
  actor: string;
  previous_status?: string;
  new_status?: string;
  comments?: string;
  timestamp: string;
}

interface ExecutiveDecisionDashboardProps {
  documentId: string;
}

export default function ExecutiveDecisionDashboard({ documentId }: ExecutiveDecisionDashboardProps) {
  const [data, setData] = useState<QualificationResponse | null>(null);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isActionLoading, setIsActionLoading] = useState<boolean>(false);
  
  // Scoring Weights Adjustments Form
  const [weights, setWeights] = useState<Record<string, number>>({});
  
  // Human Action Forms
  const [reviewer, setReviewer] = useState<string>("Executive Sponsor");
  const [approveComments, setApproveComments] = useState<string>("");
  const [overrideDecision, setOverrideDecision] = useState<string>("GO");
  const [overrideReason, setOverrideReason] = useState<string>("");
  const [newCommentAuthor, setNewCommentAuthor] = useState<string>("Bid Manager");
  const [newCommentText, setNewCommentText] = useState<string>("");

  useEffect(() => {
    if (documentId) {
      fetchQualificationData();
      fetchHistory();
    }
  }, [documentId]);

  const fetchQualificationData = async () => {
    setIsLoading(true);
    try {
      const res = await fetch(`/api/v1/rfp/${documentId}/qualification`);
      if (res.ok) {
        const json = await res.json();
        setData(json);
        // Initialize weights state
        const wMap: Record<string, number> = {};
        json.scoring_breakdowns.forEach((b: ScoringBreakdown) => {
          wMap[b.dimension] = b.weight;
        });
        setWeights(wMap);
      }
    } catch (err) {
      console.error("Error fetching qualification data:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchHistory = async () => {
    try {
      const res = await fetch(`/api/v1/rfp/${documentId}/decision-history`);
      if (res.ok) {
        setHistory(await res.json());
      }
    } catch (err) {
      console.error("Error fetching decision history:", err);
    }
  };

  const handleRecalculate = async () => {
    setIsActionLoading(true);
    try {
      const res = await fetch(`/api/v1/rfp/${documentId}/recalculate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ weights }),
      });
      if (res.ok) {
        setData(await res.json());
        await fetchHistory();
      }
    } catch (err) {
      console.error("Error recalculating weights:", err);
    } finally {
      setIsActionLoading(false);
    }
  };

  const handleApprove = async () => {
    if (!reviewer.trim()) {
      alert("Reviewer name is required.");
      return;
    }
    setIsActionLoading(true);
    try {
      const res = await fetch(`/api/v1/rfp/${documentId}/approve-decision`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ reviewer, comments: approveComments }),
      });
      if (res.ok) {
        setData(await res.json());
        setApproveComments("");
        await fetchHistory();
      }
    } catch (err) {
      console.error("Error approving decision:", err);
    } finally {
      setIsActionLoading(false);
    }
  };

  const handleOverride = async () => {
    if (!overrideReason.trim()) {
      alert("Override reason is required.");
      return;
    }
    setIsActionLoading(true);
    try {
      const res = await fetch(`/api/v1/rfp/${documentId}/override-decision`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          new_decision: overrideDecision,
          override_reason: overrideReason,
          overridden_by: reviewer,
        }),
      });
      if (res.ok) {
        setData(await res.json());
        setOverrideReason("");
        await fetchHistory();
      }
    } catch (err) {
      console.error("Error overriding decision:", err);
    } finally {
      setIsActionLoading(false);
    }
  };

  const handleAddComment = async () => {
    if (!newCommentText.trim()) return;
    setIsActionLoading(true);
    try {
      const res = await fetch(`/api/v1/rfp/${documentId}/comments`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ author: newCommentAuthor, comment_text: newCommentText }),
      });
      if (res.ok) {
        setNewCommentText("");
        await fetchQualificationData();
      }
    } catch (err) {
      console.error("Error adding comment:", err);
    } finally {
      setIsActionLoading(false);
    }
  };

  const handleWeightChange = (dimension: string, value: number) => {
    setWeights((prev) => ({ ...prev, [dimension]: value }));
  };

  const getRecommendationColor = (rec: string) => {
    switch (rec?.toUpperCase()) {
      case "GO":
        return "bg-emerald-500/20 text-emerald-400 border-emerald-500/30";
      case "GO_WITH_CONDITIONS":
        return "bg-cyan-500/20 text-cyan-400 border-cyan-500/30";
      case "ESCALATE":
        return "bg-amber-500/20 text-amber-400 border-amber-500/30";
      case "NO_GO":
        return "bg-rose-500/20 text-rose-400 border-rose-500/30";
      default:
        return "bg-slate-800 text-slate-400 border-slate-700";
    }
  };

  if (isLoading) {
    return (
      <div className="py-20 flex flex-col justify-center items-center gap-3">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-400" />
        <span className="text-sm text-slate-400 font-mono">Synthesizing executive recommendation...</span>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="py-20 text-center border border-dashed border-slate-800 rounded-xl bg-slate-950/20">
        <h3 className="text-sm font-semibold text-slate-300">No Qualification Decision Found</h3>
        <p className="text-xs text-slate-500 max-w-sm mx-auto mt-1">
          Trigger the qualification engine to calculate Opportunity Scores and generate an explainable recommendation.
        </p>
      </div>
    );
  }

  return (
    <div className="border border-slate-800 bg-slate-900/60 backdrop-blur-xl rounded-xl p-6 mt-6 shadow-2xl space-y-8">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center border-b border-slate-800 pb-5">
        <div>
          <h2 className="text-xl font-bold bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
            Executive Decision & Qualification Console
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Consolidated decision intelligence linking sub-department evaluations, risk thresholds, and active policies
          </p>
        </div>
        <div className="mt-3 md:mt-0 flex gap-2">
          <span className={`px-3 py-1 text-xs font-bold rounded-full border ${getRecommendationColor(data.recommendation)}`}>
            REC: {data.recommendation}
          </span>
          <span className="bg-slate-950/40 text-[10px] text-slate-400 border border-slate-800 px-3 py-1 rounded-full font-mono flex items-center">
            STATUS: {data.status}
          </span>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-slate-950/40 border border-slate-800 p-4 rounded-xl space-y-1">
          <span className="text-[10px] text-slate-500 uppercase tracking-wider block font-semibold">Opportunity Score</span>
          <span className="text-3xl font-black text-indigo-400 block">{data.opportunity_score.toFixed(1)}<span className="text-xs text-slate-600 font-normal">/100</span></span>
          <span className="text-[10px] text-slate-400 block">Weighted average of core business criteria</span>
        </div>
        <div className="bg-slate-950/40 border border-slate-800 p-4 rounded-xl space-y-1">
          <span className="text-[10px] text-slate-500 uppercase tracking-wider block font-semibold">Estimated Win Probability</span>
          <span className="text-3xl font-black text-purple-400 block">{data.estimated_win_probability.toFixed(0)}%</span>
          <span className="text-[10px] text-amber-500/70 block">Decision-support estimate (not a guarantee)</span>
        </div>
        <div className="bg-slate-950/40 border border-slate-800 p-4 rounded-xl space-y-1">
          <span className="text-[10px] text-slate-500 uppercase tracking-wider block font-semibold">AI Confidence Level</span>
          <span className="text-3xl font-black text-teal-400 block">{(data.confidence * 100).toFixed(0)}%</span>
          <span className="text-[10px] text-slate-400 block">Gemini evaluation certainty index</span>
        </div>
        <div className="bg-slate-950/40 border border-slate-800 p-4 rounded-xl space-y-1">
          <span className="text-[10px] text-slate-500 uppercase tracking-wider block font-semibold">Blocking Issues Count</span>
          <span className="text-3xl font-black text-rose-400 block">{data.blocking_issues.length}</span>
          <span className="text-[10px] text-slate-400 block">Policies/veto constraints violated</span>
        </div>
      </div>

      {/* Main Grid: Executive Summary & Weight Adjuster */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Side: Summary & Explanations */}
        <div className="lg:col-span-2 space-y-6">
          <div className="border border-slate-800 bg-slate-950/20 p-5 rounded-xl space-y-3">
            <span className="text-xs font-bold text-slate-200 block border-b border-slate-900 pb-2">Executive Evaluation Summary</span>
            <p className="text-xs text-slate-300 leading-relaxed">{data.executive_summary}</p>
            <div className="text-xs text-slate-400 bg-slate-950 p-3 rounded border border-slate-900 mt-2">
              <span className="font-bold text-indigo-400 block mb-1">Win Probability Context:</span>
              {data.win_probability_explanation}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="border border-slate-800 bg-slate-950/20 p-4 rounded-lg space-y-2">
              <span className="text-xs font-bold text-emerald-400 block border-b border-slate-900 pb-1.5">Positive Capture Factors</span>
              <ul className="list-disc list-inside text-xs text-slate-400 space-y-1">
                {data.positive_factors.map((f, i) => <li key={i}>{f}</li>)}
              </ul>
            </div>
            <div className="border border-slate-800 bg-slate-950/20 p-4 rounded-lg space-y-2">
              <span className="text-xs font-bold text-rose-400 block border-b border-slate-900 pb-1.5">Risks / Negative Factors</span>
              <ul className="list-disc list-inside text-xs text-slate-400 space-y-1">
                {data.negative_factors.map((f, i) => <li key={i}>{f}</li>)}
              </ul>
            </div>
          </div>
        </div>

        {/* Right Side: Weight Adjustments Slider Panel */}
        <div className="border border-slate-800 bg-slate-950/40 p-5 rounded-xl space-y-4">
          <span className="text-xs font-bold text-slate-200 block border-b border-slate-900 pb-2">Scoring Weights Adjustments</span>
          <div className="space-y-4">
            {data.scoring_breakdowns.map((b) => (
              <div key={b.dimension} className="space-y-1">
                <div className="flex justify-between text-[11px] text-slate-400 font-mono">
                  <span className="capitalize">{b.dimension.replace("_", " ")}</span>
                  <span>{(weights[b.dimension] * 100).toFixed(0)}% (Raw: {b.raw_score.toFixed(0)})</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.05"
                  value={weights[b.dimension] || 0}
                  onChange={(e) => handleWeightChange(b.dimension, parseFloat(e.target.value))}
                  className="w-full h-1 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-indigo-500"
                />
              </div>
            ))}
            <button
              onClick={handleRecalculate}
              disabled={isActionLoading}
              className="w-full py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold rounded-lg transition duration-200 disabled:opacity-50"
            >
              {isActionLoading ? "Recalculating..." : "Recalculate Opportunity Score"}
            </button>
          </div>
        </div>
      </div>

      {/* Human-in-the-Loop Actions Panel */}
      <div className="border border-slate-800/80 bg-slate-950/40 rounded-xl p-6 space-y-6">
        <span className="text-xs font-bold text-slate-200 block border-b border-slate-900 pb-2">Human Authorization Workflow</span>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Block: Approval & comments */}
          <div className="space-y-4">
            <div className="space-y-1.5">
              <label className="text-[10px] text-slate-500 uppercase block font-semibold">Authorized Reviewer Name</label>
              <input
                type="text"
                placeholder="Name of executive signing off..."
                value={reviewer}
                onChange={(e) => setReviewer(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 text-xs text-slate-300 px-3 py-2.5 rounded-lg focus:outline-none focus:border-indigo-500"
              />
            </div>
            <div className="space-y-1.5">
              <label className="text-[10px] text-slate-500 uppercase block font-semibold">Approval Comments</label>
              <textarea
                placeholder="Include validation details or comments..."
                value={approveComments}
                onChange={(e) => setApproveComments(e.target.value)}
                className="w-full h-20 bg-slate-950 border border-slate-800 text-xs text-slate-300 p-3 rounded-lg focus:outline-none focus:border-indigo-500 resize-none"
              />
            </div>
            <button
              onClick={handleApprove}
              disabled={isActionLoading}
              className="px-5 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold rounded-lg transition disabled:opacity-50"
            >
              Approve Recommendation
            </button>
          </div>

          {/* Right Block: Override Forms */}
          <div className="space-y-4 border-t lg:border-t-0 lg:border-l border-slate-800 pt-4 lg:pt-0 lg:pl-8">
            <div className="space-y-1.5">
              <label className="text-[10px] text-slate-500 uppercase block font-semibold">Override Recommendation</label>
              <select
                value={overrideDecision}
                onChange={(e) => setOverrideDecision(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 text-xs text-slate-300 p-2.5 rounded-lg focus:outline-none focus:border-indigo-500"
              >
                <option value="GO">GO</option>
                <option value="GO_WITH_CONDITIONS">GO WITH CONDITIONS</option>
                <option value="ESCALATE">ESCALATE FOR EXECUTIVE REVIEW</option>
                <option value="NO_GO">NO_GO</option>
              </select>
            </div>
            <div className="space-y-1.5">
              <label className="text-[10px] text-slate-500 uppercase block font-semibold">Reason for Override</label>
              <textarea
                placeholder="Provide detailed explanation for the audit database log..."
                value={overrideReason}
                onChange={(e) => setOverrideReason(e.target.value)}
                className="w-full h-20 bg-slate-950 border border-slate-800 text-xs text-slate-300 p-3 rounded-lg focus:outline-none focus:border-indigo-500 resize-none"
              />
            </div>
            <button
              onClick={handleOverride}
              disabled={isActionLoading}
              className="px-5 py-2 bg-rose-600 hover:bg-rose-500 text-white text-xs font-bold rounded-lg transition disabled:opacity-50"
            >
              Submit Override
            </button>
          </div>
        </div>
      </div>

      {/* Collaboration logs & Decision Audits */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 pt-4 border-t border-slate-800">
        {/* Comments Section */}
        <div className="space-y-4">
          <span className="text-xs font-bold text-slate-200 block border-b border-slate-900 pb-2">Executive Collaboration Comments</span>
          <div className="flex gap-2">
            <input
              type="text"
              placeholder="Author..."
              value={newCommentAuthor}
              onChange={(e) => setNewCommentAuthor(e.target.value)}
              className="w-1/3 bg-slate-950 border border-slate-800 text-xs text-slate-300 px-3 py-2 rounded-lg focus:outline-none focus:border-indigo-500"
            />
            <input
              type="text"
              placeholder="Comment narrative..."
              value={newCommentText}
              onChange={(e) => setNewCommentText(e.target.value)}
              className="flex-1 bg-slate-950 border border-slate-800 text-xs text-slate-300 px-3 py-2 rounded-lg focus:outline-none focus:border-indigo-500"
            />
            <button
              onClick={handleAddComment}
              disabled={isActionLoading}
              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-bold rounded-lg border border-slate-700 transition"
            >
              Add Note
            </button>
          </div>

          <div className="space-y-2 mt-2 bg-slate-950/60 p-4 rounded-xl border border-slate-900 max-h-[220px] overflow-y-auto">
            {data.comments.length === 0 ? (
              <span className="text-xs text-slate-600 block text-center">No executive comments logged.</span>
            ) : (
              data.comments.map((comment) => (
                <div key={comment.id} className="text-xs text-slate-400 border-b border-slate-900 pb-2 mb-2 last:border-0 last:pb-0 last:mb-0">
                  <span className="text-[9px] text-slate-500 font-mono block">{comment.author} • {new Date(comment.timestamp).toLocaleString()}</span>
                  {comment.comment_text}
                </div>
              ))
            )}
          </div>
        </div>

        {/* Audit Trails History Section */}
        <div className="space-y-4">
          <span className="text-xs font-bold text-slate-200 block border-b border-slate-900 pb-2">Decision Trail History</span>
          <div className="space-y-2 bg-slate-950/60 p-4 rounded-xl border border-slate-900 max-h-[268px] overflow-y-auto">
            {history.length === 0 ? (
              <span className="text-xs text-slate-600 block text-center">No audit trail items found.</span>
            ) : (
              history.map((item) => (
                <div key={item.id} className="text-xs text-slate-400 border-b border-slate-900 pb-2.5 mb-2.5 last:border-0 last:pb-0 last:mb-0">
                  <div className="flex justify-between w-full">
                    <span className="text-[10px] font-bold text-slate-300 uppercase font-mono">{item.action}</span>
                    <span className="text-[9px] text-slate-500 font-mono">{new Date(item.timestamp).toLocaleString()}</span>
                  </div>
                  <div className="text-[11px] text-slate-400 mt-1 leading-relaxed">
                    By <span className="font-semibold text-slate-200">{item.actor}</span>: "{item.comments}"
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
