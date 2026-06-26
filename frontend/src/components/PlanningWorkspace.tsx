"use client";

import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";

interface Section {
  id: string;
  proposal_plan_id: string;
  title: string;
  content?: string;
  status: string;
  owner?: string;
  reviewer?: string;
  approver?: string;
  estimated_hours: number;
  dependencies: string[];
  priority: string;
  risk_level: string;
  is_human_editable: boolean;
}

interface Task {
  id: string;
  proposal_plan_id: string;
  parent_task_id?: string | null;
  title: string;
  owner: string;
  priority: string;
  estimated_hours: number;
  status: string;
  dependencies: string[];
  due_date?: string | null;
  is_critical_path: boolean;
}

interface Milestone {
  id: string;
  proposal_plan_id: string;
  name: string;
  start_date?: string | null;
  end_date?: string | null;
  status: string;
}

interface RequiredDocument {
  id: string;
  proposal_plan_id: string;
  document_name: string;
  document_type: string;
  status: string;
  required_by_date?: string | null;
  notes?: string | null;
}

interface ClarificationRequest {
  id: string;
  proposal_plan_id: string;
  question: string;
  reason?: string | null;
  related_requirement_id?: string | null;
  priority: string;
  owner: string;
  status: string;
  client_response?: string | null;
  impact?: string | null;
  resolution?: string | null;
}

interface HistoryRecord {
  id: string;
  proposal_plan_id: string;
  action: string;
  actor: string;
  comments: string;
  payload?: any;
  timestamp: string;
}

interface ProposalPlan {
  id: string;
  opportunity_id: string;
  title: string;
  client?: string;
  rfp_name?: string;
  proposal_type?: string;
  submission_deadline?: string | null;
  estimated_duration_days: number;
  estimated_effort_hours: number;
  complexity: string;
  priority: string;
  required_departments: string[];
  executive_sponsor?: string | null;
  proposal_owner?: string | null;
  status: string;
  version: string;
  planning_notes?: string | null;
  created_at: string;
  updated_at: string;
  sections: Section[];
  tasks: Task[];
  milestones: Milestone[];
  required_documents: RequiredDocument[];
  clarification_requests: ClarificationRequest[];
  history: HistoryRecord[];
}

interface ComplianceItem {
  id: string;
  compliance_matrix_id: string;
  requirement_id: string;
  proposal_section_id?: string | null;
  status: string;
  explanation?: string | null;
  responsible_department: string;
  responsible_owner: string;
  priority: string;
  mandatory: boolean;
  evidence_required?: string | null;
  source_page?: number | null;
  source_paragraph?: string | null;
  risk_if_missing?: string | null;
  dependencies: string[];
  reviewer: string;
  approval_status: string;
  traceability_links: string[];
  confidence: number;
  comments?: string | null;
}

interface PlanningWorkspaceProps {
  documentId: string;
}

