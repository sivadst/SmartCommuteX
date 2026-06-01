export type Objective = "balanced" | "fastest" | "cheapest" | "greenest" | "least_traffic";
export type Mode = "walk" | "bike" | "ev" | "rideshare" | "transit";

export type PlannerPoint = {
  label: string;
  lat: number;
  lng: number;
  address?: string;
};

export type SavedPlace = {
  id: string;
  label: string;
  address: string;
  lat: number;
  lng: number;
};

export type SearchSuggestion = {
  mapbox_id: string;
  name: string;
  full_address: string;
  feature_type: string;
  coordinates?: PlannerPoint | null;
};

export type SearchSuggestResponse = {
  session_token: string;
  suggestions: SearchSuggestion[];
};

export type SearchRetrieveResponse = {
  mapbox_id: string;
  label: string;
  address: string;
  point: PlannerPoint;
};

export type RouteOption = {
  snapshot_id: string | null;
  mode: Mode;
  title: string;
  provider: string;
  route_variant: string;
  route_confidence_label: string;
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
    confidence_score: number;
    weather_penalty: number;
    habit_affinity: number;
    anomaly_score: number;
  };
  scores: {
    time: number;
    cost: number;
    carbon: number;
    traffic: number;
    comfort: number;
    confidence: number;
    personalization: number;
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
    live_refresh_recommended: boolean;
  };
  routes: RouteOption[];
  unavailable_modes: Mode[];
};

export type CommandCenterSnapshot = {
  generated_at: string;
  city_pulse: Array<{
    label: string;
    value: string;
    signal: "stable" | "watch" | "critical" | "positive";
  }>;
  predictive_congestion: Array<{
    corridor: string;
    intensity: string;
    recommendation: string;
    confidence: number;
  }>;
  insights_timeline: Array<{
    timestamp: string;
    headline: string;
    narrative: string;
    severity: "info" | "watch" | "critical" | "positive";
  }>;
  live_refresh_recommended: boolean;
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
  command_center: CommandCenterSnapshot;
};
