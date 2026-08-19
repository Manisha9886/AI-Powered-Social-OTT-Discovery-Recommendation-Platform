import os
import json

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

# 1. Backend Movies Endpoint
movies_py = """
from fastapi import APIRouter, HTTPException, Query
import json
import os
from typing import List, Optional

router = APIRouter()

# Load movie lookup data
LOOKUP_PATH = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'data', 'processed', 'movie_lookup.json')
movies_data = {}

try:
    with open(LOOKUP_PATH, 'r', encoding='utf-8') as f:
        movies_data = json.load(f)
except Exception as e:
    print(f"Failed to load movie_lookup.json: {e}")

@router.get("/")
def get_movies(page: int = Query(1, ge=1), page_size: int = Query(24, ge=1, le=100)):
    movies_list = list(movies_data.values())
    total = len(movies_list)
    
    start = (page - 1) * page_size
    end = start + page_size
    
    return {
        "page": page,
        "page_size": page_size,
        "total": total,
        "movies": movies_list[start:end]
    }

@router.get("/{movie_id}")
def get_movie(movie_id: str):
    if movie_id not in movies_data:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movies_data[movie_id]
"""
write_file("backend/app/api/endpoints/movies.py", movies_py.strip())

# 2. Modify api_v1.py
api_v1_py = """
from fastapi import APIRouter
from .endpoints import health, recommendations, ai, movies

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(movies.router, prefix="/movies", tags=["movies"])
"""
write_file("backend/app/api/api_v1.py", api_v1_py.strip())

# 3. Frontend Types
types_ts = """
export interface Movie {
  movie_id: number | string;
  title: string;
  release_year: number;
  overview?: string;
  genres: string[];
  vote_average?: number;
  poster_path?: string;
}

export interface RecommendationResponse {
  user_id: number;
  recommendations: any[];
  strategy_used: string;
  total_count: number;
}
"""
write_file("frontend/src/types/index.ts", types_ts.strip())

# 4. Frontend API Service
api_ts = """
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5001/api/v1';

export const api = axios.create({
  baseURL: API_BASE,
});

export const movieService = {
  getMovies: (page = 1, pageSize = 24) => api.get(`/movies?page=${page}&page_size=${pageSize}`),
  getMovie: (id: string) => api.get(`/movies/${id}`),
};

export const aiService = {
  recommend: (query: string) => api.post('/ai/recommend', { query }),
};

export const recommendationService = {
  getRecommendations: (userId: number = 101) => api.get(`/recommendations?user_id=${userId}`),
};
"""
write_file("frontend/src/services/api.ts", api_ts.strip())

# 5. Frontend Components - Navbar
navbar_tsx = """
import { Link, useLocation } from 'react-router-dom';
import { Film, Sparkles, LayoutGrid, MonitorPlay } from 'lucide-react';

export default function Navbar() {
  const location = useLocation();
  const isActive = (path: string) => location.pathname === path ? 'text-white' : 'text-neutral-500 hover:text-white';

  return (
    <nav className="fixed top-0 inset-x-0 z-50 bg-[#0a0a0a]/80 backdrop-blur-xl border-b border-white/5">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between font-medium">
        <Link to="/" className="text-white font-bold tracking-widest text-lg flex items-center gap-2">
          <MonitorPlay className="w-5 h-5 text-blue-500" />
          MOVIEAI
        </Link>
        <div className="flex gap-8 text-sm">
          <Link to="/movies" className={`flex items-center gap-2 transition-colors ${isActive('/movies')}`}>
            <Film className="w-4 h-4" /> Movies
          </Link>
          <Link to="/recommendations" className={`flex items-center gap-2 transition-colors ${isActive('/recommendations')}`}>
            <LayoutGrid className="w-4 h-4" /> Recommendations
          </Link>
          <Link to="/ai" className={`flex items-center gap-2 transition-colors ${isActive('/ai')}`}>
            <Sparkles className="w-4 h-4" /> AI Assistant
          </Link>
          <Link to="/demo" className={`flex items-center gap-2 transition-colors ${isActive('/demo')} text-blue-400`}>
            Demo
          </Link>
        </div>
      </div>
    </nav>
  );
}
"""
write_file("frontend/src/components/Navbar.tsx", navbar_tsx.strip())

