import { useState, useEffect } from 'react';
import { movieService } from '../services/api';
import { Movie } from '../types';
import MovieCard from '../components/MovieCard';
import { Search, Loader2 } from 'lucide-react';

export default function Movies() {
  const [movies, setMovies] = useState<Movie[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    movieService.getMovies(1, 100).then(res => {
      setMovies(res.data.movies);
      setLoading(false);
    }).catch(err => {
      console.error(err);
      setError(true);
      setLoading(false);
    });
  }, []);

  const filteredMovies = movies.filter(movie => {
    if (!searchQuery.trim()) return true;
    const query = searchQuery.toLowerCase();
    const titleMatch = movie.title.toLowerCase().includes(query);
    const rawGenres: any = movie.genres;
    const genreMatch = Array.isArray(rawGenres) 
      ? rawGenres.some((g: any) => String(g).toLowerCase().includes(query))
      : (typeof rawGenres === 'string' && (rawGenres as string).toLowerCase().includes(query));
    return titleMatch || genreMatch;
  });

  return (
    <div className="max-w-7xl mx-auto px-6 py-24 min-h-screen">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-12">
        <div>
          <h1 className="text-4xl md:text-5xl font-display font-bold text-white mb-3">Explore Movies</h1>
          <p className="text-neutral-400 text-lg">Browse our entire knowledge base of cinematic experiences.</p>
        </div>
        
        {/* Real-Time Live Search Bar */}
        <div className="relative w-full md:w-80">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
          <input 
            type="text" 
            placeholder="Search catalog by title or genre..." 
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-cinematic-surface border border-cinematic-border text-white placeholder-neutral-500 rounded-full py-2.5 pl-11 pr-4 focus:outline-none focus:border-neutral-400 transition-colors text-sm shadow-inner"
          />
        </div>
      </div>

      {loading ? (
        <div className="flex flex-col items-center justify-center py-32 text-neutral-500 space-y-4">
          <Loader2 className="w-8 h-8 animate-spin text-netflix-red" />
          <p className="font-medium animate-pulse">Loading catalog...</p>
        </div>
      ) : error ? (
        <div className="text-center py-32 space-y-4">
          <p className="text-xl text-neutral-300">We couldn't load the catalog right now.</p>
          <button onClick={() => window.location.reload()} className="px-6 py-2 bg-white/10 hover:bg-white/20 rounded-full text-white font-medium transition-colors">
            Try Again
          </button>
        </div>
      ) : filteredMovies.length === 0 ? (
        <div className="text-center py-32 bg-cinematic-surface border border-cinematic-border rounded-2xl p-8">
          <p className="text-xl font-semibold text-neutral-300 mb-1">No movies found</p>
          <p className="text-sm text-neutral-500">No movies match "{searchQuery}". Try searching for another title or genre.</p>
        </div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-6">
          {filteredMovies.map(movie => (
            <MovieCard key={movie.movie_id} movie={movie} />
          ))}
        </div>
      )}
    </div>
  );
}