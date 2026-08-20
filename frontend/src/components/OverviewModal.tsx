import React, { useState, useEffect } from 'react';
import { movieService } from '../services/api';
import { X, Loader2, Star, Clock, Film, Info } from 'lucide-react';

interface OverviewModalProps {
  movieId: number | string | null;
  movieData?: any;
  onClose: () => void;
}

export default function OverviewModal({ movieId, movieData, onClose }: OverviewModalProps) {
  const [overview, setOverview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [source, setSource] = useState<string>('');

  useEffect(() => {
    if (movieId) {
      setLoading(true);
      setOverview(null);
      movieService.getOverview(movieId)
        .then(res => {
          setOverview(res.data?.overview || "Overview is currently unavailable for this movie.");
          setSource(res.data?.source || '');
        })
        .catch(err => {
          console.error(err);
          setOverview("Overview is currently unavailable for this movie.");
        })
        .finally(() => setLoading(false));
    }
  }, [movieId]);

  if (!movieId) return null;

  const posterUrl = movieData?.poster_path 
    ? (movieData.poster_path.startsWith('http') ? movieData.poster_path : `https://image.tmdb.org/t/p/w500${movieData.poster_path}`)
    : null;

  const genres = movieData?.genres || [];
  const ratingScore = movieData?.vote_average ?? movieData?.rating_score;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-fade-in">
      <div className="relative w-full max-w-2xl bg-cinematic-surface border border-cinematic-border rounded-2xl p-6 md:p-8 shadow-2xl overflow-hidden max-h-[90vh] overflow-y-auto">
        <button 
          onClick={onClose}
          className="absolute top-4 right-4 z-10 p-2 text-neutral-400 hover:text-white bg-black/40 hover:bg-black/80 rounded-full transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex flex-col md:flex-row gap-6">
          {/* Poster */}
          <div className="w-full md:w-48 aspect-[2/3] shrink-0 bg-neutral-900 rounded-xl overflow-hidden border border-white/10">
            {posterUrl ? (
              <img src={posterUrl} alt={movieData?.title || 'Movie'} className="w-full h-full object-cover" />
            ) : (
              <div className="w-full h-full flex items-center justify-center p-4 text-center">
                <span className="font-bold text-2xl text-neutral-600 uppercase">{movieData?.title?.slice(0, 1) || 'M'}</span>
              </div>
            )}
          </div>

          {/* Content */}
          <div className="flex-1 space-y-4">
            <h2 className="text-2xl md:text-3xl font-display font-bold text-white leading-tight">
              {movieData?.title || 'Movie Overview'}
            </h2>

            <div className="flex flex-wrap items-center gap-3 text-xs font-medium text-neutral-400">
              {ratingScore !== undefined && (
                <span className="flex items-center gap-1 text-yellow-500 bg-yellow-500/10 px-2.5 py-1 rounded-full border border-yellow-500/20">
                  <Star className="w-3.5 h-3.5 fill-current" /> {Number(ratingScore).toFixed(1)}
                </span>
              )}
              {movieData?.release_year && (
                <span className="flex items-center gap-1 bg-white/5 px-2.5 py-1 rounded-full border border-white/10">
                  <Clock className="w-3.5 h-3.5" /> {movieData.release_year}
                </span>
              )}
              {genres.length > 0 && (
                <span className="flex items-center gap-1 bg-white/5 px-2.5 py-1 rounded-full border border-white/10">
                  <Film className="w-3.5 h-3.5" /> {Array.isArray(genres) ? genres.join(', ') : genres}
                </span>
              )}
            </div>

            <div className="pt-2 border-t border-white/5">
              <h3 className="text-sm font-semibold text-white mb-2 flex items-center gap-2">
                <Info className="w-4 h-4 text-blue-400" /> Overview
              </h3>
              {loading ? (
                <div className="flex items-center gap-3 py-6 text-neutral-400 text-sm">
                  <Loader2 className="w-5 h-5 animate-spin text-netflix-red" />
                  <span>Fetching knowledge-based overview...</span>
                </div>
              ) : (
                <div className="space-y-3">
                  <p className="text-neutral-300 text-sm leading-relaxed font-light bg-black/30 p-4 rounded-xl border border-white/5">
                    {overview}
                  </p>
                  {source && (
                    <span className="inline-block text-[10px] text-neutral-500 uppercase tracking-widest font-mono">
                      Source: {source}
                    </span>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