# 6. Frontend App
app_tsx = """
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import MentorShowcase from '../pages/MentorShowcase';
import Navbar from '../components/Navbar';
import Home from '../pages/Home';
import Movies from '../pages/Movies';
import MovieDetails from '../pages/MovieDetails';
import Recommendations from '../pages/Recommendations';
import AIAssistant from '../pages/AIAssistant';

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-[#0a0a0a] text-neutral-200 font-sans">
        <Navbar />
        <div className="pt-16">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/movies" element={<Movies />} />
            <Route path="/movies/:id" element={<MovieDetails />} />
            <Route path="/recommendations" element={<Recommendations />} />
            <Route path="/ai" element={<AIAssistant />} />
            <Route path="/demo" element={<MentorShowcase />} />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  );
}
"""
write_file("frontend/src/app/App.tsx", app_tsx.strip())

# 7. Frontend Home
home_tsx = """
import { Link } from 'react-router-dom';

export default function Home() {
  return (
    <div className="min-h-[calc(100vh-64px)] flex flex-col items-center justify-center text-center px-6 relative overflow-hidden">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-blue-900/20 via-[#0a0a0a] to-[#0a0a0a] pointer-events-none" />
      <div className="relative z-10 max-w-3xl mx-auto space-y-8">
        <h1 className="text-5xl md:text-7xl font-semibold tracking-tight text-white leading-[1.1]">
          DISCOVER YOUR<br />NEXT FAVORITE MOVIE
        </h1>
        <p className="text-lg text-neutral-400 max-w-xl mx-auto leading-relaxed">
          Personalized recommendations powered by movie intelligence, hybrid recommendation models, semantic retrieval and explainable AI.
        </p>
        <div className="flex justify-center gap-4 pt-4">
          <Link to="/movies" className="px-6 py-3 bg-white text-black font-medium rounded-full hover:bg-neutral-200 transition-colors">
            Explore Movies
          </Link>
          <Link to="/ai" className="px-6 py-3 bg-blue-600 text-white font-medium rounded-full hover:bg-blue-500 transition-colors">
            Ask AI
          </Link>
          <Link to="/recommendations" className="px-6 py-3 bg-white/5 text-white font-medium rounded-full hover:bg-white/10 transition-colors border border-white/5">
            Get Recommendations
          </Link>
        </div>
      </div>
    </div>
  );
}
"""
write_file("frontend/src/pages/Home.tsx", home_tsx.strip())

