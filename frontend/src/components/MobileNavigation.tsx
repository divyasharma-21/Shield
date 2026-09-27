import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Shield, PhoneCall, AlertTriangle, Lock, X } from 'lucide-react';
import { useHealth } from '../hooks/useHealth';

interface MobileNavigationProps {
  isOpen: boolean;
  onClose: () => void;
}

export const MobileNavigation: React.FC<MobileNavigationProps> = ({ isOpen, onClose }) => {
  const location = useLocation();
  const { data: health } = useHealth();

  if (!isOpen) return null;

  const navLinks = [
    { to: '/', label: 'Home', icon: Shield, desc: 'Overview & quick scan portal' },
    { to: '/parent-call', label: 'ParentCall Guardian', icon: PhoneCall, desc: 'Analyze calls, messages & recordings' },
    { to: '/response', label: 'How to Respond', icon: AlertTriangle, desc: 'Immediate steps & emergency helplines' },
    { to: '/privacy', label: 'Privacy & Safety', icon: Lock, desc: 'Zero recording & data protection rules' },
  ];

  return (
    <div className="fixed inset-0 z-50 md:hidden flex flex-col justify-end bg-black/80 backdrop-blur-sm transition-opacity">
      <div className="bg-surface border-t border-surface-border p-6 rounded-t-3xl w-full max-h-[85vh] overflow-y-auto shadow-2xl">
        <div className="flex items-center justify-between pb-4 border-b border-surface-border">
          <div className="flex items-center gap-2">
            <Shield className="w-5 h-5 text-cyan-accent" />
            <span className="font-bold text-white">SentryMesh Menu</span>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-surface-elevated"
            aria-label="Close menu"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <nav className="mt-4 space-y-2">
          {navLinks.map((link) => {
            const Icon = link.icon;
            const isActive = location.pathname === link.to;
            return (
              <Link
                key={link.to}
                to={link.to}
                onClick={onClose}
                className={`flex items-start gap-3 p-3 rounded-xl transition-all ${
                  isActive
                    ? 'bg-cyan-950/80 text-cyan-300 border border-cyan-500/40'
                    : 'text-slate-300 hover:bg-surface-elevated'
                }`}
              >
                <div className={`p-2 rounded-lg mt-0.5 ${isActive ? 'bg-cyan-900/50 text-cyan-400' : 'bg-surface-elevated text-slate-400'}`}>
                  <Icon className="w-5 h-5" />
                </div>
                <div>
                  <div className="font-medium text-white">{link.label}</div>
                  <div className="text-xs text-slate-400">{link.desc}</div>
                </div>
              </Link>
            );
          })}
        </nav>

        <div className="mt-6 pt-4 border-t border-surface-border text-xs text-slate-400 flex items-center justify-between">
          <span>SentryMesh V4 Active Model</span>
          <span className="font-mono text-cyan-400">
            Threshold: {health?.selected_suspicious_threshold ?? 0.40}
          </span>
        </div>
      </div>
    </div>
  );
};
