"use client";

import { motion } from "framer-motion";
import { Clock3, Leaf, Route, Wallet } from "lucide-react";
import { useCommuteStore } from "@/store/commute-store";

const recommendationCards = [
  {
    title: "Metro + Walk",
    eta: "34 min",
    cost: "$2.75",
    carbon: "0.4 kg",
    summary: "Best for reliability and carbon efficiency during peak load."
  },
  {
    title: "EV Ride Share",
    eta: "28 min",
    cost: "$12.40",
    carbon: "1.1 kg",
    summary: "Fastest premium option with lower emissions than default auto routing."
  },
  {
    title: "Bike + Bus",
    eta: "31 min",
    cost: "$3.20",
    carbon: "0.3 kg",
    summary: "Balanced option when weather and bus headway conditions are favorable."
  }
];

export function CommandCenter() {
  const { priority, setPriority } = useCommuteStore();

  return (
    <motion.section
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.55, delay: 0.18 }}
      className="panel rounded-[2rem] border border-white/10 p-6 shadow-glow lg:p-7"
    >
      <div className="flex flex-col gap-4 border-b border-white/10 pb-6 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-sm uppercase tracking-[0.2em] text-white/44">Command Center</p>
          <h2 className="mt-2 text-2xl font-semibold text-white">Rank the right commute mode.</h2>
        </div>
        <div className="flex flex-wrap gap-2">
          {["balanced", "time", "cost", "carbon"].map((mode) => {
            const active = priority === mode;
            return (
              <button
                key={mode}
                onClick={() => setPriority(mode)}
                className={`rounded-full px-4 py-2 text-sm capitalize transition ${
                  active
                    ? "bg-accent text-surface"
                    : "border border-white/10 bg-white/5 text-white/70 hover:bg-white/8"
                }`}
              >
                {mode}
              </button>
            );
          })}
        </div>
      </div>

      <div className="mt-6 grid gap-4">
        {recommendationCards.map((card) => (
          <article
            key={card.title}
            className="rounded-[1.5rem] border border-white/10 bg-white/5 p-5 transition hover:border-accent/40"
          >
            <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <h3 className="text-xl font-medium text-white">{card.title}</h3>
                <p className="mt-2 max-w-xl text-sm leading-6 text-white/64">{card.summary}</p>
              </div>
              <div className="grid grid-cols-3 gap-3">
                <MetricBadge icon={Clock3} label="ETA" value={card.eta} />
                <MetricBadge icon={Wallet} label="Cost" value={card.cost} />
                <MetricBadge icon={Leaf} label="Carbon" value={card.carbon} />
              </div>
            </div>
          </article>
        ))}
      </div>

      <div className="mt-6 rounded-[1.5rem] border border-dashed border-white/12 bg-black/20 p-5 text-sm leading-6 text-white/62">
        Current optimization bias is <span className="text-accent">{priority}</span>. The UI state
        is managed through Zustand so exploration settings remain local and fast while API-backed
        recommendations can stay in React Query cache.
      </div>
    </motion.section>
  );
}

type MetricBadgeProps = {
  icon: typeof Route;
  label: string;
  value: string;
};

function MetricBadge({ icon: Icon, label, value }: MetricBadgeProps) {
  return (
    <div className="rounded-[1.2rem] border border-white/10 bg-black/20 px-4 py-3">
      <div className="flex items-center gap-2 text-xs uppercase tracking-[0.14em] text-white/46">
        <Icon className="h-3.5 w-3.5 text-signal-cyan" />
        {label}
      </div>
      <p className="mt-2 text-lg font-semibold text-white">{value}</p>
    </div>
  );
}

