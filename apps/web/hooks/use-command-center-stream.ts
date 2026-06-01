"use client";

import { startTransition, useEffect, useState } from "react";
import { getCommandCenterStreamUrl } from "@/lib/api/client";
import type { CommandCenterSnapshot } from "@/types/mobility";

export function useCommandCenterStream(enabled: boolean) {
  const [snapshot, setSnapshot] = useState<CommandCenterSnapshot | null>(null);

  useEffect(() => {
    if (!enabled) {
      return;
    }

    const eventSource = new EventSource(getCommandCenterStreamUrl());
    eventSource.addEventListener("city_pulse", (event) => {
      const payload = JSON.parse((event as MessageEvent<string>).data) as CommandCenterSnapshot;
      startTransition(() => setSnapshot(payload));
    });

    return () => {
      eventSource.close();
    };
  }, [enabled]);

  return snapshot;
}

