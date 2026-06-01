"use client";

import { motion } from "framer-motion";
import { Activity, Sparkles, Waves } from "lucide-react";
import type { CommandCenterSnapshot, DashboardOverviewResponse } from "@/types/mobility";

type AnalyticsBoardProps = {
  dashboard: DashboardOverviewResponse | undefined;
  liveSnapshot: CommandCenterSnapshot | null;
  isLoading: boolean;
};

const toneMap = {
  accent: "text-accent",
  cyan: "text-signal-cyan",
  lime: "text-signal-lime",
  amber: "text-signal-amber"
} as const;

const signalMap = {
  stable: "text-white/72",
  watch: "text-signal-amber",
  critical: "text-[#ff8f7a]",
  positive: "text-accent"
} as const;

export function AnalyticsBoard({ dashboard, liveSnapshot, isLoading }: AnalyticsBoardProps) {
  if (isLoading) {
    return (
      <section className="grid gap-4 xl:grid-cols-[1.1fr_0.9fr]">
        <div className="panel h-[420px] animate-pulse rounded-[2rem] border border-white/10 bg-white/5" />
        <div className="panel h-[420px] animate-pulse rounded-[2rem] border border-white/10 bg-white/5" />
      </section>
    );
  }

  const commandCenter = liveSnapshot ?? dashboard?.command_center;

  return (
    <section className="grid gap-4 xl:grid-cols-[1.08fr_0.92fr]">
      <motion.article
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        className="panel rounded-[2rem] border border-white/10 p-6 shadow-glow"
      >
        <div className="flex items-center justify-between gap-4">
          <div>
            <p className="text-sm uppercase tracking-[0.2em] text-white/44">City Pulse</p>
            <h2 className="mt-2 text-2xl font-semibold text-white">Live urban operating state.</h2>
          </div>
          <Activity className="h-5 w-5 text-accent" />
        </div>
        <div className="mt-6 grid gap-4 md:grid-cols-2">
          {dashboard?.metrics.map((metric) => (
            <div key={metric.label} className="rounded-[1.5rem] border border-white/10 bg-white/5 p-5">
              <p className="text-sm text-white/52">{metric.label}</p>
              <p className={`mt-3 text-3xl font-semibold ${toneMap[metric.tone]}`}>{metric.value}</p>
              <p className="mt-2 text-sm text-white/58">{metric.delta}</p>
            </div>
          ))}
        </div>
        <div className="mt-6 grid gap-4 lg:grid-cols-[0.9fr_1.1fr]">
          <div className="rounded-[1.6rem] border border-white/10 bg-black/20 p-5">
            <div className="flex items-center gap-2">
              <Waves className="h-4 w-4 text-signal-cyan" />
              <p className="text-xs uppercase tracking-[0.18em] text-white/42">Pulse metrics</p>
            </div>
            <div className="mt-4 space-y-4">
              {commandCenter?.city_pulse.map((item) => (
                <div key={item.label}>
                  <p className="text-sm text-white/46">{item.label}</p>
                  <p className={`mt-1 text-xl font-semibold ${signalMap[item.signal]}`}>{item.value}</p>
                </div>
              ))}
            </div>
          </div>
          <div className="rounded-[1.6rem] border border-white/10 bg-black/20 p-5">
            <p className="text-xs uppercase tracking-[0.18em] text-white/42">Carbon impact</p>
            <div className="mt-5">
              <div className="h-3 overflow-hidden rounded-full bg-white/8">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-[#74dfff] via-[#86ffca] to-[#d3ff74]"
                  style={{
                    width: `${Math.min(
                      100,
                      (dashboard?.sustainability.savings_vs_rideshare_kg ?? 0) * 12
                    )}%`
                  }}
                />
              </div>
              <div className="mt-4 grid gap-3 sm:grid-cols-2">
                <MetricColumn
                  label="Saved vs rideshare"
                  value={`${dashboard?.sustainability.savings_vs_rideshare_kg ?? 0} kg`}
                />
                <MetricColumn
                  label="Average trip emissions"
                  value={`${dashboard?.sustainability.average_trip_emissions_kg ?? 0} kg`}
                />
                <MetricColumn
                  label="Total trip emissions"
                  value={`${dashboard?.sustainability.total_emissions_kg ?? 0} kg`}
                />
                <MetricColumn
                  label="Greenest mode leader"
                  value={dashboard?.sustainability.greenest_mode_share ?? "No data"}
                />
              </div>
            </div>
          </div>
        </div>
      </motion.article>

      <motion.article
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.08 }}
        className="space-y-4"
      >
        <div className="panel rounded-[2rem] border border-white/10 p-6 shadow-glow">
          <div className="flex items-center justify-between gap-4">
            <div>
              <p className="text-sm uppercase tracking-[0.2em] text-white/44">Predictive Panels</p>
              <h2 className="mt-2 text-2xl font-semibold text-white">Congestion and route intelligence.</h2>
            </div>
            <Sparkles className="h-5 w-5 text-accent" />
          </div>
          <div className="mt-6 space-y-3">
            {commandCenter?.predictive_congestion.map((panel) => (
              <div key={panel.corridor} className="rounded-[1.4rem] border border-white/10 bg-white/5 p-4">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="text-sm font-medium text-white">{panel.corridor}</p>
                    <p className="mt-1 text-sm text-white/56">{panel.recommendation}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-xs uppercase tracking-[0.16em] text-white/42">{panel.intensity}</p>
                    <p className="mt-2 text-sm text-accent">Confidence {panel.confidence}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="panel rounded-[2rem] border border-white/10 p-6 shadow-glow">
          <p className="text-sm uppercase tracking-[0.2em] text-white/44">Insights Timeline</p>
          <div className="mt-5 space-y-4">
            {commandCenter?.insights_timeline.map((item) => (
              <div key={`${item.timestamp}-${item.headline}`} className="rounded-[1.4rem] border border-white/10 bg-black/20 p-4">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="text-sm font-medium text-white">{item.headline}</p>
                    <p className="mt-2 text-sm leading-6 text-white/58">{item.narrative}</p>
                  </div>
                  <p className={`text-xs uppercase tracking-[0.18em] ${severityColor(item.severity)}`}>
                    {item.severity}
                  </p>
                </div>
              </div>
            ))}
          </div>
          <div className="mt-6 space-y-3">
            {dashboard?.ai_recommendations.map((recommendation) => (
              <div key={recommendation.title} className="rounded-[1.4rem] border border-white/10 bg-white/5 p-4">
                <p className="text-sm font-medium text-white">{recommendation.title}</p>
                <p className="mt-2 text-sm leading-6 text-white/62">{recommendation.narrative}</p>
                <p className="mt-3 text-xs uppercase tracking-[0.16em] text-accent">
                  {recommendation.impact_label}
                </p>
              </div>
            ))}
          </div>
        </div>
      </motion.article>
    </section>
  );
}

function MetricColumn({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-sm text-white/48">{label}</p>
      <p className="mt-2 text-xl font-semibold text-white">{value}</p>
    </div>
  );
}

function severityColor(severity: "info" | "watch" | "critical" | "positive") {
  if (severity === "critical") return "text-[#ff8f7a]";
  if (severity === "watch") return "text-signal-amber";
  if (severity === "positive") return "text-accent";
  return "text-white/46";
}
