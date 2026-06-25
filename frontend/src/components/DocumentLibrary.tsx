"use client";

import React, { useState, useEffect } from "react";
import { FileText, Eye, HardDrive, RefreshCw } from "lucide-react";

interface Document {
  id: string;
  opportunity_id: string;
  file_name: string;
  uploaded_at: string;
}

interface Metadata {
  id: string;
  file_name: string;
  page_count: number;
  word_count: number;
  paragraph_count?: number;
  author: string;
  format: string;
}

interface DocumentLibraryProps {
  refreshTrigger: number;
}

export default function DocumentLibrary({ refreshTrigger }: DocumentLibraryProps) {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [selectedDocId, setSelectedDocId] = useState<string | null>(null);
  const [metadata, setMetadata] = useState<Metadata | null>(null);
  const [loading, setLoading] = useState(false);
  const [metaLoading, setMetaLoading] = useState(false);

  const fetchDocuments = async () => {
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/api/v1/documents");
      if (res.ok) {
        const data = await res.json();
        setDocuments(data);
      }
    } catch (e) {
      console.error("Failed to load documents", e);
    } finally {
      setLoading(false);
    }
  };

  const fetchMetadata = async (id: string) => {
    setMetaLoading(true);
    setSelectedDocId(id);
    try {
      const res = await fetch(`http://localhost:8000/api/v1/documents/${id}/metadata`);
      if (res.ok) {
        const data = await res.json();
        setMetadata(data);
      } else {
        setMetadata(null);
      }
    } catch (e) {
      console.error("Failed to load metadata", e);
      setMetadata(null);
    } finally {
      setMetaLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, [refreshTrigger]);

  return (
    <div className="w-full bg-neutral-900 border border-neutral-800 rounded-lg p-6 font-sans grid grid-cols-1 md:grid-cols-3 gap-6">
      
      {/* Document List */}
      <div className="md:col-span-2 flex flex-col">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-display font-semibold text-white">Document Library</h2>
          <button
            onClick={fetchDocuments}
            className="p-1 hover:bg-neutral-800 rounded text-neutral-400 hover:text-white"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
          </button>
        </div>

        {documents.length === 0 ? (
          <div className="flex-1 border border-neutral-800 rounded-lg bg-neutral-950/20 flex flex-col items-center justify-center p-8 text-neutral-500">
            <FileText className="w-8 h-8 mb-2" />
            <p className="text-sm">No ingested documents found.</p>
          </div>
        ) : (
          <div className="space-y-2 max-h-[300px] overflow-y-auto pr-2">
            {documents.map((doc) => (
              <div
                key={doc.id}
                onClick={() => fetchMetadata(doc.id)}
                className={`p-3 border rounded-lg flex items-center justify-between cursor-pointer transition-all ${
                  selectedDocId === doc.id
                    ? "bg-emerald-950/20 border-emerald-500/50"
                    : "bg-neutral-950/40 border-neutral-800 hover:border-neutral-700"
                }`}
              >
                <div className="flex items-center gap-3">
                  <FileText className="w-5 h-5 text-neutral-400" />
                  <div>
                    <p className="text-sm font-medium text-white truncate max-w-[200px] md:max-w-xs">{doc.file_name}</p>
                    <p className="text-xs text-neutral-500">{new Date(doc.uploaded_at).toLocaleString()}</p>
                  </div>
                </div>
                <Eye className="w-4 h-4 text-neutral-500" />
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Metadata Detail Panel */}
      <div className="border-l border-neutral-800 pl-6 flex flex-col">
        <h2 className="text-lg font-display font-semibold mb-4 text-white">Intelligence Summary</h2>
        
        {metaLoading ? (
          <div className="flex-1 flex flex-col items-center justify-center text-neutral-500">
            <RefreshCw className="w-6 h-6 animate-spin mb-2" />
            <p className="text-xs">Extracting metadata structure...</p>
          </div>
        ) : selectedDocId && metadata ? (
          <div className="space-y-4 text-sm text-neutral-300">
            <div className="pb-3 border-b border-neutral-800">
              <p className="text-xs text-neutral-500">Document ID</p>
              <p className="font-mono text-xs text-neutral-400 truncate">{metadata.id}</p>
            </div>
            
            <div className="grid grid-cols-2 gap-3">
              <div>
                <p className="text-xs text-neutral-500">Format</p>
                <span className="inline-block px-2 py-0.5 bg-emerald-950/50 border border-emerald-500/30 text-emerald-400 text-xs font-mono rounded mt-1">
                  {metadata.format}
                </span>
              </div>
              <div>
                <p className="text-xs text-neutral-500">Page Count</p>
                <p className="font-semibold text-white mt-1">{metadata.page_count}</p>
              </div>
            </div>

            <div>
              <p className="text-xs text-neutral-500">Word Count</p>
              <p className="font-semibold text-white mt-1">{metadata.word_count.toLocaleString()}</p>
            </div>

            {metadata.paragraph_count !== undefined && (
              <div>
                <p className="text-xs text-neutral-500">Paragraph Count</p>
                <p className="font-semibold text-white mt-1">{metadata.paragraph_count}</p>
              </div>
            )}

            <div>
              <p className="text-xs text-neutral-500">Author</p>
              <p className="text-white truncate mt-1">{metadata.author}</p>
            </div>

            <div className="pt-2 border-t border-neutral-800 flex items-center gap-2 text-xs text-neutral-500">
              <HardDrive className="w-3.5 h-3.5" />
              <span>Storage status: Local disk</span>
            </div>
          </div>
        ) : (
          <div className="flex-1 flex flex-col items-center justify-center text-neutral-500 p-4 border border-neutral-800 border-dashed rounded-lg bg-neutral-950/10">
            <p className="text-xs text-center">Select a document from the library to inspect structural intelligence</p>
          </div>
        )}
      </div>

    </div>
  );
}
