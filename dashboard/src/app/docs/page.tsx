import Sidebar from '@/components/Sidebar';
import * as motion from "framer-motion/client";
import { BookOpen, Code2, Database, Zap, Terminal, ShieldCheck } from 'lucide-react';

export default function Documentation() {
  const sections = [
    {
      title: "Getting Started",
      icon: Zap,
      items: [
        { name: "Quickstart Guide", desc: "Setting up your first analytics pipeline in under 5 minutes." },
        { name: "Project Architecture", desc: "Understanding the hybrid Python/Next.js data flow." },
      ]
    },
    {
      title: "Core Modules",
      icon: Database,
      items: [
        { name: "TApps Scraper", desc: "How we collect marketplace data from Telegram Mini Apps." },
        { name: "TON Indexer", desc: "Blockchain contract monitoring and revenue calculation." },
        { name: "Ads & Social", desc: "Monitoring ad campaigns and channel engagement (ERR)." },
      ]
    },
    {
      title: "API & Data",
      icon: Code2,
      items: [
        { name: "Schema Overview", desc: "Detailed information about the PostgreSQL/SQLite tables." },
        { name: "API Reference", desc: "Internal endpoints for data retrieval and automation." },
      ]
    }
  ];

  return (
    <div className="flex min-h-screen bg-[#02040a] text-slate-300 font-sans">
      <Sidebar />
      <main className="flex-1 overflow-y-auto px-10 py-12 space-y-12 max-w-[1400px] mx-auto">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 flex items-center justify-center border border-indigo-500/20">
            <BookOpen className="w-6 h-6 text-indigo-400" />
          </div>
          <div>
            <h1 className="text-4xl font-bold font-heading text-white tracking-tight mb-2">Documentation</h1>
            <p className="text-slate-500 font-medium italic">Master the TMA Analytics ecosystem</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-8">
          {sections.map((section, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.1, duration: 0.4 }}
              className="space-y-6"
            >
              <div className="flex items-center gap-3 border-b border-white/5 pb-4">
                <section.icon className="w-5 h-5 text-indigo-400" />
                <h2 className="text-lg font-bold text-white uppercase tracking-widest">{section.title}</h2>
              </div>
              <div className="space-y-4">
                {section.items.map((item, i) => (
                  <div 
                    key={i} 
                    className="group glass-card p-5 rounded-2xl border border-white/5 hover:border-indigo-500/30 transition-all cursor-pointer"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="font-bold text-white group-hover:text-indigo-400 transition-colors">{item.name}</h3>
                      <Terminal className="w-3 h-3 text-slate-600 group-hover:text-indigo-500 transition-all" />
                    </div>
                    <p className="text-xs text-slate-500 leading-relaxed font-medium">
                      {item.desc}
                    </p>
                  </div>
                ))}
              </div>
            </motion.div>
          ))}
        </div>

        {/* Community & Safety Banner */}
        <div className="glass-card p-10 rounded-[3rem] border border-white/5 bg-gradient-to-r from-indigo-500/10 to-transparent">
          <div className="flex flex-col md:flex-row items-center justify-between gap-8">
            <div className="space-y-4 max-w-xl">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/20 text-indigo-400 text-[10px] font-bold uppercase border border-indigo-500/20">
                <ShieldCheck className="w-3 h-3" /> System Security
              </div>
              <h2 className="text-3xl font-bold text-white">Trust is our Priority</h2>
              <p className="text-slate-400 text-sm leading-relaxed font-medium">
                Our analytics engine uses verifiable on-chain data and transparent scraping methodologies. 
                All data points can be traced back to their source on the TON blockchain or public Telegram meta-data.
              </p>
              <div className="pt-4 flex items-center gap-4">
                <button className="px-6 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold rounded-xl transition-all">
                  Open Source Repo
                </button>
                <button className="px-6 py-2 bg-white/5 border border-white/10 text-slate-300 hover:bg-white/10 text-xs font-bold rounded-xl transition-all">
                  Join Discord
                </button>
              </div>
            </div>
            <div className="hidden xl:block">
              <div className="w-64 h-64 bg-slate-900 border border-white/5 rounded-[2rem] flex items-center justify-center p-8 relative">
                <div className="absolute inset-0 bg-indigo-500/5 blur-3xl rounded-full" />
                <BookOpen className="w-24 h-24 text-indigo-500/20" />
                <div className="absolute bottom-6 right-6 w-12 h-12 bg-indigo-600 rounded-xl flex items-center justify-center shadow-lg shadow-indigo-600/20">
                  <Zap className="w-6 h-6 text-white" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
