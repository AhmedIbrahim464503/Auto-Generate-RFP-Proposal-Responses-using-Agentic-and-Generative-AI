"use client";

import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";

interface Chunk {
  id: string;
  parent_asset_id: string;
  parent_section?: string | null;
  chunk_index: number;
  content: string;
  metadata?: any;
  source_location?: string | null;
}

interface GovernanceRecord {
  id: string;
  asset_id: string;
  action: string;
  actor: string;
  comments?: string | null;
  payload?: any;
  timestamp: string;
}

interface KnowledgeAsset {
  id: string;
  title: string;
  content: string;
  asset_type?: string | null;
  version: string;
  owner?: string | null;
  department?: string | null;
  tags: string[];
  source: string;
  approval_status: string;
  review_date?: string | null;
  expiration_date?: string | null;
  quality_score: number;
  usage_count: number;
  last_retrieved_at?: string | null;
  trust_score: number;
  embedding_version?: string | null;
  created_at: string;
  updated_at: string;
  is_deleted: boolean;
  chunks: Chunk[];
  governance_records: GovernanceRecord[];
}

interface SearchResultItem {
  content: string;
  citation: {
    chunk_id: string;
    parent_asset_id: string;
    document_title: string;
    page?: number | null;
    section?: string | null;
    paragraph?: string | null;
    similarity_score: number;
    rerank_score: number;
    embedding_version: string;
    knowledge_version: string;
  };
}

interface SearchLog {
  id: string;
  query_text: string;
  filters?: any;
  results?: any[];
  latency_ms: number;
  timestamp: string;
}

