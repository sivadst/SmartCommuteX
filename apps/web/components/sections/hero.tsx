"use client";

import { motion } from "framer-motion";
import { ArrowRight, Orbit, ShieldCheck, Sparkles } from "lucide-react";
import { Navbar } from "@/components/layout/navbar";

const featureChips = [
  "Predictive ETA intelligence",
  "Carbon-aware route ranking",
  "Multimodal optimization",
  "EV + transit support"
];

export function Hero() {
  return (
    <section className="space-y-6">
      <Navbar />
      <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, ease: "easeOut" }}
          className="panel grid-pattern overflow-hidden rounded-[2rem] border border-white/10 bg-grid-radial px-7 py-8 shadow-glow lg:px-10 lg:py-10"
        >
          <div className="space-y-7">
            <div className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-2 text-xs uppercase tracking-[0.2em] text-white/70">
              <Sparkles className="h-3.5 w-3.5 text-accent" />
              Mobility OS for sustainable cities
            </div>
            <div className="max-w-3xl space-y-5">
              <h1 className="text-4xl font-semibold leading-tight text-white md:text-6xl">
                Commute intelligence built for decisions, not directions.
              </h1>
              <p className="max-w-2xl text-base leading-7 text-white/68 md:text-lg">
                SmartCommuteX ranks the best trip across transit, walking, micro-mobility, and EV
                paths by time, cost, carbon, reliability, and mode fit.
              </p>
            </div>
            <div className="flex flex-wrap gap-3">
              {featureChips.map((chip) => (
                <span
                  key={chip}
                  className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-white/76"
                >
                  {chip}
                </span>
              ))}
            </div>
            <div className="flex flex-wrap items-center gap-4 pt-2">
              <button className="inline-flex items-center gap-2 rounded-full bg-accent px-5 py-3 text-sm font-semibold text-surface transition hover:translate-y-[-1px]">
                Launch Command Surface
                <ArrowRight className="h-4 w-4" />
              </button>
              <div className="inline-flex items-center gap-2 text-sm text-white/66">
                <ShieldCheck className="h-4 w-4 text-signal-lime" />
                Scale-ready architecture baseline
              </div>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.96 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.75, ease: "easeOut", delay: 0.1 }}
          className="panel relative overflow-hidden rounded-[2rem] border border-white/10 p-6 shadow-glow"
        >
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(134,255,202,0.18),transparent_32%),radial-gradient(circle_at_bottom_left,rgba(116,223,255,0.18),transparent_26%)]" />
          <div className="relative flex h-full flex-col justify-between">
            <div className="flex items-center justify-between">
              <p className="text-sm uppercase tracking-[0.2em] text-white/48">Mobility Signal</p>
              <Orbit className="h-5 w-5 text-accent" />
            </div>
            <div className="space-y-6 py-8">
              <div className="rounded-[1.5rem] border border-white/10 bg-black/20 p-5">
                <p className="text-sm text-white/54">Predicted network pressure</p>
                <p className="mt-2 text-4xl font-semibold">Low-Moderate</p>
                <p className="mt-3 text-sm leading-6 text-white/66">
                  AI routing fabric suggests hybrid metro + walk commute windows between 08:10 and
                  08:40 with 21% lower carbon cost than rideshare default.
                </p>
              </div>
              <div className="grid gap-4 sm:grid-cols-2">
                <div className="rounded-[1.5rem] border border-white/10 bg-white/5 p-4">
                  <p className="text-sm text-white/52">Savings opportunity</p>
                  <p className="mt-2 text-3xl font-semibold text-accent">31%</p>
                </div>
                <div className="rounded-[1.5rem] border border-white/10 bg-white/5 p-4">
                  <p className="text-sm text-white/52">Carbon delta</p>
                  <p className="mt-2 text-3xl font-semibold text-signal-cyan">-2.8 kg</p>
                </div>
              </div>
            </div>
            <p className="text-xs uppercase tracking-[0.18em] text-white/42">
              Forecast layer wired for route graphs, transit feeds, and ML inference
            </p>
          </div>
        </motion.div>
      </div>
    </section>
  );
}

