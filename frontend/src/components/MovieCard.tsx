import { Link } from 'react-router-dom';
import { Star, Info } from 'lucide-react';

export interface MovieCardProps {
  movie: {
    movie_id: number | string;
    title: string;
    release_year?: number;
    poster_path?: string;
    vote_average?: number;
    genres?: string[] | string;
    score?: number;
  };
  showScore?: boolean;
}

export default function MovieCard({ movie, showScore }: MovieCardProps) {
  // Cinematic fallback for missing posters
  const posterUrl = movie.poster_path
    ? (movie.poster_path.startsWith('http') ? movie.poster_path : `https://image.tmdb.org/t/p/w500${movie.poster_path}`)
    : null;

  // Format genres
  const genreText = Array.isArray(movie.genres) 
    ? movie.genres.slice(0, 2).join(', ') 
    : (typeof movie.genres === 'string' ? movie.genres.split(',').slice(0,2).join(', ') : 'Unknown');

  return (
    <div className="group relative flex flex-col rounded-xl overflow-hidden bg-cinematic-surface border border-cinematic-border shadow-lg transition-all duration-300 hover:scale-[1.02] hover:shadow-2xl hover:border-white/20">
      {/* Poster Image Container */}
      <div className="relative aspect-[2/3] w-full overflow-hidden bg-gradient-to-br from-neutral-800 to-black">
        {posterUrl ? (
          <img 
            src={posterUrl} 
            alt={movie.title} 
            className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
            loading="lazy"
            onError={(e) => {
              // Fallback to gradient if image fails to load
              e.currentTarget.style.display = 'none';
              e.currentTarget.parentElement?.classList.add('flex', 'items-center', 'justify-center');
            }}
          />
        ) : (
          <div className="w-full h-full flex flex-col items-center justify-center p-4 text-center">
             <span className="font-display font-bold text-xl text-neutral-600 uppercase tracking-widest">{movie.title.slice(0, 1)}</span>
          </div>
        )}
        
        {/* Overlay on hover */}
        <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center backdrop-blur-sm">
           <Link 
            to={`/movies/${movie.movie_id}`}
            className="px-6 py-2 bg-netflix-red text-white font-medium rounded-full transform translate-y-4 group-hover:translate-y-0 transition-all duration-300 shadow-lg flex items-center gap-2"
           >
            <Info className="w-4 h-4" />
            Details
           </Link>
        </div>
      </div>

      {/* Metadata Section */}
      <div className="p-4 flex flex-col gap-1 z-10 bg-cinematic-surface relative flex-1">
        <h3 className="font-display font-semibold text-white truncate text-base leading-tight" title={movie.title}>
          {movie.title}
        </h3>
        
        <div className="flex items-center justify-between text-xs text-neutral-400 mt-1">
          <span>{movie.release_year || 'N/A'}</span>
          {movie.vote_average ? (
             <div className="flex items-center gap-1 text-yellow-500">
                <Star className="w-3 h-3 fill-current" />
                <span className="font-medium">{movie.vote_average.toFixed(1)}</span>
             </div>
          ) : null}
        </div>
        
        <div className="text-xs text-neutral-500 truncate mt-1">
          {genreText}
        </div>

        {/* Optional Score display (for recommendations/search) */}
        {showScore && movie.score !== undefined && (
          <div className="mt-auto pt-3 border-t border-white/5 flex items-center justify-between">
            <span className="text-xs text-neutral-500 uppercase tracking-wider font-semibold">Match</span>
            <span className="text-xs font-bold text-blue-400 bg-blue-500/10 px-2 py-0.5 rounded">
              {(movie.score * 100).toFixed(0)}%
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
