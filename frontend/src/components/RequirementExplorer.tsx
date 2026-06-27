"use client";

import React, { useState, useEffect } from "react";

interface Requirement {
  id: string;
  title: string;
  text_content: string;
  category: string;
  priority: string;
  req_type: string;
  mandatory: boolean;
  source_section: string;
  source_page: number;
  parent_id: string | null;
  confidence: number;
  assigned_departments: string[];
}

interface Deliverable {
  id: string;
  description: string;
  deadline: string;
  due_stage: string;
  mandatory: boolean;
  responsible_department: string;
  confidence: number;
}

interface EvaluationCriteria {
  id: string;
  criteria_text: string;
  weight: string;
  factor: string;
  scoring_methodology: string;
  ranking_criteria: string;
  selection_method: string;
  tie_break_rules: string;
  preferred_experience: string;
  preferred_certifications: string;
  confidence: number;
}

interface SubmissionInstruction {
  id: string;
  instruction_text: string;
  format_type: string;
  submission_method: string;
  portal: string;
  email: string;
  file_naming_rules: string;
  file_formats: string;
  max_size: string;
  required_signatures: string;
  required_forms: string;
  num_copies: number;
  submission_sequence: string;
  late_policy: string;
  confidence: number;
}

interface ComplianceObligation {
  id: string;
  name: string;
  status: string;
  department_owner: string;
  evidence_required: string;
  priority: string;
  blocking: boolean;
  confidence: number;
}

interface RFPRisk {
  id: string;
  description: string;
  severity: string;
  likelihood: string;
  business_impact: string;
  mitigation_suggestion: string;
  confidence: number;
}

interface ClarificationQuestion {
  id: string;
  question_text: string;
  priority: string;
  reason: string;
  suggested_recipient: string;
  business_impact: string;
  confidence: number;
}

interface GraphNode {
  id: string;
  type: string;
  label: string;
}

interface GraphEdge {
  id: string;
  source: string;
  target: string;
  relationship: string;
}

interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

interface RequirementExplorerProps {
  documentId: string;
}

