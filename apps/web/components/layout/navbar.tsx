"use client";

import { motion } from "framer-motion";
import { Radar, Waypoints } from "lucide-react";

export function Navbar() {
  return (
    <motion.header
      initial={{ opacity: 0, y: -16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.55, ease: "easeOut" }}
      className="panel flex items-center justify-between rounded-full border border-white/10 px-5 py-4 shadow-glow"
    >
      <div className="flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-accent-soft text-accent">
          <Waypoints className="h-5 w-5" />
        </div>
        <div>
          <p className="text-sm uppercase tracking-[0.24em] text-white/45">SmartCommuteX</p>
          <p className="text-sm text-white/70">Urban Mobility Intelligence</p>
        </div>
      </div>
      <div className="hidden items-center gap-3 rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-white/75 md:flex">
        <Radar className="h-4 w-4 text-signal-cyan" />
        Live AI routing fabric
      </div>
    </motion.header>
  );
}

