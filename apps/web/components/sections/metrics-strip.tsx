"use client";

import { motion } from "framer-motion";

const metrics = [
  { label: "Avg. ETA confidence", value: "94.2%" },
  { label: "Modal ranking latency", value: "128 ms" },
  { label: "Emissions avoided", value: "18.4 t" },
  { label: "Network nodes modeled", value: "2.3 M" }
];

export function MetricsStrip() {
  return (
    <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      {metrics.map((metric, index) => (
        <motion.article
          key={metric.label}
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.45, delay: 0.12 + index * 0.07 }}
          className="panel rounded-[1.5rem] border border-white/10 px-5 py-5"
        >
          <p className="text-sm text-white/52">{metric.label}</p>
          <p className="mt-3 text-3xl font-semibold text-white">{metric.value}</p>
        </motion.article>
      ))}
    </section>
  );
}