# 8. Frontend AIAssistant
ai_tsx = """
import { useState } from 'react';
import { aiService } from '../services/api';
import { Sparkles, Send } from 'lucide-react';

export default function AIAssistant() {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setResponse('');
    try {
      const res = await aiService.recommend(query);
      setResponse(res.data.response);
    } catch (err) {
      setResponse("AI service temporarily unavailable. Please check the backend connection.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-6 py-12">
      <div className="mb-12 space-y-4">
        <h1 className="text-4xl font-semibold tracking-tight text-white flex items-center gap-3">
          <Sparkles className="w-8 h-8 text-blue-500" /> AI Movie Assistant
        </h1>
        <p className="text-neutral-400">Grounded in the movie knowledge base.</p>
      </div>

      <div className="bg-neutral-900/50 border border-white/5 rounded-3xl overflow-hidden shadow-2xl flex flex-col min-h-[500px]">
        <div className="flex-1 p-8 overflow-y-auto flex flex-col justify-end space-y-6">
          {response ? (
            <>
              <div className="flex justify-end">
                <div className="bg-blue-600/20 text-blue-100 px-6 py-4 rounded-2xl rounded-tr-none max-w-[80%] border border-blue-500/20">
                  <div className="text-xs text-blue-400 mb-1">You</div>
                  <div className="text-lg">{query}</div>
                </div>
              </div>
              <div className="flex gap-4">
                <div className="w-8 h-8 rounded-full bg-blue-500/20 text-blue-400 flex items-center justify-center font-bold text-xs shrink-0 mt-1">AI</div>
                <div className="bg-white/5 text-white px-6 py-4 rounded-2xl rounded-tl-none max-w-[90%] border border-white/5">
                  <div className="whitespace-pre-wrap leading-relaxed">{response}</div>
                </div>
              </div>
            </>
          ) : loading ? (
             <div className="text-center text-neutral-500 space-y-2 font-mono text-sm animate-pulse">
                <div>Understanding query...</div>
                <div>Searching movie knowledge...</div>
                <div>Retrieving relevant movies...</div>
                <div>Generating recommendation...</div>
             </div>
          ) : (
            <div className="text-center text-neutral-500">
              <Sparkles className="w-12 h-12 mx-auto mb-4 opacity-20" />
              <p>Ask me to recommend a movie.</p>
              <div className="mt-8 flex flex-wrap justify-center gap-2">
                {["Recommend dark sci-fi movies", "Something like Interstellar but darker", "Find a funny movie for tonight"].map(q => (
                  <button key={q} onClick={() => setQuery(q)} className="px-4 py-2 bg-white/5 rounded-full text-xs hover:bg-white/10 transition-colors">
                    {q}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="p-4 bg-black border-t border-white/5">
          <form onSubmit={handleSubmit} className="relative">
            <input 
              type="text" 
              value={query}
              onChange={e => setQuery(e.target.value)}
              placeholder="Recommend me dark sci-fi movies..."
              className="w-full bg-white/5 border border-white/10 rounded-xl py-4 pl-6 pr-16 text-white focus:outline-none focus:border-white/20 focus:bg-white/10 transition-all placeholder:text-neutral-600"
            />
            <button type="submit" disabled={loading} className="absolute right-3 top-1/2 -translate-y-1/2 w-10 h-10 flex items-center justify-center bg-white text-black rounded-lg hover:bg-neutral-200 transition-colors disabled:opacity-50">
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
"""
write_file("frontend/src/pages/AIAssistant.tsx", ai_tsx.strip())

# 9. Frontend Movies
movies_tsx = """
import { useState, useEffect } from 'react';
import { movieService } from '../services/api';
import { Movie } from '../types';
import { Link } from 'react-router-dom';

export default function Movies() {
  const [movies, setMovies] = useState<Movie[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    movieService.getMovies(1, 24).then(res => {
      setMovies(res.data.movies);
      setLoading(false);
    }).catch(err => {
      console.error(err);
      setLoading(false);
    });
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-6 py-12">
      <h1 className="text-3xl font-semibold tracking-tight text-white mb-8">Movie Catalog</h1>
      {loading ? (
        <div className="text-center text-neutral-500 py-20">Loading movies...</div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-6">
          {movies.map(movie => (
            <Link key={movie.movie_id} to={`/movies/${movie.movie_id}`} className="group block">
              <div className="aspect-[2/3] bg-neutral-900 rounded-xl overflow-hidden border border-white/5 mb-3 relative">
                {movie.poster_path ? (
                  <img src={`https://image.tmdb.org/t/p/w500${movie.poster_path}`} alt={movie.title} className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110" />
                ) : (
                  <div className="w-full h-full flex flex-col items-center justify-center p-4 text-center bg-gradient-to-br from-neutral-800 to-black">
                     <span className="text-white font-bold opacity-50 text-sm">{movie.title}</span>
                  </div>
                )}
                <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center text-white text-xs font-medium backdrop-blur-sm">View Details</div>
              </div>
              <h3 className="text-sm font-medium text-white truncate">{movie.title}</h3>
              <p className="text-xs text-neutral-500">{movie.release_year}</p>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
"""
write_file("frontend/src/pages/Movies.tsx", movies_tsx.strip())

