"use client";

import { useEffect, useRef } from "react";
import mapboxgl, { type GeoJSONSource, type Map } from "mapbox-gl";
import type { Feature, FeatureCollection, LineString } from "geojson";
import { cn } from "@/lib/utils";
import type { PlannerPoint, RouteOption } from "@/types/mobility";

type TripMapProps = {
  token?: string;
  origin: PlannerPoint;
  destination: PlannerPoint;
  routes: RouteOption[];
  selectedRouteId: string | null;
  onMapPick?: (lng: number, lat: number) => void;
  mapSelectionTarget: "origin" | "destination" | null;
};

const styleUrl = process.env.NEXT_PUBLIC_MAPBOX_STYLE ?? "mapbox://styles/mapbox/dark-v11";

export function TripMap({
  token,
  origin,
  destination,
  routes,
  selectedRouteId,
  onMapPick,
  mapSelectionTarget
}: TripMapProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<Map | null>(null);
  const originMarkerRef = useRef<mapboxgl.Marker | null>(null);
  const destinationMarkerRef = useRef<mapboxgl.Marker | null>(null);

  useEffect(() => {
    if (!containerRef.current || mapRef.current || !token) {
      return;
    }

    mapboxgl.accessToken = token;
    const map = new mapboxgl.Map({
      container: containerRef.current,
      style: styleUrl,
      center: [origin.lng, origin.lat],
      zoom: 11.5,
      pitch: 52,
      bearing: -22,
      antialias: true
    });

    map.addControl(new mapboxgl.NavigationControl({ visualizePitch: true }), "top-right");

    map.on("load", () => {
      map.addSource("routes", {
        type: "geojson",
        data: emptyCollection()
      });

      map.addLayer({
        id: "route-alternatives",
        type: "line",
        source: "routes",
        filter: ["!=", ["get", "routeId"], selectedRouteId ?? ""],
        paint: {
          "line-color": ["coalesce", ["get", "color"], "#5FB8FF"],
          "line-width": 4,
          "line-opacity": 0.42,
          "line-blur": 0.4
        }
      });

      map.addLayer({
        id: "route-selected-glow",
        type: "line",
        source: "routes",
        filter: ["==", ["get", "routeId"], selectedRouteId ?? ""],
        paint: {
          "line-color": "#86FFCA",
          "line-width": 12,
          "line-opacity": 0.14,
          "line-blur": 1.2
        }
      });

      map.addLayer({
        id: "route-selected",
        type: "line",
        source: "routes",
        filter: ["==", ["get", "routeId"], selectedRouteId ?? ""],
        paint: {
          "line-color": ["coalesce", ["get", "color"], "#86FFCA"],
          "line-width": 6,
          "line-opacity": 0.96,
          "line-dasharray": [0, 4, 3]
        }
      });

      map.addLayer({
        id: "route-hit",
        type: "line",
        source: "routes",
        paint: {
          "line-width": 16,
          "line-opacity": 0
        }
      });

      map.on("mousemove", "route-hit", () => {
        map.getCanvas().style.cursor = "pointer";
      });
      map.on("mouseleave", "route-hit", () => {
        map.getCanvas().style.cursor = "";
      });
    });

    map.on("click", (event) => {
      if (!onMapPick || !mapSelectionTarget) {
        return;
      }
      onMapPick(event.lngLat.lng, event.lngLat.lat);
    });

    mapRef.current = map;

    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, [token, origin.lng, origin.lat, onMapPick, mapSelectionTarget, selectedRouteId]);

  useEffect(() => {
    if (!mapRef.current || !mapRef.current.isStyleLoaded()) {
      return;
    }

    const map = mapRef.current;
    const source = map.getSource("routes") as GeoJSONSource | undefined;
    if (source) {
      source.setData(buildRouteCollection(routes));
    }

    if (map.getLayer("route-alternatives")) {
      map.setFilter("route-alternatives", ["!=", ["get", "routeId"], selectedRouteId ?? ""]);
    }
    if (map.getLayer("route-selected-glow")) {
      map.setFilter("route-selected-glow", ["==", ["get", "routeId"], selectedRouteId ?? ""]);
    }
    if (map.getLayer("route-selected")) {
      map.setFilter("route-selected", ["==", ["get", "routeId"], selectedRouteId ?? ""]);
    }

    if (routes.length) {
      const bounds = new mapboxgl.LngLatBounds();
      for (const route of routes) {
        for (const [lng, lat] of route.geometry.coordinates) {
          bounds.extend([lng, lat]);
        }
      }
      bounds.extend([origin.lng, origin.lat]);
      bounds.extend([destination.lng, destination.lat]);
      map.fitBounds(bounds, { padding: 80, duration: 1100, pitch: 48 });
    } else {
      map.flyTo({
        center: [origin.lng, origin.lat],
        zoom: 11.5,
        duration: 1200
      });
    }

    return animateSelectedRoute({
      map,
      selectedRouteId
    });
  }, [routes, selectedRouteId, origin, destination]);

  useEffect(() => {
    if (!mapRef.current || !mapRef.current.isStyleLoaded()) {
      return;
    }

    originMarkerRef.current?.remove();
    destinationMarkerRef.current?.remove();

    originMarkerRef.current = new mapboxgl.Marker({ color: "#86FFCA" })
      .setLngLat([origin.lng, origin.lat])
      .setPopup(new mapboxgl.Popup({ offset: 12 }).setHTML(`<strong>${origin.label}</strong>`))
      .addTo(mapRef.current);

    destinationMarkerRef.current = new mapboxgl.Marker({ color: "#74DFFF" })
      .setLngLat([destination.lng, destination.lat])
      .setPopup(new mapboxgl.Popup({ offset: 12 }).setHTML(`<strong>${destination.label}</strong>`))
      .addTo(mapRef.current);
  }, [origin, destination]);

  return (
    <div className="relative h-full min-h-[520px] overflow-hidden rounded-[2rem] border border-white/10">
      {!token ? (
        <div className="panel flex h-full items-center justify-center px-8 text-center">
          <div>
            <p className="text-sm uppercase tracking-[0.22em] text-white/45">Mapbox Required</p>
            <h3 className="mt-4 text-2xl font-semibold text-white">
              Set `NEXT_PUBLIC_MAPBOX_TOKEN` to unlock the live trip canvas.
            </h3>
            <p className="mt-3 text-sm leading-6 text-white/62">
              The routing stack is ready for real overlays, animated paths, and dynamic markers as
              soon as the token is available.
            </p>
          </div>
        </div>
      ) : (
        <div
          ref={containerRef}
          className={cn(
            "h-full w-full bg-[radial-gradient(circle_at_top,rgba(134,255,202,0.1),transparent_35%),linear-gradient(180deg,#061015,#081319)]",
            mapSelectionTarget && "ring-2 ring-accent/50"
          )}
        />
      )}
      {mapSelectionTarget ? (
        <div className="pointer-events-none absolute left-4 top-4 rounded-full border border-accent/30 bg-black/45 px-4 py-2 text-xs uppercase tracking-[0.18em] text-accent">
          Click map to place {mapSelectionTarget}
        </div>
      ) : null}
      {routes.length ? (
        <div className="pointer-events-none absolute bottom-4 left-4 max-w-sm rounded-[1.4rem] border border-white/10 bg-black/45 px-4 py-4 backdrop-blur-xl">
          <p className="text-xs uppercase tracking-[0.18em] text-white/42">Selected route intelligence</p>
          <p className="mt-2 text-lg font-semibold text-white">
            {(routes.find((route) => route.snapshot_id === selectedRouteId) ?? routes[0]).title}
          </p>
          <p className="mt-2 text-sm text-white/58">
            Confidence{" "}
            {(routes.find((route) => route.snapshot_id === selectedRouteId) ?? routes[0]).analytics.confidence_score}
            {" · "}
            Traffic{" "}
            {(routes.find((route) => route.snapshot_id === selectedRouteId) ?? routes[0]).analytics.traffic_score}
          </p>
        </div>
      ) : null}
    </div>
  );
}

function animateSelectedRoute({
  map,
  selectedRouteId
}: {
  map: Map;
  selectedRouteId: string | null;
}) {
  const dashFrames = [
    [0, 4, 3],
    [0.8, 4, 2.2],
    [1.6, 4, 1.4],
    [2.4, 4, 0.6]
  ];
  let frame = 0;
  let timeoutId: number | null = null;
  let cancelled = false;

  const tick = () => {
    if (cancelled) {
      return;
    }
    if (map.getLayer("route-selected")) {
      map.setPaintProperty("route-selected", "line-dasharray", dashFrames[frame]);
      frame = (frame + 1) % dashFrames.length;
    }
    timeoutId = window.setTimeout(() => {
      requestAnimationFrame(tick);
    }, 180);
  };

  if (selectedRouteId) {
    tick();
  }

  return () => {
    cancelled = true;
    if (timeoutId !== null) {
      window.clearTimeout(timeoutId);
    }
  };
}

function buildRouteCollection(routes: RouteOption[]): FeatureCollection<LineString> {
  const features: Feature<LineString>[] = routes.map((route) => ({
    type: "Feature",
    geometry: {
      type: "LineString",
      coordinates: route.geometry.coordinates.map(([lng, lat]) => [lng, lat])
    },
    properties: {
      routeId: route.snapshot_id ?? route.mode,
      mode: route.mode,
      color: route.mode === "bike" ? "#86FFCA" : route.mode === "walk" ? "#D3FF74" : route.mode === "ev" ? "#74DFFF" : "#FFD27A"
    }
  }));

  return {
    type: "FeatureCollection",
    features
  };
}

function emptyCollection(): FeatureCollection<LineString> {
  return {
    type: "FeatureCollection",
    features: []
  };
}