export default function KnowledgeWorkspace() {
  const [activeTab, setActiveTab] = useState<string>("dashboard");
  const [assets, setAssets] = useState<KnowledgeAsset[]>([]);
  const [selectedAsset, setSelectedAsset] = useState<KnowledgeAsset | null>(null);
  const [searchLogs, setSearchLogs] = useState<SearchLog[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isSearchLoading, setIsSearchLoading] = useState<boolean>(false);

  // Upload Form
  const [newTitle, setNewTitle] = useState<string>("");
  const [newContent, setNewContent] = useState<string>("");
  const [newType, setNewType] = useState<string>("policy");
  const [newOwner, setNewOwner] = useState<string>("Capture Manager");
  const [newDepartment, setNewDepartment] = useState<string>("Operations");
  const [newTagsString, setNewTagsString] = useState<string>("compliance, guide");

  // Search Playground
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [searchTopK, setSearchTopK] = useState<number>(3);
  const [searchThreshold, setSearchThreshold] = useState<number>(0.2);
  const [searchDeptFilter, setSearchDeptFilter] = useState<string>("");
  const [searchTypeFilter, setSearchTypeFilter] = useState<string>("");
  const [searchResults, setSearchResults] = useState<SearchResultItem[]>([]);
  const [searchLatency, setSearchLatency] = useState<number>(0.0);

  useEffect(() => {
    fetchAssets();
    fetchLogs();
  }, []);

  const fetchAssets = async () => {
    setIsLoading(true);
    try {
      const res = await fetch("/api/v1/knowledge");
      if (res.ok) {
        setAssets(await res.json());
      }
    } catch (err) {
      console.error("Error fetching assets:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchLogs = async () => {
    try {
      const res = await fetch("/api/v1/knowledge/history");
      if (res.ok) {
        setSearchLogs(await res.json());
      }
    } catch (err) {
      console.error("Error fetching logs:", err);
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim() || !newContent.trim()) {
      alert("Title and Content are required.");
      return;
    }

    try {
      const res = await fetch("/api/v1/knowledge/upload", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: newTitle,
          content: newContent,
          asset_type: newType,
          owner: newOwner,
          department: newDepartment,
          tags: newTagsString.split(",").map((t) => t.trim()).filter((t) => t),
        }),
      });

      if (res.ok) {
        alert("Knowledge Asset uploaded and semantically indexed!");
        setNewTitle("");
        setNewContent("");
        fetchAssets();
      }
    } catch (err) {
      console.error("Error uploading asset:", err);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    setIsSearchLoading(true);
    try {
      let url = `/api/v1/knowledge/search?query=${encodeURIComponent(searchQuery)}&top_k=${searchTopK}&confidence_threshold=${searchThreshold}`;
      if (searchDeptFilter) url += `&department=${encodeURIComponent(searchDeptFilter)}`;
      if (searchTypeFilter) url += `&asset_type=${encodeURIComponent(searchTypeFilter)}`;

      const res = await fetch(url);
      if (res.ok) {
        const data = await res.json();
        setSearchResults(data.results || []);
        setSearchLatency(data.latency_ms || 0.0);
        fetchLogs();
      }
    } catch (err) {
      console.error("Search failed:", err);
    } finally {
      setIsSearchLoading(false);
    }
  };

  const handleIndex = async (assetId: string) => {
    try {
      const res = await fetch(`/api/v1/knowledge/index?id=${assetId}`, { method: "POST" });
      if (res.ok) {
        alert("Re-index successful!");
        fetchAssets();
      }
    } catch (err) {
      console.error("Reindexing failed:", err);
    }
  };

  const handleApproval = async (assetId: string, status: string) => {
    try {
      const res = await fetch(`/api/v1/knowledge/${assetId}/update`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ approval_status: status }),
      });
      if (res.ok) {
        alert(`Status updated to: ${status}`);
        fetchAssets();
      }
    } catch (err) {
      console.error("Approval state failed:", err);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toUpperCase()) {
      case "APPROVED":
        return "bg-emerald-500/20 text-emerald-400 border-emerald-500/30";
      case "REJECTED":
        return "bg-rose-500/20 text-rose-400 border-rose-500/30";
      case "EXPIRED":
        return "bg-slate-800 text-slate-400 border-slate-700";
      case "DRAFT":
      default:
        return "bg-amber-500/20 text-amber-400 border-amber-500/30";
    }
  };

  const getConfidenceColor = (val: number) => {
    if (val >= 0.7) return "text-emerald-400";
    if (val >= 0.4) return "text-amber-400";
    return "text-rose-400";
  };

  return (
    <div className="border border-slate-800 bg-slate-900/60 backdrop-blur-xl rounded-xl p-6 mt-6 shadow-2xl space-y-6">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center border-b border-slate-800 pb-5">
        <div>
          <h2 className="text-xl font-bold bg-gradient-to-r from-teal-400 to-indigo-400 bg-clip-text text-transparent">
            Enterprise Knowledge Platform (RAG & Governance)
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Centrally organize, semantically index, retrieve, and govern boilerplate answers and company qualifications
          </p>
        </div>
        <div className="mt-3 md:mt-0 flex gap-2 font-mono">
          <span className="bg-slate-950/40 text-[10px] text-slate-400 border border-slate-800 px-3 py-1 rounded-full flex items-center">
            ACTIVE ASSETS: {assets.length}
          </span>
          <span className="bg-slate-950/40 text-[10px] text-teal-400 border border-teal-500/20 px-3 py-1 rounded-full flex items-center">
            EMBEDDING: BGE-v1.5
          </span>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-slate-800 overflow-x-auto gap-2 pb-px scrollbar-none">
        {[
          { id: "dashboard", label: "Overview & Upload" },
          { id: "library", label: "Knowledge Library" },
          { id: "playground", label: "Semantic Search Console" },
          { id: "history", label: "Governance Auditing" },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => {
              setActiveTab(tab.id);
              setSelectedAsset(null);
            }}
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

      {/* Contents */}
      <div className="min-h-[400px]">
        {activeTab === "dashboard" && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 animate-fadeIn">
            {/* KPI Summaries */}
            <div className="lg:col-span-2 space-y-6">
              <div className="grid grid-cols-3 gap-4">
                <div className="bg-slate-950/40 border border-slate-800 p-4 rounded-xl space-y-1">
                  <span className="text-[10px] text-slate-500 uppercase tracking-wider block font-semibold">Indexed Chunks</span>
                  <span className="text-2xl font-black text-teal-400 block">
                    {assets.reduce((sum, a) => sum + a.chunks.length, 0)}
                  </span>
                </div>
                <div className="bg-slate-950/40 border border-slate-800 p-4 rounded-xl space-y-1">
                  <span className="text-[10px] text-slate-500 uppercase tracking-wider block font-semibold">Avg Latency</span>
                  <span className="text-2xl font-black text-indigo-400 block">
                    {searchLogs.length > 0
                      ? (searchLogs.reduce((sum, l) => sum + l.latency_ms, 0) / searchLogs.length).toFixed(1)
                      : "0.0"} <span className="text-xs text-slate-600 font-normal">ms</span>
                  </span>
                </div>
                <div className="bg-slate-950/40 border border-slate-800 p-4 rounded-xl space-y-1">
                  <span className="text-[10px] text-slate-500 uppercase tracking-wider block font-semibold">Approved Boilerplate</span>
                  <span className="text-2xl font-black text-purple-400 block">
                    {assets.filter((a) => a.approval_status === "APPROVED").length}
                  </span>
                </div>
              </div>

              {/* Upload Form */}
              <form onSubmit={handleUpload} className="border border-slate-800 bg-slate-950/20 p-5 rounded-xl space-y-4">
                <span className="text-xs font-bold text-slate-200 block border-b border-slate-900 pb-2">Add New Knowledge Asset</span>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="space-y-1">
                    <label className="text-[10px] text-slate-500 uppercase block font-semibold">Asset Title</label>
                    <input
                      type="text"
                      placeholder="e.g. SOC2 Security Guidelines"
                      value={newTitle}
                      onChange={(e) => setNewTitle(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 text-xs text-slate-300 px-3 py-2 rounded-lg focus:outline-none focus:border-teal-500"
                    />
                  </div>
                  <div className="space-y-1">
                    <label className="text-[10px] text-slate-500 uppercase block font-semibold">Category / Type</label>
                    <select
                      value={newType}
                      onChange={(e) => setNewType(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 text-xs text-slate-300 p-2 rounded-lg focus:outline-none focus:border-teal-500"
                    >
                      <option value="policy">Policy / Guideline</option>
                      <option value="historical_proposal">Past Proposal Answer</option>
                      <option value="product_wiki">Product Wiki</option>
                      <option value="case_study">Case Study</option>
                      <option value="cv">Resume / CV</option>
                    </select>
                  </div>
                  <div className="space-y-1">
                    <label className="text-[10px] text-slate-500 uppercase block font-semibold">Tags (comma separated)</label>
                    <input
                      type="text"
                      placeholder="e.g. security, cloud, aws"
                      value={newTagsString}
                      onChange={(e) => setNewTagsString(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 text-xs text-slate-300 px-3 py-2 rounded-lg focus:outline-none focus:border-teal-500"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-1">
                    <label className="text-[10px] text-slate-500 uppercase block font-semibold">Owner</label>
                    <input
                      type="text"
                      value={newOwner}
                      onChange={(e) => setNewOwner(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 text-xs text-slate-300 px-3 py-2 rounded-lg"
                    />
                  </div>
                  <div className="space-y-1">
                    <label className="text-[10px] text-slate-500 uppercase block font-semibold">Department</label>
                    <input
                      type="text"
                      value={newDepartment}
                      onChange={(e) => setNewDepartment(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 text-xs text-slate-300 px-3 py-2 rounded-lg"
                    />
                  </div>
                </div>

                <div className="space-y-1.5">
                  <label className="text-[10px] text-slate-500 uppercase block font-semibold">Document Content (Text or Markdown)</label>
                  <textarea
                    placeholder="Provide full text body of the reusable document..."
                    value={newContent}
                    onChange={(e) => setNewContent(e.target.value)}
                    className="w-full h-40 bg-slate-950 border border-slate-800 text-xs text-slate-300 p-3 rounded-lg focus:outline-none focus:border-teal-500 resize-none"
                  />
                </div>

                <button
                  type="submit"
                  className="px-6 py-2 bg-teal-600 hover:bg-teal-500 text-white text-xs font-bold rounded-lg transition"
                >
                  Upload & Index Asset
                </button>
              </form>
            </div>

            {/* Architecture Details Sidebar */}
            <div className="border border-slate-800 bg-slate-950/40 p-5 rounded-xl space-y-4">
              <span className="text-xs font-bold text-slate-200 block border-b border-slate-900 pb-2">RAG Architecture Status</span>
              <div className="space-y-3 text-xs text-slate-400 font-mono">
                <div className="flex justify-between border-b border-slate-900 pb-1.5">
                  <span>Chunknig:</span>
                  <span className="text-white">Semantic Heading</span>
                </div>
                <div className="flex justify-between border-b border-slate-900 pb-1.5">
                  <span>Chunk Max Length:</span>
                  <span className="text-white">700 characters</span>
                </div>
                <div className="flex justify-between border-b border-slate-900 pb-1.5">
                  <span>Embedding:</span>
                  <span className="text-teal-400">BGE-large-en-v1.5</span>
                </div>
                <div className="flex justify-between border-b border-slate-900 pb-1.5">
                  <span>Vector Database:</span>
                  <span className="text-white">FAISS (SQLite Fallback)</span>
                </div>
                <div className="flex justify-between border-b border-slate-900 pb-1.5">
                  <span>Search Weights:</span>
                  <span className="text-white">0.7 Sem / 0.3 Keyword</span>
                </div>
              </div>
              <p className="text-[10px] text-slate-500 leading-relaxed">
                Future proposal drafting and generation jobs will extract contextual inputs exclusively from this governed repository layer, ensuring document consistency.
              </p>
            </div>
          </div>
        )}

        {activeTab === "library" && (
          <div className="space-y-4 animate-fadeIn">
            {selectedAsset ? (
              <div className="space-y-4">
                <div className="flex justify-between items-center border-b border-slate-800 pb-3">
                  <button
                    onClick={() => setSelectedAsset(null)}
                    className="text-xs text-teal-400 hover:text-teal-300"
                  >
                    ← Back to Library
                  </button>
                  <h3 className="text-sm font-bold text-slate-200">{selectedAsset.title}</h3>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {/* Metadata and Audits */}
                  <div className="space-y-4">
                    <div className="bg-slate-950/40 border border-slate-800 p-4 rounded-xl space-y-2">
                      <h4 className="text-xs font-bold text-slate-300 border-b border-slate-900 pb-1">Governance Meta</h4>
                      <div className="space-y-2 text-xs font-mono">
                        <div className="flex justify-between text-[11px]"><span className="text-slate-500">Version:</span> <span className="text-slate-300">{selectedAsset.version}</span></div>
                        <div className="flex justify-between text-[11px]"><span className="text-slate-500">Owner:</span> <span className="text-slate-300">{selectedAsset.owner}</span></div>
                        <div className="flex justify-between text-[11px]"><span className="text-slate-500">BU:</span> <span className="text-slate-300">{selectedAsset.department}</span></div>
                        <div className="flex justify-between text-[11px]"><span className="text-slate-500">Quality Index:</span> <span className="text-teal-400">{selectedAsset.quality_score}</span></div>
                        <div className="flex justify-between text-[11px]"><span className="text-slate-500">Trust Score:</span> <span className="text-indigo-400">{selectedAsset.trust_score}</span></div>
                        <div className="flex justify-between text-[11px]"><span className="text-slate-500">Usage Hits:</span> <span className="text-white">{selectedAsset.usage_count}</span></div>
                      </div>
                    </div>

                    <div className="bg-slate-950/40 border border-slate-800 p-4 rounded-xl space-y-2">
                      <h4 className="text-xs font-bold text-slate-300 border-b border-slate-900 pb-1">Audit Actions</h4>
                      <div className="space-y-2 max-h-[200px] overflow-y-auto pr-1">
                        {selectedAsset.governance_records.map((rec) => (
                          <div key={rec.id} className="text-[11px] border-b border-slate-900 pb-1.5 last:border-0 last:pb-0">
                            <span className="font-bold text-slate-200 block">{rec.action}</span>
                            <span className="text-slate-500 text-[10px] block">{rec.actor} • {new Date(rec.timestamp).toLocaleString()}</span>
                            <p className="text-slate-400 mt-0.5">{rec.comments}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

                  {/* Chunks Explorer */}
                  <div className="md:col-span-2 space-y-4 border-l border-slate-800 pl-6">
                    <h4 className="text-xs font-bold text-slate-200">Semantic Segment Chunks</h4>
                    <div className="space-y-3 max-h-[400px] overflow-y-auto pr-1">
                      {selectedAsset.chunks.map((chunk) => (
                        <div key={chunk.id} className="bg-slate-950/30 border border-slate-850 p-4 rounded-lg space-y-2">
                          <div className="flex justify-between items-center text-[10px] font-mono text-slate-500 border-b border-slate-900 pb-1">
                            <span>Index Chapter {chunk.chunk_index} ({chunk.parent_section || "General"})</span>
                            <span>📍 {chunk.source_location || "N/A"}</span>
                          </div>
                          <p className="text-xs text-slate-300 font-mono leading-relaxed whitespace-pre-wrap">{chunk.content}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="overflow-x-auto border border-slate-800 rounded-xl bg-slate-950/20">
                <table className="w-full border-collapse text-left text-xs text-slate-400">
                  <thead className="bg-slate-950 text-slate-200 font-mono text-[10px] uppercase border-b border-slate-800">
                    <tr>
                      <th className="p-3">Title</th>
                      <th className="p-3">Type</th>
                      <th className="p-3">BU / Owner</th>
                      <th className="p-3">Quality Score</th>
                      <th className="p-3">Status</th>
                      <th className="p-3 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-850">
                    {assets.map((asset) => (
                      <tr key={asset.id} className="hover:bg-slate-900/40">
                        <td className="p-3 font-semibold text-slate-200">
                          <button
                            onClick={() => setSelectedAsset(asset)}
                            className="hover:underline text-left text-teal-400 font-bold"
                          >
                            {asset.title}
                          </button>
                          <span className="text-[10px] text-slate-500 font-mono block mt-0.5">v{asset.version} • {asset.chunks.length} chunks</span>
                        </td>
                        <td className="p-3 font-mono text-[10px] uppercase">{asset.asset_type || "N/A"}</td>
                        <td className="p-3">
                          <div>{asset.department}</div>
                          <div className="text-[10px] text-slate-500 font-semibold">{asset.owner}</div>
                        </td>
                        <td className="p-3 font-mono font-bold text-teal-400">{asset.quality_score}</td>
                        <td className="p-3">
                          <span className={`px-2.5 py-0.5 rounded-full text-[9px] font-bold border ${getStatusColor(asset.approval_status)}`}>
                            {asset.approval_status}
                          </span>
                        </td>
                        <td className="p-3 text-right space-x-2">
                          <button
                            onClick={() => handleIndex(asset.id)}
                            className="px-2 py-1 bg-slate-800 text-[10px] text-slate-300 rounded border border-slate-700 hover:bg-slate-750"
                          >
                            Reindex
                          </button>
                          {asset.approval_status !== "APPROVED" ? (
                            <button
                              onClick={() => handleApproval(asset.id, "APPROVED")}
                              className="px-2 py-1 bg-emerald-950/20 text-emerald-400 border border-emerald-500/20 text-[10px] rounded hover:bg-emerald-900/20"
                            >
                              Approve
                            </button>
                          ) : (
                            <button
                              onClick={() => handleApproval(asset.id, "EXPIRED")}
                              className="px-2 py-1 bg-rose-950/20 text-rose-400 border border-rose-500/20 text-[10px] rounded hover:bg-rose-900/20"
                            >
                              Expire
                            </button>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {activeTab === "playground" && (
          <div className="space-y-6 animate-fadeIn">
            {/* Search Controls */}
            <div className="border border-slate-800 bg-slate-950/20 p-5 rounded-xl space-y-4">
              <span className="text-xs font-bold text-slate-200 block border-b border-slate-900 pb-2">RAG Search Parameters</span>
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="Ask a question of corporate knowledge bases (e.g. 'What is our SOC2 policy?')..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="flex-1 bg-slate-950 border border-slate-800 text-xs text-slate-300 px-3 py-2.5 rounded-lg focus:outline-none focus:border-teal-500"
                />
                <button
                  onClick={handleSearch}
                  disabled={isSearchLoading}
                  className="px-6 bg-teal-600 hover:bg-teal-500 text-white text-xs font-bold rounded-lg transition disabled:opacity-50"
                >
                  {isSearchLoading ? "Searching..." : "Execute Search"}
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 pt-2">
                <div className="space-y-1">
                  <span className="text-[10px] text-slate-500 uppercase font-semibold block">Retrieve top-K ({searchTopK})</span>
                  <input
                    type="range"
                    min="1"
                    max="10"
                    value={searchTopK}
                    onChange={(e) => setSearchTopK(parseInt(e.target.value))}
                    className="w-full accent-teal-500 cursor-pointer h-1"
                  />
                </div>
                <div className="space-y-1">
                  <span className="text-[10px] text-slate-500 uppercase font-semibold block">Confidence Threshold ({searchThreshold})</span>
                  <input
                    type="range"
                    min="0.0"
                    max="0.9"
                    step="0.05"
                    value={searchThreshold}
                    onChange={(e) => setSearchThreshold(parseFloat(e.target.value))}
                    className="w-full accent-teal-500 cursor-pointer h-1"
                  />
                </div>
                <div className="space-y-1">
                  <span className="text-[10px] text-slate-500 uppercase font-semibold block">BU Filter</span>
                  <input
                    type="text"
                    placeholder="BU Name"
                    value={searchDeptFilter}
                    onChange={(e) => setSearchDeptFilter(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-850 text-xs text-slate-300 px-2 py-1 rounded"
                  />
                </div>
                <div className="space-y-1">
                  <span className="text-[10px] text-slate-500 uppercase font-semibold block">Asset Type Filter</span>
                  <input
                    type="text"
                    placeholder="policy, study..."
                    value={searchTypeFilter}
                    onChange={(e) => setSearchTypeFilter(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-850 text-xs text-slate-300 px-2 py-1 rounded"
                  />
                </div>
              </div>
            </div>

            {/* Results */}
            {searchResults.length > 0 && (
              <div className="space-y-4">
                <div className="flex justify-between items-center text-[10px] font-mono text-slate-400 border-b border-slate-800 pb-2">
                  <span>RAG RETRIEVAL PIPELINE RESULTS ({searchResults.length} hits)</span>
                  <span>Pipeline Latency: {searchLatency.toFixed(1)} ms</span>
                </div>

                <div className="space-y-4">
                  {searchResults.map((result, idx) => (
                    <div key={idx} className="bg-slate-950/40 border border-slate-800 p-4 rounded-xl space-y-3">
                      <div className="flex justify-between items-start text-xs border-b border-slate-900 pb-2">
                        <div>
                          <span className="font-bold text-slate-200">{result.citation.document_title}</span>
                          <span className="text-[10px] text-slate-500 block font-mono">
                            Section: {result.citation.section} • Location: {result.citation.paragraph}
                          </span>
                        </div>
                        <div className="text-right font-mono text-[10px]">
                          <div>Similarity: <span className={getConfidenceColor(result.citation.similarity_score)}>{result.citation.similarity_score.toFixed(3)}</span></div>
                          <div>Rerank Similarity: <span className="text-teal-400">{result.citation.rerank_score.toFixed(3)}</span></div>
                        </div>
                      </div>
                      <p className="text-xs text-slate-300 font-mono leading-relaxed whitespace-pre-wrap">{result.content}</p>
                      
                      <div className="pt-2 flex flex-wrap gap-2 text-[9px] font-mono text-slate-500 border-t border-slate-900/50">
                        <span>Chunk ID: {result.citation.chunk_id.slice(0,8)}</span>
                        <span>Embedding Version: {result.citation.embedding_version}</span>
                        <span>Doc Version: v{result.citation.knowledge_version}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === "history" && (
          <div className="space-y-4 animate-fadeIn">
            <div>
              <h3 className="text-sm font-semibold text-slate-200">RAG Query Latency & Governance History</h3>
              <p className="text-xs text-slate-500">Trace searches, model swapper indices, and citation logs.</p>
            </div>

            <div className="space-y-2 bg-slate-950/60 p-4 rounded-xl border border-slate-900 max-h-[500px] overflow-y-auto pr-1">
              {searchLogs.length === 0 ? (
                <span className="text-xs text-slate-650 block text-center py-4 font-mono">No search logs registered.</span>
              ) : (
                searchLogs.map((log) => (
                  <div key={log.id} className="text-xs text-slate-400 border-b border-slate-900 pb-3 mb-3 last:border-0 last:pb-0 last:mb-0 space-y-1">
                    <div className="flex justify-between w-full font-mono text-[10px]">
                      <span className="text-teal-400 font-bold">QUERY_LOG</span>
                      <span className="text-slate-550">{new Date(log.timestamp).toLocaleString()}</span>
                    </div>
                    <div className="text-slate-300">
                      Query: <span className="text-white font-semibold font-mono">"{log.query_text}"</span>
                    </div>
                    <div className="flex gap-4 text-[10px] text-slate-500 font-mono">
                      <span>Latency: <strong className="text-slate-300">{log.latency_ms.toFixed(1)} ms</strong></span>
                      <span>Filters: <strong className="text-slate-300">{JSON.stringify(log.filters || {})}</strong></span>
                      <span>Results Hits: <strong className="text-slate-300">{log.results?.length || 0}</strong></span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
