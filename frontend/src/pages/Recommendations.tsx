import { useState, useEffect } from 'react';
import { recommendationService, movieService, aiService } from '../services/api';
import { Link } from 'react-router-dom';
import { RecommendationItem, Movie } from '../types';
import { Star, ChevronDown, ChevronUp, AlertCircle, Film, Sparkles, Loader2 } from 'lucide-react';

export default function Recommendations() {
  const [recommendations, setRecommendations] = useState<RecommendationItem[]>([]);
  const [metadata, setMetadata] = useState<Record<number, Movie>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedId, setExpandedId] = useState<number | null>(null);
  
  // AI Explanation State
  const [explanations, setExplanations] = useState<Record<number, string>>({});
  const [isExplaining, setIsExplaining] = useState<Record<number, boolean>>({});
  const [explanationErrors, setExplanationErrors] = useState<Record<number, string>>({});

  const fetchRecommendations = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await recommendationService.getRecommendations(101);
      const recs: RecommendationItem[] = res.data.recommendations || [];
      setRecommendations(recs);

      if (recs.length === 0) {
        setLoading(false);
        return;
      }

      const metadataPromises = recs.map(rec => movieService.getMovie(rec.movie_id.toString()));
      const results = await Promise.allSettled(metadataPromises);

      const newMetadata: Record<number, Movie> = {};
      results.forEach((result, idx) => {
        if (result.status === 'fulfilled' && result.value.data) {
          newMetadata[recs[idx].movie_id] = result.value.data;
        }
      });
      setMetadata(newMetadata);
    } catch (err) {
      console.error(err);
      setError("Unable to load recommendations.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecommendations();
  }, []);

  const toggleEvidence = (id: number) => {
    setExpandedId(expandedId === id ? null : id);
  };
  
  const generateExplanation = async (rec: RecommendationItem) => {
    // Prevent duplicate calls if already generated or currently loading
    if (explanations[rec.movie_id] || isExplaining[rec.movie_id]) return;

    setIsExplaining(prev => ({ ...prev, [rec.movie_id]: true }));
    setExplanationErrors(prev => ({ ...prev, [rec.movie_id]: "" }));
    
    try {
      // Pass the user's intent if available in the global context, here using empty string for generic context
      const res = await aiService.explainRecommendation(rec.movie_id, "", rec.evidence);
      setExplanations(prev => ({ ...prev, [rec.movie_id]: res.data.explanation }));
    } catch (err) {
      console.error(err);
      setExplanationErrors(prev => ({ ...prev, [rec.movie_id]: "AI explanation temporarily unavailable." }));
    } finally {
      setIsExplaining(prev => ({ ...prev, [rec.movie_id]: false }));
    }
  };

    if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-6 pt-32 pb-12 min-h-screen">
        <div className="mb-12">
          <h1 className="text-4xl md:text-5xl font-display font-bold text-white mb-3">Your Recommendations</h1>
          <p className="text-neutral-400 text-lg">Finding your next favorites...</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {[1, 2, 3, 4, 5, 6].map(i => (
            <div key={i} className="animate-pulse flex flex-col space-y-4">
              <div className="bg-cinematic-surface rounded-xl h-64 w-full border border-white/5"></div>
              <div className="bg-cinematic-surface rounded h-6 w-3/4"></div>
              <div className="bg-cinematic-surface rounded h-4 w-1/2"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-6 py-20 flex flex-col items-center justify-center text-center">
        <AlertCircle className="w-16 h-16 text-red-500 mb-6" />
        <h2 className="text-2xl font-bold text-white mb-4">{error}</h2>
        <button 
          onClick={fetchRecommendations}
          className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors font-medium"
        >
          Retry
        </button>
      </div>
    );
  }

  if (recommendations.length === 0) {
    return (
      <div className="max-w-7xl mx-auto px-6 py-20 flex flex-col items-center justify-center text-center">
        <Film className="w-16 h-16 text-neutral-600 mb-6" />
        <h2 className="text-2xl font-bold text-white mb-4">No recommendations available yet.</h2>
        <p className="text-neutral-400 mb-8 max-w-md">We need a bit more data to personalize your experience.</p>
        <div className="flex gap-4">
          <Link to="/movies" className="px-6 py-3 bg-white/10 hover:bg-white/20 text-white rounded-lg transition-colors font-medium">
            Explore Movies
          </Link>
          <Link to="/ai" className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors font-medium">
            Try AI Assistant
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-6 pt-32 pb-12 min-h-screen">
      <div className="mb-12">
        <h1 className="text-4xl md:text-5xl font-display font-bold text-white mb-3">Your Recommendations</h1>
        <p className="text-neutral-400 text-lg">Personalized picks powered by our hybrid recommendation engine.</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">
        {recommendations.map((rec) => {
          const meta = metadata[rec.movie_id] || (rec as any);
          const hasEvidence = rec.evidence && Object.keys(rec.evidence).length > 0;
          const getRecPoster = () => {
            const p = (rec as any).poster_path || meta?.poster_path;
            if (p && (p.startsWith('http') || p.startsWith('/'))) {
              return p.startsWith('http') ? p : `https://image.tmdb.org/t/p/w500${p}`;
            }
            const gArr = (rec as any).genres || meta?.genres;
            const g = gArr ? (Array.isArray(gArr) ? gArr.join(' ') : String(gArr)) : '';
            if (g.toLowerCase().includes('action') || g.toLowerCase().includes('adventure')) {
              return 'https://images.unsplash.com/photo-1536440136628-849c177e76a1?w=500&auto=format&fit=crop';
            } else if (g.toLowerCase().includes('sci-fi') || g.toLowerCase().includes('fantasy')) {
              return 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=500&auto=format&fit=crop';
            } else if (g.toLowerCase().includes('animation') || g.toLowerCase().includes('family')) {
              return 'https://images.unsplash.com/photo-1534447677768-be436bb09401?w=500&auto=format&fit=crop';
            } else if (g.toLowerCase().includes('horror') || g.toLowerCase().includes('thriller')) {
              return 'https://images.unsplash.com/photo-1509198397868-475647b2a1e5?w=500&auto=format&fit=crop';
            }
            return 'https://images.unsplash.com/photo-1485846234645-a62644f84728?w=500&auto=format&fit=crop';
          };
          
          const posterUrl = getRecPoster();
          const releaseYear = (rec as any).release_year || meta?.release_year;
          const genreList = (rec as any).genres || meta?.genres || [];
          const voteAvg = (rec as any).vote_average || meta?.vote_average;
          const scoreVal = rec.score !== undefined ? rec.score : (rec.final_score !== undefined ? rec.final_score : 0.85);

          return (
            <div key={rec.movie_id} className="group relative flex flex-col bg-cinematic-surface border border-cinematic-border rounded-2xl overflow-hidden hover:border-white/20 transition-all duration-300 shadow-xl hover:-translate-y-1 hover:shadow-2xl">
              
              {/* Cinematic Poster */}
              <Link to={`/movies/${rec.movie_id}`} className="relative h-64 w-full bg-gradient-to-br from-neutral-800 to-black overflow-hidden flex flex-col items-center justify-center text-center p-4">
                <img src={posterUrl} alt={rec.title} className="absolute inset-0 w-full h-full object-cover opacity-80 group-hover:opacity-100 transition-opacity" />
                
                {/* Score Badge */}
                <div className="absolute top-4 right-4 z-20 bg-black/60 backdrop-blur-md px-3 py-1 rounded-full border border-white/10 flex items-center space-x-1">
                  <Star className="w-3 h-3 text-yellow-500 fill-yellow-500" />
                  <span className="text-xs font-bold text-white">{(scoreVal * 100).toFixed(0)}%</span>
                </div>
              </Link>
              
              <div className="p-5 flex flex-col flex-grow">
                <Link to={`/movies/${rec.movie_id}`} className="text-xl font-bold text-white hover:text-blue-400 mb-1 line-clamp-1">
                  {rec.title}
                </Link>
                
                {/* Metadata Row */}
                <div className="flex items-center space-x-3 text-xs text-neutral-400 mb-4 font-medium">
                  {releaseYear && <span>{releaseYear}</span>}
                  {releaseYear && genreList.length > 0 && <span>•</span>}
                  {genreList.length > 0 && <span className="truncate">{Array.isArray(genreList) ? genreList[0] : genreList}</span>}
                  {voteAvg ? (
                    <>
                      <span>•</span>
                      <span className="flex items-center text-neutral-300">
                        {Number(voteAvg).toFixed(1)}/10
                      </span>
                    </>
                  ) : null}
                </div>

                <div className="mt-auto">
                  {hasEvidence && (
                    <button 
                      onClick={() => toggleEvidence(rec.movie_id)}
                      className="w-full flex items-center justify-between px-4 py-2 bg-white/5 hover:bg-white/10 border border-white/5 rounded-lg text-xs font-medium text-neutral-300 transition-colors"
                    >
                      <span>Why this movie?</span>
                      {expandedId === rec.movie_id ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                    </button>
                  )}
                  
                  {/* Expandable Evidence Section */}
                  {expandedId === rec.movie_id && hasEvidence && (
                    <div className="mt-2 p-4 bg-black/50 border border-white/5 rounded-lg text-xs space-y-3">
                      
                      {/* Mathematical Evidence */}
                      <div className="space-y-3">
                        <div className="text-neutral-500 uppercase tracking-wider text-[10px] font-bold">Mathematical Evidence</div>
                        {Object.entries(rec.evidence).map(([key, value]) => {
                          if (value === undefined || value === null) return null;
                          const score = typeof value === 'number' ? value : parseFloat(value);
                          if (isNaN(score)) return null;
                          
                          // Convert raw score to a visually meaningful progress bar width (assuming 0-1 range roughly, capped at 1)
                          const width = Math.min(100, Math.max(0, score * 100));
                          
                          return (
                            <div key={key} className="space-y-1">
                              <div className="flex justify-between items-center">
                                <span className="text-neutral-400 capitalize">{key.replace(/_/g, ' ')}</span>
                                <span className="text-white font-mono text-[10px]">{score.toFixed(3)}</span>
                              </div>
                              <div className="h-1.5 w-full bg-black rounded-full overflow-hidden">
                                <div 
                                  className="h-full bg-blue-500 rounded-full" 
                                  style={{ width: `${width}%` }}
                                />
                              </div>
                            </div>
                          );
                        })}
                      </div>
                      
                      {/* Reason Codes */}
                      {rec.reason_codes && rec.reason_codes.length > 0 && (
                        <div className="space-y-1 pt-2 border-t border-white/10">
                          <div className="text-neutral-500 uppercase tracking-wider text-[10px] font-bold mb-1">Reason Codes</div>
                          <div className="flex flex-wrap gap-1">
                            {rec.reason_codes.map(code => (
                              <span key={code} className="px-2 py-0.5 bg-blue-900/30 text-blue-300 rounded text-[10px]">
                                {code}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                      
                      <div className="border-t border-white/10 my-3" />
                      
                      {/* Explainable AI Button / Result */}
                      {!explanations[rec.movie_id] && !isExplaining[rec.movie_id] && (
                        <button
                          onClick={() => generateExplanation(rec)}
                          className="w-full flex items-center justify-center space-x-2 px-3 py-2.5 bg-netflix-red/10 hover:bg-netflix-red/20 text-netflix-red border border-netflix-red/20 rounded-lg transition-colors mt-4"
                        >
                          <Sparkles className="w-3.5 h-3.5" />
                          <span className="font-medium text-[11px] uppercase tracking-wider">Explain This Recommendation</span>
                        </button>
                      )}
                      
                      {isExplaining[rec.movie_id] && (
                        <div className="w-full flex items-center justify-center space-x-2 px-3 py-2.5 bg-cinematic-surface text-neutral-400 border border-white/5 rounded-lg mt-4">
                          <Loader2 className="w-3.5 h-3.5 animate-spin text-netflix-red" />
                          <span className="font-medium text-[11px] uppercase tracking-wider">Generating explanation...</span>
                        </div>
                      )}
                      
                      {explanationErrors[rec.movie_id] && (
                        <div className="mt-4 space-y-2">
                           <div className="text-red-400 text-[11px] text-center">{explanationErrors[rec.movie_id]}</div>
                           <button
                             onClick={() => generateExplanation(rec)}
                             className="w-full flex items-center justify-center px-3 py-1.5 bg-white/5 hover:bg-white/10 text-neutral-300 rounded-lg transition-colors text-[11px]"
                           >
                             Try Again
                           </button>
                        </div>
                      )}
                      
                      {explanations[rec.movie_id] && (
                        <div className="mt-4 p-4 bg-cinematic-base border border-blue-500/20 rounded-xl relative overflow-hidden shadow-inner">
                          <div className="absolute top-0 left-0 w-1 h-full bg-gradient-to-b from-blue-400 to-blue-600" />
                          <div className="flex items-center space-x-1.5 mb-3">
                            <Sparkles className="w-4 h-4 text-blue-400" />
                            <span className="text-blue-400 text-[10px] font-bold uppercase tracking-wider">AI EXPLANATION</span>
                          </div>
                          <p className="text-neutral-300 text-xs leading-relaxed font-light">
                            {explanations[rec.movie_id]}
                          </p>
                          <div className="mt-3 pt-3 border-t border-white/5 flex flex-col gap-1">
                             <span className="text-[9px] text-neutral-500 uppercase tracking-widest">Grounded in verified movie context</span>
                             <span className="text-[9px] text-neutral-500 uppercase tracking-widest">Powered by Llama 3.1 RAG</span>
                          </div>
                        </div>
                      )}

                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}