# 10. Frontend MovieDetails
movie_details_tsx = """
import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { movieService } from '../services/api';
import { Movie } from '../types';

export default function MovieDetails() {
  const { id } = useParams();
  const [movie, setMovie] = useState<Movie | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (id) {
      movieService.getMovie(id).then(res => {
        setMovie(res.data);
        setLoading(false);
      }).catch(err => {
        console.error(err);
        setLoading(false);
      });
    }
  }, [id]);

  if (loading) return <div className="text-center py-20 text-neutral-500">Loading details...</div>;
  if (!movie) return <div className="text-center py-20 text-neutral-500">Movie not found</div>;

  return (
    <div className="max-w-5xl mx-auto px-6 py-12">
      <div className="flex flex-col md:flex-row gap-12">
        <div className="w-full md:w-1/3 shrink-0">
          <div className="aspect-[2/3] bg-neutral-900 rounded-2xl overflow-hidden border border-white/10 shadow-2xl">
            {movie.poster_path ? (
               <img src={`https://image.tmdb.org/t/p/w500${movie.poster_path}`} alt={movie.title} className="w-full h-full object-cover" />
            ) : (
               <div className="w-full h-full flex items-center justify-center text-center p-6 bg-gradient-to-br from-neutral-800 to-black">
                 <span className="text-2xl font-bold text-white/20">{movie.title}</span>
               </div>
            )}
          </div>
        </div>
        <div className="w-full space-y-6 pt-4">
          <h1 className="text-4xl md:text-5xl font-bold text-white">{movie.title}</h1>
          <div className="flex flex-wrap gap-4 text-sm font-medium">
            <span className="px-3 py-1 bg-white/10 rounded-full text-white">{movie.release_year}</span>
            <span className="px-3 py-1 bg-blue-500/20 text-blue-400 rounded-full">★ {movie.vote_average?.toFixed(1) || 'N/A'}</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {movie.genres?.map(g => (
              <span key={g} className="text-xs px-2 py-1 border border-white/10 rounded text-neutral-400">{g}</span>
            ))}
          </div>
          <div className="h-px w-full bg-white/5 my-6"></div>
          <div>
            <h3 className="text-lg font-semibold text-white mb-2">Overview</h3>
            <p className="text-neutral-400 leading-relaxed">{movie.overview}</p>
          </div>
        </div>
      </div>
    </div>
  );
}
"""
write_file("frontend/src/pages/MovieDetails.tsx", movie_details_tsx.strip())

# 11. Frontend Recommendations
recommendations_tsx = """
import { useState, useEffect } from 'react';
import { recommendationService } from '../services/api';
import { Link } from 'react-router-dom';

export default function Recommendations() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    recommendationService.getRecommendations().then(res => {
      setData(res.data);
      setLoading(false);
    }).catch(err => {
      console.error(err);
      setLoading(false);
    });
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-6 py-12">
      <div className="mb-12">
        <h1 className="text-3xl font-semibold tracking-tight text-white mb-2">Recommended For You</h1>
        <p className="text-neutral-400">Powered by Hybrid Recommendation Engine</p>
      </div>
      
      {loading ? (
        <div className="text-center text-neutral-500 py-20">Analyzing your preferences...</div>
      ) : (
        <div className="space-y-8">
           <div className="inline-block px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-sm text-neutral-300 font-mono">
             Strategy: {data?.strategy_used}
           </div>
           
           <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
             {data?.recommendations?.map((rec: any, idx: number) => (
               <div key={idx} className="bg-neutral-900/40 border border-white/5 rounded-2xl p-6 hover:bg-neutral-900/60 transition-colors">
                 <Link to={`/movies/${rec.movie_id}`} className="text-xl font-bold text-white hover:text-blue-400 block mb-2">{rec.title}</Link>
                 <div className="flex justify-between items-center mb-4">
                   <span className="text-xs text-neutral-500">Score: {rec.score.toFixed(4)}</span>
                   <span className="text-xs px-2 py-1 bg-white/10 rounded text-neutral-300">Rank #{idx+1}</span>
                 </div>
                 {rec.evidence && (
                   <div className="bg-black/50 p-4 rounded-xl text-xs space-y-2 border border-white/5">
                     <div className="text-neutral-400 font-medium mb-1">Why this movie?</div>
                     {Object.entries(rec.evidence).map(([k, v]) => (
                       <div key={k} className="flex justify-between font-mono">
                         <span className="text-neutral-500">{k}:</span>
                         <span className="text-blue-400">{String(v)}</span>
                       </div>
                     ))}
                   </div>
                 )}
               </div>
             ))}
           </div>
        </div>
      )}
    </div>
  );
}
"""
write_file("frontend/src/pages/Recommendations.tsx", recommendations_tsx.strip())

print("Files generated successfully!")
