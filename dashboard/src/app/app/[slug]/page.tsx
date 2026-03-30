import { getAppDetail } from '@/lib/db';
import Sidebar from '@/components/Sidebar';
import Link from 'next/link';
import { ArrowLeft, TrendingUp, Users, Coins, Brain, Target, ExternalLink } from 'lucide-react';
import * as motion from "framer-motion/client";
import { notFound } from 'next/navigation';

export const dynamic = 'force-dynamic';

interface AppDetailPageProps {
  params: Promise<{ slug: string }>;
}

export default async function AppDetailPage({ params }: AppDetailPageProps) {
  const { slug } = await params;
  const appName = decodeURIComponent(slug);

  const detail = await getAppDetail(appName);

  if (!detail.analytics) {
    notFound();
  }

  const a = detail.analytics as any;
  const ton = detail.ton as any;
  const channel = detail.channel as any;
  const posHistory = detail.positionHistory as any[];
  const analyticsHistory = detail.analyticsHistory as any[];

  const initials = appName.split(' ').map((n: string) => n[0]).join('').slice(0, 2).toUpperCase();

  return (
    <div className="flex min-h-screen bg-[#02040a] text-slate-300 font-sans">
      <Sidebar />
      <main className="flex-1 overflow-y-auto px-10 py-12 space-y-8 max-w-[1400px] mx-auto">
        {/* Back nav */}
        <Link href="/top-charts" className="inline-flex items-center gap-2 text-slate-500 hover:text-white transition-colors text-sm">
          <ArrowLeft className="w-4 h-4" /> Back to Top Charts
        </Link>

        {/* Hero Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-card p-8 rounded-[2rem] relative overflow-hidden"
        >
          <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-500/5 blur-[100px] -mr-32 -mt-32" />
          <div className="relative z-10 flex items-start gap-6">
            <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-indigo-500/20 to-purple-500/20 flex items-center justify-center font-black text-2xl text-indigo-300 border border-white/5 shrink-0">
              {initials}
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-3 mb-2">
                <h1 className="text-3xl font-bold font-heading text-white truncate">{appName}</h1>
                <span className="px-2 py-0.5 bg-indigo-500/10 text-indigo-400 text-[9px] font-bold rounded-lg border border-indigo-500/10 uppercase tracking-widest">
                  {a.category || 'Unknown'}
                </span>
              </div>
              <p className="text-slate-400 text-sm mb-4 line-clamp-2">{a.description || 'No description available.'}</p>
              <div className="flex items-center gap-6 text-xs text-slate-500">
                <span>Rank <strong className="text-white">#{a.position}</strong></span>
                <span>Growth <strong className={a.growth > 0 ? 'text-emerald-400' : a.growth < 0 ? 'text-red-400' : 'text-slate-400'}>{a.growth > 0 ? '+' : ''}{a.growth}</strong></span>
                <span>Updated <strong className="text-white">{a.date}</strong></span>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { label: 'Daily Revenue', value: `${Math.round(a.revenue_ton || 0).toLocaleString()} TON`, icon: Coins, color: 'indigo' },
            { label: 'Active Wallets', value: (a.dau || 0).toLocaleString(), icon: Users, color: 'blue' },
            { label: 'Trend Score', value: `${(a.trend_score || 0).toFixed(1)}/100`, icon: TrendingUp, color: 'emerald' },
            { label: '7D Forecast', value: `#${a.prediction_7d || a.position}`, icon: Target, color: 'purple' },
          ].map((stat, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 + i * 0.05 }}
              className="glass-card p-5 rounded-2xl"
            >
              <stat.icon className={`w-5 h-5 text-${stat.color}-400 mb-3`} />
              <div className="text-[10px] text-slate-500 uppercase tracking-widest font-bold mb-1">{stat.label}</div>
              <div className="text-xl font-bold text-white">{stat.value}</div>
            </motion.div>
          ))}
        </div>

        {/* Two-column detail grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Organic & Sentiment */}
          <div className="glass-card p-6 rounded-2xl space-y-5">
            <h3 className="text-sm font-bold text-white uppercase tracking-widest">Market Signals</h3>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-slate-500">Organic Index</span>
                  <span className="font-bold text-white">{Math.round(a.organic_index || 0)}%</span>
                </div>
                <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full transition-all" style={{ width: `${Math.min(100, a.organic_index || 0)}%` }} />
                </div>
              </div>
              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-slate-500">Market Sentiment</span>
                  <span className="font-bold text-white">{Math.round(a.market_sentiment || 50)}/100</span>
                </div>
                <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
                  <div className={`h-full rounded-full transition-all ${a.market_sentiment > 70 ? 'bg-emerald-500' : a.market_sentiment > 40 ? 'bg-amber-500' : 'bg-red-500'}`} style={{ width: `${Math.min(100, a.market_sentiment || 50)}%` }} />
                </div>
              </div>
              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-slate-500">Trend Score</span>
                  <span className="font-bold text-white">{(a.trend_score || 0).toFixed(1)}/100</span>
                </div>
                <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-blue-500 to-cyan-500 rounded-full transition-all" style={{ width: `${Math.min(100, a.trend_score || 0)}%` }} />
                </div>
              </div>
            </div>
          </div>

          {/* TON On-Chain */}
          <div className="glass-card p-6 rounded-2xl space-y-5">
            <h3 className="text-sm font-bold text-white uppercase tracking-widest">On-Chain Data</h3>
            {ton ? (
              <div className="space-y-4">
                <div className="flex items-center justify-between p-3 bg-slate-800/30 rounded-xl">
                  <span className="text-xs text-slate-500">Contract</span>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono text-slate-300 truncate max-w-[180px]">{ton.contract_address}</span>
                    <ExternalLink className="w-3 h-3 text-slate-500" />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div className="p-3 bg-slate-800/30 rounded-xl">
                    <div className="text-[10px] text-slate-500 uppercase tracking-widest mb-1">Revenue</div>
                    <div className="text-lg font-bold text-indigo-400">{Math.round(ton.daily_revenue_ton || 0).toLocaleString()}</div>
                    <div className="text-[10px] text-slate-500">TON/day</div>
                  </div>
                  <div className="p-3 bg-slate-800/30 rounded-xl">
                    <div className="text-[10px] text-slate-500 uppercase tracking-widest mb-1">DAU</div>
                    <div className="text-lg font-bold text-blue-400">{(ton.daily_active_wallets || 0).toLocaleString()}</div>
                    <div className="text-[10px] text-slate-500">wallets</div>
                  </div>
                </div>
              </div>
            ) : (
              <p className="text-slate-500 text-sm">No on-chain data available.</p>
            )}
          </div>

          {/* Social / Channel */}
          <div className="glass-card p-6 rounded-2xl space-y-5">
            <h3 className="text-sm font-bold text-white uppercase tracking-widest">Social Presence</h3>
            {channel ? (
              <div className="space-y-3">
                <div className="flex items-center justify-between p-3 bg-slate-800/30 rounded-xl">
                  <span className="text-xs text-slate-500">Channel</span>
                  <span className="text-xs font-mono text-indigo-400">@{channel.handle}</span>
                </div>
                <div className="grid grid-cols-3 gap-3">
                  <div className="p-3 bg-slate-800/30 rounded-xl text-center">
                    <div className="text-lg font-bold text-white">{(channel.subscribers || 0).toLocaleString()}</div>
                    <div className="text-[10px] text-slate-500">Subscribers</div>
                  </div>
                  <div className="p-3 bg-slate-800/30 rounded-xl text-center">
                    <div className="text-lg font-bold text-white">{(channel.avg_views || 0).toLocaleString()}</div>
                    <div className="text-[10px] text-slate-500">Avg Views</div>
                  </div>
                  <div className="p-3 bg-slate-800/30 rounded-xl text-center">
                    <div className="text-lg font-bold text-emerald-400">{(channel.err || 0).toFixed(1)}%</div>
                    <div className="text-[10px] text-slate-500">ERR</div>
                  </div>
                </div>
              </div>
            ) : (
              <p className="text-slate-500 text-sm">No channel data available.</p>
            )}
          </div>

          {/* Position History */}
          <div className="glass-card p-6 rounded-2xl space-y-5">
            <h3 className="text-sm font-bold text-white uppercase tracking-widest">Position History (30d)</h3>
            {posHistory.length > 0 ? (
              <div className="space-y-1 max-h-[200px] overflow-y-auto">
                {posHistory.map((ph: any, i: number) => (
                  <div key={i} className="flex items-center justify-between py-1.5 px-3 rounded-lg hover:bg-slate-800/30 transition-colors">
                    <span className="text-xs text-slate-500">{ph.date}</span>
                    <span className={`text-sm font-bold ${ph.position <= 10 ? 'text-amber-400' : ph.position <= 50 ? 'text-indigo-400' : 'text-slate-400'}`}>
                      #{ph.position}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-slate-500 text-sm">No position history available.</p>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
