import type { DashboardOverviewResponse, MobilityPlanResponse, Mode, Objective } from "@/types/mobility";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

type PlanPayload = {
  origin: { label: string; lat: number; lng: number };
  destination: { label: string; lat: number; lng: number };
  objective: Objective;
  allowed_modes: Mode[];
};

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {})
    },
    cache: "no-store"
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => null);
    throw new Error(errorBody?.detail ?? "SmartCommuteX request failed.");
  }

  return response.json() as Promise<T>;
}

export async function fetchDashboardOverview(): Promise<DashboardOverviewResponse> {
  return request<DashboardOverviewResponse>("/dashboard/overview");
}

export async function planCommute(payload: PlanPayload): Promise<MobilityPlanResponse> {
  return request<MobilityPlanResponse>("/mobility/plan", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

