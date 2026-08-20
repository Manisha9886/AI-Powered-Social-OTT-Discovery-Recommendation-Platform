import { useState } from 'react';
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

const POPULAR_POSTERS: Record<string, string> = {
  'Avatar': 'https://m.media-amazon.com/images/M/MV5BMDEzMmQwZjctZWU2My00MWNlLWE0NjItMDJlYTRlNGJiZjcyXkEyXkFqcGc@._V1_SX300.jpg',
  "Pirates of the Caribbean: At World's End": 'https://m.media-amazon.com/images/M/MV5BMjIyNjkxNzEyMl5BMl5BanBnXkFtZTYwMjc3MDE3._V1_SX300.jpg',
  'Spectre': 'https://m.media-amazon.com/images/M/MV5BMzA5MzFiNDAtYTI0NC00MDE5LTljYTctYTNkODk1OTZlODI5XkEyXkFqcGc@._V1_SX300.jpg',
  'The Dark Knight Rises': 'https://m.media-amazon.com/images/M/MV5BMTk4ODQzNDY3Ml5BMl5BanBnXkFtZTcwODA0NTM4Nw@@._V1_SX300.jpg',
  'John Carter': 'https://m.media-amazon.com/images/M/MV5BZWNmZGYzZjUtODRmOS00ODgzLWE4NWQtMDI3MGUwNjRjYjY0XkEyXkFqcGc@._V1_SX300.jpg',
  'Spider-Man 3': 'https://m.media-amazon.com/images/M/MV5BODE2NzNhMDctYjUzMC00Y2M5LWI2Y2EtODJkZTFjN2Y5ODlmXkEyXkFqcGc@._V1_SX300.jpg',
  'Tangled': 'https://m.media-amazon.com/images/M/MV5BMTAxNDYxMjg0MjNeQTJeQWpwZ15BbWU3MDcyNTk2OTM@._V1_SX300.jpg',
  'Avengers: Age of Ultron': 'https://m.media-amazon.com/images/M/MV5BODBhYTg1NGQtNGVmNS00ZTdiLThjYTYtZDFkNzRiNTZmNDZjXkEyXkFqcGc@._V1_SX300.jpg',
  'Harry Potter and the Half-Blood Prince': 'https://m.media-amazon.com/images/M/MV5BNzU3NDg4NTAyNV5BMl5BanBnXkFtZTcwOTg2ODgwMw@@._V1_SX300.jpg',
  'Batman v Superman: Dawn of Justice': 'https://m.media-amazon.com/images/M/MV5BYThjYzcyYzItNTVjNy00NDVhLWIwMWItDhhn_V1_SX300.jpg',
  'The Dark Knight': 'https://m.media-amazon.com/images/M/MV5BMTMxNTMwODM0NF5BMl5BanBnXkFtZTcwODAyMTk2Mw@@._V1_SX300.jpg',
  'Inception': 'https://m.media-amazon.com/images/M/MV5BMjAxMzY3NjcxNF5BMl5BanBnXkFtZTcwNTI5OTM0Mw@@._V1_SX300.jpg',
  'Interstellar': 'https://m.media-amazon.com/images/M/MV5BYzdjMDAxZGItMjI2My00ODA1LTlkNzItOWFjMDU5ZDJlYWY3XkEyXkFqcGc@._V1_SX300.jpg',
  'Titanic': 'https://m.media-amazon.com/images/M/MV5BMDdmZGU3NDQtY2E5My00ZTliLWEzOTUtMTY4ZGI1YjdiNjk3XkEyXkFqcGc@._V1_SX300.jpg',
  'Inside Out': 'https://m.media-amazon.com/images/M/MV5BOTgxMDQwMDk0OF5BMl5BanBnXkFtZTgwNjU5OTg2NV5BMl5BanBnXkFtZTgwNjU5OTg2NV@@._V1_SX300.jpg',
  'Iron Man': 'https://m.media-amazon.com/images/M/MV5BMTczNTI2ODUwOF5BMl5BanBnXkFtZTcwMTU0NTIzMw@@._V1_SX300.jpg',
  'Up': 'https://m.media-amazon.com/images/M/MV5BMTk3NDE2NzI4NF5BMl5BanBnXkFtZTcwNzE1MzEyMw@@._V1_SX300.jpg'
};

export default function MovieCard({ movie, showScore }: MovieCardProps) {
  const [isOverviewOpen, setIsOverviewOpen] = useState(false);
  const [imgError, setImgError] = useState(false);

  const getPosterUrl = () => {
    if (POPULAR_POSTERS[movie.title]) return POPULAR_POSTERS[movie.title];
    
    const path = movie.poster_path;
    if (path && (path.startsWith('/') || path.includes('image.tmdb.org') || path.includes('media-amazon.com') || path.includes('wikimedia.org') || path.match(/\.(jpg|jpeg|png|webp)(\?.*)?$/i))) {
      return path.startsWith('http') ? path : `https://image.tmdb.org/t/p/w500${path}`;
    }
    
    const genreStr = Array.isArray(movie.genres) ? movie.genres.join(' ').toLowerCase() : String(movie.genres || '').toLowerCase();
    if (genreStr.includes('action') || genreStr.includes('adventure')) {
      return 'https://images.unsplash.com/photo-1536440136628-849c177e76a1?w=500&auto=format&fit=crop';
    } else if (genreStr.includes('sci-fi') || genreStr.includes('science fiction') || genreStr.includes('fantasy')) {
      return 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=500&auto=format&fit=crop';
    } else if (genreStr.includes('animation') || genreStr.includes('family')) {
      return 'https://images.unsplash.com/photo-1534447677768-be436bb09401?w=500&auto=format&fit=crop';
    } else if (genreStr.includes('horror') || genreStr.includes('thriller') || genreStr.includes('crime')) {
      return 'https://images.unsplash.com/photo-1509198397868-475647b2a1e5?w=500&auto=format&fit=crop';
    } else if (genreStr.includes('comedy')) {
      return 'https://images.unsplash.com/photo-1517604931442-7e0c8ed2963c?w=500&auto=format&fit=crop';
    } else {
      return 'https://images.unsplash.com/photo-1485846234645-a62644f84728?w=500&auto=format&fit=crop';
    }
  };

  const posterUrl = !imgError ? getPosterUrl() : 'https://images.unsplash.com/photo-1485846234645-a62644f84728?w=500&auto=format&fit=crop';

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
