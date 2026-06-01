"use client";

import { Loader2, MapPin, Navigation, Zap } from "lucide-react";
import { startTransition } from "react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import { usePlannerStore } from "@/store/planner-store";
import type { MobilityPlanResponse, Mode, Objective, PlannerPoint } from "@/types/mobility";

type PlannerPanelProps = {
  plan: MobilityPlanResponse | undefined;
  isPending: boolean;
  errorMessage: string | null;
  onSubmit: () => void;
  onPointChange: (target: "origin" | "destination", key: keyof PlannerPoint, value: string) => void;
};

const objectiveOptions: Array<{ value: Objective; label: string }> = [
  { value: "balanced", label: "Balanced" },
  { value: "fastest", label: "Fastest" },
  { value: "cheapest", label: "Cheapest" },
  { value: "greenest", label: "Greenest" },
  { value: "least_traffic", label: "Least traffic" }
];

const modeOptions: Array<{ value: Mode; label: string }> = [
  { value: "walk", label: "Walk" },
  { value: "bike", label: "Bike" },
  { value: "ev", label: "EV" },
  { value: "rideshare", label: "Ride share" }
];

export function PlannerPanel({
  plan,
  isPending,
  errorMessage,
  onSubmit,
  onPointChange
}: PlannerPanelProps) {
  const {
    origin,
    destination,
    objective,
    allowedModes,
    mapSelectionTarget,
    setObjective,
    toggleMode,
    armMapSelection
  } = usePlannerStore();

  return (
    <motion.section
      initial={{ opacity: 0, x: 18 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.5, delay: 0.08 }}
      className="panel rounded-[2rem] border border-white/10 p-6 shadow-glow"
    >
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm uppercase tracking-[0.2em] text-white/44">Planning Core</p>
          <h2 className="mt-2 text-2xl font-semibold text-white">Compose the route objective.</h2>
        </div>
        <div className="rounded-full border border-white/10 bg-white/5 px-3 py-2 text-xs uppercase tracking-[0.18em] text-white/62">
          Live graph routing
        </div>
      </div>

      <div className="mt-6 grid gap-4">
        <PlannerPointCard
          title="Origin"
          point={origin}
          icon={Navigation}
          isArmed={mapSelectionTarget === "origin"}
          onSelectFromMap={() => armMapSelection(mapSelectionTarget === "origin" ? null : "origin")}
          onChange={(key, value) => onPointChange("origin", key, value)}
        />
        <PlannerPointCard
          title="Destination"
          point={destination}
          icon={MapPin}
          isArmed={mapSelectionTarget === "destination"}
          onSelectFromMap={() =>
            armMapSelection(mapSelectionTarget === "destination" ? null : "destination")
          }
          onChange={(key, value) => onPointChange("destination", key, value)}
        />
      </div>

      <div className="mt-6">
        <p className="text-xs uppercase tracking-[0.18em] text-white/44">Optimization objective</p>
        <div className="mt-3 grid grid-cols-2 gap-2">
          {objectiveOptions.map((option) => (
            <button
              key={option.value}
              onClick={() => startTransition(() => setObjective(option.value))}
              className={cn(
                "rounded-[1.2rem] border px-4 py-3 text-left text-sm transition",
                objective === option.value
                  ? "border-accent/40 bg-accent-soft text-white"
                  : "border-white/10 bg-white/5 text-white/72 hover:bg-white/8"
              )}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>

      <div className="mt-6">
        <p className="text-xs uppercase tracking-[0.18em] text-white/44">Modal envelope</p>
        <div className="mt-3 flex flex-wrap gap-2">
          {modeOptions.map((option) => {
            const active = allowedModes.includes(option.value);
            return (
              <button
                key={option.value}
                onClick={() => toggleMode(option.value)}
                className={cn(
                  "rounded-full border px-4 py-2 text-sm transition",
                  active
                    ? "border-accent/40 bg-accent-soft text-white"
                    : "border-white/10 bg-white/5 text-white/72 hover:bg-white/8"
                )}
              >
                {option.label}
              </button>
            );
          })}
        </div>
      </div>

      <button
        onClick={onSubmit}
        disabled={isPending}
        className="mt-6 inline-flex w-full items-center justify-center gap-2 rounded-full bg-accent px-5 py-3 text-sm font-semibold text-surface transition hover:translate-y-[-1px] disabled:cursor-not-allowed disabled:opacity-70"
      >
        {isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Zap className="h-4 w-4" />}
        Generate live mobility plan
      </button>

      {errorMessage ? (
        <div className="mt-4 rounded-[1.2rem] border border-red-400/20 bg-red-400/10 px-4 py-3 text-sm text-red-100">
          {errorMessage}
        </div>
      ) : null}

      {plan ? (
        <div className="mt-6 rounded-[1.5rem] border border-white/10 bg-white/5 p-5">
          <p className="text-xs uppercase tracking-[0.18em] text-white/42">AI recommendation</p>
          <h3 className="mt-3 text-lg font-semibold text-white">
            {plan.summary.recommendation_title}
          </h3>
          <p className="mt-2 text-sm leading-6 text-white/64">
            {plan.summary.recommendation_reason}
          </p>
          {plan.unavailable_modes.length ? (
            <p className="mt-4 text-xs uppercase tracking-[0.16em] text-amber-200/80">
              Unavailable modes: {plan.unavailable_modes.join(", ")}
            </p>
          ) : null}
        </div>
      ) : (
        <div className="mt-6 rounded-[1.5rem] border border-dashed border-white/12 bg-black/20 p-5 text-sm leading-6 text-white/58">
          Submit a plan to fetch live routes from GraphHopper, persist snapshots, and populate the
          mobility analytics surfaces.
        </div>
      )}
    </motion.section>
  );
}

function PlannerPointCard({
  title,
  point,
  icon: Icon,
  isArmed,
  onSelectFromMap,
  onChange
}: {
  title: string;
  point: PlannerPoint;
  icon: typeof Navigation;
  isArmed: boolean;
  onSelectFromMap: () => void;
  onChange: (key: keyof PlannerPoint, value: string) => void;
}) {
  return (
    <div className="rounded-[1.5rem] border border-white/10 bg-white/5 p-4">
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <Icon className="h-4 w-4 text-accent" />
          <p className="text-sm font-medium text-white">{title}</p>
        </div>
        <button
          onClick={onSelectFromMap}
          className={cn(
            "rounded-full border px-3 py-1.5 text-xs uppercase tracking-[0.16em] transition",
            isArmed
              ? "border-accent/40 bg-accent-soft text-accent"
              : "border-white/10 text-white/62 hover:bg-white/8"
          )}
        >
          {isArmed ? "Armed" : "Pick on map"}
        </button>
      </div>

      <div className="mt-4 grid gap-3">
        <input
          value={point.label}
          onChange={(event) => onChange("label", event.target.value)}
          className="rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-sm text-white outline-none placeholder:text-white/32 focus:border-accent/40"
          placeholder={`${title} label`}
        />
        <div className="grid grid-cols-2 gap-3">
          <input
            value={point.lat}
            onChange={(event) => onChange("lat", event.target.value)}
            className="rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-sm text-white outline-none placeholder:text-white/32 focus:border-accent/40"
            placeholder="Latitude"
          />
          <input
            value={point.lng}
            onChange={(event) => onChange("lng", event.target.value)}
            className="rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-sm text-white outline-none placeholder:text-white/32 focus:border-accent/40"
            placeholder="Longitude"
          />
        </div>
      </div>
    </div>
  );
}