export default function PlanningWorkspace({ documentId }: PlanningWorkspaceProps) {
  const [activeTab, setActiveTab] = useState<string>("dashboard");
  const [plan, setPlan] = useState<ProposalPlan | null>(null);
  const [complianceItems, setComplianceItems] = useState<ComplianceItem[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isComplianceLoading, setIsComplianceLoading] = useState<boolean>(false);
  const [isActionLoading, setIsActionLoading] = useState<boolean>(false);

  // Editing state for outline / sections
  const [editedSections, setEditedSections] = useState<Section[]>([]);
  const [planTitle, setPlanTitle] = useState<string>("");
  const [planClient, setPlanClient] = useState<string>("");
  const [planOwner, setPlanOwner] = useState<string>("");
  const [planNotes, setPlanNotes] = useState<string>("");

  // Approval gate state
  const [reviewerName, setReviewerName] = useState<string>("Proposal Director");
  const [gateComments, setGateComments] = useState<string>("");

  useEffect(() => {
    if (documentId) {
      fetchPlan();
      fetchCompliance();
    }
  }, [documentId]);

  const fetchPlan = async () => {
    setIsLoading(true);
    try {
      const res = await fetch(`/api/v1/proposals/${documentId}/planning`);
      if (res.ok) {
        const data: ProposalPlan = await res.json();
        setPlan(data);
        setEditedSections(data.sections || []);
        setPlanTitle(data.title || "");
        setPlanClient(data.client || "");
        setPlanOwner(data.proposal_owner || "");
        setPlanNotes(data.planning_notes || "");
      }
    } catch (err) {
      console.error("Error fetching proposal plan:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchCompliance = async () => {
    setIsComplianceLoading(true);
    try {
      const res = await fetch(`/api/v1/proposals/${documentId}/compliance-matrix`);
      if (res.ok) {
        const data = await res.json();
        setComplianceItems(data);
      }
    } catch (err) {
      console.error("Error fetching compliance matrix:", err);
    } finally {
      setIsComplianceLoading(false);
    }
  };

  const handleGenerate = async () => {
    setIsActionLoading(true);
    try {
      const res = await fetch(`/api/v1/proposals/${documentId}/planning`, {
        method: "POST",
      });
      if (res.ok) {
        const data: ProposalPlan = await res.json();
        setPlan(data);
        setEditedSections(data.sections || []);
        setPlanTitle(data.title || "");
        setPlanClient(data.client || "");
        setPlanOwner(data.proposal_owner || "");
        setPlanNotes(data.planning_notes || "");
        await fetchCompliance();
      } else {
        const errJson = await res.json();
        alert(errJson.detail || "Failed to generate planning package.");
      }
    } catch (err) {
      console.error("Error generating planning package:", err);
    } finally {
      setIsActionLoading(false);
    }
  };

  const handleUpdatePlan = async () => {
    if (!plan) return;
    setIsActionLoading(true);
    try {
      const res = await fetch(`/api/v1/proposals/${documentId}/update-plan`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: planTitle,
          client: planClient,
          proposal_owner: planOwner,
          planning_notes: planNotes,
          sections: editedSections.map((s) => ({
            id: s.id,
            title: s.title,
            owner: s.owner,
            reviewer: s.reviewer,
            approver: s.approver,
            estimated_hours: s.estimated_hours,
            priority: s.priority,
            risk_level: s.risk_level,
          })),
        }),
      });

      if (res.ok) {
        const data: ProposalPlan = await res.json();
        setPlan(data);
        setEditedSections(data.sections || []);
        alert("Planning package successfully updated!");
      } else {
        const errJson = await res.json();
        alert(errJson.detail || "Update failed.");
      }
    } catch (err) {
      console.error("Error updating plan:", err);
    } finally {
      setIsActionLoading(false);
    }
  };

  const handleLockUnlock = async (lock: boolean) => {
    setIsActionLoading(true);
    try {
      const endpoint = lock ? "lock-plan" : "unlock-plan";
      const res = await fetch(`/api/v1/proposals/${documentId}/${endpoint}`, {
        method: "POST",
      });
      if (res.ok) {
        const data = await res.json();
        setPlan(data);
        alert(lock ? "Proposal plan locked!" : "Proposal plan unlocked!");
      } else {
        const errJson = await res.json();
        alert(errJson.detail || "Action failed.");
      }
    } catch (err) {
      console.error("Error toggling lock state:", err);
    } finally {
      setIsActionLoading(false);
    }
  };

  const handleApproveReject = async (approve: boolean) => {
    if (!reviewerName.trim()) {
      alert("Reviewer name is required.");
      return;
    }
    setIsActionLoading(true);
    try {
      const res = await fetch(`/api/v1/proposals/${documentId}/approve-plan`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          reviewer: reviewerName,
          action: approve ? "APPROVE" : "REJECT",
          comments: gateComments,
        }),
      });

      if (res.ok) {
        const data = await res.json();
        setPlan(data);
        setGateComments("");
        alert(approve ? "Proposal plan approved!" : "Proposal plan rejected/reset to draft.");
      } else {
        const errJson = await res.json();
        alert(errJson.detail || "Action failed.");
      }
    } catch (err) {
      console.error("Error setting approval state:", err);
    } finally {
      setIsActionLoading(false);
    }
  };

  const moveSection = (index: number, direction: "up" | "down") => {
    if (plan?.status === "LOCKED") return;
    const newSecs = [...editedSections];
    if (direction === "up" && index > 0) {
      const temp = newSecs[index];
      newSecs[index] = newSecs[index - 1];
      newSecs[index - 1] = temp;
    } else if (direction === "down" && index < newSecs.length - 1) {
      const temp = newSecs[index];
      newSecs[index] = newSecs[index + 1];
      newSecs[index + 1] = temp;
    }
    setEditedSections(newSecs);
  };

  const updateSectionField = (index: number, field: keyof Section, value: any) => {
    if (plan?.status === "LOCKED") return;
    const newSecs = [...editedSections];
    newSecs[index] = { ...newSecs[index], [field]: value };
    setEditedSections(newSecs);
  };

  const getStatusBadgeColor = (status?: string) => {
    switch (status?.toUpperCase()) {
      case "APPROVED":
        return "bg-emerald-500/20 text-emerald-400 border-emerald-500/30";
      case "LOCKED":
        return "bg-rose-500/20 text-rose-400 border-rose-500/30";
      case "DRAFT":
      default:
        return "bg-amber-500/20 text-amber-400 border-amber-500/30";
    }
  };

  const getPriorityColor = (priority?: string) => {
    switch (priority?.toUpperCase()) {
      case "HIGH":
        return "text-rose-400 bg-rose-500/10 border border-rose-500/20";
      case "MEDIUM":
        return "text-amber-400 bg-amber-500/10 border border-amber-500/20";
      case "LOW":
      default:
        return "text-slate-400 bg-slate-500/10 border border-slate-500/20";
    }
  };

  if (isLoading) {
    return (
      <div className="py-20 flex flex-col justify-center items-center gap-3">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-400" />
        <span className="text-sm text-slate-400 font-mono">Loading proposal planning engine...</span>
      </div>
    );
  }

  if (!plan) {
    return (
      <div className="py-20 text-center border border-dashed border-slate-800 rounded-xl bg-slate-950/20">
        <h3 className="text-sm font-semibold text-slate-300">No Proposal Plan Found</h3>
        <p className="text-xs text-slate-500 max-w-sm mx-auto mt-1 mb-4">
          Establish an automated outline, Compliance Matrix, Work Breakdown Structure, and timelines.
        </p>
        <button
          onClick={handleGenerate}
          disabled={isActionLoading}
          className="px-6 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold rounded-lg transition disabled:opacity-50"
        >
          {isActionLoading ? "Generating Plan..." : "Generate proposal plan"}
        </button>
      </div>
    );
  }

  return (
    <div className="border border-slate-800 bg-slate-900/60 backdrop-blur-xl rounded-xl p-6 mt-6 shadow-2xl space-y-6">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center border-b border-slate-800 pb-5">
        <div>
          <h2 className="text-xl font-bold bg-gradient-to-r from-teal-400 to-indigo-400 bg-clip-text text-transparent">
            Proposal Planning & Execution Workspace
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Build custom outlines, compliance trackers, milestone schedules, and task assignments for the proposal captures
          </p>
        </div>
        <div className="mt-3 md:mt-0 flex gap-2 font-mono">
          <span className="bg-slate-950/40 text-[10px] text-slate-400 border border-slate-800 px-3 py-1 rounded-full flex items-center">
            VERSION: {plan.version}
          </span>
          <span className={`px-3 py-1 text-[10px] font-bold rounded-full border ${getStatusBadgeColor(plan.status)}`}>
            STATUS: {plan.status}
          </span>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-slate-800 overflow-x-auto gap-2 pb-px scrollbar-none">
        {[
          { id: "dashboard", label: "Dashboard & Gates" },
          { id: "outline", label: "Outline Builder" },
          { id: "compliance", label: "Compliance Matrix" },
          { id: "tasks", label: "WBS Task Board" },
          { id: "timeline", label: "Milestones Timeline" },
          { id: "attachments", label: "Document Checklist" },
          { id: "clarifications", label: "Clarification Center" },
          { id: "audit", label: "Audit Logs" },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2.5 text-xs font-semibold whitespace-nowrap transition border-b-2 -mb-px ${
              activeTab === tab.id
                ? "border-teal-500 text-teal-400"
                : "border-transparent text-slate-400 hover:text-slate-200"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Contents */}
      <div className="min-h-[400px]">
        {activeTab === "dashboard" && (
          <div className="space-y-6">
            {/* Metadata and Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-slate-950/40 border border-slate-800 p-4 rounded-xl space-y-1">
                <span className="text-[10px] text-slate-500 uppercase tracking-wider block font-semibold">Total Effort</span>
                <span className="text-2xl font-black text-teal-400 block">
                  {plan.estimated_effort_hours} <span className="text-xs text-slate-600 font-normal">hrs</span>
                </span>
                <span className="text-[10px] text-slate-400 block">Sum of outline section budgets</span>
              </div>
              <div className="bg-slate-950/40 border border-slate-800 p-4 rounded-xl space-y-1">
                <span className="text-[10px] text-slate-500 uppercase tracking-wider block font-semibold">Duration Plan</span>
                <span className="text-2xl font-black text-indigo-400 block">
                  {plan.estimated_duration_days} <span className="text-xs text-slate-600 font-normal">days</span>
                </span>
                <span className="text-[10px] text-slate-400 block">From kickoff to draft buffers</span>
              </div>
              <div className="bg-slate-950/40 border border-slate-800 p-4 rounded-xl space-y-1">
                <span className="text-[10px] text-slate-500 uppercase tracking-wider block font-semibold">Complexity Index</span>
                <span className="text-2xl font-black text-amber-400 block">{plan.complexity || "Medium"}</span>
                <span className="text-[10px] text-slate-400 block">Risk and structural severity</span>
              </div>
              <div className="bg-slate-950/40 border border-slate-800 p-4 rounded-xl space-y-1">
                <span className="text-[10px] text-slate-500 uppercase tracking-wider block font-semibold">Outline Chapters</span>
                <span className="text-2xl font-black text-purple-400 block">{plan.sections.length}</span>
                <span className="text-[10px] text-slate-400 block">Required proposal headings</span>
              </div>
            </div>

            {/* Document Details Form */}
            <div className="border border-slate-800 bg-slate-950/20 p-5 rounded-xl space-y-4">
              <span className="text-xs font-bold text-slate-200 block border-b border-slate-900 pb-2">Proposal Metadata</span>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-1.5">
                  <label className="text-[10px] text-slate-500 uppercase block font-semibold">Proposal Title</label>
                  <input
                    type="text"
                    disabled={plan.status === "LOCKED"}
                    value={planTitle}
                    onChange={(e) => setPlanTitle(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 text-xs text-slate-300 px-3 py-2 rounded-lg focus:outline-none focus:border-teal-500 disabled:opacity-50"
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="text-[10px] text-slate-500 uppercase block font-semibold">Target Client</label>
                  <input
                    type="text"
                    disabled={plan.status === "LOCKED"}
                    value={planClient}
                    onChange={(e) => setPlanClient(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 text-xs text-slate-300 px-3 py-2 rounded-lg focus:outline-none focus:border-teal-500 disabled:opacity-50"
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="text-[10px] text-slate-500 uppercase block font-semibold">Proposal Owner / Lead</label>
                  <input
                    type="text"
                    disabled={plan.status === "LOCKED"}
                    value={planOwner}
                    onChange={(e) => setPlanOwner(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 text-xs text-slate-300 px-3 py-2 rounded-lg focus:outline-none focus:border-teal-500 disabled:opacity-50"
                  />
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-[10px] text-slate-500 uppercase block font-semibold">Planning Notes & Strategies</label>
                <textarea
                  disabled={plan.status === "LOCKED"}
                  value={planNotes}
                  onChange={(e) => setPlanNotes(e.target.value)}
                  className="w-full h-24 bg-slate-950 border border-slate-800 text-xs text-slate-300 p-3 rounded-lg focus:outline-none focus:border-teal-500 disabled:opacity-50 resize-none"
                />
              </div>

              {plan.status !== "LOCKED" && (
                <button
                  onClick={handleUpdatePlan}
                  disabled={isActionLoading}
                  className="px-4 py-2 bg-teal-600 hover:bg-teal-500 text-white text-xs font-bold rounded-lg transition disabled:opacity-50"
                >
                  Save Metadata Changes
                </button>
              )}
            </div>

            {/* Approval Gate Panel */}
            <div className="border border-slate-800 bg-slate-950/40 rounded-xl p-6 space-y-6">
              <span className="text-xs font-bold text-slate-200 block border-b border-slate-900 pb-2">Human Approval Gate & Lock Controls</span>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Lock/Unlock Gate */}
                <div className="space-y-4">
                  <h4 className="text-xs font-bold text-slate-300">Locking Constraints</h4>
                  <p className="text-[11px] text-slate-400 leading-relaxed">
                    Locking the proposal plan freezes all chapter structures, compliance matrix allocations, timelines, and tasks. Locked plans cannot be updated or regenerated without an unlock event.
                  </p>
                  <div className="flex gap-2">
                    {plan.status !== "LOCKED" ? (
                      <button
                        onClick={() => handleLockUnlock(true)}
                        disabled={isActionLoading}
                        className="px-4 py-2 bg-rose-900/60 hover:bg-rose-900 border border-rose-700/50 text-rose-200 text-xs font-bold rounded-lg transition disabled:opacity-50"
                      >
                        Lock Plan Configuration
                      </button>
                    ) : (
                      <button
                        onClick={() => handleLockUnlock(false)}
                        disabled={isActionLoading}
                        className="px-4 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 text-xs font-bold rounded-lg transition disabled:opacity-50"
                      >
                        Unlock Plan Configuration
                      </button>
                    )}
                  </div>
                </div>

                {/* Director Approve/Reject */}
                <div className="space-y-4 border-t lg:border-t-0 lg:border-l border-slate-800 pt-4 lg:pt-0 lg:pl-8">
                  <h4 className="text-xs font-bold text-slate-300">Executive Approval Sign-Off</h4>
                  <div className="space-y-3">
                    <div className="space-y-1">
                      <label className="text-[10px] text-slate-500 uppercase block font-semibold">Approver Name</label>
                      <input
                        type="text"
                        value={reviewerName}
                        onChange={(e) => setReviewerName(e.target.value)}
                        className="w-full bg-slate-950 border border-slate-800 text-xs text-slate-300 px-3 py-2 rounded-lg focus:outline-none focus:border-teal-500"
                      />
                    </div>
                    <div className="space-y-1">
                      <label className="text-[10px] text-slate-500 uppercase block font-semibold">Review / Rejection Comments</label>
                      <textarea
                        placeholder="Provide details for approval or draft-reset rationale..."
                        value={gateComments}
                        onChange={(e) => setGateComments(e.target.value)}
                        className="w-full h-16 bg-slate-950 border border-slate-800 text-xs text-slate-300 p-2 rounded-lg focus:outline-none focus:border-teal-500 resize-none"
                      />
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleApproveReject(true)}
                        disabled={isActionLoading}
                        className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold rounded-lg transition disabled:opacity-50"
                      >
                        Approve Plan
                      </button>
                      <button
                        onClick={() => handleApproveReject(false)}
                        disabled={isActionLoading}
                        className="px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white text-xs font-bold rounded-lg transition disabled:opacity-50"
                      >
                        Reject & Reset to Draft
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === "outline" && (
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <div>
                <h3 className="text-sm font-semibold text-slate-200">Adaptive Outline Chapters</h3>
                <p className="text-xs text-slate-500">Reorder headings, set efforts, and assign sub-chapter owners.</p>
              </div>
              {plan.status !== "LOCKED" ? (
                <button
                  onClick={handleUpdatePlan}
                  disabled={isActionLoading}
                  className="px-4 py-2 bg-teal-600 hover:bg-teal-500 text-white text-xs font-bold rounded-lg transition disabled:opacity-50"
                >
                  Save Outline Changes
                </button>
              ) : (
                <span className="text-xs text-rose-400 font-mono">Plan is LOCKED. Outline cannot be updated.</span>
              )}
            </div>

            <div className="space-y-3 max-h-[600px] overflow-y-auto pr-1">
              {editedSections.map((sec, index) => (
                <div
                  key={sec.id || index}
                  className="border border-slate-800 bg-slate-950/40 p-4 rounded-xl flex flex-col md:flex-row gap-4 items-start md:items-center justify-between"
                >
                  <div className="flex items-center gap-3">
                    <div className="flex flex-col gap-1">
                      <button
                        disabled={plan.status === "LOCKED" || index === 0}
                        onClick={() => moveSection(index, "up")}
                        className="p-1 hover:bg-slate-800 rounded text-slate-500 hover:text-slate-300 disabled:opacity-30"
                      >
                        ▲
                      </button>
                      <button
                        disabled={plan.status === "LOCKED" || index === editedSections.length - 1}
                        onClick={() => moveSection(index, "down")}
                        className="p-1 hover:bg-slate-800 rounded text-slate-500 hover:text-slate-300 disabled:opacity-30"
                      >
                        ▼
                      </button>
                    </div>
                    <div className="space-y-1">
                      <input
                        type="text"
                        disabled={plan.status === "LOCKED"}
                        value={sec.title}
                        onChange={(e) => updateSectionField(index, "title", e.target.value)}
                        className="bg-transparent border-b border-transparent hover:border-slate-800 focus:border-teal-500 focus:outline-none text-sm font-semibold text-slate-200 px-1 py-0.5 w-64 disabled:opacity-80"
                      />
                      <span className="text-[10px] text-slate-500 block font-mono">ID: {sec.id.slice(0, 8)}</span>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 md:flex gap-3 items-center flex-1 justify-end w-full md:w-auto">
                    <div className="flex flex-col gap-0.5">
                      <span className="text-[9px] text-slate-500 uppercase font-semibold">Owner</span>
                      <input
                        type="text"
                        disabled={plan.status === "LOCKED"}
                        value={sec.owner || ""}
                        onChange={(e) => updateSectionField(index, "owner", e.target.value)}
                        className="bg-slate-950 border border-slate-800 text-[11px] text-slate-300 px-2 py-1 rounded w-28 focus:outline-none focus:border-teal-500 disabled:opacity-50"
                      />
                    </div>
                    <div className="flex flex-col gap-0.5">
                      <span className="text-[9px] text-slate-500 uppercase font-semibold">Reviewer</span>
                      <input
                        type="text"
                        disabled={plan.status === "LOCKED"}
                        value={sec.reviewer || ""}
                        onChange={(e) => updateSectionField(index, "reviewer", e.target.value)}
                        className="bg-slate-950 border border-slate-800 text-[11px] text-slate-300 px-2 py-1 rounded w-28 focus:outline-none focus:border-teal-500 disabled:opacity-50"
                      />
                    </div>
                    <div className="flex flex-col gap-0.5">
                      <span className="text-[9px] text-slate-500 uppercase font-semibold">Hours</span>
                      <input
                        type="number"
                        disabled={plan.status === "LOCKED"}
                        value={sec.estimated_hours}
                        onChange={(e) => updateSectionField(index, "estimated_hours", parseInt(e.target.value) || 0)}
                        className="bg-slate-950 border border-slate-800 text-[11px] text-slate-300 px-2 py-1 rounded w-16 focus:outline-none focus:border-teal-500 disabled:opacity-50"
                      />
                    </div>
                    <div className="flex flex-col gap-0.5">
                      <span className="text-[9px] text-slate-500 uppercase font-semibold">Risk</span>
                      <select
                        disabled={plan.status === "LOCKED"}
                        value={sec.risk_level || "Low"}
                        onChange={(e) => updateSectionField(index, "risk_level", e.target.value)}
                        className="bg-slate-950 border border-slate-800 text-[11px] text-slate-300 p-1 rounded w-20 focus:outline-none focus:border-teal-500 disabled:opacity-50"
                      >
                        <option value="Low">Low</option>
                        <option value="Medium">Medium</option>
                        <option value="High">High</option>
                      </select>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === "compliance" && (
          <div className="space-y-4">
            <div>
              <h3 className="text-sm font-semibold text-slate-200">RFP Compliance Matrix Mapping</h3>
              <p className="text-xs text-slate-500">Every requirement extracted must be accounted for and traceably assigned.</p>
            </div>

            {isComplianceLoading ? (
              <div className="py-10 text-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-teal-400 mx-auto" />
                <span className="text-xs text-slate-400 mt-2 block font-mono">Loading matrix rows...</span>
              </div>
            ) : complianceItems.length === 0 ? (
              <div className="py-10 text-center border border-dashed border-slate-800 rounded-xl bg-slate-950/20">
                <span className="text-xs text-slate-500">No compliance obligations mapped. Generate plan above first.</span>
              </div>
            ) : (
              <div className="overflow-x-auto border border-slate-800 rounded-xl bg-slate-950/20">
                <table className="w-full border-collapse text-left text-xs text-slate-400">
                  <thead className="bg-slate-950 text-slate-200 font-mono text-[10px] uppercase border-b border-slate-800">
                    <tr>
                      <th className="p-3">Ref ID</th>
                      <th className="p-3">Requirement</th>
                      <th className="p-3">Page/Para</th>
                      <th className="p-3">Responsible BU</th>
                      <th className="p-3">Owner</th>
                      <th className="p-3">Approval</th>
                      <th className="p-3">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-850">
                    {complianceItems.map((item) => (
                      <tr key={item.id} className="hover:bg-slate-900/40">
                        <td className="p-3 font-mono text-[10px] text-teal-400">{item.requirement_id.slice(0, 8)}</td>
                        <td className="p-3 max-w-xs truncate" title={item.evidence_required || ""}>
                          {item.evidence_required || "N/A"}
                        </td>
                        <td className="p-3 font-mono text-[10px]">
                          p.{item.source_page || "0"}, para.{item.source_paragraph ? item.source_paragraph.slice(0, 10) : "0"}
                        </td>
                        <td className="p-3 font-semibold text-slate-300">{item.responsible_department}</td>
                        <td className="p-3">{item.responsible_owner}</td>
                        <td className="p-3 font-mono text-[10px]">{item.approval_status}</td>
                        <td className="p-3">
                          <span className="px-2 py-0.5 rounded-full text-[9px] font-bold bg-slate-850 text-slate-300 border border-slate-700">
                            {item.status}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {activeTab === "tasks" && (
          <div className="space-y-4">
            <div>
              <h3 className="text-sm font-semibold text-slate-200">Work Breakdown Structure (WBS) Kanban</h3>
              <p className="text-xs text-slate-500">Proposal operations divided into specific execution states.</p>
            </div>

            {plan.tasks.length === 0 ? (
              <div className="py-10 text-center border border-dashed border-slate-800 rounded-xl bg-slate-950/20">
                <span className="text-xs text-slate-500">No tasks generated for this plan.</span>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                {["TODO", "IN_PROGRESS", "REVIEW", "DONE"].map((column) => {
                  const filtered = plan.tasks.filter((t) => t.status?.toUpperCase() === column);
                  return (
                    <div key={column} className="bg-slate-950/40 border border-slate-800 rounded-xl p-4 flex flex-col min-h-[300px]">
                      <div className="flex justify-between items-center mb-3 pb-2 border-b border-slate-800">
                        <span className="text-xs font-bold text-slate-300 font-mono tracking-wider">{column}</span>
                        <span className="text-[10px] bg-slate-900 px-2 py-0.5 rounded-full text-slate-500 font-mono">
                          {filtered.length}
                        </span>
                      </div>
                      <div className="space-y-3 flex-1 overflow-y-auto">
                        {filtered.map((task) => (
                          <div key={task.id} className="bg-slate-900 border border-slate-850 p-3 rounded-lg space-y-2 hover:border-slate-700 transition">
                            <h5 className="text-xs font-bold text-slate-200 leading-snug">{task.title}</h5>
                            <div className="flex justify-between items-center text-[10px] text-slate-400">
                              <span>👤 {task.owner}</span>
                              <span className="font-mono text-teal-400">{task.estimated_hours} hrs</span>
                            </div>
                            <div className="flex justify-between items-center text-[9px] pt-1.5 border-t border-slate-950">
                              <span className={`px-2 py-0.5 rounded font-bold ${getPriorityColor(task.priority)}`}>
                                {task.priority}
                              </span>
                              {task.is_critical_path && (
                                <span className="text-rose-400 font-mono font-bold animate-pulse">⚡ CRITICAL</span>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}

        {activeTab === "timeline" && (
          <div className="space-y-4">
            <div>
              <h3 className="text-sm font-semibold text-slate-200">Chronological Proposal Milestones</h3>
              <p className="text-xs text-slate-500">Timeline checkpoints mapped for delivery assurance.</p>
            </div>

            {plan.milestones.length === 0 ? (
              <div className="py-10 text-center border border-dashed border-slate-800 rounded-xl bg-slate-950/20">
                <span className="text-xs text-slate-500">No milestones mapped.</span>
              </div>
            ) : (
              <div className="space-y-6 relative before:absolute before:left-3 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-800">
                {plan.milestones.map((ms, index) => (
                  <div key={ms.id || index} className="flex gap-4 items-start relative pl-8">
                    <span className="absolute left-1.5 top-1.5 w-3 h-3 rounded-full bg-teal-500 border-2 border-slate-900 z-10" />
                    <div className="bg-slate-950/40 border border-slate-800 p-4 rounded-xl flex-1 grid grid-cols-1 md:grid-cols-3 gap-3 items-center">
                      <div>
                        <h4 className="text-xs font-bold text-slate-200">{ms.name}</h4>
                        <span className="text-[10px] bg-slate-900 border border-slate-800 px-2 py-0.5 rounded-full text-slate-400 font-mono mt-1 inline-block">
                          {ms.status}
                        </span>
                      </div>
                      <div className="text-xs text-slate-400 font-mono">
                        <div>Start: {ms.start_date ? new Date(ms.start_date).toLocaleDateString() : "TBD"}</div>
                        <div>End: {ms.end_date ? new Date(ms.end_date).toLocaleDateString() : "TBD"}</div>
                      </div>
                      <div className="text-right">
                        <span className="text-xs text-teal-400 font-mono font-semibold">
                          Checkpoint {index + 1}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === "attachments" && (
          <div className="space-y-4">
            <div>
              <h3 className="text-sm font-semibold text-slate-200">Required Attachments & Documents Checklist</h3>
              <p className="text-xs text-slate-500">Track standard credentials, resumes, and certification files required by client.</p>
            </div>

            {plan.required_documents.length === 0 ? (
              <div className="py-10 text-center border border-dashed border-slate-800 rounded-xl bg-slate-950/20">
                <span className="text-xs text-slate-500">No required documents listed.</span>
              </div>
            ) : (
              <div className="overflow-x-auto border border-slate-800 rounded-xl bg-slate-950/20">
                <table className="w-full border-collapse text-left text-xs text-slate-400">
                  <thead className="bg-slate-950 text-slate-200 font-mono text-[10px] uppercase border-b border-slate-800">
                    <tr>
                      <th className="p-3">Document Name</th>
                      <th className="p-3">Document Type</th>
                      <th className="p-3">Required By</th>
                      <th className="p-3">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-850">
                    {plan.required_documents.map((doc) => (
                      <tr key={doc.id} className="hover:bg-slate-900/40">
                        <td className="p-3 font-semibold text-slate-200">{doc.document_name}</td>
                        <td className="p-3 font-mono text-[10px]">{doc.document_type}</td>
                        <td className="p-3 font-mono text-[10px]">
                          {doc.required_by_date ? new Date(doc.required_by_date).toLocaleDateString() : "TBD"}
                        </td>
                        <td className="p-3">
                          <span className="px-2 py-0.5 rounded-full text-[9px] font-bold bg-amber-500/10 text-amber-400 border border-amber-500/20">
                            {doc.status}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {activeTab === "clarifications" && (
          <div className="space-y-4">
            <div>
              <h3 className="text-sm font-semibold text-slate-200">Client Clarification Center</h3>
              <p className="text-xs text-slate-500">Track and manage clarification questions compiled for submission to client.</p>
            </div>

            {plan.clarification_requests.length === 0 ? (
              <div className="py-10 text-center border border-dashed border-slate-800 rounded-xl bg-slate-950/20">
                <span className="text-xs text-slate-500">No client clarification questions compiled.</span>
              </div>
            ) : (
              <div className="space-y-3">
                {plan.clarification_requests.map((req) => (
                  <div key={req.id} className="border border-slate-800 bg-slate-950/40 p-4 rounded-xl space-y-3">
                    <div className="flex justify-between items-start">
                      <div>
                        <h4 className="text-xs font-bold text-slate-200">{req.question}</h4>
                        {req.reason && <p className="text-[11px] text-slate-400 mt-1">{req.reason}</p>}
                      </div>
                      <span className="text-[9px] bg-slate-900 px-2 py-0.5 rounded-full text-slate-500 font-mono">
                        {req.status}
                      </span>
                    </div>

                    {req.client_response && (
                      <div className="bg-slate-950 p-3 rounded-lg border border-slate-900 text-xs">
                        <span className="text-[10px] font-bold text-teal-400 block mb-1">Client Response:</span>
                        <p className="text-slate-300 font-mono">{req.client_response}</p>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === "audit" && (
          <div className="space-y-4">
            <div>
              <h3 className="text-sm font-semibold text-slate-200">Proposal Plan Audit Trail</h3>
              <p className="text-xs text-slate-500">Traceable tracking of all adjustments, lock changes, and approvals.</p>
            </div>

            {plan.history.length === 0 ? (
              <div className="py-10 text-center border border-dashed border-slate-800 rounded-xl bg-slate-950/20">
                <span className="text-xs text-slate-500">No audit logs recorded.</span>
              </div>
            ) : (
              <div className="space-y-2 bg-slate-950/60 p-4 rounded-xl border border-slate-900 max-h-[400px] overflow-y-auto">
                {plan.history.map((record) => (
                  <div key={record.id} className="text-xs text-slate-400 border-b border-slate-900 pb-2 mb-2 last:border-0 last:pb-0 last:mb-0">
                    <div className="flex justify-between w-full">
                      <span className="text-[10px] font-bold text-slate-300 uppercase font-mono">{record.action}</span>
                      <span className="text-[9px] text-slate-500 font-mono">{new Date(record.timestamp).toLocaleString()}</span>
                    </div>
                    <div className="text-[11px] text-slate-400 mt-1">
                      By <span className="font-semibold text-slate-200">{record.actor}</span>: "{record.comments}"
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
