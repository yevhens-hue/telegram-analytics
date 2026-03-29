'use client';

import { useState } from 'react';
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
              <span className="text-sm font-semibold text-white">
                {payload[0].value.toLocaleString()} {payload[0].name === 'Revenue' ? 'TON' : 'Wallets'}
              </span>
            </div>
          )}
        </div>
      </div>
    );
  }
  return null;
};

type ChartMode = 'revenue' | 'users';

export default function TrendChart({ data }: { data: { date: string; total_ton: number; total_dau: number }[] }) {
  const [mode, setMode] = useState<ChartMode>('revenue');

  const isRevenue = mode === 'revenue';
  const dataKey = isRevenue ? 'total_ton' : 'total_dau';
  const strokeColor = isRevenue ? '#3b82f6' : '#818cf8';
  const gradientId = isRevenue ? 'colorTon' : 'colorDau';
  const gradientColor = isRevenue ? '#3b82f6' : '#6366f1';

  return (
    <div>
      <div className="flex items-center justify-between mb-2">
        <h2 className="text-xl font-bold font-heading text-white">Consolidated Growth</h2>
        <div className="bg-slate-800/50 p-1 rounded-lg flex gap-1">
          <button
            onClick={() => setMode('revenue')}
            className={`px-3 py-1 text-[10px] font-bold rounded-md transition-colors ${
              isRevenue ? 'text-white bg-indigo-600' : 'text-slate-500 hover:text-white'
            }`}
          >
            Revenue
          </button>
          <button
            onClick={() => setMode('users')}
            className={`px-3 py-1 text-[10px] font-bold rounded-md transition-colors ${
              !isRevenue ? 'text-white bg-indigo-600' : 'text-slate-500 hover:text-white'
            }`}
          >
            Users
          </button>
        </div>
      </div>
      <p className="text-xs text-slate-500 font-medium mb-8">
        {isRevenue
          ? 'Aggregate network activity across tracked smart contracts'
          : 'Unique active wallets interacting with tracked contracts'}
      </p>
      <div className="h-80 w-full mt-6">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data}>
            <defs>
              <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={gradientColor} stopOpacity={0.25} />
                <stop offset="95%" stopColor={gradientColor} stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#ffffff08" vertical={false} />
            <XAxis
              dataKey="date"
              stroke="#94a3b8"
              tick={{ fill: '#64748b', fontSize: 11, fontWeight: 500 }}
              axisLine={false}
              tickLine={false}
              dy={10}
            />
            <YAxis
              stroke="#94a3b8"
              tick={{ fill: '#64748b', fontSize: 11 }}
              axisLine={false}
              tickLine={false}
              width={40}
            />
            <Tooltip content={<CustomTooltip />} />
            <Area
              type="monotone"
              dataKey={dataKey}
              stroke={strokeColor}
              strokeWidth={3}
              fillOpacity={1}
              fill={`url(#${gradientId})`}
              name={isRevenue ? 'Revenue' : 'Wallets'}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
