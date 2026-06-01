import { CommandCenter } from "@/components/sections/command-center";
import { Hero } from "@/components/sections/hero";
import { MetricsStrip } from "@/components/sections/metrics-strip";
import { PlatformPillars } from "@/components/sections/platform-pillars";

export default function HomePage() {
  return (
    <main className="mx-auto flex min-h-screen max-w-7xl flex-col gap-10 px-6 py-8 lg:px-10">
      <Hero />
      <MetricsStrip />
      <div className="grid gap-6 lg:grid-cols-[1.35fr_0.9fr]">
        <CommandCenter />
        <PlatformPillars />
      </div>
    </main>
  );
}

