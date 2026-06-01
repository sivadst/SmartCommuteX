import type {
  DashboardOverviewResponse,
  MobilityPlanResponse,
  Mode,
  Objective,
  SearchRetrieveResponse,
  SearchSuggestResponse
} from "@/types/mobility";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

type PlanPayload = {
  origin: { label: string; lat: number; lng: number };
  destination: { label: string; lat: number; lng: number };
  objective: Objective;
  allowed_modes: Mode[];
  live_refresh?: boolean;
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

export async function fetchSearchSuggestions(params: {
  query: string;
  sessionToken?: string;
  proximity?: { lat: number; lng: number };
}): Promise<SearchSuggestResponse> {
  const searchParams = new URLSearchParams({
    q: params.query
  });

  if (params.sessionToken) {
    searchParams.set("session_token", params.sessionToken);
  }
  if (params.proximity) {
    searchParams.set("lat", String(params.proximity.lat));
    searchParams.set("lng", String(params.proximity.lng));
  }

  return request<SearchSuggestResponse>(`/search/suggest?${searchParams.toString()}`);
}

export async function retrieveLocation(params: {
  mapboxId: string;
  sessionToken: string;
}): Promise<SearchRetrieveResponse> {
  const searchParams = new URLSearchParams({
    session_token: params.sessionToken
  });
  return request<SearchRetrieveResponse>(
    `/search/retrieve/${params.mapboxId}?${searchParams.toString()}`
  );
}

export async function reverseGeocode(params: {
  lat: number;
  lng: number;
}): Promise<SearchRetrieveResponse> {
  const searchParams = new URLSearchParams({
    lat: String(params.lat),
    lng: String(params.lng)
  });
  return request<SearchRetrieveResponse>(`/search/reverse?${searchParams.toString()}`);
}

export function getCommandCenterStreamUrl(): string {
  return `${API_BASE_URL}/realtime/command-center`;
}
