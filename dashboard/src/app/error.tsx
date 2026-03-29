"use client";

export default function Error({
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="flex min-h-screen bg-[#02040a] text-slate-300 items-center justify-center">
      <div className="glass-card p-12 rounded-[2rem] max-w-md text-center space-y-6">
        <div className="w-16 h-16 rounded-2xl bg-red-500/10 border border-red-500/20 flex items-center justify-center mx-auto">
          <span className="text-2xl">!</span>
        </div>
        <h2 className="text-2xl font-bold font-heading text-white">Something went wrong</h2>
        <p className="text-sm text-slate-400">
          Failed to load dashboard data. The database might be unavailable.
        </p>
        <button
          onClick={reset}
          className="px-6 py-3 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-bold rounded-xl shadow-lg shadow-indigo-600/20 transition-all"
        >
          Try again
        </button>
      </div>
    </div>
  );
}
