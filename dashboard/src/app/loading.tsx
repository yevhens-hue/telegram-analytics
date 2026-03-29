export default function Loading() {
  return (
    <div className="flex min-h-screen bg-[#02040a] text-slate-300">
      <div className="w-64 border-r border-slate-800/50 bg-[#02040a] p-8">
        <div className="w-8 h-8 rounded-lg bg-slate-800 animate-pulse" />
      </div>
      <main className="flex-1 px-10 py-12 space-y-12 max-w-[1400px] mx-auto">
        <div className="flex justify-between items-end">
          <div className="space-y-3">
            <div className="h-10 w-64 bg-slate-800/60 rounded-xl animate-pulse" />
            <div className="h-4 w-96 bg-slate-800/40 rounded-lg animate-pulse" />
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 xl:grid-cols-4 gap-6">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="glass-card p-6 rounded-3xl h-36 animate-pulse">
              <div className="h-12 w-12 bg-slate-800/60 rounded-2xl mb-4" />
              <div className="h-3 w-24 bg-slate-800/40 rounded mb-2" />
              <div className="h-8 w-32 bg-slate-800/60 rounded" />
            </div>
          ))}
        </div>
        <div className="glass-card p-8 rounded-[2rem] h-96 animate-pulse">
          <div className="h-6 w-48 bg-slate-800/60 rounded mb-4" />
          <div className="h-full bg-slate-800/30 rounded-2xl" />
        </div>
      </main>
    </div>
  );
}
