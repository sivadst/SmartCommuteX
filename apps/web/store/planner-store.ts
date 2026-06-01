import { create } from "zustand";
import { createJSONStorage, persist } from "zustand/middleware";
import type { Mode, Objective, PlannerPoint, SavedPlace } from "@/types/mobility";

type MapSelectionTarget = "origin" | "destination" | null;

type PlannerState = {
  origin: PlannerPoint;
  destination: PlannerPoint;
  objective: Objective;
  allowedModes: Mode[];
  selectedRouteId: string | null;
  mapSelectionTarget: MapSelectionTarget;
  recentSearches: SavedPlace[];
  savedPlaces: SavedPlace[];
  liveSync: boolean;
  commandPaletteOpen: boolean;
  setObjective: (objective: Objective) => void;
  toggleMode: (mode: Mode) => void;
  setPoint: (target: Exclude<MapSelectionTarget, null>, point: PlannerPoint) => void;
  armMapSelection: (target: MapSelectionTarget) => void;
  selectRoute: (routeId: string | null) => void;
  addRecentSearch: (place: SavedPlace) => void;
  savePlace: (place: SavedPlace) => void;
  setLiveSync: (liveSync: boolean) => void;
  setCommandPaletteOpen: (open: boolean) => void;
};

function dedupePlaces(places: SavedPlace[]): SavedPlace[] {
  const seen = new Map<string, SavedPlace>();
  for (const place of places) {
    seen.set(`${place.label}:${place.lat}:${place.lng}`, place);
  }
  return Array.from(seen.values());
}

export const usePlannerStore = create<PlannerState>()(
  persist(
    (set) => ({
      origin: {
        label: "Chennai Central",
        address: "Chennai Central, Tamil Nadu",
        lat: 13.0827,
        lng: 80.2707
      },
      destination: {
        label: "T Nagar",
        address: "T Nagar, Chennai",
        lat: 13.0418,
        lng: 80.2337
      },
      objective: "balanced",
      allowedModes: ["walk", "bike", "ev", "rideshare"],
      selectedRouteId: null,
      mapSelectionTarget: null,
      recentSearches: [],
      savedPlaces: [],
      liveSync: true,
      commandPaletteOpen: false,
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
      selectRoute: (selectedRouteId) => set({ selectedRouteId }),
      addRecentSearch: (place) =>
        set((state) => ({
          recentSearches: dedupePlaces([place, ...state.recentSearches]).slice(0, 8)
        })),
      savePlace: (place) =>
        set((state) => ({
          savedPlaces: dedupePlaces([place, ...state.savedPlaces]).slice(0, 8)
        })),
      setLiveSync: (liveSync) => set({ liveSync }),
      setCommandPaletteOpen: (commandPaletteOpen) => set({ commandPaletteOpen })
    }),
    {
      name: "smartcommutex-planner-store",
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        recentSearches: state.recentSearches,
        savedPlaces: state.savedPlaces,
        liveSync: state.liveSync,
        origin: state.origin,
        destination: state.destination,
        objective: state.objective,
        allowedModes: state.allowedModes
      })
    }
  )
);
