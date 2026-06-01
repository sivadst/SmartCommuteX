import { create } from "zustand";

type PriorityMode = "balanced" | "time" | "cost" | "carbon";

type CommuteState = {
  priority: PriorityMode;
  setPriority: (priority: PriorityMode) => void;
};

export const useCommuteStore = create<CommuteState>((set) => ({
  priority: "balanced",
  setPriority: (priority) => set({ priority })
}));

