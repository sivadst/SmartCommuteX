"use client";

import dynamic from "next/dynamic";
import { useMutation, useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { Activity, Command, Waypoints } from "lucide-react";
import { startTransition, useCallback, useEffect, useRef } from "react";
import { fetchDashboardOverview, planCommute, reverseGeocode } from "@/lib/api/client";
import { AnalyticsBoard } from "@/components/dashboard/analytics-board";
import { CommandPalette } from "@/components/dashboard/command-palette";
import { PlannerPanel } from "@/components/dashboard/planner-panel";
import { RouteComparison } from "@/components/dashboard/route-comparison";
import { Navbar } from "@/components/layout/navbar";
import { useCommandCenterStream } from "@/hooks/use-command-center-stream";
import { MotionPanel } from "@/components/ui/motion";
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
    mapSelectionTarget,
    liveSync,
    addRecentSearch
  } = usePlannerStore();
  const lastRefreshRef = useRef<number>(0);

  const dashboardQuery = useQuery({
    queryKey: ["dashboard-overview"],
    queryFn: fetchDashboardOverview,
    staleTime: 60_000
  });

  const liveSnapshot = useCommandCenterStream(true);

  const planMutation = useMutation({
    mutationFn: planCommute,
    onSuccess: (response) => {
      startTransition(() => {
        selectRoute(response.routes[0]?.snapshot_id ?? null);
      });
      lastRefreshRef.current = Date.now();
      void dashboardQuery.refetch();
    }
  });

  useEffect(() => {
    if (!planMutation.data?.routes.length || selectedRouteId) {
      return;
    }
    selectRoute(planMutation.data.routes[0].snapshot_id ?? null);
  }, [planMutation.data, selectedRouteId, selectRoute]);

  const submitPlan = useCallback(
    (liveRefresh = false) => {
      planMutation.mutate({
        origin,
        destination,
        objective,
        allowed_modes: allowedModes,
        live_refresh: liveRefresh
      });
    },
    [allowedModes, destination, objective, origin, planMutation]
  );

  useEffect(() => {
    if (!liveSync || !liveSnapshot?.live_refresh_recommended || !planMutation.data) {
      return;
    }

    const now = Date.now();
    if (now - lastRefreshRef.current < 45_000) {
      return;
    }

    submitPlan(true);
  }, [liveSnapshot, liveSync, planMutation.data, submitPlan]);

  async function handleMapPick(lng: number, lat: number) {
    if (!mapSelectionTarget) {
      return;
    }

    try {
      const response = await reverseGeocode({ lat, lng });
      const nextPoint = {
        ...response.point,
        label: response.label,
        address: response.address
      };
      setPoint(mapSelectionTarget, nextPoint);
      addRecentSearch({
        id: `${response.label}-${lat}-${lng}`,
        label: response.label,
        address: response.address,
        lat,
        lng
      });
    } catch {
      const current = mapSelectionTarget === "origin" ? origin : destination;
      setPoint(mapSelectionTarget, {
        ...current,
        lng: Number(lng.toFixed(6)),
        lat: Number(lat.toFixed(6))
      });
    }
  }

  function handlePointSelect(target: "origin" | "destination", point: PlannerPoint) {
    setPoint(target, point);
  }

  const activeRoute =
    planMutation.data?.routes.find((route) => route.snapshot_id === selectedRouteId) ??
    planMutation.data?.routes[0];

  return (
    <main className="mx-auto flex min-h-screen max-w-[1550px] flex-col gap-6 px-5 py-6 lg:px-8">
      <Navbar />
      <CommandPalette onPlan={() => submitPlan()} />
      <MotionPanel className="panel grid gap-6 overflow-hidden rounded-[2.2rem] border border-white/10 px-6 py-7 shadow-glow lg:grid-cols-[1.12fr_0.88fr] lg:px-8">
        <div>
          <div className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-2 text-xs uppercase tracking-[0.18em] text-white/68">
            <Waypoints className="h-3.5 w-3.5 text-accent" />
            Intelligent Urban Mobility Layer
          </div>
          <h1 className="mt-5 max-w-3xl text-4xl font-semibold leading-tight text-white md:text-5xl">
            Command search, predictive routing, and live city awareness from one operating surface.
          </h1>
          <p className="mt-4 max-w-2xl text-base leading-7 text-white/66">
            SmartCommuteX now unifies search, adaptive route ranking, weather and congestion intelligence, and live command-center telemetry.
          </p>
        </div>
        <div className="grid gap-4 sm:grid-cols-3">
          <HighlightCard label="Search fabric" value="Mapbox search intelligence" />
          <HighlightCard label="Model layer" value="Swappable inference providers" />
          <HighlightCard label="Live awareness" value="SSE command-center stream" />
        </div>
      </MotionPanel>

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
        <div className="space-y-6">
          <PlannerPanel
            plan={planMutation.data}
            isPending={planMutation.isPending}
            errorMessage={planMutation.error instanceof Error ? planMutation.error.message : null}
            onSubmit={() => submitPlan()}
            onPointSelect={handlePointSelect}
          />
          <div className="panel rounded-[2rem] border border-white/10 p-5 shadow-glow">
            <div className="flex items-center justify-between gap-3">
              <div>
                <p className="text-sm uppercase tracking-[0.2em] text-white/44">Live Route Pulse</p>
                <h3 className="mt-2 text-xl font-semibold text-white">Current selection state.</h3>
              </div>
              <Command className="h-5 w-5 text-accent" />
            </div>
            {activeRoute ? (
              <div className="mt-5 space-y-3">
                <PulseRow label="Confidence" value={activeRoute.analytics.confidence_score.toFixed(2)} />
                <PulseRow label="Weather penalty" value={activeRoute.analytics.weather_penalty.toFixed(2)} />
                <PulseRow label="Habit affinity" value={activeRoute.analytics.habit_affinity.toFixed(2)} />
                <PulseRow label="Live refresh" value={planMutation.data?.summary.live_refresh_recommended ? "Recommended" : "Stable"} />
              </div>
            ) : (
              <p className="mt-5 text-sm leading-6 text-white/58">
                Once a route is generated, SmartCommuteX will surface confidence, anomaly, and refresh signals here.
              </p>
            )}
          </div>
        </div>
      </section>

      <AnalyticsBoard
        dashboard={dashboardQuery.data}
        liveSnapshot={liveSnapshot}
        isLoading={dashboardQuery.isLoading}
      />
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

function PulseRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between rounded-[1.2rem] border border-white/10 bg-white/5 px-4 py-3">
      <div className="flex items-center gap-2">
        <Activity className="h-4 w-4 text-signal-cyan" />
        <span className="text-sm text-white/62">{label}</span>
      </div>
      <span className="text-sm font-medium text-white">{value}</span>
    </div>
  );
}
