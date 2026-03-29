import { getMarketDepth, getSocialStats } from '@/lib/db';
import Sidebar from '@/components/Sidebar';
import * as motion from "framer-motion/client";
import { Megaphone, Users, Eye, Percent } from 'lucide-react';

export const dynamic = 'force-dynamic';

interface AdCampaign {
  app_name: string;
  platform: string;
  estimated_budget: number;
  status: string;
}

interface ChannelStat {
  app_name: string;
  handle: string;
  subscribers: number;
  avg_views: number;
  err: number;
}

export default async function MarketDepth() {
  let campaigns: AdCampaign[] = [];
  let social: ChannelStat[] = [];
  
  try {
    [campaigns, social] = await Promise.all([
      getMarketDepth() as Promise<AdCampaign[]>,
      getSocialStats() as Promise<ChannelStat[]>
    ]);
  } catch (e) {
    console.error('Failed to load market depth data:', e);
  }

  const totalAdBudget = campaigns.reduce((sum, c) => sum + c.estimated_budget, 0);

  return (
    <div className="flex min-h-screen bg-[#02040a] text-slate-300 font-sans">
      <Sidebar />
      <main className="flex-1 overflow-y-auto px-10 py-12 space-y-12 max-w-[1400px] mx-auto">
        <div>
          <h1 className="text-4xl font-bold font-heading text-white tracking-tight mb-2">Market Depth</h1>
          <p className="text-slate-500 font-medium italic">Marketing influence and social engagement metrics</p>
        </div>

        {/* Ad Campaigns Section */}
        <section className="space-y-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Megaphone className="w-6 h-6 text-indigo-400" />
              <h2 className="text-2xl font-bold text-white">Ad Campaigns</h2>
            </div>
            <div className="glass px-4 py-2 rounded-xl border border-white/5">
              <span className="text-xs text-slate-500 font-bold uppercase tracking-widest mr-2">Est. Market Spend:</span>
              <span className="text-sm font-bold text-indigo-400">${totalAdBudget.toLocaleString()}</span>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {campaigns.map((camp, i) => (
              <motion.div
                key={`${camp.app_name}-${i}`}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: i * 0.05, duration: 0.3 }}
                className="glass-card p-6 rounded-2xl border border-white/5 hover:border-indigo-500/20 transition-all"
              >
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <div className="font-bold text-white">{camp.app_name}</div>
                    <div className="text-[10px] text-slate-500 uppercase font-bold mt-1">{camp.platform}</div>
                  </div>
                  <div className="px-2 py-1 rounded-md bg-white/5 border border-white/5 text-[9px] font-bold text-emerald-400 uppercase">
                    {camp.status}
                  </div>
                </div>
                <div className="flex items-end justify-between">
                  <div className="text-2xl font-black text-white tabular-nums">${camp.estimated_budget.toLocaleString()}</div>
                  <div className="text-[10px] text-slate-600 font-bold uppercase">Budget Est.</div>
                </div>
              </motion.div>
            ))}
          </div>
          {campaigns.length === 0 && (
            <div className="glass-card p-12 rounded-[2rem] text-center opacity-50">
              <p className="text-slate-500">No active ad campaigns detected.</p>
            </div>
          )}
        </section>

        {/* Social Engagement Section */}
        <section className="space-y-6">
          <div className="flex items-center gap-3">
            <Users className="w-6 h-6 text-blue-400" />
            <h2 className="text-2xl font-bold text-white">Social Engagement</h2>
          </div>

          <div className="overflow-x-auto rounded-[2rem] border border-white/5 glass-card">
            <table className="w-full text-left border-collapse min-w-[800px]">
              <thead>
                <tr className="bg-white/5 text-slate-500 text-[10px] font-bold uppercase tracking-widest">
                  <th className="px-8 py-6">Unified Channel</th>
                  <th className="px-8 py-6 text-center">Subscribers</th>
                  <th className="px-8 py-6 text-center">Avg. Views</th>
                  <th className="px-8 py-6 text-center">ERR %</th>
                  <th className="px-8 py-6 text-right">Engagement Quality</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {social.map((chan, i) => (
                  <motion.tr
                    key={`${chan.handle}-${i}`}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.2 + i * 0.03, duration: 0.3 }}
                    className="hover:bg-blue-500/5 transition-all group"
                  >
                    <td className="px-8 py-6">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-slate-800 flex items-center justify-center font-bold text-slate-400 group-hover:bg-blue-600 group-hover:text-white transition-all">
                          {chan.app_name[0]}
                        </div>
                        <div>
                          <div className="font-bold text-white">{chan.app_name}</div>
                          <div className="text-[10px] text-blue-400 font-medium">@{chan.handle}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-8 py-6 text-center tabular-nums font-bold text-slate-300">
                      {chan.subscribers.toLocaleString()}
                    </td>
                    <td className="px-8 py-6 text-center">
                      <div className="flex flex-col items-center">
                        <div className="flex items-center gap-1 text-sm font-bold text-slate-400">
                          <Eye className="w-3 h-3" /> {chan.avg_views.toLocaleString()}
                        </div>
                        <div className="text-[8px] text-slate-600 font-bold uppercase mt-1">Per Post</div>
                      </div>
                    </td>
                    <td className="px-8 py-6 text-center">
                      <div className="inline-flex items-center gap-1 px-2 py-1 rounded-lg bg-emerald-500/10 text-emerald-400 text-xs font-bold border border-emerald-500/20">
                        <Percent className="w-3 h-3" /> {chan.err.toFixed(1)}%
                      </div>
                    </td>
                    <td className="px-8 py-6">
                      <div className="flex items-center justify-end gap-3">
                        <div className="w-24 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                          <div 
                            className="h-full bg-blue-500 transition-all" 
                            style={{ width: `${Math.min(100, chan.err * 10)}%` }} 
                          />
                        </div>
                      </div>
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>
          {social.length === 0 && (
            <div className="glass-card p-12 rounded-[2rem] text-center opacity-50">
              <p className="text-slate-500">No social stats available for tracked apps.</p>
            </div>
          )}
        </section>

      </main>
    </div>
  );
}
