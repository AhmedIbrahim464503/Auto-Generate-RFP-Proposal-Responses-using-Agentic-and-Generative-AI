"use client";

import React from "react";
import { motion } from "framer-motion";

export default function LandingPage() {
  return (
    <div className="flex flex-col flex-1 items-center justify-center p-8 bg-gradient-to-br from-neutral-950 via-neutral-900 to-black text-white relative overflow-hidden">
      {/* Background Micro Grid pattern */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#8080800a_1px,transparent_1px),linear-gradient(to_bottom,#8080800a_1px,transparent_1px)] bg-[size:14px_24px] pointer-events-none" />

      {/* Cybernetic Accent Ring */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[500px] h-[500px] bg-emerald-500/10 rounded-full blur-[120px] pointer-events-none" />

      <main className="z-10 max-w-4xl text-center flex flex-col items-center">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="inline-flex items-center gap-2 px-3 py-1 text-xs font-mono tracking-widest text-emerald-400 bg-emerald-950/40 border border-emerald-500/30 rounded-full mb-6"
        >
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          SECURE ENTERPRISE AI
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="text-4xl md:text-6xl font-display font-bold tracking-tight mb-4"
        >
          SPS Capture Manager
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
          className="text-neutral-400 max-w-2xl text-lg mb-8 leading-relaxed"
        >
          An enterprise-grade AI decision support platform orchestrating requirement intelligence, risk compliance matrices, and agentic RFP draft generation with strict human-in-the-loop oversight gates.
        </motion.p>

        {/* Console Command Box */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8, delay: 0.6 }}
          className="w-full max-w-xl bg-neutral-900/80 border border-neutral-800 rounded-lg p-6 font-mono text-left shadow-2xl relative"
        >
          <div className="flex items-center gap-2 border-b border-neutral-800 pb-3 mb-4 text-xs text-neutral-500">
            <span className="w-3 h-3 rounded-full bg-neutral-800" />
            <span className="w-3 h-3 rounded-full bg-neutral-800" />
            <span className="w-3 h-3 rounded-full bg-neutral-800" />
            <span className="ml-2">system_handshake.sh</span>
          </div>
          <div className="space-y-2 text-sm">
            <p className="text-neutral-500">$ initialize_sps_capture_manager --phase=1</p>
            <p className="text-emerald-400">✓ Repository foundation: OK</p>
            <p className="text-emerald-400">✓ PostgreSQL session pool: OK</p>
            <p className="text-emerald-400">✓ FastAPI app bootstrap: OK</p>
            <p className="text-neutral-500">Waiting for transaction signoff...</p>
          </div>
        </motion.div>
      </main>

      <footer className="absolute bottom-6 text-xs text-neutral-600 font-mono">
        SPS ENTERPRISE AI • PROPRIETARY SYSTEM
      </footer>
    </div>
  );
}
