"use client";

import React, { useState } from "react";
import { motion } from "framer-motion";
import UploadCenter from "../components/UploadCenter";
import DocumentLibrary from "../components/DocumentLibrary";

export default function LandingPage() {
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const handleUploadSuccess = () => {
    setRefreshTrigger((prev) => prev + 1);
  };

  return (
    <div className="flex flex-col flex-1 p-8 bg-neutral-950 text-white relative overflow-hidden min-h-screen">
      {/* Background Micro Grid pattern */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808005_1px,transparent_1px),linear-gradient(to_bottom,#80808005_1px,transparent_1px)] bg-[size:24px_24px] pointer-events-none" />

      {/* Cybernetic Accent Blur */}
      <div className="absolute top-0 right-1/4 w-[600px] h-[600px] bg-emerald-500/5 rounded-full blur-[160px] pointer-events-none" />

      <header className="z-10 flex items-center justify-between mb-8 pb-4 border-b border-neutral-950/20">
        <div>
          <h1 className="text-2xl font-display font-bold tracking-tight text-white">SPS Proposal Capture Manager</h1>
          <p className="text-xs text-neutral-500 font-mono mt-0.5">Enterprise AI Decision Platform • Document Intake Workspace</p>
        </div>
        <div className="inline-flex items-center gap-2 px-3 py-1 text-xs font-mono text-emerald-400 bg-emerald-950/20 border border-emerald-500/20 rounded-full">
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse" />
          SYSTEM_ONLINE
        </div>
      </header>

      <main className="z-10 grid grid-cols-1 gap-8 max-w-6xl mx-auto w-full">
        {/* Ingestion Panel */}
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <UploadCenter onUploadSuccess={handleUploadSuccess} />
        </motion.div>

        {/* Library & Metadata Panel */}
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
        >
          <DocumentLibrary refreshTrigger={refreshTrigger} />
        </motion.div>
      </main>

      <footer className="mt-auto pt-8 text-center text-[10px] text-neutral-600 font-mono">
        SPS ENTERPRISE AI • ACCESS RESTRICTED TO AUTHORIZED CAPTURE TEAMS ONLY
      </footer>
    </div>
  );
}
