"use client";

import React, { useState, useEffect } from "react";
import { Folder, FolderOpen, Play, ShieldAlert, Award, FileText, UserCheck, ShieldCheck } from "lucide-react";

interface StructureExplorerProps {
  documentId: string;
}

interface TreeNode {
  title: string;
  classification?: string;
  confidence: number;
  page_start: number;
  page_end: number;
  subsections: TreeNode[];
}

interface Metadata {
  document_title: string;
  client_name: string;
  project_name: string;
  rfp_number: string;
  issue_date: string;
  submission_deadline: string;
  contacts: any[];
}

interface Quality {
  quality_score: number;
  missing_pages_detected: boolean;
  unreadable_sections_detected: boolean;
  corrupted_content_detected: boolean;
  duplicate_sections_detected: boolean;
  empty_sections_detected: boolean;
}

export default function StructureExplorer({ documentId }: StructureExplorerProps) {
  const [analyzing, setAnalyzing] = useState(false);
  const [tree, setTree] = useState<TreeNode[]>([]);
  const [meta, setMeta] = useState<Metadata | null>(null);
  const [quality, setQuality] = useState<Quality | null>(null);
  const [activeTab, setActiveTab] = useState<"structure" | "meta" | "quality">("structure");

  const runAnalysis = async () => {
    setAnalyzing(true);
    try {
      const res = await fetch(`http://localhost:8000/api/v1/documents/${documentId}/analyze`, {
        method: "POST",
      });
      if (res.ok) {
        fetchData();
      }
    } catch (e) {
      console.error("Analysis trigger failed", e);
    } finally {
      setAnalyzing(false);
    }
  };

  const fetchData = async () => {
    try {
      // Fetch structure
      const resTree = await fetch(`http://localhost:8000/api/v1/documents/${documentId}/structure`);
      if (resTree.ok) {
        setTree(await resTree.json());
      }
      
      // Fetch metadata
      const resMeta = await fetch(`http://localhost:8000/api/v1/documents/${documentId}/metadata`);
      if (resMeta.ok) {
        setMeta(await resMeta.json());
      }

      // Fetch quality
      const resQual = await fetch(`http://localhost:8000/api/v1/documents/${documentId}/quality`);
      if (resQual.ok) {
        setQuality(await resQual.json());
      }
    } catch (e) {
      console.error("Failed loading analysis results", e);
    }
  };

  useEffect(() => {
    fetchData();
  }, [documentId]);

  const renderTree = (nodes: TreeNode[]) => {
    return (
      <ul className="pl-4 space-y-1.5 border-l border-neutral-800 ml-2 mt-1">
        {nodes.map((node, index) => (
          <li key={index} className="text-sm">
            <div className="flex items-center gap-2 text-neutral-300 hover:text-white transition-colors py-0.5">
              {node.subsections.length > 0 ? (
                <FolderOpen className="w-4 h-4 text-emerald-500" />
              ) : (
                <FileText className="w-3.5 h-3.5 text-neutral-500" />
              )}
              <span className="font-medium">{node.title}</span>
              {node.classification && (
                <span className="text-[10px] font-mono px-1.5 py-0.5 bg-neutral-800 rounded text-neutral-400">
                  {node.classification} ({Math.round(node.confidence * 100)}%)
                </span>
              )}
              <span className="text-[10px] text-neutral-500 font-mono ml-auto">
                Pages {node.page_start}-{node.page_end}
              </span>
            </div>
            {node.subsections.length > 0 && renderTree(node.subsections)}
          </li>
        ))}
      </ul>
    );
  };

  return (
    <div className="w-full bg-neutral-900 border border-neutral-800 rounded-lg p-6 font-sans">
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between mb-6 pb-4 border-b border-neutral-800 gap-4">
        <div>
          <h2 className="text-lg font-display font-semibold text-white">AI Document Intelligence Dashboard</h2>
          <p className="text-xs text-neutral-500">Analyze page hierarchies, quality limits, and contract dates.</p>
        </div>
        <button
          onClick={runAnalysis}
          disabled={analyzing}
          className="flex items-center gap-2 px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-500 disabled:bg-neutral-800 text-xs font-mono tracking-wider font-semibold rounded text-white transition-all shadow-lg shadow-emerald-950/20"
        >
          <Play className="w-3.5 h-3.5 fill-current" />
          {analyzing ? "ANALYZING STRUCTURE..." : "RUN INTEL ANALYSIS"}
        </button>
      </div>

      {tree.length === 0 ? (
        <div className="flex flex-col items-center justify-center p-12 border border-dashed border-neutral-800 rounded-lg bg-neutral-950/20 text-neutral-500">
          <FileText className="w-10 h-10 mb-3" />
          <p className="text-sm font-medium text-neutral-400">Analysis Not Yet Executed</p>
          <p className="text-xs text-neutral-600 mt-1 max-w-sm text-center">
            Click 'RUN INTEL ANALYSIS' to execute Gemini segmentation modeling on the uploaded RFP text.
          </p>
        </div>
      ) : (
        <div>
          {/* Navigation Tabs */}
          <div className="flex gap-2 border-b border-neutral-800 mb-4 pb-2">
            <button
              onClick={() => setActiveTab("structure")}
              className={`px-3 py-1.5 rounded text-xs font-mono transition-all ${
                activeTab === "structure" ? "bg-emerald-950/40 text-emerald-400 border border-emerald-500/20" : "text-neutral-400 hover:text-white"
              }`}
            >
              STRUCTURE TREE
            </button>
            <button
              onClick={() => setActiveTab("meta")}
              className={`px-3 py-1.5 rounded text-xs font-mono transition-all ${
                activeTab === "meta" ? "bg-emerald-950/40 text-emerald-400 border border-emerald-500/20" : "text-neutral-400 hover:text-white"
              }`}
            >
              EXTRACTED METADATA
            </button>
            <button
              onClick={() => setActiveTab("quality")}
              className={`px-3 py-1.5 rounded text-xs font-mono transition-all ${
                activeTab === "quality" ? "bg-emerald-950/40 text-emerald-400 border border-emerald-500/20" : "text-neutral-400 hover:text-white"
              }`}
            >
              QUALITY LIMITS
            </button>
          </div>

          {/* Structure Tree view */}
          {activeTab === "structure" && (
            <div className="bg-neutral-950/50 p-4 border border-neutral-800 rounded-lg max-h-[300px] overflow-y-auto">
              {renderTree(tree)}
            </div>
          )}

          {/* Metadata Tab */}
          {activeTab === "meta" && meta && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 bg-neutral-950/50 p-6 border border-neutral-800 rounded-lg text-sm text-neutral-300">
              <div className="space-y-3">
                <div>
                  <span className="text-[10px] font-mono text-neutral-500">DOCUMENT TITLE</span>
                  <p className="font-semibold text-white mt-0.5">{meta.document_title}</p>
                </div>
                <div>
                  <span className="text-[10px] font-mono text-neutral-500">CLIENT NAME</span>
                  <p className="font-semibold text-white mt-0.5">{meta.client_name}</p>
                </div>
                <div>
                  <span className="text-[10px] font-mono text-neutral-500">PROJECT DESIGNATION</span>
                  <p className="font-semibold text-white mt-0.5">{meta.project_name}</p>
                </div>
                <div>
                  <span className="text-[10px] font-mono text-neutral-500">RFP NUMBER</span>
                  <p className="font-mono text-white mt-0.5">{meta.rfp_number}</p>
                </div>
              </div>

              <div className="space-y-4">
                <div className="p-3 bg-neutral-900 border border-neutral-800 rounded flex items-center gap-3">
                  <Award className="w-5 h-5 text-emerald-400" />
                  <div>
                    <span className="text-[10px] font-mono text-neutral-500 block">SUBMISSION DEADLINE</span>
                    <span className="text-xs font-semibold text-neutral-200">{meta.submission_deadline}</span>
                  </div>
                </div>

                <div>
                  <span className="text-[10px] font-mono text-neutral-500 block mb-2">PRIMARY AUDIT CONTACTS</span>
                  {meta.contacts.map((c, i) => (
                    <div key={i} className="p-3 bg-neutral-900 border border-neutral-800 rounded-lg space-y-1">
                      <div className="flex items-center gap-2 text-xs text-white">
                        <UserCheck className="w-4 h-4 text-neutral-500" />
                        <span className="font-semibold">{c.primary_contact}</span>
                        <span className="text-[10px] text-neutral-500">({c.organization} {c.department})</span>
                      </div>
                      <p className="text-xs text-neutral-400 pl-6">Email: {c.email}</p>
                      {c.phone && <p className="text-xs text-neutral-400 pl-6">Phone: {c.phone}</p>}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Quality Report Tab */}
          {activeTab === "quality" && quality && (
            <div className="bg-neutral-950/50 p-6 border border-neutral-800 rounded-lg text-sm">
              <div className="flex items-center gap-4 pb-4 border-b border-neutral-800 mb-4">
                <div className="w-14 h-14 rounded-full border-4 border-emerald-500/20 bg-emerald-500/5 flex items-center justify-center text-lg font-bold text-white">
                  {Math.round(quality.quality_score * 100)}%
                </div>
                <div>
                  <p className="font-semibold text-white">Extraction Integrity Report</p>
                  <p className="text-xs text-neutral-500">Evaluated structural density and scan anomalies.</p>
                </div>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                <div className="p-3 bg-neutral-900 border border-neutral-800 rounded-lg flex items-center gap-3">
                  <ShieldCheck className={`w-5 h-5 ${quality.missing_pages_detected ? "text-red-500" : "text-emerald-400"}`} />
                  <div>
                    <p className="text-xs font-medium text-white">Missing Pages</p>
                    <p className="text-[10px] text-neutral-500">{quality.missing_pages_detected ? "Anomalies found" : "Clean pass"}</p>
                  </div>
                </div>

                <div className="p-3 bg-neutral-900 border border-neutral-800 rounded-lg flex items-center gap-3">
                  <ShieldCheck className={`w-5 h-5 ${quality.unreadable_sections_detected ? "text-red-500" : "text-emerald-400"}`} />
                  <div>
                    <p className="text-xs font-medium text-white">Unreadable Blocks</p>
                    <p className="text-[10px] text-neutral-500">{quality.unreadable_sections_detected ? "Corruption alert" : "Clean pass"}</p>
                  </div>
                </div>

                <div className="p-3 bg-neutral-900 border border-neutral-800 rounded-lg flex items-center gap-3">
                  <ShieldCheck className={`w-5 h-5 ${quality.duplicate_sections_detected ? "text-red-500" : "text-emerald-400"}`} />
                  <div>
                    <p className="text-xs font-medium text-white">Duplicate Headers</p>
                    <p className="text-[10px] text-neutral-500">{quality.duplicate_sections_detected ? "Overlaps found" : "Clean pass"}</p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
