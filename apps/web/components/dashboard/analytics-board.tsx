"use client";

import { motion } from "framer-motion";
import { Sparkles } from "lucide-react";
import type { DashboardOverviewResponse } from "@/types/mobility";

type AnalyticsBoardProps = {
  dashboard: DashboardOverviewResponse | undefined;
  isLoading: boolean;
};

const toneMap = {
  accent: "text-accent",
  cyan: "text-signal-cyan",
  lime: "text-signal-lime",
  amber: "text-signal-amber"
} as const;

export function AnalyticsBoard({ dashboard, isLoading }: AnalyticsBoardProps) {
  if (isLoading) {
    return (
      <section className="grid gap-4 xl:grid-cols-[1.1fr_0.9fr]">
        <div className="panel h-[340px] animate-pulse rounded-[2rem] border border-white/10 bg-white/5" />
        <div className="panel h-[340px] animate-pulse rounded-[2rem] border border-white/10 bg-white/5" />
      </section>
    );
  }

  return (
    <section className="grid gap-4 xl:grid-cols-[1.1fr_0.9fr]">
      <motion.article
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        className="panel rounded-[2rem] border border-white/10 p-6 shadow-glow"
      >
        <div className="flex items-center justify-between gap-4">
          <div>
            <p className="text-sm uppercase tracking-[0.2em] text-white/44">Commute Analytics</p>
            <h2 className="mt-2 text-2xl font-semibold text-white">Live platform health.</h2>
          </div>
          <Sparkles className="h-5 w-5 text-accent" />
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
        <div className="mt-6 rounded-[1.5rem] border border-white/10 bg-black/20 p-5">
          <p className="text-xs uppercase tracking-[0.18em] text-white/42">Sustainability</p>
          <div className="mt-4 grid gap-4 sm:grid-cols-2">
            <MetricColumn
              label="Total trip emissions"
              value={`${dashboard?.sustainability.total_emissions_kg ?? 0} kg`}
            />
            <MetricColumn
              label="Saved vs rideshare"
              value={`${dashboard?.sustainability.savings_vs_rideshare_kg ?? 0} kg`}
            />
            <MetricColumn
              label="Average per trip"
              value={`${dashboard?.sustainability.average_trip_emissions_kg ?? 0} kg`}
            />
            <MetricColumn
              label="Current greenest leader"
              value={dashboard?.sustainability.greenest_mode_share ?? "No data"}
            />
          </div>
        </div>
      </motion.article>

      <motion.article
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.08 }}
        className="panel rounded-[2rem] border border-white/10 p-6 shadow-glow"
      >
        <div>
          <p className="text-sm uppercase tracking-[0.2em] text-white/44">Mobility Memory</p>
          <h2 className="mt-2 text-2xl font-semibold text-white">Trip history and AI guidance.</h2>
        </div>
        <div className="mt-6 space-y-3">
          {dashboard?.recent_trips.length ? (
            dashboard.recent_trips.map((trip) => (
              <div
                key={trip.trip_id}
                className="rounded-[1.4rem] border border-white/10 bg-white/5 p-4"
              >
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="text-sm font-medium text-white">
                      {trip.origin_label} to {trip.destination_label}
                    </p>
                    <p className="mt-1 text-sm text-white/56">
                      {trip.selected_mode} · {trip.predicted_duration_minutes} min ·{" "}
                      {trip.objective.replace("_", " ")}
                    </p>
                  </div>
                  <p className="text-sm text-signal-lime">{trip.carbon_kg} kg</p>
                </div>
              </div>
            ))
          ) : (
            <div className="rounded-[1.4rem] border border-dashed border-white/12 bg-black/20 p-4 text-sm text-white/58">
              Planned trips will begin to accumulate here once you run live route plans.
            </div>
          )}
        </div>
        <div className="mt-6 space-y-3">
          {dashboard?.ai_recommendations.map((recommendation) => (
            <div key={recommendation.title} className="rounded-[1.4rem] border border-white/10 bg-black/20 p-4">
              <p className="text-sm font-medium text-white">{recommendation.title}</p>
              <p className="mt-2 text-sm leading-6 text-white/62">{recommendation.narrative}</p>
              <p className="mt-3 text-xs uppercase tracking-[0.16em] text-accent">
                {recommendation.impact_label}
              </p>
            </div>
          ))}
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

