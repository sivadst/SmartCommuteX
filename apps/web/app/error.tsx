"use client";

export default function GlobalError({
  error,
  reset
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <html lang="en">
      <body className="flex min-h-screen items-center justify-center bg-[#071014] px-6 text-white">
        <div className="panel max-w-lg rounded-[2rem] border border-white/10 p-8 text-center shadow-glow">
          <p className="text-sm uppercase tracking-[0.24em] text-white/45">System Fault</p>
          <h1 className="mt-4 text-3xl font-semibold">The mobility surface hit an unexpected error.</h1>
          <p className="mt-3 text-sm leading-6 text-white/65">{error.message}</p>
          <button
            onClick={reset}
            className="mt-6 rounded-full bg-accent px-5 py-3 text-sm font-semibold text-surface"
          >
            Reload experience
          </button>
        </div>
      </body>
    </html>
  );
}

