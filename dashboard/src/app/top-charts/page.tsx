import { getTopApps } from '@/lib/db';
import Sidebar from '@/components/Sidebar';
import { TrendingUp, Activity, Search } from 'lucide-react';
import * as motion from "framer-motion/client";

export const dynamic = 'force-dynamic';

interface AppData {
  app_name: string;
  category: string;
  position: number;
  daily_revenue_ton: number;
  daily_active_wallets: number;
  growth: number;
  organic_index: number;
  trend_score: number;
  market_sentiment: number;
  prediction_7d: number;
}

export default async function TopCharts({
  searchParams,
}: {
  searchParams: Promise<{ q?: string; sort?: string; category?: string }>;
}) {
  const params = await searchParams;
  const query = params?.q?.toLowerCase() || '';
  const sortBy = params?.sort || 'position';
  const category = params?.category || '';

  let apps: AppData[] = [];
  try {
    apps = (await getTopApps()) as unknown as AppData[];
  } catch (e) {
    console.error('Failed to load apps:', e);
  }

  let filtered = apps;
  if (query) {
    filtered = filtered.filter(a => a.app_name.toLowerCase().includes(query));
  }
  if (category) {
    filtered = filtered.filter(a => a.category === category);
  }

  const sorted = [...filtered].sort((a, b) => {
    switch (sortBy) {
      case 'revenue': return b.daily_revenue_ton - a.daily_revenue_ton;
      case 'dau': return b.daily_active_wallets - a.daily_active_wallets;
      case 'growth': return b.growth - a.growth;
      case 'trend': return b.trend_score - a.trend_score;
      default: return a.position - b.position;
    }
  });

  const categories = [...new Set(apps.map(a => a.category))];

  return (
    <div className="flex min-h-screen bg-[#02040a] text-slate-300 font-sans">
      <Sidebar />
      <main className="flex-1 overflow-y-auto px-10 py-12 space-y-8 max-w-[1400px] mx-auto">
        <div>
          <h1 className="text-4xl font-bold font-heading text-white tracking-tight mb-2">Top Charts</h1>
          <p className="text-slate-500 font-medium italic">Browse and filter all tracked Telegram Mini Apps</p>
        </div>

        <form className="flex gap-4 flex-wrap" action="/top-charts" method="get">
          <div className="relative flex-1 min-w-[200px]">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
            <input
              type="text"
              name="q"
              defaultValue={query}
              placeholder="Search apps..."
              className="w-full pl-10 pr-4 py-2.5 bg-slate-800/50 border border-white/5 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500/50"
            />
          </div>
          <select
            name="sort"
            defaultValue={sortBy}
            className="px-4 py-2.5 bg-slate-800/50 border border-white/5 rounded-xl text-sm text-white focus:outline-none focus:border-indigo-500/50"
          >
            <option value="position">Sort by Rank</option>
            <option value="revenue">Sort by Revenue</option>
            <option value="dau">Sort by DAU</option>
            <option value="growth">Sort by Growth</option>
            <option value="trend">Sort by Trend Score</option>
          </select>
          <select
            name="category"
            defaultValue={category}
            className="px-4 py-2.5 bg-slate-800/50 border border-white/5 rounded-xl text-sm text-white focus:outline-none focus:border-indigo-500/50"
          >
            <option value="">All Categories</option>
            {categories.map(cat => (
              <option key={cat} value={cat}>{cat}</option>
            ))}
          </select>
          <button type="submit" className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-bold rounded-xl transition-all">
            Apply
          </button>
        </form>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {sorted.map((app, i) => (
            <motion.div
              key={`${app.app_name}-${i}`}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.02, duration: 0.3 }}
              className="glass-card p-6 rounded-2xl border border-white/5 hover:border-indigo-500/30 transition-all"
            >
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className={`w-8 h-8 rounded-lg flex items-center justify-center text-sm font-bold ${app.position <= 3 ? 'bg-amber-500 text-white' : 'bg-slate-800 text-slate-400'}`}>
                    {app.position}
                  </div>
                  <div>
                    <div className="font-bold text-white">{app.app_name}</div>
                    <div className="text-[10px] text-slate-500 uppercase tracking-widest">{app.category}</div>
                  </div>
                </div>
                {app.growth > 0 ? (
                  <div className="flex items-center gap-1 text-emerald-400 text-xs font-bold">
                    <TrendingUp className="w-3 h-3" /> +{app.growth}
                  </div>
                ) : app.growth < 0 ? (
                  <div className="flex items-center gap-1 text-red-400 text-xs font-bold">
                    <Activity className="w-3 h-3 rotate-180" /> {app.growth}
                  </div>
                ) : null}
              </div>
              <div className="grid grid-cols-3 gap-3 text-center">
                <div>
                  <div className="text-xs text-slate-500 mb-1">Revenue</div>
                  <div className="text-sm font-bold text-indigo-400">{Math.round(app.daily_revenue_ton).toLocaleString()} TON</div>
                </div>
                <div>
                  <div className="text-xs text-slate-500 mb-1">DAU</div>
                  <div className="text-sm font-bold text-blue-400">{app.daily_active_wallets.toLocaleString()}</div>
                </div>
                <div>
                  <div className="text-xs text-slate-500 mb-1">Trend</div>
                  <div className="text-sm font-bold text-purple-400">{app.trend_score.toFixed(0)}</div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {sorted.length === 0 && (
          <div className="glass-card p-12 rounded-[2rem] text-center">
            <p className="text-slate-500 text-lg">No apps found matching your criteria.</p>
            <p className="text-slate-600 text-sm mt-2">Try adjusting your search or filters.</p>
          </div>
        )}
      </main>
    </div>
  );
}
