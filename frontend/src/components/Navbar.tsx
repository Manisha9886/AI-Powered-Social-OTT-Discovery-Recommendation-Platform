import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Film, Sparkles, LayoutGrid, MonitorPlay, Bookmark, User, LogOut, SlidersHorizontal } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import AuthModal from './AuthModal';

export default function Navbar() {
  const location = useLocation();
  const { user, logout } = useAuth();
  const [isAuthOpen, setIsAuthOpen] = useState(false);

  const isActive = (path: string) => location.pathname === path ? 'text-white font-medium' : 'text-neutral-400 hover:text-white';

  return (
    <>
      <nav className="fixed top-0 inset-x-0 z-40 glass-panel border-b-0 border-white/10 bg-cinematic-base/60 transition-all duration-300">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <Link to="/" className="text-white font-display font-bold tracking-widest text-lg flex items-center gap-2 hover:opacity-80 transition-opacity">
            <MonitorPlay className="w-5 h-5 text-netflix-red" />
            <span>MOVIEAI</span>
          </Link>
          
          <div className="flex items-center gap-6 md:gap-8 text-sm font-medium">
            <Link to="/movies" className={`flex items-center gap-2 transition-colors ${isActive('/movies')}`}>
              <Film className="w-4 h-4" /> Movies
            </Link>
            <Link to="/recommendations" className={`flex items-center gap-2 transition-colors ${isActive('/recommendations')}`}>
              <LayoutGrid className="w-4 h-4" /> Recommendations
            </Link>
            <Link to="/ai" className={`flex items-center gap-2 transition-colors ${isActive('/ai')}`}>
              <Sparkles className="w-4 h-4" /> AI Assistant
            </Link>
            <Link to="/watchlist" className={`flex items-center gap-2 transition-colors ${isActive('/watchlist')}`}>
              <Bookmark className="w-4 h-4" /> Watchlist
            </Link>
            {user && (
              <Link to="/onboarding" className={`flex items-center gap-2 transition-colors ${isActive('/onboarding')}`}>
                <SlidersHorizontal className="w-4 h-4" /> My Preferences
              </Link>
            )}

            {user ? (
              <div className="flex items-center gap-4 border-l border-white/10 pl-6">
                <span className="text-xs font-semibold text-white bg-white/10 px-3 py-1.5 rounded-full flex items-center gap-1.5">
                  <User className="w-3.5 h-3.5 text-blue-400" />
                  {user.username}
                </span>
                <button 
                  onClick={logout}
                  title="Sign Out"
                  className="text-neutral-400 hover:text-red-400 transition-colors p-1.5"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <button
                onClick={() => setIsAuthOpen(true)}
                className="px-4 py-1.5 bg-netflix-red hover:bg-red-700 text-white font-medium rounded-full text-xs transition-all shadow-md"
              >
                Sign In
              </button>
            )}
          </div>
        </div>
      </nav>

      <AuthModal isOpen={isAuthOpen} onClose={() => setIsAuthOpen(false)} />
    </>
  );
}