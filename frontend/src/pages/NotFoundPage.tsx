import React from 'react';
import { Link } from 'react-router-dom';
import { ShieldAlert, Home, ArrowLeft } from 'lucide-react';

export const NotFoundPage: React.FC = () => {
  return (
    <div className="max-w-md mx-auto py-20 px-4 text-center space-y-6">
      <div className="w-16 h-16 rounded-2xl bg-amber-950/60 border border-amber-500/40 text-amber-400 mx-auto flex items-center justify-center">
        <ShieldAlert className="w-8 h-8" />
      </div>
      <div className="space-y-2">
        <h1 className="text-2xl font-bold text-white">Page Not Found</h1>
        <p className="text-sm text-slate-400">
          The requested page does not exist in SentryMesh Guardian.
        </p>
      </div>
      <div className="pt-2">
        <Link
          to="/"
          className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-semibold text-sm transition-colors"
        >
          <Home className="w-4 h-4" />
          <span>Return Home</span>
        </Link>
      </div>
    </div>
  );
};
