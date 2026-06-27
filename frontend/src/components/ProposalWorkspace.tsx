"use client";

import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";

import ProposalReviewDashboard from "./ProposalReviewDashboard";
import WorkflowMonitor from "./WorkflowMonitor";

interface Citation {
  id: string;
  generated_section_id: string;
  paragraph_index: number;
  knowledge_asset_id?: string | null;
  knowledge_chunk_id?: string | null;
  requirement_id?: string | null;
  compliance_item_id?: string | null;
  source_title: string;
  source_location?: string | null;
  confidence: number;
}


interface EvidenceLink {
  id: string;
  generated_section_id: string;
  source_type: string;
  source_id: string;
  relevance_score: number;
}

interface GeneratedSection {
  id: string;
  proposal_plan_id: string;
  proposal_section_id: string;
  chunk_index: number;
  content: string;
  tone_style: string;
  word_count: number;
  confidence: number;
  quality_score: number;
  prompt_version: string;
  model_version: string;
  created_at: string;
  updated_at: string;
  citations: Citation[];
  evidence_links: EvidenceLink[];
}

interface ProposalSection {
  id: string;
  proposal_plan_id: string;
  title: string;
  owner?: string | null;
  reviewer?: string | null;
  estimated_hours: number;
  priority: string;
  risk_level: string;
}

interface HistoryItem {
  id: string;
  proposal_plan_id: string;
  proposal_section_id: string;
  action: string;
  actor: string;
  comments?: string | null;
  content_snapshot: string;
  timestamp: string;
}

interface ProposalWorkspaceProps {
  documentId: string;
}

