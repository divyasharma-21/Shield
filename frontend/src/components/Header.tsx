import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Shield, PhoneCall, AlertTriangle, Lock, Radio } from 'lucide-react';
import { useHealth } from '../hooks/useHealth';

interface HeaderProps {
  onMenuToggle?: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onMenuToggle }) => {
  const location = useLocation();
  const { data: health } = useHealth();

  const navLinks = [
    { to: '/', label: 'Home', icon: Shield },
    { to: '/parent-call', label: 'ParentCall Guardian', icon: PhoneCall },
    { to: '/response', label: 'How to Respond', icon: AlertTriangle },
    { to: '/privacy', label: 'Privacy & Safety', icon: Lock },
  ];

  return (
    <header className="sticky top-0 z-40 w-full glass-panel border-b border-surface-border">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 sm:h-20">

          {/* Logo and Brand */}
          <Link to="/" className="flex items-center gap-3 group focus:outline-none">
            <div className="w-10 h-10 rounded-xl bg-cyan-950/80 border border-cyan-500/40 flex items-center justify-center text-cyan-400 group-hover:border-cyan-400 transition-colors shadow-lg shadow-cyan-950/50">
              <Shield className="w-5 h-5 text-cyan-accent" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-lg sm:text-xl tracking-tight text-white group-hover:text-cyan-light transition-colors">
                  SentryMesh
                </span>
                <span className="text-xs px-2 py-0.5 rounded-full font-medium bg-cyan-950 border border-cyan-800 text-cyan-300">
                  Guardian
                </span>
              </div>
              <p className="text-xs text-slate-400 font-medium">
                Pause. Verify. Protect.
              </p>
            </div>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center gap-1">
            {navLinks.map((link) => {
              const Icon = link.icon;
              const isActive = location.pathname === link.to;
              return (
                <Link
                  key={link.to}
                  to={link.to}
                  className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-cyan-950/70 text-cyan-300 border border-cyan-500/30 shadow-sm'
                      : 'text-slate-300 hover:text-white hover:bg-surface-elevated'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {link.label}
                </Link>
              );
            })}
          </nav>

          {/* Status Indicator */}
          <div className="hidden sm:flex items-center gap-3">
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-surface border border-surface-border text-xs">
              <Radio className={`w-3.5 h-3.5 ${health?.model_loaded ? 'text-emerald-400 animate-pulse' : 'text-amber-400'}`} />
              <span className="text-slate-300 font-mono">
                {health?.model_loaded ? 'V4 Active' : 'Model Connecting...'}
              </span>
            </div>
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden flex items-center">
            <button
              onClick={onMenuToggle}
              type="button"
              className="p-2 rounded-lg text-slate-300 hover:text-white hover:bg-surface-elevated focus:outline-none focus:ring-2 focus:ring-cyan-500"
              aria-label="Toggle navigation menu"
            >
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16m-7 6h7" />
              </svg>
            </button>
          </div>

        </div>
      </div>
    </header>
  );
};
