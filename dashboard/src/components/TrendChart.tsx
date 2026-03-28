'use client';

import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

interface TooltipProps {
  active?: boolean;
  payload?: { value: number; name: string; color: string }[];
  label?: string;
}

const CustomTooltip = ({ active, payload, label }: TooltipProps) => {
  if (active && payload && payload.length > 0) {
    return (
      <div className="glass-card p-4 rounded-xl border border-white/10 shadow-2xl backdrop-blur-2xl">
        <p className="text-xs font-bold text-gray-500 mb-2 uppercase tracking-widest">{label}</p>
        <div className="space-y-1.5">
          {payload[0] && (
            <div className="flex items-center gap-3">
              <div className="w-2 h-2 rounded-full bg-blue-500 shadow-[0_0_8px_#3b82f6]" />
              <span className="text-sm font-semibold text-white">{payload[0].value.toLocaleString()} TON</span>
            </div>
          )}
          {payload[1] && (
            <div className="flex items-center gap-3">
              <div className="w-2 h-2 rounded-full bg-indigo-400 shadow-[0_0_8px_#818cf8]" />
              <span className="text-sm font-medium text-slate-400">{payload[1].value.toLocaleString()} Wallets</span>
            </div>
          )}
        </div>
      </div>
    );
  }
  return null;
};

export default function TrendChart({ data }: { data: { date: string; total_ton: number; total_dau: number }[] }) {
  return (
    <div className="h-80 w-full mt-6">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data}>
          <defs>
            <linearGradient id="colorTon" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.25}/>
              <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
            </linearGradient>
            <linearGradient id="colorDau" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#6366f1" stopOpacity={0.15}/>
              <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#ffffff08" vertical={false} />
          <XAxis 
            dataKey="date" 
            stroke="#94a3b8" 
            tick={{fill: '#64748b', fontSize: 11, fontWeight: 500}} 
            axisLine={false} 
            tickLine={false}
            dy={10}
          />
          <YAxis 
            stroke="#94a3b8" 
            tick={{fill: '#64748b', fontSize: 11}} 
            axisLine={false} 
            tickLine={false}
            width={40}
          />
          <Tooltip content={<CustomTooltip />} />
          <Area 
            type="monotone" 
            dataKey="total_ton" 
            stroke="#3b82f6" 
            strokeWidth={3}
            fillOpacity={1} 
            fill="url(#colorTon)"
            name="Revenue" 
          />
          <Area 
            type="monotone" 
            dataKey="total_dau" 
            stroke="#818cf8" 
            strokeWidth={2}
            strokeDasharray="5 5"
            fillOpacity={1} 
            fill="url(#colorDau)"
            name="Wallets" 
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
