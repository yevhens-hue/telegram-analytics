"use client";

import { motion } from "framer-motion";
import { AlertCircle, AlertTriangle, Bell, CheckCircle } from "lucide-react";

interface Alert {
  app_name: string;
  message: string;
  severity: string;
  date: string;
}

interface SystemAlertsProps {
  alerts: Alert[];
}

export default function SystemAlerts({ alerts }: SystemAlertsProps) {
  if (alerts.length === 0) return null;

  return (
    <section className="mt-12">
      <div className="flex items-center gap-3 mb-6">
        <div className="p-3 bg-red-500/10 rounded-2xl">
          <Bell className="w-6 h-6 text-red-400" />
        </div>
        <h2 className="text-2xl font-bold font-heading text-white tracking-tight">System Alerts</h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {alerts.map((alert, idx) => (
          <motion.div
            key={`${alert.app_name}-${idx}`}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: idx * 0.05 }}
            className={`glass-card p-5 rounded-3xl border-l-4 ${
              alert.severity === 'high' ? 'border-red-500/50 hover:bg-red-500/5' :
              alert.severity === 'medium' ? 'border-amber-500/50 hover:bg-amber-500/5' :
              'border-emerald-500/50 hover:bg-emerald-500/5'
            } transition-all`}
          >
            <div className="flex items-start gap-4">
              <div className={`mt-1 ${
                alert.severity === 'high' ? 'text-red-400' :
                alert.severity === 'medium' ? 'text-amber-400' :
                'text-emerald-400'
              }`}>
                {alert.severity === 'high' ? <AlertCircle className="w-5 h-5" /> :
                 alert.severity === 'medium' ? <AlertTriangle className="w-5 h-5" /> :
                 <CheckCircle className="w-5 h-5" />
                }
              </div>
              <div className="flex-1">
                <div className="flex justify-between items-center mb-1">
                  <h4 className="font-bold text-white text-sm">{alert.app_name}</h4>
                  <span className="text-[10px] text-slate-500 uppercase tracking-widest">{alert.date}</span>
                </div>
                <p className="text-slate-400 text-sm leading-relaxed">{alert.message}</p>
                <div className="mt-3 flex items-center gap-2">
                  <span className={`text-[9px] font-bold px-2 py-0.5 rounded-full uppercase tracking-tighter ${
                    alert.severity === 'high' ? 'bg-red-500/10 text-red-400' :
                    alert.severity === 'medium' ? 'bg-amber-500/10 text-amber-400' :
                    'bg-emerald-500/10 text-emerald-400'
                  }`}>
                    {alert.severity}
                  </span>
                </div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </section>
  );
}
