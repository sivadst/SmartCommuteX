"use client";

import dynamic from "next/dynamic";
import { useMutation, useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { Waypoints } from "lucide-react";
import { startTransition, useEffect } from "react";
import { fetchDashboardOverview, planCommute } from "@/lib/api/client";
import { AnalyticsBoard } from "@/components/dashboard/analytics-board";
import { PlannerPanel } from "@/components/dashboard/planner-panel";
import { RouteComparison } from "@/components/dashboard/route-comparison";
import { Navbar } from "@/components/layout/navbar";
import { usePlannerStore } from "@/store/planner-store";
import type { PlannerPoint } from "@/types/mobility";

const MAPBOX_TOKEN = process.env.NEXT_PUBLIC_MAPBOX_TOKEN;
const TripMap = dynamic(
  () => import("@/components/map/trip-map").then((module) => module.TripMap),
  {
    ssr: false,
    loading: () => (
      <div className="panel min-h-[520px] animate-pulse rounded-[2rem] border border-white/10 bg-white/5 shadow-glow" />
    )
  }
);

export function MobilitySurface() {
  const {
    origin,
    destination,
    objective,
    allowedModes,
    selectedRouteId,
    setPoint,
    selectRoute,
    mapSelectionTarget
  } = usePlannerStore();

  const dashboardQuery = useQuery({
    queryKey: ["dashboard-overview"],
    queryFn: fetchDashboardOverview
  });

  const planMutation = useMutation({
    mutationFn: planCommute,
    onSuccess: (response) => {
      startTransition(() => {
        selectRoute(response.routes[0]?.snapshot_id ?? null);
      });
      void dashboardQuery.refetch();
    }
  });

  useEffect(() => {
    if (!planMutation.data?.routes.length || selectedRouteId) {
      return;
    }
    selectRoute(planMutation.data.routes[0].snapshot_id ?? null);
  }, [planMutation.data, selectedRouteId, selectRoute]);

  function submitPlan() {
    planMutation.mutate({
      origin,
      destination,
      objective,
      allowed_modes: allowedModes
    });
  }

  function handlePointChange(
    target: "origin" | "destination",
    key: keyof PlannerPoint,
    value: string
  ) {
    const current = target === "origin" ? origin : destination;
    const nextPoint: PlannerPoint = {
      ...current,
      [key]: key === "label" ? value : Number(value)
    };
    setPoint(target, nextPoint);
  }

  function handleMapPick(lng: number, lat: number) {
    if (!mapSelectionTarget) {
      return;
    }

    const current = mapSelectionTarget === "origin" ? origin : destination;
    setPoint(mapSelectionTarget, {
      ...current,
      lng: Number(lng.toFixed(6)),
      lat: Number(lat.toFixed(6))
    });
  }

  return (
    <main className="mx-auto flex min-h-screen max-w-[1500px] flex-col gap-6 px-5 py-6 lg:px-8">
      <Navbar />
      <motion.section
        initial={{ opacity: 0, y: 18 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.55 }}
        className="panel grid gap-6 overflow-hidden rounded-[2.2rem] border border-white/10 px-6 py-7 shadow-glow lg:grid-cols-[1.15fr_0.85fr] lg:px-8"
      >
        <div>
          <div className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-2 text-xs uppercase tracking-[0.18em] text-white/68">
            <Waypoints className="h-3.5 w-3.5 text-accent" />
            Urban Mobility Operating System
          </div>
          <h1 className="mt-5 max-w-3xl text-4xl font-semibold leading-tight text-white md:text-5xl">
            Real-time routing, sustainability intelligence, and commute decision support in one surface.
          </h1>
          <p className="mt-4 max-w-2xl text-base leading-7 text-white/66">
            SmartCommuteX now plans live routes, scores them on traffic, cost, and carbon, and
            turns each trip into persisted mobility intelligence.
          </p>
        </div>
        <div className="grid gap-4 sm:grid-cols-3">
          <HighlightCard label="Routing fabric" value="GraphHopper + OSM" />
          <HighlightCard label="Prediction stack" value="Travel time + traffic" />
          <HighlightCard label="Storage layer" value="Async PostgreSQL" />
        </div>
      </motion.section>

      <section className="grid gap-6 xl:grid-cols-[1.35fr_0.65fr]">
        <div className="space-y-6">
          <TripMap
            token={MAPBOX_TOKEN}
            origin={origin}
            destination={destination}
            routes={planMutation.data?.routes ?? []}
            selectedRouteId={selectedRouteId}
            onMapPick={handleMapPick}
            mapSelectionTarget={mapSelectionTarget}
          />
          <RouteComparison plan={planMutation.data} isPending={planMutation.isPending} />
        </div>
        <PlannerPanel
          plan={planMutation.data}
          isPending={planMutation.isPending}
          errorMessage={planMutation.error instanceof Error ? planMutation.error.message : null}
          onSubmit={submitPlan}
          onPointChange={handlePointChange}
        />
      </section>

      <AnalyticsBoard dashboard={dashboardQuery.data} isLoading={dashboardQuery.isLoading} />
    </main>
  );
}

function HighlightCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-[1.5rem] border border-white/10 bg-white/5 p-4">
      <p className="text-sm text-white/48">{label}</p>
      <p className="mt-3 text-lg font-semibold text-white">{value}</p>
    </div>
  );
}
