"use client";

import { motion } from "framer-motion";
import { BrainCircuit, Gauge, MapPinned, Trees } from "lucide-react";

const pillars = [
  {
    title: "Predictive traffic layer",
    copy: "Forecast congestion and reliability drift before route selection happens.",
    icon: BrainCircuit
  },
  {
    title: "Routing graph intelligence",
    copy: "Fuse street, transit, EV, and micro-mobility networks into a single decision surface.",
    icon: MapPinned
  },
  {
    title: "Carbon scoring engine",
    copy: "Make sustainability visible at decision time, not buried in a report.",
    icon: Trees
  },
  {
    title: "Latency-disciplined UX",
    copy: "Keep trip ranking and network exploration responsive under load and poor networks.",
    icon: Gauge
  }
];

export function PlatformPillars() {
  return (
    <motion.aside
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.55, delay: 0.24 }}
      className="panel rounded-[2rem] border border-white/10 p-6 shadow-glow"
    >
      <div>
        <p className="text-sm uppercase tracking-[0.2em] text-white/44">Platform Pillars</p>
        <h2 className="mt-2 text-2xl font-semibold text-white">Built like a mobility stack.</h2>
      </div>
      <div className="mt-6 grid gap-4">
        {pillars.map(({ title, copy, icon: Icon }) => (
          <article key={title} className="rounded-[1.5rem] border border-white/10 bg-white/5 p-5">
            <div className="flex items-start gap-4">
              <div className="mt-0.5 flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-accent-soft text-accent">
                <Icon className="h-5 w-5" />
              </div>
              <div>
                <h3 className="text-lg font-medium text-white">{title}</h3>
                <p className="mt-2 text-sm leading-6 text-white/62">{copy}</p>
              </div>
            </div>
          </article>
        ))}
      </div>
    </motion.aside>
  );
}

