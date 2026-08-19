import React, { useState, useEffect } from 'react';
import { RecommendationItem, RecommendationResponse } from './types';
import { RecommendationCard } from './RecommendationCard';
import { EvidenceModal } from './EvidenceModal';
import axios from 'axios';

export const RecommendationDashboard: React.FC = () => {
  const [recommendations, setRecommendations] = useState<RecommendationItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [strategy, setStrategy] = useState<'hybrid' | 'popularity' | 'content_based' | 'collaborative'>('hybrid');
  const [selectedGenre, setSelectedGenre] = useState<string>('All');
  const [selectedItem, setSelectedItem] = useState<RecommendationItem | null>(null);

  const availableGenres = ['All', 'Action', 'Science Fiction', 'Adventure', 'Drama', 'Comedy', 'Thriller', 'Fantasy'];

  const fetchRecommendations = async () => {
    setLoading(true);
    try {
      // Call FastAPI backend endpoint
      const params: any = { strategy, top_n: 12 };
      if (selectedGenre !== 'All') {
        params.genres = selectedGenre;
      }

      const response = await axios.get<RecommendationResponse>('/api/v1/recommendations/', { params });
      if (response.data && response.data.recommendations) {
        setRecommendations(response.data.recommendations);
      }
    } catch (err) {
      console.warn('Backend unavailable, rendering sample fallback data:', err);
      // Fallback mock recommendations
      setRecommendations(getMockFallbackItems(strategy, selectedGenre));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecommendations();
  }, [strategy, selectedGenre]);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6">
      {/* Header Banner */}
      <div className="max-w-7xl mx-mx-auto mb-8 bg-gradient-to-r from-indigo-950 via-slate-900 to-purple-950 border border-slate-800 rounded-3xl p-8 shadow-2xl relative overflow-hidden">
        <div className="relative z-10">
          <div className="inline-block bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 px-3.5 py-1 rounded-full text-xs font-bold uppercase tracking-wider mb-3">
            Team Member 2 — Recommendation Intelligence
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
            Hybrid Recommendation Engine
          </h1>
          <p className="text-slate-400 text-sm max-w-2xl mt-2 leading-relaxed">
            Multi-model candidate generation combining Bayesian Popularity, TF-IDF / Embedding Content similarity, and SVD Collaborative filtering with explainability evidence metrics.
          </p>
        </div>
      </div>

      {/* Filter Controls Bar */}
      <div className="max-w-7xl mx-auto mb-8 space-y-4">
        {/* Strategy Selector Tabs */}
        <div className="flex flex-wrap items-center gap-2 bg-slate-900/80 p-2 rounded-2xl border border-slate-800">
          <span className="text-xs text-slate-400 font-semibold px-3 uppercase tracking-wider">
            Algorithm Strategy:
          </span>
          {[
            { id: 'hybrid', label: '⚡ Hybrid Ranking Engine' },
            { id: 'popularity', label: '🔥 Popularity & Trends' },
            { id: 'content_based', label: '🎯 Content Similarity' },
            { id: 'collaborative', label: '👥 Collaborative Filtering' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setStrategy(tab.id as any)}
              className={`text-xs font-semibold px-4 py-2 rounded-xl transition-all duration-200 ${
                strategy === tab.id
                  ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/30'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Genre Filter Chips */}
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs text-slate-400 font-semibold px-1 uppercase tracking-wider">
            Genre Filter:
          </span>
          {availableGenres.map((genre) => (
            <button
              key={genre}
              onClick={() => setSelectedGenre(genre)}
              className={`text-xs font-medium px-3.5 py-1.5 rounded-full border transition-all duration-200 ${
                selectedGenre === genre
                  ? 'bg-purple-600/30 text-purple-300 border-purple-500 font-bold'
                  : 'bg-slate-900/60 text-slate-400 border-slate-800 hover:border-slate-700 hover:text-slate-200'
              }`}
            >
              {genre}
            </button>
          ))}
        </div>
      </div>

      {/* Recommendations Cards Grid */}
      <div className="max-w-7xl mx-auto">
        {loading ? (
          <div className="flex flex-col items-center justify-center py-20 text-slate-400 space-y-3">
            <div className="w-10 h-10 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin" />
            <p className="text-sm font-medium">Computing hybrid candidate recommendations...</p>
          </div>
        ) : recommendations.length === 0 ? (
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-12 text-center text-slate-400">
            <p className="text-lg font-bold text-slate-300">No movies match the selected filter criteria.</p>
            <p className="text-xs mt-1">Try switching algorithm strategies or selecting a different genre.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            {recommendations.map((item) => (
              <RecommendationCard
                key={item.movie_id}
                item={item}
                onSelectEvidence={(selected) => setSelectedItem(selected)}
              />
            ))}
          </div>
        )}
      </div>

      {/* Explainability Evidence Modal */}
      <EvidenceModal item={selectedItem} onClose={() => setSelectedItem(null)} />
    </div>
  );
};

// Fallback Mock Items Generator
function getMockFallbackItems(strategy: string, genre: string): RecommendationItem[] {
  const baseItems: RecommendationItem[] = [
    {
      movie_id: 19995,
      title: 'Avatar',
      final_score: 0.94,
      content_score: 0.92,
      collaborative_score: 0.88,
      popularity_score: 0.96,
      genres: ['Action', 'Adventure', 'Science Fiction'],
      vote_average: 7.2,
      release_year: 2009,
      runtime: 162,
      overview: 'In the 22nd century, a paraplegic Marine is dispatched to the moon Pandora on a unique mission...',
      reason_codes: ['GENRE_MATCH', 'SIMILAR_TO_LIKED_MOVIES', 'POPULAR_TRENDING'],
      confidence: 'high',
      evidence: {
        content_similarity: 0.92,
        collaborative_score: 0.88,
        popularity_score: 0.96,
        preference_match: 0.94,
        runtime_constraint_satisfied: true,
      },
    },
    {
      movie_id: 49026,
      title: 'The Dark Knight Rises',
      final_score: 0.91,
      content_score: 0.89,
      collaborative_score: 0.92,
      popularity_score: 0.90,
      genres: ['Action', 'Crime', 'Drama'],
      vote_average: 7.6,
      release_year: 2012,
      runtime: 165,
      overview: 'Following the death of District Attorney Harvey Dent, Batman assumes responsibility for Dent\'s crimes...',
      reason_codes: ['HIGHLY_RATED_BY_SIMILAR_USERS', 'GENRE_MATCH'],
      confidence: 'high',
      evidence: {
        content_similarity: 0.89,
        collaborative_score: 0.92,
        popularity_score: 0.90,
        preference_match: 0.91,
        runtime_constraint_satisfied: true,
      },
    },
    {
      movie_id: 285,
      title: "Pirates of the Caribbean: At World's End",
      final_score: 0.87,
      content_score: 0.86,
      collaborative_score: 0.84,
      popularity_score: 0.88,
      genres: ['Adventure', 'Fantasy', 'Action'],
      vote_average: 6.9,
      release_year: 2007,
      runtime: 169,
      overview: 'Captain Barbossa, long believed to be dead, has come back to life and is headed to the edge of the Earth...',
      reason_codes: ['GENRE_MATCH', 'TOP_RECOMMENDED'],
      confidence: 'high',
      evidence: {
        content_similarity: 0.86,
        collaborative_score: 0.84,
        popularity_score: 0.88,
        preference_match: 0.87,
        runtime_constraint_satisfied: true,
      },
    },
    {
      movie_id: 206647,
      title: 'Spectre',
      final_score: 0.82,
      content_score: 0.80,
      collaborative_score: 0.79,
      popularity_score: 0.85,
      genres: ['Action', 'Adventure', 'Crime'],
      vote_average: 6.3,
      release_year: 2015,
      runtime: 148,
      overview: 'A cryptic message from Bond’s past sends him on a trail to uncover a sinister organization...',
      reason_codes: ['POPULAR_TRENDING'],
      confidence: 'medium',
      evidence: {
        content_similarity: 0.80,
        collaborative_score: 0.79,
        popularity_score: 0.85,
        preference_match: 0.82,
        runtime_constraint_satisfied: true,
      },
    },
  ];

  if (genre !== 'All') {
    return baseItems.filter((i) => i.genres.includes(genre));
  }
  return baseItems;
}
