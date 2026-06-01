"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { Loader2, Search, Star } from "lucide-react";
import { useDeferredValue, useEffect, useMemo, useState } from "react";
import {
  fetchSearchSuggestions,
  retrieveLocation
} from "@/lib/api/client";
import { useDebouncedValue } from "@/hooks/use-debounced-value";
import { cn } from "@/lib/utils";
import type { PlannerPoint, SavedPlace, SearchSuggestion } from "@/types/mobility";

type LocationSearchFieldProps = {
  label: string;
  value: PlannerPoint;
  onSelect: (point: PlannerPoint) => void;
  recentSearches: SavedPlace[];
  savedPlaces: SavedPlace[];
  smartSuggestions: SavedPlace[];
  onSavePlace: () => void;
};

export function LocationSearchField({
  label,
  value,
  onSelect,
  recentSearches,
  savedPlaces,
  smartSuggestions,
  onSavePlace
}: LocationSearchFieldProps) {
  const [query, setQuery] = useState(value.label);
  const [focused, setFocused] = useState(false);
  const [sessionToken, setSessionToken] = useState(() => crypto.randomUUID());
  const deferredQuery = useDeferredValue(query);
  const debouncedQuery = useDebouncedValue(deferredQuery, 240);

  useEffect(() => {
    setQuery(value.label);
  }, [value.label]);

  const suggestionQuery = useQuery({
    queryKey: ["location-suggest", debouncedQuery, sessionToken],
    queryFn: () =>
      fetchSearchSuggestions({
        query: debouncedQuery,
        sessionToken
      }),
    enabled: focused && debouncedQuery.trim().length >= 2,
    staleTime: 45_000
  });

  const retrieveMutation = useMutation({
    mutationFn: (suggestion: SearchSuggestion) =>
      retrieveLocation({
        mapboxId: suggestion.mapbox_id,
        sessionToken
      }),
    onSuccess: (response) => {
      onSelect({
        ...response.point,
        label: response.label,
        address: response.address
      });
      setQuery(response.label);
      setFocused(false);
      setSessionToken(crypto.randomUUID());
    }
  });

  const suggestionDeck = useMemo(() => {
    if (debouncedQuery.trim().length >= 2 && suggestionQuery.data) {
      return {
        title: "Search results",
        items: suggestionQuery.data.suggestions.map((suggestion) => ({
          id: suggestion.mapbox_id,
          label: suggestion.name,
          address: suggestion.full_address,
          onClick: () => retrieveMutation.mutate(suggestion)
        }))
      };
    }

    return [
      {
        title: "Saved places",
        items: savedPlaces.map((place) => ({
          id: place.id,
          label: place.label,
          address: place.address,
          onClick: () => onSelect(place)
        }))
      },
      {
        title: "Recent searches",
        items: recentSearches.map((place) => ({
          id: place.id,
          label: place.label,
          address: place.address,
          onClick: () => onSelect(place)
        }))
      },
      {
        title: "Smart suggestions",
        items: smartSuggestions.map((place) => ({
          id: place.id,
          label: place.label,
          address: place.address,
          onClick: () => onSelect(place)
        }))
      }
    ];
  }, [
    debouncedQuery,
    suggestionQuery.data,
    retrieveMutation,
    savedPlaces,
    recentSearches,
    smartSuggestions,
    onSelect
  ]);

  const sections = Array.isArray(suggestionDeck) ? suggestionDeck : [suggestionDeck];
  const hasDropdownContent = sections.some((section) => section.items.length > 0);

  return (
    <div className="relative">
      <label className="mb-2 block text-xs uppercase tracking-[0.16em] text-white/42">{label}</label>
      <div className="rounded-[1.35rem] border border-white/10 bg-black/25">
        <div className="flex items-center gap-3 px-4 py-3">
          <Search className="h-4 w-4 text-white/48" />
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            onFocus={() => setFocused(true)}
            onBlur={() => {
              window.setTimeout(() => setFocused(false), 120);
            }}
            className="w-full bg-transparent text-sm text-white outline-none placeholder:text-white/28"
            placeholder={`Search ${label.toLowerCase()}...`}
          />
          <button
            type="button"
            onClick={onSavePlace}
            className="rounded-full border border-white/10 p-2 text-white/58 transition hover:bg-white/8"
            aria-label={`Save ${label.toLowerCase()} place`}
          >
            <Star className="h-4 w-4" />
          </button>
        </div>
      </div>

      {focused && hasDropdownContent ? (
        <div className="panel absolute left-0 right-0 top-[calc(100%+0.65rem)] z-20 rounded-[1.4rem] border border-white/10 p-3 shadow-glow">
          {suggestionQuery.isLoading || retrieveMutation.isPending ? (
            <div className="flex items-center gap-2 px-3 py-3 text-sm text-white/62">
              <Loader2 className="h-4 w-4 animate-spin" />
              Loading location intelligence...
            </div>
          ) : null}
          <div className="space-y-3">
            {sections.map((section) =>
              section.items.length ? (
                <div key={section.title}>
                  <p className="px-3 text-[11px] uppercase tracking-[0.18em] text-white/34">
                    {section.title}
                  </p>
                  <div className="mt-2 space-y-1">
                    {section.items.map((item) => (
                      <button
                        key={item.id}
                        type="button"
                        onClick={item.onClick}
                        className={cn(
                          "flex w-full items-start justify-between gap-3 rounded-[1rem] px-3 py-3 text-left transition hover:bg-white/6"
                        )}
                      >
                        <div>
                          <p className="text-sm font-medium text-white">{item.label}</p>
                          <p className="mt-1 text-sm text-white/52">{item.address}</p>
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
              ) : null
            )}
          </div>
        </div>
      ) : null}
    </div>
  );
}

