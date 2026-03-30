"use client";

import { motion } from "framer-motion";
import { Brain, TrendingUp, TrendingDown, Minus } from "lucide-react";

interface NewsItem {
  app_name: string;
  content: string;
  sentiment_score: number;
  date: string;
}

interface NewsSentimentProps {
  news: NewsItem[];
}

export default function NewsSentiment({ news }: NewsSentimentProps) {
  if (news.length === 0) return null;

  return (
    <section className="mt-12 bg-white/5 rounded-3xl p-8 border border-white/10 backdrop-blur-xl">
      <div className="flex items-center gap-3 mb-8">
        <div className="p-3 bg-indigo-500/10 rounded-2xl">
          <Brain className="w-6 h-6 text-indigo-400" />
        </div>
        <div>
          <h2 className="text-2xl font-bold font-heading text-white tracking-tight">Market Intelligence</h2>
          <p className="text-slate-500 text-sm tracking-wide">Real-time sentiment monitoring through the Telegram ecosystem</p>
        </div>
      </div>

      <div className="space-y-4">
        {news.map((item, idx) => {
          const score = item.sentiment_score;
          const isBullish = score > 60;
          const isBearish = score < 40;
          
          return (
            <motion.div
              key={`${item.app_name}-${idx}`}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.05 }}
              className="flex items-start gap-4 p-4 rounded-2xl hover:bg-white/5 border border-transparent hover:border-white/10 group transition-all"
            >
              <div className={`mt-1 p-2 rounded-xl border ${
                isBullish ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/10 group-hover:bg-emerald-500/20' :
                isBearish ? 'bg-red-500/10 text-red-400 border-red-500/10 group-hover:bg-red-500/20' :
                'bg-slate-500/10 text-slate-400 border-slate-500/10 group-hover:bg-slate-500/20'
              } transition-all`}>
                {isBullish ? <TrendingUp className="w-4 h-4" /> :
                 isBearish ? <TrendingDown className="w-4 h-4" /> :
                 <Minus className="w-4 h-4" />
                }
              </div>

              <div className="flex-1">
                <div className="flex justify-between items-center mb-1">
                  <h4 className="font-bold text-white text-[15px]">{item.app_name}</h4>
                  <span className="text-[10px] text-slate-500 uppercase tracking-widest font-bold">{item.date}</span>
                </div>
                <p className="text-slate-400 text-sm line-clamp-2 leading-relaxed italic">{item.content}</p>
                
                <div className="mt-3 flex items-center gap-4">
                  <div className="flex-1 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                    <div 
                      className={`h-full transition-all duration-1000 ${
                        isBullish ? 'bg-emerald-400' :
                        isBearish ? 'bg-red-400' :
                        'bg-slate-400'
                      }`}
                      style={{ width: `${score}%` }}
                    />
                  </div>
                  <span className={`text-xs font-bold font-mono min-w-[3ch] text-right ${
                    isBullish ? 'text-emerald-400' :
                    isBearish ? 'text-red-400' :
                    'text-slate-400'
                  }`}>
                    {score.toFixed(0)}%
                  </span>
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>
    </section>
  );
}
