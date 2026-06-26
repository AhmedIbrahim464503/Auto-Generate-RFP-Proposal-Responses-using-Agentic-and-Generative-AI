"use client";

import React, { useState, useEffect } from "react";

interface DepartmentStatus {
  status: string; // PENDING, REVIEWED, APPROVED, OVERRIDDEN, ESCALATED
  decision?: string;
  confidence?: number;
  reviewer?: string;
  escalation_required: boolean;
  is_overridden: boolean;
  override_decision?: string;
  override_reason?: string;
  findings: string[];
  risks: string[];
  evidence?: string;
  recommendations: string[];
}

interface AllReviewsStatus {
  opportunity_id: string;
  financial: DepartmentStatus;
  legal: DepartmentStatus;
  operations: DepartmentStatus;
  technical: DepartmentStatus;
}

interface AggregatedRisk {
  severity: string;
  likelihood: string;
  business_impact: string;
  mitigation: string;
  owning_department: string;
  description: string;
}

interface DepartmentReviewProps {
  documentId: string;
}

export default function DepartmentReview({ documentId }: DepartmentReviewProps) {
  const [activeDept, setActiveDept] = useState<string>("financial");
  const [reviewsStatus, setReviewsStatus] = useState<AllReviewsStatus | null>(null);
  const [aggregatedRisks, setAggregatedRisks] = useState<AggregatedRisk[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isProcessing, setIsProcessing] = useState<boolean>(false);

  // Override Form states
  const [overrideDecision, setOverrideDecision] = useState<string>("GO");
  const [overrideReason, setOverrideReason] = useState<string>("");
  const [overrideUser, setOverrideUser] = useState<string>("Capture Manager");
  const [comments, setComments] = useState<string[]>([]);
  const [newComment, setNewComment] = useState<string>("");

  useEffect(() => {
    if (documentId) {
      fetchReviews();
    }
  }, [documentId]);

  const fetchReviews = async () => {
    setIsLoading(true);
    try {
      const [statusRes, risksRes] = await Promise.all([
        fetch(`/api/v1/rfp/${documentId}/reviews`),
        fetch(`/api/v1/rfp/${documentId}/risks`),
      ]);
      if (statusRes.ok) setReviewsStatus(await statusRes.json());
      if (risksRes.ok) setAggregatedRisks(await risksRes.json());
    } catch (err) {
      console.error("Error fetching reviews:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const triggerReview = async (dept: string) => {
    setIsProcessing(true);
    try {
      let url = `/api/v1/rfp/${documentId}/reviews/${dept}`;
      if (dept === "financial") {
        url += "?payment_terms=NET45&insurance_limit=6000000"; // Test rules triggering
      }
      const res = await fetch(url, { method: "POST" });
      if (res.ok) {
        await fetchReviews();
      }
    } catch (err) {
      console.error(`Error triggering ${dept} review:`, err);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleApprove = async (dept: string) => {
    setIsProcessing(true);
    try {
      const res = await fetch(`/api/v1/rfp/${documentId}/reviews/${dept}/approve`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ reviewer: "Human Reviewer" }),
      });
      if (res.ok) {
        await fetchReviews();
      }
    } catch (err) {
      console.error(`Approval error:`, err);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleOverride = async (dept: string) => {
    if (!overrideReason.trim()) {
      alert("Override reason is required.");
      return;
    }
    setIsProcessing(true);
    try {
      const res = await fetch(`/api/v1/rfp/${documentId}/reviews/${dept}/override`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          new_decision: overrideDecision,
          override_reason: overrideReason,
          overridden_by: overrideUser,
        }),
      });
      if (res.ok) {
        setOverrideReason("");
        await fetchReviews();
      }
    } catch (err) {
      console.error(`Override error:`, err);
    } finally {
      setIsProcessing(false);
    }
  };

  const addComment = () => {
    if (newComment.trim()) {
      setComments([...comments, newComment]);
      setNewComment("");
    }
  };

  const getStatusBadgeColor = (status: string) => {
    switch (status) {
      case "APPROVED":
        return "bg-emerald-500/20 text-emerald-300 border-emerald-500/40";
      case "OVERRIDDEN":
        return "bg-cyan-500/20 text-cyan-300 border-cyan-500/40";
      case "ESCALATED":
        return "bg-amber-500/20 text-amber-300 border-amber-500/40";
      case "REVIEWED":
        return "bg-blue-500/20 text-blue-300 border-blue-500/40";
      default:
        return "bg-slate-500/20 text-slate-400 border-slate-800";
    }
  };

  const getDecisionBadgeColor = (decision?: string) => {
    switch (decision?.toUpperCase()) {
      case "GO":
        return "bg-emerald-500/20 text-emerald-400 border-emerald-500/20";
      case "NO_GO":
        return "bg-rose-500/20 text-rose-400 border-rose-500/20";
      case "CONDITIONALLY_GO":
        return "bg-amber-500/20 text-amber-400 border-amber-500/20";
      default:
        return "bg-slate-900 text-slate-400 border-slate-800";
    }
  };

  const activeReview: DepartmentStatus | undefined = reviewsStatus
    ? (reviewsStatus as any)[activeDept]
    : undefined;

  return (
    <div className="border border-slate-800 bg-slate-900/60 backdrop-blur-xl rounded-xl p-6 mt-6 shadow-2xl">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center border-b border-slate-800 pb-4 mb-6">
        <div>
          <h2 className="text-xl font-bold bg-gradient-to-r from-teal-400 to-cyan-400 bg-clip-text text-transparent">
            Enterprise Department Review Engine
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Simulate independent audits for Financial, Legal, Operations, and Technical bidding feasibility
          </p>
        </div>
        <div className="flex gap-2 mt-3 md:mt-0">
          <button
            onClick={() => triggerReview(activeDept)}
            disabled={isProcessing}
            className="px-4 py-2 bg-gradient-to-r from-teal-500 to-cyan-600 hover:from-teal-400 hover:to-cyan-500 text-white text-xs font-semibold rounded-lg shadow-lg shadow-cyan-900/40 transition duration-300 disabled:opacity-50"
          >
            {isProcessing ? "Analyzing..." : `Trigger ${activeDept.toUpperCase()} Review`}
          </button>
        </div>
      </div>

      {isLoading ? (
        <div className="py-20 flex flex-col justify-center items-center gap-3">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-teal-400" />
          <span className="text-sm text-slate-400">Evaluating departmental criteria...</span>
        </div>
      ) : !reviewsStatus ? (
        <div className="py-20 text-center border border-dashed border-slate-800 rounded-xl bg-slate-950/20">
          <h3 className="text-sm font-semibold text-slate-300">No Review Records Found</h3>
          <p className="text-xs text-slate-500 max-w-sm mx-auto mt-1">
            Select a department tab below and click analyze to start generating structured feasibility reviews.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Department Selection Sidebar */}
          <div className="lg:col-span-1 space-y-2 border-r border-slate-800 pr-4">
            {["financial", "legal", "operations", "technical"].map((dept) => {
              const status: DepartmentStatus = (reviewsStatus as any)[dept];
              return (
                <button
                  key={dept}
                  onClick={() => setActiveDept(dept)}
                  className={`w-full text-left p-3 rounded-lg border transition-all duration-200 flex flex-col justify-between gap-1.5 ${
                    activeDept === dept
                      ? "bg-slate-800/80 border-teal-500/50"
                      : "bg-slate-950/20 border-slate-800 hover:border-slate-700"
                  }`}
                >
                  <div className="flex justify-between items-center w-full">
                    <span className="text-xs font-bold uppercase tracking-wider text-slate-200">{dept}</span>
                    <span className={`text-[9px] px-1.5 py-0.5 rounded border font-mono ${getStatusBadgeColor(status.status)}`}>
                      {status.status}
                    </span>
                  </div>
                  {status.status !== "PENDING" && (
                    <div className="flex justify-between items-center w-full mt-1">
                      <span className={`text-[9px] px-1.5 py-0.2 rounded border font-semibold ${getDecisionBadgeColor(status.is_overridden ? status.override_decision : status.decision)}`}>
                        {status.is_overridden ? status.override_decision : status.decision}
                      </span>
                      <span className="text-[10px] text-teal-400 font-semibold">
                        {status.confidence ? `${(status.confidence * 100).toFixed(0)}%` : ""}
                      </span>
                    </div>
                  )}
                </button>
              );
            })}
          </div>

          {/* Active Review Details Workspace */}
          <div className="lg:col-span-3 space-y-6">
            {activeReview && activeReview.status !== "PENDING" ? (
              <div className="space-y-6">
                {/* Decision Panel */}
                <div className="border border-slate-800 bg-slate-950/40 rounded-xl p-4 flex flex-col md:flex-row justify-between gap-4">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-slate-500">Decision Outcome:</span>
                      <span className={`text-xs font-bold px-2 py-0.5 rounded border ${getDecisionBadgeColor(activeReview.is_overridden ? activeReview.override_decision : activeReview.decision)}`}>
                        {activeReview.is_overridden ? activeReview.override_decision : activeReview.decision}
                      </span>
                      {activeReview.is_overridden && (
                        <span className="text-[10px] text-cyan-400 bg-cyan-950/20 border border-cyan-500/20 px-2 py-0.5 rounded font-mono">
                          OVERRIDDEN BY {activeReview.reviewer || "HUMAN"}
                        </span>
                      )}
                      {activeReview.escalation_required && (
                        <span className="text-[10px] text-amber-400 bg-amber-950/20 border border-amber-500/20 px-2 py-0.5 rounded font-mono">
                          ESCALATED
                        </span>
                      )}
                    </div>
                    <div className="text-xs text-slate-400 pt-1 leading-relaxed">
                      <span className="text-slate-500 font-semibold">Evidence Quote:</span> "{activeReview.evidence}"
                    </div>
                  </div>
                  <div className="flex flex-col items-end justify-center min-w-[100px] border-t md:border-t-0 md:border-l border-slate-800 pt-2 md:pt-0 md:pl-4">
                    <span className="text-[9px] text-slate-500 uppercase tracking-wider">AI Confidence</span>
                    <span className="text-2xl font-black text-teal-400">
                      {activeReview.confidence ? `${(activeReview.confidence * 100).toFixed(0)}%` : "N/A"}
                    </span>
                  </div>
                </div>

                {/* Audit, Findings, Recommendations */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="border border-slate-800 bg-slate-950/20 rounded-lg p-4 space-y-3">
                    <span className="text-xs font-bold text-slate-300 block border-b border-slate-900 pb-1.5">Key Findings</span>
                    <ul className="list-disc list-inside text-xs text-slate-400 space-y-1.5">
                      {activeReview.findings.map((f, i) => <li key={i}>{f}</li>)}
                    </ul>
                  </div>
                  <div className="border border-slate-800 bg-slate-950/20 rounded-lg p-4 space-y-3">
                    <span className="text-xs font-bold text-slate-300 block border-b border-slate-900 pb-1.5">Recommendations</span>
                    <ul className="list-disc list-inside text-xs text-slate-400 space-y-1.5">
                      {activeReview.recommendations.map((r, i) => <li key={i}>{r}</li>)}
                    </ul>
                  </div>
                </div>

                {/* Risk Register section */}
                <div className="border border-slate-800 bg-slate-950/20 rounded-lg p-4 space-y-3">
                  <span className="text-xs font-bold text-rose-400 block border-b border-rose-950/20 pb-1.5">Consolidated Departmental Risks</span>
                  <div className="space-y-2">
                    {activeReview.risks.map((risk, i) => (
                      <div key={i} className="text-xs text-slate-400 bg-slate-950/60 p-2.5 rounded border border-slate-800/60 leading-relaxed">
                        {risk}
                      </div>
                    ))}
                  </div>
                </div>

                {/* HITL Action Controls */}
                <div className="border border-slate-800/80 bg-slate-950/40 rounded-xl p-6 space-y-6">
                  <span className="text-xs font-bold text-slate-300 block border-b border-slate-900 pb-2">Human-in-the-Loop Controls</span>
                  <div className="flex gap-4">
                    <button
                      onClick={() => handleApprove(activeDept)}
                      className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold rounded-lg shadow transition"
                    >
                      Approve AI Review
                    </button>
                  </div>

                  {/* Override controls */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 border-t border-slate-900">
                    <div className="space-y-2">
                      <label className="text-[10px] text-slate-500 uppercase block font-semibold">Override Decision</label>
                      <select
                        value={overrideDecision}
                        onChange={(e) => setOverrideDecision(e.target.value)}
                        className="w-full bg-slate-950 border border-slate-800 text-xs text-slate-300 p-2.5 rounded-lg focus:outline-none focus:border-teal-500"
                      >
                        <option value="GO">GO</option>
                        <option value="NO_GO">NO_GO</option>
                        <option value="CONDITIONALLY_GO">CONDITIONALLY_GO</option>
                      </select>
                    </div>
                    <div className="md:col-span-2 space-y-2">
                      <label className="text-[10px] text-slate-500 uppercase block font-semibold">Reason for Override</label>
                      <div className="flex gap-2">
                        <input
                          type="text"
                          placeholder="Provide explanation for database audit logging..."
                          value={overrideReason}
                          onChange={(e) => setOverrideReason(e.target.value)}
                          className="flex-1 bg-slate-950 border border-slate-800 text-xs text-slate-300 px-3 py-2.5 rounded-lg focus:outline-none focus:border-teal-500"
                        />
                        <button
                          onClick={() => handleOverride(activeDept)}
                          className="px-4 py-2.5 bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold rounded-lg transition"
                        >
                          Override
                        </button>
                      </div>
                    </div>
                  </div>

                  {/* Comments/Notes section */}
                  <div className="space-y-3 pt-4 border-t border-slate-900">
                    <label className="text-[10px] text-slate-500 uppercase block font-semibold">Collaboration Logs / Notes</label>
                    <div className="flex gap-2">
                      <input
                        type="text"
                        placeholder="Add review feedback note..."
                        value={newComment}
                        onChange={(e) => setNewComment(e.target.value)}
                        className="flex-1 bg-slate-950 border border-slate-800 text-xs text-slate-300 px-3 py-2 rounded-lg focus:outline-none focus:border-teal-500"
                      />
                      <button
                        onClick={addComment}
                        className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold rounded-lg border border-slate-700 transition"
                      >
                        Add Note
                      </button>
                    </div>
                    {comments.length > 0 && (
                      <div className="space-y-2 mt-2 bg-slate-950/60 p-3 rounded-lg border border-slate-900 max-h-[150px] overflow-y-auto">
                        {comments.map((comment, index) => (
                          <div key={index} className="text-xs text-slate-400 leading-relaxed border-b border-slate-900 pb-1.5 mb-1.5 last:border-b-0 last:pb-0 last:mb-0">
                            <span className="text-[9px] text-slate-500 font-mono block">Reviewer • {new Date().toLocaleTimeString()}</span>
                            {comment}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ) : (
              <div className="py-20 text-center border border-dashed border-slate-800 rounded-xl bg-slate-950/20">
                <svg className="mx-auto h-12 w-12 text-slate-600 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <h3 className="text-sm font-semibold text-slate-300">feasisibilty check pending</h3>
                <p className="text-xs text-slate-500 max-w-sm mx-auto mt-1">
                  Trigger the AI agent feasibility review above to generate explainable departmental results for {activeDept}.
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
