import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Star, Info, BookOpen, Film } from 'lucide-react';
import OverviewModal from './OverviewModal';

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
  const [isOverviewOpen, setIsOverviewOpen] = useState(false);
  const [imgError, setImgError] = useState(false);

  const isValidImage = (path?: string) => {
    if (!path) return false;
    if (path.startsWith('/')) return true; // TMDB relative image path
    if (path.includes('image.tmdb.org') || path.includes('media-amazon.com') || path.includes('ssl-images-amazon.com') || path.includes('wikimedia.org')) return true;
    if (path.match(/\.(jpg|jpeg|png|webp)(\?.*)?$/i)) return true;
    return false;
  };

  const posterUrl = (!imgError && isValidImage(movie.poster_path))
    ? (movie.poster_path!.startsWith('http') ? movie.poster_path! : `https://image.tmdb.org/t/p/w500${movie.poster_path}`)
    : null;

  const genreText = Array.isArray(movie.genres) 
    ? movie.genres.slice(0, 2).join(', ') 
    : (typeof movie.genres === 'string' ? movie.genres.split(',').slice(0,2).join(', ') : 'Unknown');

  return (
    <>
      <div className="group relative flex flex-col rounded-xl overflow-hidden bg-cinematic-surface border border-cinematic-border shadow-lg transition-all duration-300 hover:scale-[1.02] hover:shadow-2xl hover:border-white/20">
        {/* Poster Image Container */}
        <div className="relative aspect-[2/3] w-full overflow-hidden bg-gradient-to-b from-neutral-800 via-neutral-900 to-black">
          {posterUrl ? (
            <img 
              src={posterUrl} 
              alt={movie.title} 
              className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
              loading="lazy"
              onError={() => setImgError(true)}
            />
          ) : (
            <div className="w-full h-full flex flex-col items-center justify-between p-5 text-center bg-gradient-to-br from-red-950/40 via-neutral-900 to-neutral-950 border border-white/5 relative overflow-hidden">
              <div className="w-full flex justify-between items-center text-[10px] uppercase font-bold tracking-widest text-neutral-500">
                <span className="flex items-center gap-1 text-netflix-red"><Film className="w-3 h-3" /> MOVIEAI</span>
                <span>{movie.release_year || ''}</span>
              </div>

              <div className="my-auto px-2 py-4 space-y-2">
                <span className="inline-block p-3 rounded-full bg-white/5 border border-white/10 text-netflix-red mb-1">
                  <Film className="w-6 h-6" />
                </span>
                <h4 className="font-display font-bold text-white text-sm line-clamp-3 leading-snug tracking-tight">
                  {movie.title}
                </h4>
              </div>

              <div className="w-full pt-2 border-t border-white/5 text-[10px] text-neutral-400 truncate">
                {genreText}
              </div>
            </div>
          )}
          
          {/* Overlay on hover */}
          <div className="absolute inset-0 bg-black/75 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex flex-col items-center justify-center gap-3 backdrop-blur-sm p-4">
            <button 
              onClick={() => setIsOverviewOpen(true)}
              className="w-full py-2 bg-white/10 hover:bg-white/20 text-white font-medium rounded-full transform translate-y-2 group-hover:translate-y-0 transition-all duration-300 shadow-lg flex items-center justify-center gap-2 border border-white/20 text-xs"
            >
              <BookOpen className="w-3.5 h-3.5" />
              Overview
            </button>

            <Link 
              to={`/movies/${movie.movie_id}`}
              className="w-full py-2 bg-netflix-red hover:bg-red-700 text-white font-medium rounded-full transform translate-y-2 group-hover:translate-y-0 transition-all duration-300 shadow-lg flex items-center justify-center gap-2 text-xs"
            >
              <Info className="w-3.5 h-3.5" />
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
            {(movie.vote_average !== undefined || (movie as any).rating_score !== undefined) ? (
              <div className="flex items-center gap-1 text-yellow-500">
                <Star className="w-3 h-3 fill-current" />
                <span className="font-medium">
                  {((movie.vote_average ?? (movie as any).rating_score) || 0).toFixed(1)}
                </span>
              </div>
            ) : null}
          </div>
          
          <div className="text-xs text-neutral-500 truncate mt-1">
            {genreText}
          </div>

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

      <OverviewModal 
        movieId={isOverviewOpen ? movie.movie_id : null} 
        movieData={movie} 
        onClose={() => setIsOverviewOpen(false)} 
      />
    </>
  );
}
