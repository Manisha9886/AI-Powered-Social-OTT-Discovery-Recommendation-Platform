import React from 'react';
import { RecommendationItem } from './types';

interface RecommendationCardProps {
  item: RecommendationItem;
  onSelectEvidence: (item: RecommendationItem) => void;
}

export const RecommendationCard: React.FC<RecommendationCardProps> = ({ item, onSelectEvidence }) => {
  const matchPercentage = Math.round((item.final_score || 0.5) * 100);

  return (
    <div className="group relative bg-slate-900/90 border border-slate-800 rounded-2xl overflow-hidden shadow-lg hover:shadow-2xl hover:border-indigo-500/50 transition-all duration-300 flex flex-col justify-between">
      {/* Top Banner Image / Fallback Header */}
      <div className="relative h-48 bg-gradient-to-br from-indigo-900/40 via-slate-800 to-purple-900/40 flex items-center justify-center p-4 overflow-hidden">
        {item.poster_path ? (
          <img
            src={item.poster_path}
            alt={item.title}
            className="absolute inset-0 w-full h-full object-cover group-hover:scale-105 transition-transform duration-500 opacity-80"
            onError={(e) => {
              (e.target as HTMLElement).style.display = 'none';
            }}
          />
        ) : null}
        
        {/* Dark overlay gradient */}
        <div className="absolute inset-0 bg-gradient-to-t from-slate-900 via-slate-900/40 to-transparent" />

        {/* Match Percentage Badge */}
        <div className="absolute top-3 right-3 bg-indigo-600/90 text-white font-extrabold text-xs px-3 py-1.5 rounded-full shadow-lg backdrop-blur-md border border-indigo-400/30 flex items-center gap-1">
          <span>✨</span>
          <span>{matchPercentage}% Match</span>
        </div>

        {/* Title overlay */}
        <div className="absolute bottom-3 left-4 right-4">
          <h3 className="text-lg font-bold text-white leading-snug drop-shadow-md truncate">
            {item.title}
          </h3>
          <div className="flex items-center gap-2 text-xs text-slate-300 mt-1 font-medium">
            {item.release_year ? <span>{item.release_year}</span> : null}
            {item.runtime ? <span>• {item.runtime} min</span> : null}
            {item.vote_average ? (
              <span className="text-amber-400 font-bold flex items-center gap-1">
                ★ {item.vote_average}
              </span>
            ) : null}
          </div>
        </div>
      </div>

      {/* Card Content Body */}
      <div className="p-4 flex-1 flex flex-col justify-between space-y-3">
        {/* Genres Pill Row */}
        <div className="flex flex-wrap gap-1.5">
          {item.genres?.slice(0, 3).map((genre, idx) => (
            <span
              key={idx}
              className="bg-slate-800 text-slate-300 text-[11px] px-2 py-0.5 rounded-md font-medium border border-slate-700"
            >
              {genre}
            </span>
          ))}
        </div>

        {/* Overview snippet */}
        {item.overview ? (
          <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed">
            {item.overview}
          </p>
        ) : null}

        {/* Reason Codes Badges */}
        <div className="flex flex-wrap gap-1">
          {item.reason_codes.slice(0, 2).map((code, idx) => (
            <span
              key={idx}
              className="bg-indigo-950/80 text-indigo-300 text-[10px] px-2 py-0.5 rounded font-semibold border border-indigo-800/40"
            >
              {code.replace(/_/g, ' ')}
            </span>
          ))}
        </div>

        {/* Action Button */}
        <button
          onClick={() => onSelectEvidence(item)}
          className="w-full mt-2 bg-slate-800 hover:bg-indigo-600 text-slate-200 hover:text-white text-xs font-semibold py-2 px-3 rounded-xl border border-slate-700 hover:border-indigo-500 transition-all duration-200 flex items-center justify-center gap-1.5 shadow-sm"
        >
          <span>🔍 View AI Evidence & Scores</span>
        </button>
      </div>
    </div>
  );
};
