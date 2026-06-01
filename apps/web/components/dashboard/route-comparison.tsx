"use client";

import { ArrowRight, Clock3, Leaf, ShieldCheck, Wallet } from "lucide-react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import { usePlannerStore } from "@/store/planner-store";
import type { MobilityPlanResponse } from "@/types/mobility";

type RouteComparisonProps = {
  plan: MobilityPlanResponse | undefined;
  isPending: boolean;
};

export function RouteComparison({ plan, isPending }: RouteComparisonProps) {
  const { selectedRouteId, selectRoute } = usePlannerStore();

  if (isPending) {
    return (
      <section className="grid gap-4 lg:grid-cols-2">
        {Array.from({ length: 4 }).map((_, index) => (
          <div
            key={index}
            className="panel h-[188px] animate-pulse rounded-[1.75rem] border border-white/10 bg-white/5"
          />
        ))}
      </section>
    );
  }

  if (!plan) {
    return (
      <section className="panel rounded-[2rem] border border-white/10 p-6 shadow-glow">
        <p className="text-sm uppercase tracking-[0.2em] text-white/44">Route Comparison</p>
        <h2 className="mt-2 text-2xl font-semibold text-white">No route plan loaded yet.</h2>
        <p className="mt-3 max-w-2xl text-sm leading-6 text-white/64">
          The comparison deck activates once the planner fetches live routes from the routing
          engine.
        </p>
      </section>
    );
  }

  return (
    <section className="space-y-4">
      <div className="flex items-end justify-between gap-4">
        <div>
          <p className="text-sm uppercase tracking-[0.2em] text-white/44">Route Comparison</p>
          <h2 className="mt-2 text-2xl font-semibold text-white">
            Ranked by {plan.objective.replace("_", " ")} intelligence.
          </h2>
        </div>
        <div className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-white/72">
          {plan.summary.route_count} live options
        </div>
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        {plan.routes.map((route, index) => {
          const routeId = route.snapshot_id ?? `${route.mode}-${index}`;
          const active = (selectedRouteId ?? plan.routes[0]?.snapshot_id) === routeId;
          return (
            <motion.article
              key={routeId}
              initial={{ opacity: 0, y: 14 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.34, delay: 0.04 * index }}
              onClick={() => selectRoute(routeId)}
              className={cn(
                "panel cursor-pointer rounded-[1.75rem] border p-5 shadow-glow transition",
                active
                  ? "border-accent/35 bg-accent-soft/60"
                  : "border-white/10 bg-white/5 hover:border-white/18"
              )}
            >
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="text-sm uppercase tracking-[0.18em] text-white/44">{route.mode}</p>
                  <h3 className="mt-2 text-xl font-semibold text-white">{route.title}</h3>
                </div>
                <div className="rounded-full border border-white/10 bg-black/20 px-3 py-1.5 text-sm text-white/72">
                  Score {route.mobility_score}
                </div>
              </div>
              <div className="mt-5 grid grid-cols-2 gap-3 md:grid-cols-4">
                <MetricChip icon={Clock3} label="ETA" value={`${route.analytics.predicted_duration_minutes} min`} />
                <MetricChip icon={Wallet} label="Cost" value={`$${route.analytics.cost_usd}`} />
                <MetricChip icon={Leaf} label="Carbon" value={`${route.analytics.carbon_kg} kg`} />
                <MetricChip icon={ShieldCheck} label="Traffic" value={`${route.analytics.traffic_score}`} />
              </div>
              <div className="mt-4 flex flex-wrap gap-2">
                <span className="rounded-full border border-white/10 bg-black/20 px-3 py-1.5 text-xs uppercase tracking-[0.14em] text-white/62">
                  {route.route_variant.replace("_", " ")}
                </span>
                <span className="rounded-full border border-accent/20 bg-accent-soft/40 px-3 py-1.5 text-xs uppercase tracking-[0.14em] text-accent">
                  {route.route_confidence_label}
                </span>
                <span className="rounded-full border border-white/10 bg-black/20 px-3 py-1.5 text-xs uppercase tracking-[0.14em] text-white/62">
                  Weather penalty {route.analytics.weather_penalty}
                </span>
              </div>
              <p className="mt-5 text-sm leading-6 text-white/64">{route.rationale}</p>
              <div className="mt-4 inline-flex items-center gap-2 text-sm text-accent">
                Focus this route on map
                <ArrowRight className="h-4 w-4" />
              </div>
            </motion.article>
          );
        })}
      </div>
    </section>
  );
}

function MetricChip({
  icon: Icon,
  label,
  value
}: {
  icon: typeof Clock3;
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-[1.1rem] border border-white/10 bg-black/20 px-3 py-3">
      <div className="flex items-center gap-2 text-xs uppercase tracking-[0.16em] text-white/42">
        <Icon className="h-3.5 w-3.5 text-signal-cyan" />
        {label}
      </div>
      <p className="mt-2 text-sm font-medium text-white">{value}</p>
    </div>
  );
}
