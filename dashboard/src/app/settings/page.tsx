"use client";

import Sidebar from '@/components/Sidebar';
import { motion } from "framer-motion";
import { User, Bell, Shield, Brain, Database, Save, LogOut } from 'lucide-react';
import { useState } from 'react';

export default function Settings() {
  const [activeTab, setActiveTab] = useState('profile');
  const [saving, setSaving] = useState(false);

  const tabs = [
    { id: 'profile', label: 'Profile', icon: User },
    { id: 'alerts', label: 'Alert Rules', icon: Bell },
    { id: 'ai', label: 'AI Models', icon: Brain },
    { id: 'data', label: 'Data & Sync', icon: Database },
    { id: 'security', label: 'Security', icon: Shield },
  ];

  const handleSave = () => {
    setSaving(true);
    setTimeout(() => setSaving(false), 800);
  };

  return (
    <div className="flex min-h-screen bg-[#02040a] text-slate-300 font-sans">
      <Sidebar />
      <main className="flex-1 overflow-y-auto px-10 py-12 space-y-8 max-w-[1400px] mx-auto">
        <div className="flex justify-between items-end">
          <div>
            <h1 className="text-4xl font-bold font-heading text-white tracking-tight mb-2">Settings</h1>
            <p className="text-slate-500 font-medium italic">Manage your TMA Analytics experience and preferences</p>
          </div>
          <button 
            onClick={handleSave}
            disabled={saving}
            className={`flex items-center gap-2 px-6 py-2.5 rounded-xl font-bold text-sm transition-all shadow-lg ${
              saving 
                ? 'bg-slate-800 text-slate-500 cursor-not-allowed' 
                : 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-indigo-600/20'
            }`}
          >
            <Save className={`w-4 h-4 ${saving ? 'animate-spin' : ''}`} />
            {saving ? 'Saving...' : 'Save Changes'}
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Tabs Sidebar */}
          <div className="lg:col-span-1 space-y-1">
            {tabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${
                  activeTab === tab.id
                    ? 'bg-white/5 text-white border border-white/10 shadow-xl'
                    : 'text-slate-500 hover:text-slate-300 hover:bg-white/5'
                }`}
              >
                <tab.icon className={`w-4 h-4 ${activeTab === tab.id ? 'text-indigo-400' : ''}`} />
                <span className="text-sm font-bold">{tab.label}</span>
              </button>
            ))}
            <div className="pt-8">
              <button className="w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all text-red-500 hover:bg-red-500/5">
                <LogOut className="w-4 h-4" />
                <span className="text-sm font-bold">Sign Out</span>
              </button>
            </div>
          </div>

          {/* Settings Content Area */}
          <div className="lg:col-span-3">
            <motion.div
              layout
              className="glass-card p-10 rounded-[2.5rem] border border-white/5 min-h-[500px]"
            >
              <div className="max-w-xl space-y-10">
                {activeTab === 'profile' && (
                  <motion.div 
                    initial={{ opacity: 0, x: 20 }} 
                    animate={{ opacity: 1, x: 0 }} 
                    className="space-y-8"
                  >
                    <div>
                      <h2 className="text-xl font-bold text-white mb-2">Profile Overview</h2>
                      <p className="text-sm text-slate-500">How you appear on the platform.</p>
                    </div>
                    
                    <div className="flex items-center gap-6">
                      <div className="w-20 h-20 rounded-3xl bg-indigo-500/20 border-2 border-dashed border-indigo-500/40 flex items-center justify-center text-indigo-400 group cursor-pointer hover:bg-indigo-500/30 transition-all">
                        <User className="w-8 h-8" />
                      </div>
                      <div className="space-y-2">
                        <button className="px-4 py-2 bg-white/5 border border-white/5 rounded-lg text-xs font-bold text-slate-300 hover:bg-white/10 transition-all">
                          Change Avatar
                        </button>
                        <p className="text-[10px] text-slate-500">JPG, PNG or GIF. Max 800K.</p>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-6">
                      <div className="space-y-2">
                        <label className="text-[10px] font-bold text-slate-500 uppercase tracking-widest pl-1">Full Name</label>
                        <input className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-indigo-500/50" defaultValue="Yevhen Developer" />
                      </div>
                      <div className="space-y-2">
                        <label className="text-[10px] font-bold text-slate-500 uppercase tracking-widest pl-1">Email Address</label>
                        <input className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-indigo-500/50" defaultValue="yevhen@dev.ton" />
                      </div>
                    </div>
                  </motion.div>
                )}

                {activeTab === 'ai' && (
                  <motion.div 
                    initial={{ opacity: 0, x: 20 }} 
                    animate={{ opacity: 1, x: 0 }} 
                    className="space-y-8"
                  >
                    <div>
                      <h2 className="text-xl font-bold text-white mb-2">AI Analytics Engine</h2>
                      <p className="text-sm text-slate-500">Configure prediction and sentiment analysis models.</p>
                    </div>
                    
                    <div className="space-y-4">
                      {[
                        { name: 'Gemini 3 Pro', desc: 'Deep reasoning and complex predictions.', active: true },
                        { name: 'Claude 3.5 Sonnet', desc: 'Fast sentiment analysis across Telegram channels.', active: false },
                        { name: 'GPT-4o', desc: 'Standard multi-modal data processing.', active: false },
                      ].map((model, i) => (
                        <div 
                          key={i} 
                          className={`flex items-center justify-between p-4 rounded-2xl border transition-all cursor-pointer ${
                            model.active ? 'bg-indigo-500/10 border-indigo-500/40 shadow-xl shadow-indigo-500/5' : 'bg-white/5 border-white/5 hover:border-white/10'
                          }`}
                        >
                          <div className="flex items-center gap-4">
                            <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${model.active ? 'bg-indigo-500 text-white' : 'bg-slate-800 text-slate-500'}`}>
                              <Brain className="w-5 h-5" />
                            </div>
                            <div>
                              <p className="text-sm font-bold text-white">{model.name}</p>
                              <p className="text-[10px] text-slate-500 font-medium">{model.desc}</p>
                            </div>
                          </div>
                          <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center transition-all ${model.active ? 'border-indigo-500 bg-indigo-500' : 'border-slate-700'}`}>
                            {model.active && <div className="w-1.5 h-1.5 rounded-full bg-white shadow-sm" />}
                          </div>
                        </div>
                      ))}
                    </div>
                  </motion.div>
                )}

                {/* Placeholder content for other tabs */}
                {['alerts', 'data', 'security'].includes(activeTab) && (
                  <div className="flex flex-col items-center justify-center h-[300px] text-center space-y-4">
                    <div className="w-16 h-16 rounded-full bg-slate-900 border border-white/5 flex items-center justify-center">
                      <SettingsComponent className="w-8 h-8 text-slate-700 animate-spin-slow" />
                    </div>
                    <div>
                      <p className="text-sm font-bold text-slate-300 capitalize">{activeTab} section available soon</p>
                      <p className="text-xs text-slate-600 max-w-xs mt-1 italic">Extended module interface is under active development for Q2 release.</p>
                    </div>
                  </div>
                )}
              </div>
            </motion.div>
          </div>
        </div>
      </main>
    </div>
  );
}

function SettingsComponent({ className }: { className?: string }) {
  return (
    <svg className={className} width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.1a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/>
      <circle cx="12" cy="12" r="3"/>
    </svg>
  );
}
