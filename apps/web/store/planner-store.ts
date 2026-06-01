import { create } from "zustand";
import type { Mode, Objective, PlannerPoint } from "@/types/mobility";

type MapSelectionTarget = "origin" | "destination" | null;

type PlannerState = {
  origin: PlannerPoint;
  destination: PlannerPoint;
  objective: Objective;
  allowedModes: Mode[];
  selectedRouteId: string | null;
  mapSelectionTarget: MapSelectionTarget;
  setObjective: (objective: Objective) => void;
  toggleMode: (mode: Mode) => void;
  setPoint: (target: Exclude<MapSelectionTarget, null>, point: PlannerPoint) => void;
  armMapSelection: (target: MapSelectionTarget) => void;
  selectRoute: (routeId: string | null) => void;
};

export const usePlannerStore = create<PlannerState>((set) => ({
  origin: {
    label: "Chennai Central",
    lat: 13.0827,
    lng: 80.2707
  },
  destination: {
    label: "T Nagar",
    lat: 13.0418,
    lng: 80.2337
  },
  objective: "balanced",
  allowedModes: ["walk", "bike", "ev", "rideshare"],
  selectedRouteId: null,
  mapSelectionTarget: null,
  setObjective: (objective) => set({ objective }),
  toggleMode: (mode) =>
    set((state) => {
      const enabled = state.allowedModes.includes(mode);
      const allowedModes = enabled
        ? state.allowedModes.filter((candidate) => candidate !== mode)
        : [...state.allowedModes, mode];

      return {
        allowedModes: allowedModes.length ? allowedModes : state.allowedModes
      };
    }),
  setPoint: (target, point) =>
    set({
      [target]: point,
      mapSelectionTarget: null
    } as Pick<PlannerState, "origin" | "destination" | "mapSelectionTarget">),
  armMapSelection: (target) => set({ mapSelectionTarget: target }),
  selectRoute: (selectedRouteId) => set({ selectedRouteId })
}));

