"use client";

import { useEffect, useMemo, useState } from "react";
import { Search } from "lucide-react";
import { cn } from "@/lib/utils";
import { usePlannerStore } from "@/store/planner-store";
import type { Objective } from "@/types/mobility";

type CommandPaletteProps = {
  onPlan: () => void;
};

const objectiveActions: Array<{ label: string; objective: Objective }> = [
  { label: "Switch to balanced objective", objective: "balanced" },
  { label: "Switch to fastest objective", objective: "fastest" },
  { label: "Switch to cheapest objective", objective: "cheapest" },
  { label: "Switch to greenest objective", objective: "greenest" },
  { label: "Switch to least traffic objective", objective: "least_traffic" }
];

export function CommandPalette({ onPlan }: CommandPaletteProps) {
  const {
    commandPaletteOpen,
    setCommandPaletteOpen,
    setObjective,
    armMapSelection,
    liveSync,
    setLiveSync
  } = usePlannerStore();
  const [query, setQuery] = useState("");

  useEffect(() => {
    const handler = (event: KeyboardEvent) => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        setCommandPaletteOpen(!commandPaletteOpen);
      }
      if (event.key === "Escape") {
        setCommandPaletteOpen(false);
      }
    };

    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [commandPaletteOpen, setCommandPaletteOpen]);

  const actions = useMemo(
    () => [
      {
        label: "Generate mobility plan",
        description: "Run live routing and intelligence scoring.",
        run: () => onPlan()
      },
      {
        label: liveSync ? "Disable live sync" : "Enable live sync",
        description: "Toggle real-time route refresh behavior.",
        run: () => setLiveSync(!liveSync)
      },
      {
        label: "Select origin on map",
        description: "Arm the map for origin placement.",
        run: () => armMapSelection("origin")
      },
      {
        label: "Select destination on map",
        description: "Arm the map for destination placement.",
        run: () => armMapSelection("destination")
      },
      ...objectiveActions.map((action) => ({
        label: action.label,
        description: "Adjust command center optimization bias.",
        run: () => setObjective(action.objective)
      }))
    ],
    [armMapSelection, liveSync, onPlan, setLiveSync, setObjective]
  );

  const filteredActions = actions.filter((action) =>
    action.label.toLowerCase().includes(query.toLowerCase())
  );

  if (!commandPaletteOpen) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center bg-black/45 px-4 py-20 backdrop-blur-sm">
      <div className="panel w-full max-w-2xl rounded-[2rem] border border-white/10 p-4 shadow-glow">
        <div className="flex items-center gap-3 rounded-[1.2rem] border border-white/10 bg-black/25 px-4 py-3">
          <Search className="h-4 w-4 text-white/46" />
          <input
            autoFocus
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            className="w-full bg-transparent text-sm text-white outline-none placeholder:text-white/28"
            placeholder="Search command center actions..."
          />
          <div className="rounded-full border border-white/10 px-2 py-1 text-[11px] uppercase tracking-[0.18em] text-white/42">
            Esc
          </div>
        </div>
        <div className="mt-4 space-y-2">
          {filteredActions.map((action) => (
            <button
              key={action.label}
              onClick={() => {
                action.run();
                setCommandPaletteOpen(false);
                setQuery("");
              }}
              className={cn(
                "flex w-full items-start justify-between rounded-[1.25rem] border border-white/10 bg-white/5 px-4 py-4 text-left transition hover:border-accent/30 hover:bg-accent-soft/40"
              )}
            >
              <div>
                <p className="text-sm font-medium text-white">{action.label}</p>
                <p className="mt-1 text-sm text-white/52">{action.description}</p>
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

