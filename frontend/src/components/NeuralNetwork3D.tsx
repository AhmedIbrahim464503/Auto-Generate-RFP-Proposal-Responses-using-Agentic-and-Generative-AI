'use client';

import React, { useEffect, useRef } from 'react';

export default function NeuralNetwork3D() {
  const containerRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationFrameId: number;
    let width = (canvas.width = containerRef.current?.clientWidth || 800);
    let height = (canvas.height = containerRef.current?.clientHeight || 300);

    const particles: Array<{
      x: number;
      y: number;
      vx: number;
      vy: number;
      radius: number;
    }> = [];

    // Create particles
    const particleCount = 40;
    for (let i = 0; i < particleCount; i++) {
      particles.push({
        x: Math.random() * width,
        y: Math.random() * height,
        vx: (Math.random() - 0.5) * 0.5,
        vy: (Math.random() - 0.5) * 0.5,
        radius: Math.random() * 2 + 1,
      });
    }

    const resizeHandler = () => {
      if (canvas && containerRef.current) {
        width = canvas.width = containerRef.current.clientWidth;
        height = canvas.height = containerRef.current.clientHeight;
      }
    };
    window.addEventListener('resize', resizeHandler);

    // Animation Loop
    const draw = () => {
      ctx.clearRect(0, 0, width, height);

      // Draw lines
      ctx.strokeStyle = 'rgba(124, 58, 237, 0.15)'; // Violet glow
      ctx.lineWidth = 0.5;
      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const dx = particles[i].x - particles[j].x;
          const dy = particles[i].y - particles[j].y;
          const dist = Math.sqrt(dx * dx + dy * dy);

          if (dist < 100) {
            ctx.beginPath();
            ctx.moveTo(particles[i].x, particles[i].y);
            ctx.lineTo(particles[j].x, particles[j].y);
            ctx.stroke();
          }
        }
      }

      // Draw particles
      ctx.fillStyle = 'rgba(167, 139, 250, 0.8)'; // Light violet
      particles.forEach((p) => {
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        ctx.fill();

        // Move
        p.x += p.vx;
        p.y += p.vy;

        // Bounce
        if (p.x < 0 || p.x > width) p.vx *= -1;
        if (p.y < 0 || p.y > height) p.vy *= -1;
      });

      animationFrameId = requestAnimationFrame(draw);
    };

    draw();

    return () => {
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener('resize', resizeHandler);
    };
  }, []);

  return (
    <div ref={containerRef} className="relative w-full h-[180px] bg-slate-950/80 rounded-xl overflow-hidden border border-slate-800/80">
      <canvas ref={canvasRef} className="absolute inset-0 block w-full h-full pointer-events-none" />
      <div className="absolute inset-0 flex flex-col justify-center px-6 z-10">
        <span className="text-[10px] font-mono text-violet-400 uppercase tracking-widest">Active Neural Engine</span>
        <h3 className="text-lg font-bold text-white mt-1">Multi-Agent Intelligence Network</h3>
        <p className="text-slate-400 text-xs mt-1 max-w-md">
          Monitoring real-time node state transitions, hybrid pgvector retrieval checkpoints, and feasibility gates.
        </p>
      </div>
    </div>
  );
}
