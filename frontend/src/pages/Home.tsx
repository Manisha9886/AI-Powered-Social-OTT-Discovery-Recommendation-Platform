import { Link } from 'react-router-dom';
import { Play, Sparkles } from 'lucide-react';

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col relative overflow-hidden bg-cinematic-base">
      {/* Background Cinematic Gradient */}
      <div className="absolute inset-0 z-0">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-900/20 via-cinematic-base to-cinematic-base" />
        <div className="absolute inset-0 bg-gradient-to-t from-cinematic-base via-transparent to-transparent" />
      </div>

      <div className="relative z-10 flex flex-col items-center justify-center flex-1 text-center px-6 pt-16">
        <div className="max-w-4xl mx-auto space-y-8 animate-fade-in">
          
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-xs font-medium text-neutral-300 mb-4 backdrop-blur-md">
            <Sparkles className="w-3 h-3 text-blue-400" />
            <span>AI-Powered OTT Platform</span>
          </div>

          <h1 className="text-5xl md:text-7xl lg:text-8xl font-bold tracking-tighter text-white leading-[1.05] drop-shadow-2xl">
            DISCOVER YOUR <br className="hidden md:block"/>
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-white to-neutral-500">NEXT FAVORITE</span>
          </h1>
          
          <p className="text-lg md:text-xl text-neutral-400 max-w-2xl mx-auto leading-relaxed font-light">
            Explore a world of cinema powered by intelligent hybrid recommendations, semantic search, and grounded AI explanations.
          </p>
          
          <div className="flex flex-col sm:flex-row justify-center gap-4 pt-8">
            <Link 
              to="/movies" 
              className="px-8 py-4 bg-white text-black font-semibold rounded-full hover:bg-neutral-200 transition-all duration-300 flex items-center justify-center gap-2 shadow-[0_0_40px_rgba(255,255,255,0.3)] hover:shadow-[0_0_60px_rgba(255,255,255,0.5)] hover:scale-105"
            >
              <Play className="w-5 h-5 fill-current" />
              Explore Movies
            </Link>
            <Link 
              to="/ai" 
              className="px-8 py-4 bg-cinematic-surface text-white font-semibold rounded-full hover:bg-white/10 transition-all duration-300 border border-cinematic-border flex items-center justify-center gap-2 hover:scale-105"
            >
              <Sparkles className="w-5 h-5" />
              Ask AI
            </Link>
          </div>
        </div>
      </div>
      
      {/* Decorative Bottom Fade */}
      <div className="absolute bottom-0 inset-x-0 h-32 bg-gradient-to-t from-cinematic-base to-transparent pointer-events-none z-20" />
    </div>
  );
}