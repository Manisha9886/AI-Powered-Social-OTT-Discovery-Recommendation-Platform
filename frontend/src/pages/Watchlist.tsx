import { useState, useEffect } from 'react';
import { watchlistService } from '../services/api';
import { useAuth } from '../context/AuthContext';
import MovieCard from '../components/MovieCard';
import { Bookmark, Loader2, Trash2 } from 'lucide-react';

export default function Watchlist() {
  const { user } = useAuth();
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchWatchlist = async () => {
    setLoading(true);
    try {
      const res = await watchlistService.getWatchlist();
      setItems(res.data || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (user) {
      fetchWatchlist();
    } else {
      setLoading(false);
    }
  }, [user]);

  const handleRemove = async (movieId: number) => {
    try {
      await watchlistService.removeFromWatchlist(movieId);
      setItems(items.filter(item => item.movie_id !== movieId));
    } catch (err) {
      console.error(err);
    }
  };

  if (!user) {
    return (
      <div className="max-w-7xl mx-auto px-6 py-32 flex flex-col items-center justify-center text-center min-h-screen">
        <Bookmark className="w-16 h-16 text-neutral-600 mb-4" />
        <h1 className="text-3xl font-display font-bold text-white mb-2">Your Watchlist</h1>
        <p className="text-neutral-400 max-w-md">Please sign in to view and manage your saved watchlist movies.</p>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-6 py-24 min-h-screen">
      <div className="mb-12">
        <h1 className="text-4xl md:text-5xl font-display font-bold text-white mb-3 flex items-center gap-3">
          <Bookmark className="w-10 h-10 text-netflix-red" /> My Watchlist
        </h1>
        <p className="text-neutral-400 text-lg">Movies you've saved to watch later.</p>
      </div>

      {loading ? (
        <div className="flex flex-col items-center justify-center py-32 text-neutral-500 space-y-4">
          <Loader2 className="w-8 h-8 animate-spin text-netflix-red" />
          <p className="font-medium animate-pulse">Loading watchlist...</p>
        </div>
      ) : items.length === 0 ? (
        <div className="text-center py-32 text-neutral-400 space-y-4">
          <p className="text-xl">Your watchlist is currently empty.</p>
          <p className="text-sm text-neutral-500">Explore movies and click the bookmark icon to save titles!</p>
        </div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-6">
          {items.map(item => {
            const movieData = item.movie_details || { movie_id: item.movie_id, title: `Movie #${item.movie_id}` };
            return (
              <div key={item.id} className="relative group">
                <MovieCard movie={movieData} />
                <button
                  onClick={() => handleRemove(item.movie_id)}
                  title="Remove from watchlist"
                  className="absolute top-3 right-3 z-20 p-2 bg-black/70 hover:bg-red-600 text-white rounded-full transition-colors backdrop-blur-md opacity-0 group-hover:opacity-100"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
