import { Link, useLocation } from 'react-router-dom';
import { Film, Sparkles, LayoutGrid, MonitorPlay } from 'lucide-react';

export default function Navbar() {
  const location = useLocation();
  const isActive = (path: string) => location.pathname === path ? 'text-white font-medium' : 'text-neutral-400 hover:text-white';

  return (
    <nav className="fixed top-0 inset-x-0 z-50 glass-panel border-b-0 border-white/10 bg-cinematic-base/60 transition-all duration-300">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        <Link to="/" className="text-white font-display font-bold tracking-widest text-lg flex items-center gap-2 hover:opacity-80 transition-opacity">
          <MonitorPlay className="w-5 h-5 text-netflix-red" />
          <span>MOVIEAI</span>
        </Link>
        <div className="flex gap-8 text-sm font-medium">
          <Link to="/movies" className={`flex items-center gap-2 transition-colors ${isActive('/movies')}`}>
            <Film className="w-4 h-4" /> Movies
          </Link>
          <Link to="/recommendations" className={`flex items-center gap-2 transition-colors ${isActive('/recommendations')}`}>
            <LayoutGrid className="w-4 h-4" /> Recommendations
          </Link>
          <Link to="/ai" className={`flex items-center gap-2 transition-colors ${isActive('/ai')}`}>
            <Sparkles className="w-4 h-4" /> AI Assistant
          </Link>
        </div>
      </div>
    </nav>
  );
}