export default function RequirementExplorer({ documentId }: RequirementExplorerProps) {
  const [activeTab, setActiveTab] = useState<string>("requirements");
  const [requirements, setRequirements] = useState<Requirement[]>([]);
  const [deliverables, setDeliverables] = useState<Deliverable[]>([]);
  const [evaluations, setEvaluations] = useState<EvaluationCriteria[]>([]);
  const [submissions, setSubmissions] = useState<SubmissionInstruction[]>([]);
  const [compliance, setCompliance] = useState<ComplianceObligation[]>([]);
  const [risks, setRisks] = useState<RFPRisk[]>([]);
  const [clarifications, setClarifications] = useState<ClarificationQuestion[]>([]);
  const [graphData, setGraphData] = useState<GraphData>({ nodes: [], edges: [] });

  const [searchQuery, setSearchQuery] = useState<string>("");
  const [filterCategory, setFilterCategory] = useState<string>("All");
  const [filterPriority, setFilterPriority] = useState<string>("All");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isExtracting, setIsExtracting] = useState<boolean>(false);

  useEffect(() => {
    if (documentId) {
      fetchData();
    }
  }, [documentId]);

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const [reqsRes, delsRes, evalsRes, subsRes, compRes, risksRes, clarsRes, graphRes] = await Promise.all([
        fetch(`/api/v1/rfp/${documentId}/requirements`),
        fetch(`/api/v1/rfp/${documentId}/deliverables`),
        fetch(`/api/v1/rfp/${documentId}/evaluation`),
        fetch(`/api/v1/rfp/${documentId}/submission`),
        fetch(`/api/v1/rfp/${documentId}/compliance`),
        fetch(`/api/v1/rfp/${documentId}/risks`),
        fetch(`/api/v1/rfp/${documentId}/clarifications`),
        fetch(`/api/v1/rfp/${documentId}/knowledge-graph`),
      ]);

      if (reqsRes.ok) setRequirements(await reqsRes.json());
      if (delsRes.ok) setDeliverables(await delsRes.json());
      if (evalsRes.ok) setEvaluations(await evalsRes.json());
      if (subsRes.ok) setSubmissions(await subsRes.json());
      if (compRes.ok) setCompliance(await compRes.json());
      if (risksRes.ok) setRisks(await risksRes.json());
      if (clarsRes.ok) setClarifications(await clarsRes.json());
      if (graphRes.ok) setGraphData(await graphRes.json());
    } catch (err) {
      console.error("Error fetching requirement intelligence data:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const triggerExtraction = async () => {
    setIsExtracting(true);
    try {
      const res = await fetch(`/api/v1/rfp/${documentId}/requirements/extract`, { method: "POST" });
      if (res.ok) {
        await fetchData();
      }
    } catch (err) {
      console.error("Extraction error:", err);
    } finally {
      setIsExtracting(false);
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority?.toLowerCase()) {
      case "high":
        return "bg-rose-500/20 text-rose-300 border-rose-500/40";
      case "medium":
        return "bg-amber-500/20 text-amber-300 border-amber-500/40";
      case "low":
        return "bg-emerald-500/20 text-emerald-300 border-emerald-500/40";
      default:
        return "bg-slate-500/20 text-slate-300 border-slate-500/40";
    }
  };

  const filteredRequirements = requirements.filter((r) => {
    const matchesSearch = r.title.toLowerCase().includes(searchQuery) || r.text_content.toLowerCase().includes(searchQuery);
    const matchesCategory = filterCategory === "All" || r.category === filterCategory;
    const matchesPriority = filterPriority === "All" || r.priority === filterPriority;
    return matchesSearch && matchesCategory && matchesPriority;
  });

  return (
    <div className="border border-slate-800 bg-slate-900/60 backdrop-blur-xl rounded-xl p-6 mt-6 shadow-2xl">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center border-b border-slate-800 pb-4 mb-6">
        <div>
          <h2 className="text-xl font-bold bg-gradient-to-r from-teal-400 to-cyan-400 bg-clip-text text-transparent">
            AI Requirement Intelligence & Knowledge Graph
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Extract, categorize, prioritize and map relational connections from your RFP document
          </p>
        </div>
        <button
          onClick={triggerExtraction}
          disabled={isExtracting}
          className="mt-3 md:mt-0 px-4 py-2 bg-gradient-to-r from-teal-500 to-cyan-600 hover:from-teal-400 hover:to-cyan-500 text-white text-xs font-semibold rounded-lg shadow-lg shadow-cyan-900/40 transition duration-300 flex items-center gap-2 disabled:opacity-50"
        >
          {isExtracting ? (
            <>
              <svg className="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              Extracting Intelligence...
            </>
          ) : (
            <>
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              Run Requirement Extraction
            </>
          )}
        </button>
      </div>

      {isLoading ? (
        <div className="py-20 flex flex-col justify-center items-center gap-3">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-teal-400" />
          <span className="text-sm text-slate-400">Loading intelligence panels...</span>
        </div>
      ) : requirements.length === 0 ? (
        <div className="py-20 text-center border border-dashed border-slate-800 rounded-xl bg-slate-950/20">
          <svg className="mx-auto h-12 w-12 text-slate-600 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
          <h3 className="text-sm font-semibold text-slate-300">No Intelligence Data Found</h3>
          <p className="text-xs text-slate-500 max-w-sm mx-auto mt-1">
            Trigger the AI Requirement Extraction engine above to parse requirements, compliance matrices, and knowledge graph linkages.
          </p>
        </div>
      ) : (
        <div>
          {/* Tabs Nav */}
          <div className="flex flex-wrap gap-2 mb-6 border-b border-slate-800 pb-3">
            {[
              { id: "requirements", label: "Requirements" },
              { id: "deliverables", label: "Deliverables" },
              { id: "evaluation", label: "Evaluation Criteria" },
              { id: "submission", label: "Submission Instructions" },
              { id: "compliance", label: "Compliance Obligations" },
              { id: "risks", label: "Risks & Clarifications" },
              { id: "graph", label: "Interactive Knowledge Graph" },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-all duration-200 ${
                  activeTab === tab.id
                    ? "bg-teal-500/20 text-teal-300 border-teal-500/40 shadow-inner"
                    : "bg-slate-950/40 text-slate-400 border-slate-800 hover:text-slate-200 hover:border-slate-700"
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Requirements Tab */}
          {activeTab === "requirements" && (
            <div>
              {/* Filters */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-4">
                <input
                  type="text"
                  placeholder="Search requirements..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value.toLowerCase())}
                  className="bg-slate-950 border border-slate-800 text-xs text-slate-300 px-3 py-2 rounded-lg focus:outline-none focus:border-teal-500"
                />
                <select
                  value={filterCategory}
                  onChange={(e) => setFilterCategory(e.target.value)}
                  className="bg-slate-950 border border-slate-800 text-xs text-slate-300 px-3 py-2 rounded-lg focus:outline-none focus:border-teal-500"
                >
                  <option value="All">All Categories</option>
                  <option value="Technical">Technical</option>
                  <option value="Security">Security</option>
                  <option value="Legal">Legal</option>
                  <option value="Financial">Financial</option>
                </select>
                <select
                  value={filterPriority}
                  onChange={(e) => setFilterPriority(e.target.value)}
                  className="bg-slate-950 border border-slate-800 text-xs text-slate-300 px-3 py-2 rounded-lg focus:outline-none focus:border-teal-500"
                >
                  <option value="All">All Priorities</option>
                  <option value="High">High</option>
                  <option value="Medium">Medium</option>
                  <option value="Low">Low</option>
                </select>
              </div>

              {/* Requirements List */}
              <div className="space-y-3 max-h-[500px] overflow-y-auto pr-2">
                {filteredRequirements.map((req) => (
                  <div key={req.id} className="border border-slate-800/80 bg-slate-950/40 rounded-lg p-4 hover:border-slate-700 transition">
                    <div className="flex justify-between items-start gap-2">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="text-xs font-semibold text-slate-300">{req.title}</span>
                        <span className={`text-[10px] px-2 py-0.5 rounded border ${getPriorityColor(req.priority)}`}>
                          {req.priority}
                        </span>
                        <span className="text-[10px] bg-slate-800 text-slate-400 px-2 py-0.5 rounded">
                          {req.category}
                        </span>
                        <span className="text-[10px] bg-slate-800 text-slate-400 px-2 py-0.5 rounded">
                          {req.req_type}
                        </span>
                        {req.mandatory && (
                          <span className="text-[10px] bg-teal-500/10 text-teal-400 border border-teal-500/20 px-2 py-0.5 rounded font-medium">
                            Mandatory
                          </span>
                        )}
                      </div>
                      <span className="text-[10px] text-slate-500">
                        {req.source_section} (pg. {req.source_page})
                      </span>
                    </div>
                    <p className="text-xs text-slate-400 mt-2 leading-relaxed">{req.text_content}</p>
                    <div className="flex justify-between items-center mt-3 pt-2 border-t border-slate-900/60">
                      <div className="flex gap-1.5 items-center">
                        <span className="text-[10px] text-slate-500">Assigned:</span>
                        {req.assigned_departments.map((dept) => (
                          <span key={dept} className="text-[9px] bg-slate-900 text-slate-400 border border-slate-800 px-1.5 py-0.5 rounded">
                            {dept}
                          </span>
                        ))}
                      </div>
                      <div className="flex items-center gap-1">
                        <span className="text-[9px] text-slate-500">AI Confidence:</span>
                        <span className="text-[10px] text-teal-400 font-semibold">{(req.confidence * 100).toFixed(0)}%</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Deliverables Tab */}
          {activeTab === "deliverables" && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-h-[500px] overflow-y-auto pr-2">
              {deliverables.map((del) => (
                <div key={del.id} className="border border-slate-800 bg-slate-950/40 rounded-lg p-4 flex flex-col justify-between">
                  <div>
                    <div className="flex justify-between items-center">
                      <span className="text-xs font-bold text-slate-300">Deliverable</span>
                      <span className="text-[10px] text-slate-500 bg-slate-900 px-2 py-0.5 rounded">{del.responsible_department}</span>
                    </div>
                    <p className="text-xs text-slate-400 mt-2 leading-relaxed">{del.description}</p>
                  </div>
                  <div className="mt-4 pt-2 border-t border-slate-900 flex justify-between items-center text-[10px]">
                    <div className="text-slate-500">
                      Due Stage: <span className="text-slate-300">{del.deadline}</span>
                    </div>
                    <div className="text-teal-400 font-semibold">{(del.confidence * 100).toFixed(0)}% Confidence</div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Evaluation Tab */}
          {activeTab === "evaluation" && (
            <div className="space-y-4 max-h-[500px] overflow-y-auto pr-2">
              {evaluations.map((eva) => (
                <div key={eva.id} className="border border-slate-800 bg-slate-950/40 rounded-lg p-4">
                  <div className="flex justify-between items-center border-b border-slate-900 pb-2 mb-2">
                    <span className="text-xs font-bold text-slate-300">{eva.factor || "General Evaluation Criteria"}</span>
                    {eva.weight && <span className="text-xs text-teal-400 font-semibold">Weight: {eva.weight}</span>}
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs text-slate-400 mt-2">
                    <div>
                      <span className="text-slate-500 block text-[10px]">Criteria Text:</span>
                      <p className="leading-relaxed text-slate-300">{eva.criteria_text}</p>
                      {eva.scoring_methodology && (
                        <>
                          <span className="text-slate-500 block text-[10px] mt-2">Scoring Methodology:</span>
                          <p>{eva.scoring_methodology}</p>
                        </>
                      )}
                    </div>
                    <div className="space-y-2 border-t md:border-t-0 md:border-l border-slate-900 md:pl-4">
                      {eva.ranking_criteria && (
                        <div>
                          <span className="text-[10px] text-slate-500 block">Ranking Criteria:</span>
                          <p>{eva.ranking_criteria}</p>
                        </div>
                      )}
                      {eva.preferred_experience && (
                        <div>
                          <span className="text-[10px] text-slate-500 block">Preferred Experience:</span>
                          <p>{eva.preferred_experience}</p>
                        </div>
                      )}
                      {eva.preferred_certifications && (
                        <div>
                          <span className="text-[10px] text-slate-500 block">Preferred Certifications:</span>
                          <p>{eva.preferred_certifications}</p>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Submission Tab */}
          {activeTab === "submission" && (
            <div className="space-y-4 max-h-[500px] overflow-y-auto pr-2">
              {submissions.map((sub) => (
                <div key={sub.id} className="border border-slate-800 bg-slate-950/40 rounded-lg p-4 text-xs text-slate-400">
                  <span className="text-xs font-bold text-slate-300 block border-b border-slate-900 pb-2 mb-2">Submission Protocol</span>
                  <p className="text-slate-300 leading-relaxed mb-4">{sub.instruction_text}</p>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div>
                      <span className="text-slate-500 block text-[10px]">Method:</span>
                      <span className="text-slate-300">{sub.submission_method}</span>
                    </div>
                    {sub.portal && (
                      <div>
                        <span className="text-slate-500 block text-[10px]">Portal:</span>
                        <a href={sub.portal} target="_blank" rel="noreferrer" className="text-cyan-400 underline">{sub.portal}</a>
                      </div>
                    )}
                    {sub.file_naming_rules && (
                      <div>
                        <span className="text-slate-500 block text-[10px]">Naming Rules:</span>
                        <span className="text-slate-300 font-mono text-[10px]">{sub.file_naming_rules}</span>
                      </div>
                    )}
                    {sub.file_formats && (
                      <div>
                        <span className="text-slate-500 block text-[10px]">File Formats:</span>
                        <span className="text-slate-300">{sub.file_formats}</span>
                      </div>
                    )}
                    {sub.max_size && (
                      <div>
                        <span className="text-slate-500 block text-[10px]">Max Size:</span>
                        <span className="text-slate-300">{sub.max_size}</span>
                      </div>
                    )}
                    {sub.required_signatures && (
                      <div>
                        <span className="text-slate-500 block text-[10px]">Signatures Required:</span>
                        <span className="text-slate-300">{sub.required_signatures}</span>
                      </div>
                    )}
                    {sub.required_forms && (
                      <div>
                        <span className="text-slate-500 block text-[10px]">Required Forms:</span>
                        <span className="text-slate-300">{sub.required_forms}</span>
                      </div>
                    )}
                    {sub.late_policy && (
                      <div>
                        <span className="text-slate-500 block text-[10px]">Late Policy:</span>
                        <span className="text-rose-400">{sub.late_policy}</span>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Compliance Tab */}
          {activeTab === "compliance" && (
            <div className="space-y-3 max-h-[500px] overflow-y-auto pr-2">
              {compliance.map((com) => (
                <div key={com.id} className="border border-slate-800 bg-slate-950/40 rounded-lg p-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold text-slate-300">{com.name}</span>
                      {com.blocking && (
                        <span className="text-[9px] bg-rose-500/10 text-rose-400 border border-rose-500/20 px-1.5 py-0.5 rounded font-medium">
                          Blocking Obligation
                        </span>
                      )}
                    </div>
                    {com.evidence_required && (
                      <p className="text-xs text-slate-400 mt-1">
                        <span className="text-slate-500">Required Evidence:</span> {com.evidence_required}
                      </p>
                    )}
                  </div>
                  <div className="flex items-center gap-4 text-xs">
                    <div>
                      <span className="text-slate-500 block text-[9px]">Department:</span>
                      <span className="text-slate-300 font-medium">{com.department_owner}</span>
                    </div>
                    <div>
                      <span className="text-slate-500 block text-[9px]">Status:</span>
                      <span className="text-slate-400 font-medium bg-slate-900 border border-slate-800 px-2 py-0.5 rounded">{com.status}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Risks & Clarifications Tab */}
          {activeTab === "risks" && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 max-h-[500px] overflow-y-auto pr-2">
              {/* Risks Column */}
              <div>
                <h3 className="text-xs font-bold text-rose-400 mb-3 border-b border-rose-500/20 pb-2">Identified Risks</h3>
                <div className="space-y-3">
                  {risks.map((risk) => (
                    <div key={risk.id} className="border border-rose-950/40 bg-rose-950/5 rounded-lg p-4">
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-xs font-bold text-rose-300">RFP Risk</span>
                        <div className="flex gap-2">
                          <span className="text-[9px] bg-rose-500/20 text-rose-300 border border-rose-500/30 px-1.5 py-0.5 rounded">
                            Severity: {risk.severity}
                          </span>
                          <span className="text-[9px] bg-rose-500/20 text-rose-300 border border-rose-500/30 px-1.5 py-0.5 rounded">
                            Likelihood: {risk.likelihood}
                          </span>
                        </div>
                      </div>
                      <p className="text-xs text-slate-400 leading-relaxed">{risk.description}</p>
                      {risk.mitigation_suggestion && (
                        <div className="mt-3 pt-2 border-t border-rose-950/20 text-xs text-slate-400">
                          <span className="text-rose-400 font-semibold block text-[10px]">Mitigation Suggestion:</span>
                          <p>{risk.mitigation_suggestion}</p>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* Clarifications Column */}
              <div>
                <h3 className="text-xs font-bold text-cyan-400 mb-3 border-b border-cyan-500/20 pb-2">Suggested Clarification Questions</h3>
                <div className="space-y-3">
                  {clarifications.map((clar) => (
                    <div key={clar.id} className="border border-cyan-950/40 bg-cyan-950/5 rounded-lg p-4">
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-xs font-bold text-cyan-300">Question</span>
                        <span className="text-[9px] bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 px-1.5 py-0.5 rounded">
                          Priority: {clar.priority}
                        </span>
                      </div>
                      <p className="text-xs text-slate-300 leading-relaxed font-medium">"{clar.question_text}"</p>
                      <div className="mt-3 pt-2 border-t border-cyan-950/20 text-xs text-slate-400 space-y-2">
                        {clar.reason && (
                          <div>
                            <span className="text-cyan-400 font-semibold block text-[10px]">Reasoning:</span>
                            <p>{clar.reason}</p>
                          </div>
                        )}
                        {clar.business_impact && (
                          <div>
                            <span className="text-cyan-400 font-semibold block text-[10px]">Business Impact:</span>
                            <p>{clar.business_impact}</p>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Graph Tab */}
          {activeTab === "graph" && (
            <div className="border border-slate-800 bg-slate-950/40 rounded-xl p-4">
              <span className="text-xs font-bold text-slate-300 block border-b border-slate-900 pb-2 mb-2">RFP Relationship Network Map</span>
              <div className="h-[400px] flex items-center justify-center relative overflow-hidden bg-slate-950/80 rounded-lg">
                <svg className="absolute inset-0 w-full h-full">
                  {/* Edges */}
                  {graphData.edges.map((edge) => {
                    const srcIndex = graphData.nodes.findIndex((n) => n.id === edge.source);
                    const tgtIndex = graphData.nodes.findIndex((n) => n.id === edge.target);
                    if (srcIndex === -1 || tgtIndex === -1) return null;
                    
                    const x1 = 150 + (srcIndex % 3) * 220;
                    const y1 = 100 + Math.floor(srcIndex / 3) * 110;
                    const x2 = 150 + (tgtIndex % 3) * 220;
                    const y2 = 100 + Math.floor(tgtIndex / 3) * 110;

                    return (
                      <g key={edge.id}>
                        <line
                          x1={x1}
                          y1={y1}
                          x2={x2}
                          y2={y2}
                          stroke="#1e293b"
                          strokeWidth="1.5"
                          strokeDasharray="4 2"
                        />
                        <text
                          x={(x1 + x2) / 2}
                          y={(y1 + y2) / 2 - 4}
                          fill="#06b6d4"
                          fontSize="8"
                          textAnchor="middle"
                          className="bg-slate-950 px-1 font-semibold"
                        >
                          {edge.relationship}
                        </text>
                      </g>
                    );
                  })}
                </svg>

                {/* Nodes */}
                <div className="absolute inset-0 flex flex-wrap items-center justify-around p-8 gap-4 pointer-events-none">
                  {graphData.nodes.map((node, index) => {
                    const getNodeColor = (type: string) => {
                      switch (type) {
                        case "requirement": return "border-teal-500 bg-teal-950/80 text-teal-300";
                        case "deliverable": return "border-amber-500 bg-amber-950/80 text-amber-300";
                        case "risk": return "border-rose-500 bg-rose-950/80 text-rose-300";
                        case "compliance_obligation": return "border-indigo-500 bg-indigo-950/80 text-indigo-300";
                        default: return "border-slate-600 bg-slate-900/80 text-slate-300";
                      }
                    };

                    return (
                      <div
                        key={node.id}
                        className={`pointer-events-auto border rounded-xl px-3 py-2 text-center shadow-lg transition-transform duration-300 hover:scale-105 select-none ${getNodeColor(node.type)}`}
                        style={{
                          width: "160px",
                          fontSize: "10px",
                          fontWeight: "600"
                        }}
                      >
                        <span className="uppercase text-[7px] text-slate-400 block mb-1">{node.type}</span>
                        <div className="truncate">{node.label}</div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
