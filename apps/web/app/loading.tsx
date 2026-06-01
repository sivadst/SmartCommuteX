export default function Loading() {
  return (
    <main className="mx-auto flex min-h-screen max-w-7xl flex-col gap-6 px-6 py-8 lg:px-10">
      <div className="h-16 animate-pulse rounded-full bg-white/5" />
      <div className="grid gap-6 lg:grid-cols-[1.35fr_0.9fr]">
        <div className="panel h-[520px] animate-pulse rounded-[2rem] border border-white/10 bg-white/5" />
        <div className="panel h-[520px] animate-pulse rounded-[2rem] border border-white/10 bg-white/5" />
      </div>
    </main>
  );
}

