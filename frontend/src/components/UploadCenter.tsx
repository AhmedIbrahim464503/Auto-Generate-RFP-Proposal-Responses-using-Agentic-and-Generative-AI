"use client";

import React, { useState, useRef } from "react";
import { motion } from "framer-motion";
import { Upload, FileText, AlertCircle, CheckCircle, RefreshCw } from "lucide-react";

interface UploadCenterProps {
  onUploadSuccess: () => void;
}

export default function UploadCenter({ onUploadSuccess }: UploadCenterProps) {
  const [dragActive, setDragActive] = useState(false);
  const [status, setStatus] = useState<"idle" | "validating" | "uploading" | "success" | "error">("idle");
  const [errorMessage, setErrorMessage] = useState("");
  const [progress, setProgress] = useState(0);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const processFile = async (file: File) => {
    const validExtensions = [".pdf", ".docx"];
    const ext = file.name.substring(file.name.lastIndexOf(".")).toLowerCase();

    if (!validExtensions.includes(ext)) {
      setStatus("error");
      setErrorMessage(`Invalid format. Only ${validExtensions.join(", ")} allowed.`);
      return;
    }

    if (file.size > 50 * 1024 * 1024) {
      setStatus("error");
      setErrorMessage("File exceeds the 50MB upload limit.");
      return;
    }

    setStatus("uploading");
    setProgress(20);

    // Mocking progress interval
    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 90) {
          clearInterval(interval);
          return 90;
        }
        return prev + 15;
      });
    }, 200);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const res = await fetch("http://localhost:8000/api/v1/documents/upload", {
        method: "POST",
        body: formData,
      });

      clearInterval(interval);

      if (!res.ok) {
        throw new Error(await res.text());
      }

      setProgress(100);
      setStatus("success");
      onUploadSuccess();
    } catch (e: any) {
      clearInterval(interval);
      setStatus("error");
      setErrorMessage("System failed to save document. Ensure backend service is running.");
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      processFile(e.target.files[0]);
    }
  };

  return (
    <div className="w-full bg-neutral-900 border border-neutral-800 rounded-lg p-6 font-sans">
      <h2 className="text-lg font-display font-semibold mb-4 text-white">Document Ingestion Center</h2>

      <div
        onDragEnter={handleDrag}
        onDragOver={handleDrag}
        onDragLeave={handleDrag}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`border-2 border-dashed rounded-lg p-8 flex flex-col items-center justify-center cursor-pointer transition-all ${
          dragActive
            ? "border-emerald-500 bg-emerald-500/5"
            : "border-neutral-800 hover:border-neutral-700 bg-neutral-950/40"
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          className="hidden"
          accept=".pdf,.docx"
          onChange={handleChange}
        />

        {status === "idle" && (
          <>
            <Upload className="w-10 h-10 text-neutral-500 mb-3" />
            <p className="text-sm text-neutral-300">Drag & drop RFP file, or click to browse</p>
            <p className="text-xs text-neutral-600 mt-1">Supports PDF & DOCX up to 50MB</p>
          </>
        )}

        {status === "uploading" && (
          <div className="w-full flex flex-col items-center">
            <RefreshCw className="w-8 h-8 text-emerald-400 animate-spin mb-3" />
            <p className="text-sm text-neutral-300 mb-2">Ingesting document... {progress}%</p>
            <div className="w-full max-w-xs bg-neutral-800 h-1.5 rounded-full overflow-hidden">
              <div
                className="bg-emerald-500 h-full transition-all duration-200"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        )}

        {status === "success" && (
          <div className="flex flex-col items-center text-center">
            <CheckCircle className="w-10 h-10 text-emerald-400 mb-3" />
            <p className="text-sm text-neutral-200 font-semibold">Document Ingested Successfully</p>
            <p className="text-xs text-neutral-500 mt-1">Metadata extracted and registered in database.</p>
            <button
              onClick={(e) => {
                e.stopPropagation();
                setStatus("idle");
              }}
              className="mt-4 px-3 py-1.5 bg-neutral-800 hover:bg-neutral-700 text-xs font-mono rounded text-neutral-300"
            >
              Upload Another
            </button>
          </div>
        )}

        {status === "error" && (
          <div className="flex flex-col items-center text-center">
            <AlertCircle className="w-10 h-10 text-red-500 mb-3" />
            <p className="text-sm text-neutral-200 font-semibold">Ingestion Failed</p>
            <p className="text-xs text-red-400 mt-1">{errorMessage}</p>
            <button
              onClick={(e) => {
                e.stopPropagation();
                setStatus("idle");
              }}
              className="mt-4 px-3 py-1.5 bg-neutral-800 hover:bg-neutral-700 text-xs font-mono rounded text-neutral-300"
            >
              Try Again
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
