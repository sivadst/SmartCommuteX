export type Objective = "balanced" | "fastest" | "cheapest" | "greenest" | "least_traffic";
export type Mode = "walk" | "bike" | "ev" | "rideshare" | "transit";

export type PlannerPoint = {
  label: string;
  lat: number;
  lng: number;
};

export type RouteOption = {
  snapshot_id: string | null;
  mode: Mode;
  title: string;
  provider: string;
  geometry: {
    type: "LineString";
    coordinates: number[][];
  };
  analytics: {
    distance_meters: number;
    base_duration_minutes: number;
    predicted_duration_minutes: number;
    traffic_score: number;
    carbon_kg: number;
    cost_usd: number;
    comfort_score: number;
    reliability_score: number;
  };
  scores: {
    time: number;
    cost: number;
    carbon: number;
    traffic: number;
    comfort: number;
  };
  mobility_score: number;
  rationale: string;
};

export type MobilityPlanResponse = {
  trip_id: string | null;
  objective: Objective;
  generated_at: string;
  summary: {
    recommendation_title: string;
    recommendation_reason: string;
    route_count: number;
    best_mode: Mode;
  };
  routes: RouteOption[];
  unavailable_modes: Mode[];
};

export type DashboardOverviewResponse = {
  metrics: Array<{
    label: string;
    value: string;
    delta: string;
    tone: "accent" | "cyan" | "lime" | "amber";
  }>;
  sustainability: {
    total_emissions_kg: number;
    savings_vs_rideshare_kg: number;
    average_trip_emissions_kg: number;
    greenest_mode_share: string;
  };
  recent_trips: Array<{
    trip_id: string;
    origin_label: string;
    destination_label: string;
    departure_time: string;
    selected_mode: string;
    predicted_duration_minutes: number;
    carbon_kg: number;
    objective: Objective;
  }>;
  ai_recommendations: Array<{
    title: string;
    narrative: string;
    impact_label: string;
  }>;
};