export default function ProposalWorkspace({ documentId }: ProposalWorkspaceProps) {
  const [sections, setSections] = useState<ProposalSection[]>([]);
  const [generatedMap, setGeneratedMap] = useState<Record<string, GeneratedSection>>({});
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [selectedSection, setSelectedSection] = useState<ProposalSection | null>(null);
  
  // Selection details
  const [toneStyle, setToneStyle] = useState<string>("Professional");
  const [additionalContext, setAdditionalContext] = useState<string>("");
  const [activeViewTab, setActiveViewTab] = useState<string>("content"); // content, citations, history
  
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isActionLoading, setIsActionLoading] = useState<boolean>(false);

  useEffect(() => {
    if (documentId) {
      fetchOutlineAndGenerated();
    }
  }, [documentId]);

  const fetchOutlineAndGenerated = async () => {
    setIsLoading(true);
    try {
      // 1. Fetch Plan Outline
      const outlineRes = await fetch(`/api/v1/proposals/${documentId}/outline`);
      let planId = "";
      if (outlineRes.ok) {
        const outlineData = await outlineRes.json();
        setSections(outlineData);
        if (outlineData.length > 0) {
          setSelectedSection(outlineData[0]);
          planId = outlineData[0].proposal_plan_id;
        }
      }

      // 2. Fetch Generated Sections
      if (planId) {
        const genRes = await fetch(`/api/v1/proposals/${planId}/generated`);
        if (genRes.ok) {
          const genData: GeneratedSection[] = await genRes.json();
          const gMap: Record<string, GeneratedSection> = {};
          genData.forEach((gs) => {
            gMap[gs.proposal_section_id] = gs;
          });
          setGeneratedMap(gMap);
        }

        // 3. Fetch History
        const histRes = await fetch(`/api/v1/proposals/${planId}/generation-history`);
        if (histRes.ok) {
          setHistory(await histRes.json());
        }
      }
    } catch (err) {
      console.error("Error fetching outline and generated proposals:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateAll = async () => {
    if (sections.length === 0) return;
    const planId = sections[0].proposal_plan_id;
    setIsActionLoading(true);
    try {
      const res = await fetch(`/api/v1/proposals/${planId}/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ tone_style: toneStyle, actor: "Bid Manager" }),
      });
      if (res.ok) {
        alert("Full proposal content successfully generated!");
        await fetchOutlineAndGenerated();
      } else {
        const errJson = await res.json();
        alert(errJson.detail || "Generation failed.");
      }
    } catch (err) {
      console.error("Error generating all sections:", err);
    } finally {
      setIsActionLoading(false);
    }
  };

  const handleGenerateSingle = async () => {
    if (!selectedSection) return;
    const planId = selectedSection.proposal_plan_id;
    setIsActionLoading(true);
    try {
      const res = await fetch(`/api/v1/proposals/${planId}/generate/section/${selectedSection.id}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          tone_style: toneStyle,
          actor: "Proposal Writer",
          additional_context: additionalContext,
        }),
      });

      if (res.ok) {
        alert(`Section '${selectedSection.title}' successfully generated!`);
        setAdditionalContext("");
        await fetchOutlineAndGenerated();
      } else {
        const errJson = await res.json();
        alert(errJson.detail || "Single section generation failed.");
      }
    } catch (err) {
      console.error("Error generating single section:", err);
    } finally {
      setIsActionLoading(false);
    }
  };

  const getQualityColor = (score: number) => {
    if (score >= 0.8) return "text-emerald-400";
    if (score >= 0.5) return "text-amber-400";
    return "text-rose-400";
  };

  const currentGen = selectedSection ? generatedMap[selectedSection.id] : null;

  if (isLoading) {
    return (
      <div className="py-20 flex flex-col justify-center items-center gap-3">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-teal-400" />
        <span className="text-sm text-slate-400 font-mono">Loading proposal writer workspace...</span>
      </div>
    );
  }

  if (sections.length === 0) {
    return (
      <div className="py-20 text-center border border-dashed border-slate-800 rounded-xl bg-slate-950/20">
        <h3 className="text-sm font-semibold text-slate-300">No Outline Chapters Found</h3>
        <p className="text-xs text-slate-500 max-w-sm mx-auto mt-1">
          Make sure to generate the adaptive plan outline configuration first to unlock the writer workspace.
        </p>
      </div>
    );
  }

  return (
    <div className="border border-slate-800 bg-slate-900/60 backdrop-blur-xl rounded-xl p-6 mt-6 shadow-2xl space-y-6">
      {/* Header Panel */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center border-b border-slate-800 pb-5">
        <div>
          <h2 className="text-xl font-bold bg-gradient-to-r from-teal-400 to-indigo-400 bg-clip-text text-transparent">
            Multi-Agent Proposal Content Workspace
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Independently compile and validate specific proposal sections grounded in governed knowledge repositories
          </p>
        </div>
        <div className="mt-3 md:mt-0 flex gap-3">
          <select
            value={toneStyle}
            onChange={(e) => setToneStyle(e.target.value)}
            className="bg-slate-950 border border-slate-800 text-xs text-slate-300 p-2 rounded-lg focus:outline-none focus:border-teal-500"
          >
            <option value="Professional">Professional Tone</option>
            <option value="Government">Government / Compliant</option>
            <option value="Technical">Technical / Specification</option>
            <option value="Commercial">Commercial / Persuasive</option>
            <option value="Executive">Executive Summary</option>
            <option value="Formal">Formal Objective</option>
          </select>
          <button
            onClick={handleGenerateAll}
            disabled={isActionLoading}
            className="px-5 py-2 bg-teal-600 hover:bg-teal-500 text-white text-xs font-bold rounded-lg transition disabled:opacity-50"
          >
            {isActionLoading ? "Synthesizing Proposals..." : "Generate Full Proposal"}
          </button>
        </div>
      </div>

      {/* Main Workspace Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Chapters Left Nav */}
        <div className="bg-slate-950/40 border border-slate-800 p-4 rounded-xl space-y-3 max-h-[500px] overflow-y-auto">
          <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider block font-mono border-b border-slate-900 pb-1.5">
            Chapters Outline
          </h3>
          <div className="space-y-1">
            {sections.map((sec) => {
              const hasGen = !!generatedMap[sec.id];
              const isSelected = selectedSection?.id === sec.id;
              return (
                <button
                  key={sec.id}
                  onClick={() => setSelectedSection(sec)}
                  className={`w-full text-left p-3 rounded-lg text-xs transition border ${
                    isSelected
                      ? "border-teal-500 bg-teal-950/20 text-teal-300"
                      : "border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-900/30"
                  }`}
                >
                  <div className="font-semibold truncate">{sec.title}</div>
                  <div className="flex justify-between items-center text-[10px] text-slate-500 mt-1 font-mono">
                    <span>Budget: {sec.estimated_hours} hrs</span>
                    {hasGen ? (
                      <span className="text-emerald-400 font-bold">✓ Generated</span>
                    ) : (
                      <span className="text-amber-500/70">✗ Pending</span>
                    )}
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Content Viewer / Editor Block */}
        <div className="lg:col-span-3 flex flex-col md:flex-row gap-6">
          {/* Main Content Area */}
          <div className="flex-1 space-y-4">
            {selectedSection && (
              <div className="flex justify-between items-center border-b border-slate-800 pb-2.5">
                <div>
                  <h4 className="text-sm font-bold text-slate-200">{selectedSection.title}</h4>
                  <span className="text-[10px] text-slate-500 font-mono">ID: {selectedSection.id.slice(0, 8)}</span>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={handleGenerateSingle}
                    disabled={isActionLoading}
                    className="px-3.5 py-1.5 bg-indigo-900/60 hover:bg-indigo-900 border border-indigo-700/50 text-indigo-200 text-xs font-bold rounded-lg transition disabled:opacity-50"
                  >
                    {isActionLoading ? "Synthesizing..." : "Regenerate Chapter"}
                  </button>
                </div>
              </div>
            )}

            {/* Writer Workspace Tab Nav */}
            <div className="flex border-b border-slate-850 gap-2 pb-px font-mono text-[10px]">
              {[
                { id: "content", label: "GEN CONTENT" },
                { id: "citations", label: "CITATIONS TRACEABILITY" },
                { id: "history", label: "GENERATION HISTORY" },
              ].map((subTab) => (
                <button
                  key={subTab.id}
                  onClick={() => setActiveViewTab(subTab.id)}
                  className={`px-3 py-1.5 transition border-b-2 -mb-px ${
                    activeViewTab === subTab.id
                      ? "border-indigo-400 text-indigo-300"
                      : "border-transparent text-slate-500 hover:text-slate-300"
                  }`}
                >
                  {subTab.label}
                </button>
              ))}
            </div>

            {/* Sub-tab Contents */}
            <div className="min-h-[250px] bg-slate-950/30 border border-slate-850 p-4 rounded-xl">
              {activeViewTab === "content" && (
                <div className="space-y-4">
                  {currentGen ? (
                    <div className="space-y-3">
                      {/* Quality Meta Bar */}
                      <div className="grid grid-cols-2 md:flex justify-between text-[11px] bg-slate-950 p-2.5 rounded border border-slate-900 font-mono text-slate-400">
                        <div>Word Count: <strong className="text-white">{currentGen.word_count}</strong></div>
                        <div>Confidence: <strong className="text-white">{(currentGen.confidence * 100).toFixed(0)}%</strong></div>
                        <div>Quality Index: <strong className={getQualityColor(currentGen.quality_score)}>{(currentGen.quality_score * 100).toFixed(0)}%</strong></div>
                        <div>Prompt Version: <strong className="text-white">{currentGen.prompt_version}</strong></div>
                      </div>

                      {/* Content Body */}
                      <div className="text-xs text-slate-300 font-mono leading-relaxed whitespace-pre-wrap select-text p-1.5 max-h-[300px] overflow-y-auto">
                        {currentGen.content}
                      </div>
                    </div>
                  ) : (
                    <div className="py-12 text-center">
                      <span className="text-xs text-slate-550 block">This chapter has not been generated yet.</span>
                      <p className="text-[10px] text-slate-600 max-w-xs mx-auto mt-1">
                        Use the single segment generator or generate all chapters in bulk using active corporate knowledge.
                      </p>
                    </div>
                  )}

                  {/* Additional Context inputs */}
                  <div className="space-y-1 pt-2 border-t border-slate-900">
                    <label className="text-[10px] text-slate-500 uppercase block font-semibold">Additional Context Override (Optional)</label>
                    <textarea
                      placeholder="Add custom pricing adjustments, specific CV templates, or local overrides for the writers..."
                      value={additionalContext}
                      onChange={(e) => setAdditionalContext(e.target.value)}
                      className="w-full h-14 bg-slate-950 border border-slate-800 text-[11px] text-slate-400 p-2 rounded focus:outline-none focus:border-teal-500 resize-none font-mono"
                    />
                  </div>
                </div>
              )}

              {activeViewTab === "citations" && (
                <div className="space-y-4">
                  {currentGen && currentGen.citations.length > 0 ? (
                    <div className="space-y-2">
                      <span className="text-[10px] text-slate-400 uppercase font-mono block">Citations Traceability Ledger</span>
                      <div className="space-y-2 max-h-[300px] overflow-y-auto pr-1">
                        {currentGen.citations.map((cit) => (
                          <div key={cit.id} className="bg-slate-950 p-3 rounded border border-slate-900 space-y-1">
                            <div className="flex justify-between items-center text-[10px] font-mono text-slate-500">
                              <span>Paragraph {cit.paragraph_index + 1} reference</span>
                              <span>Confidence: {(cit.confidence * 100).toFixed(0)}%</span>
                            </div>
                            <h5 className="text-xs font-bold text-teal-400">{cit.source_title}</h5>
                            {cit.source_location && (
                              <span className="text-[9px] bg-slate-900 border border-slate-850 text-slate-400 px-2 py-0.5 rounded font-mono">
                                {cit.source_location}
                              </span>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  ) : (
                    <div className="py-10 text-center">
                      <span className="text-xs text-slate-600 block">No evidence citation logs recorded.</span>
                    </div>
                  )}
                </div>
              )}

              {activeViewTab === "history" && (
                <div className="space-y-3">
                  <span className="text-[10px] text-slate-400 uppercase font-mono block">Generation Log Trail</span>
                  <div className="space-y-2 max-h-[300px] overflow-y-auto pr-1">
                    {history
                      .filter((h) => selectedSection && h.proposal_section_id === selectedSection.id)
                      .map((h) => (
                        <div key={h.id} className="text-[11px] border-b border-slate-900 pb-2 last:border-0 last:pb-0 text-slate-400">
                          <div className="flex justify-between w-full font-mono text-[9px]">
                            <span className="text-indigo-400 font-bold">{h.action}</span>
                            <span>{new Date(h.timestamp).toLocaleString()}</span>
                          </div>
                          <div className="mt-1 text-slate-300">
                            By <strong className="text-white">{h.actor}</strong>: "{h.comments}"
                          </div>
                        </div>
                      ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Sidebar Prompt details */}
          <div className="w-full md:w-56 space-y-4 font-mono text-xs">
            <div className="bg-slate-950/40 border border-slate-800 p-4 rounded-xl space-y-3">
              <h4 className="text-xs font-bold text-slate-300 border-b border-slate-900 pb-1 uppercase font-mono">
                Writer Blueprint
              </h4>
              {selectedSection && (
                <div className="space-y-2 text-[10px] text-slate-400">
                  <div>
                    <span className="text-slate-550 block font-semibold">Specialized Agent:</span>
                    <span className="text-white font-bold block">{selectedSection.title.slice(0, 20)} Writer</span>
                  </div>
                  <div>
                    <span className="text-slate-550 block font-semibold">Priority:</span>
                    <span className="text-white block">{selectedSection.priority || "Medium"}</span>
                  </div>
                  <div>
                    <span className="text-slate-550 block font-semibold">Risk Priority:</span>
                    <span className="text-rose-400 block">{selectedSection.risk_level || "Low"}</span>
                  </div>
                  <div className="pt-2 border-t border-slate-900 text-[9px] leading-relaxed text-slate-500">
                    Writers pull inputs from the compliant matrices, qualification decisions, and department reviews.
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
      <div className="pt-6 border-t border-slate-800 space-y-6">
        <WorkflowMonitor proposalId={documentId} />
        <ProposalReviewDashboard proposalId={documentId} />
      </div>
    </div>
  );
}
