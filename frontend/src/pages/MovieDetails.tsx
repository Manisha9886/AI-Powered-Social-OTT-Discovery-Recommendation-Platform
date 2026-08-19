import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { movieService, watchlistService } from '../services/api';
import { Movie } from '../types';
import { useAuth } from '../context/AuthContext';
import { Star, Loader2, ArrowLeft, Clock, Film, Bookmark, Check, BookOpen } from 'lucide-react';

export default function MovieDetails() {
  const { id } = useParams();
  const { user } = useAuth();
  const [movie, setMovie] = useState<Movie | null>(null);
  const [overview, setOverview] = useState<string | null>(null);
  const [overviewLoading, setOverviewLoading] = useState(true);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [isSaved, setIsSaved] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (id) {
      setLoading(true);
      setError(false);
      setOverviewLoading(true);

      movieService.getMovie(id).then(res => {
        setMovie(res.data);
        setLoading(false);
      }).catch(err => {
        console.error(err);
        setError(true);
        setLoading(false);
      });

      movieService.getOverview(id).then(res => {
        setOverview(res.data?.overview || "Overview is currently unavailable for this movie.");
      }).catch(err => {
        console.error(err);
        setOverview("Overview is currently unavailable for this movie.");
      }).finally(() => {
        setOverviewLoading(false);
      });
    }
  }, [id]);

  const handleToggleWatchlist = async () => {
    if (!user || !movie) return;
    setSaving(true);
    try {
      if (isSaved) {
        await watchlistService.removeFromWatchlist(Number(movie.movie_id));
        setIsSaved(false);
      } else {
        await watchlistService.addToWatchlist(Number(movie.movie_id));
        setIsSaved(true);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  if (loading) return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-cinematic-base text-neutral-500 space-y-4">
      <Loader2 className="w-8 h-8 animate-spin text-netflix-red" />
      <p className="animate-pulse font-medium">Loading details...</p>
    </div>
  );
  
  if (error || !movie) return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-cinematic-base text-center space-y-4">
      <p className="text-xl text-neutral-300">We couldn't load this movie.</p>
      <Link to="/movies" className="px-6 py-2 bg-white/10 hover:bg-white/20 rounded-full text-white transition-colors">
        Back to Movies
      </Link>
    </div>
  );

  const posterUrl = movie.poster_path 
    ? (movie.poster_path.startsWith('http') ? movie.poster_path : `https://image.tmdb.org/t/p/original${movie.poster_path}`) 
    : null;
    
  const genres = movie.genres || [];
  const ratingScore = movie.vote_average ?? (movie as any).rating_score;

  return (
    <div className="min-h-screen bg-cinematic-base relative pb-24">
      {/* Massive Cinematic Backdrop */}
      <div className="absolute top-0 inset-x-0 h-[70vh] z-0 overflow-hidden">
        {posterUrl ? (
          <>
            <img src={posterUrl} alt={movie.title} className="w-full h-full object-cover opacity-30 object-top" />
            <div className="absolute inset-0 bg-gradient-to-t from-cinematic-base via-cinematic-base/80 to-transparent" />
            <div className="absolute inset-0 bg-gradient-to-r from-cinematic-base via-cinematic-base/60 to-transparent" />
          </>
        ) : (
          <div className="absolute inset-0 bg-gradient-to-br from-neutral-900 to-black" />
        )}
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-6 pt-32">
        <Link to="/movies" className="inline-flex items-center gap-2 text-neutral-400 hover:text-white transition-colors mb-12">
          <ArrowLeft className="w-4 h-4" /> Back to explore
        </Link>

        <div className="flex flex-col md:flex-row gap-12 lg:gap-16">
          {/* Poster Column */}
          <div className="w-full md:w-1/3 lg:w-1/4 shrink-0">
            <div className="aspect-[2/3] bg-cinematic-surface rounded-2xl overflow-hidden shadow-2xl border border-white/10">
              {posterUrl ? (
                <img src={posterUrl} alt={movie.title} className="w-full h-full object-cover" />
              ) : (
                <div className="w-full h-full flex flex-col items-center justify-center p-6 text-center bg-gradient-to-br from-neutral-800 to-black">
                  <span className="font-display font-bold text-4xl text-neutral-600 uppercase tracking-widest">{movie.title.slice(0,1)}</span>
                </div>
              )}
            </div>
          </div>

          {/* Info Column */}
          <div className="w-full pt-4 md:pt-8 space-y-8">
            <div className="space-y-4">
              <h1 className="text-4xl md:text-5xl lg:text-6xl font-display font-bold text-white tracking-tight drop-shadow-md">
                {movie.title}
              </h1>
              
              <div className="flex flex-wrap items-center gap-4 text-sm font-medium">
                {ratingScore !== undefined ? (
                  <div className="flex items-center gap-1.5 px-3 py-1 bg-yellow-500/10 text-yellow-500 rounded-full border border-yellow-500/20">
                    <Star className="w-4 h-4 fill-current" />
                    <span>{Number(ratingScore).toFixed(1)} Rating</span>
                  </div>
                ) : null}
                <div className="flex items-center gap-1.5 px-3 py-1 bg-white/5 text-white rounded-full border border-white/10">
                  <Clock className="w-4 h-4 text-neutral-400" />
                  <span>{movie.release_year || 'Unknown Year'}</span>
                </div>
                {genres.length > 0 && (
                  <div className="flex items-center gap-1.5 px-3 py-1 bg-white/5 text-white rounded-full border border-white/10">
                    <Film className="w-4 h-4 text-neutral-400" />
                    <span>{Array.isArray(genres) ? genres.join(', ') : genres}</span>
                  </div>
                )}
              </div>
            </div>

            <div className="max-w-3xl">
              <h3 className="text-lg font-semibold text-white mb-3 font-display flex items-center gap-2">
                <BookOpen className="w-5 h-5 text-blue-400" /> Knowledge-Based Overview
              </h3>
              {overviewLoading ? (
                <div className="flex items-center gap-3 py-4 text-neutral-400 text-sm">
                  <Loader2 className="w-4 h-4 animate-spin text-netflix-red" />
                  <span>Fetching overview...</span>
                </div>
              ) : (
                <p className="text-neutral-300 leading-relaxed text-lg font-light bg-black/40 p-6 rounded-2xl border border-white/10 shadow-inner">
                  {overview}
                </p>
              )}
            </div>
            
            <div className="pt-8 border-t border-white/5 flex flex-wrap gap-4">
              <Link 
                to="/recommendations" 
                className="px-6 py-3 bg-netflix-red hover:bg-red-700 text-white font-medium rounded-full transition-colors flex items-center justify-center shadow-lg"
              >
                Find Similar Movies
              </Link>

              {user && (
                <button
                  onClick={handleToggleWatchlist}
                  disabled={saving}
                  className={`px-6 py-3 rounded-full font-medium transition-all flex items-center gap-2 shadow-lg border ${
                    isSaved 
                      ? 'bg-emerald-600/20 border-emerald-500 text-emerald-400 hover:bg-emerald-600/30' 
                      : 'bg-white/10 border-white/20 text-white hover:bg-white/20'
                  }`}
                >
                  {saving ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : isSaved ? (
                    <>
                      <Check className="w-4 h-4" /> Added to Watchlist
                    </>
                  ) : (
                    <>
                      <Bookmark className="w-4 h-4" /> Save to Watchlist
                    </>
                  )}
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}