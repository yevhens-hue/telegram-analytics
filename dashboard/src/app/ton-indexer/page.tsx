import { getTopApps } from '@/lib/db';
import Sidebar from '@/components/Sidebar';
import * as motion from "framer-motion/client";

export const dynamic = 'force-dynamic';

interface AppData {
  app_name: string;
  daily_revenue_ton: number;
  daily_active_wallets: number;
  trend_score: number;
  organic_index: number;
}

export default async function TonIndexer() {
  let apps: AppData[] = [];
  try {
    apps = (await getTopApps()) as unknown as AppData[];
  } catch (e) {
    console.error('Failed to load apps:', e);
  }

  const totalRevenue = apps.reduce((sum, a) => sum + a.daily_revenue_ton, 0);
  const totalDau = apps.reduce((sum, a) => sum + a.daily_active_wallets, 0);

  return (
    <div className="flex min-h-screen bg-[#02040a] text-slate-300 font-sans">
      <Sidebar />
      <main className="flex-1 overflow-y-auto px-10 py-12 space-y-8 max-w-[1400px] mx-auto">
        <div>
          <h1 className="text-4xl font-bold font-heading text-white tracking-tight mb-2">TON Indexer</h1>
          <p className="text-slate-500 font-medium italic">On-chain metrics from tracked smart contracts</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="glass-card p-6 rounded-2xl">
            <div className="text-xs text-slate-500 uppercase tracking-widest mb-2">Total Revenue (TON)</div>
            <div className="text-3xl font-bold text-indigo-400">{Math.round(totalRevenue).toLocaleString()}</div>
          </div>
          <div className="glass-card p-6 rounded-2xl">
            <div className="text-xs text-slate-500 uppercase tracking-widest mb-2">Total Active Wallets</div>
            <div className="text-3xl font-bold text-blue-400">{totalDau.toLocaleString()}</div>
          </div>
        </div>

        <div className="overflow-x-auto rounded-[2rem] border border-white/5 glass-card">
          <table className="w-full text-left border-collapse min-w-[700px]">
            <thead>
              <tr className="bg-white/5 text-slate-500 text-[10px] font-bold uppercase tracking-widest">
                <th className="px-8 py-6">Application</th>
                <th className="px-8 py-6 text-center">Daily Revenue (TON)</th>
                <th className="px-8 py-6 text-center">DAU</th>
                <th className="px-8 py-6 text-center">Revenue per User</th>
                <th className="px-8 py-6 text-center">Organic Index</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {apps.map((app, i) => (
                <motion.tr
                  key={`${app.app_name}-${i}`}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.03, duration: 0.3 }}
                  className="hover:bg-indigo-500/5 transition-all"
                >
                  <td className="px-8 py-6">
                    <div className="font-bold text-white">{app.app_name}</div>
                  </td>
                  <td className="px-8 py-6 text-center">
                    <span className="font-bold text-indigo-400 tabular-nums">{Math.round(app.daily_revenue_ton).toLocaleString()}</span>
                  </td>
                  <td className="px-8 py-6 text-center">
                    <span className="font-bold text-blue-400 tabular-nums">{app.daily_active_wallets.toLocaleString()}</span>
                  </td>
                  <td className="px-8 py-6 text-center">
                    <span className="font-bold text-purple-400 tabular-nums">
                      {app.daily_active_wallets > 0 ? (app.daily_revenue_ton / app.daily_active_wallets).toFixed(4) : '0'} TON
                    </span>
                  </td>
                  <td className="px-8 py-6 text-center">
                    <div className="flex items-center justify-center gap-2">
                      <div className="w-16 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-indigo-500 to-purple-500"
                          style={{ width: `${Math.min(100, app.organic_index)}%` }}
                        />
                      </div>
                      <span className="text-xs font-bold text-slate-400 tabular-nums">{Math.round(app.organic_index)}%</span>
                    </div>
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>

        {apps.length === 0 && (
          <div className="glass-card p-12 rounded-[2rem] text-center">
            <p className="text-slate-500 text-lg">No on-chain data available.</p>
            <p className="text-slate-600 text-sm mt-2">Run the analytics pipeline to index TON contracts.</p>
          </div>
        )}
      </main>
    </div>
  );
}
