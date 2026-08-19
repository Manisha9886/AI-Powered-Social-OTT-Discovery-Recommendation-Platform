import React from 'react';
import { RecommendationItem } from './types';

interface EvidenceModalProps {
  item: RecommendationItem | null;
  onClose: () => void;
}

export const EvidenceModal: React.FC<EvidenceModalProps> = ({ item, onClose }) => {
  if (!item) return null;

  const matchPercentage = Math.round((item.final_score || 0.5) * 100);
  const evidence = item.evidence;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4 animate-fadeIn">
      <div className="bg-slate-900 border border-slate-700 rounded-2xl max-w-lg w-full p-6 text-slate-100 shadow-2xl relative">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-400 hover:text-white text-xl font-bold p-1 transition"
          aria-label="Close modal"
        >
          ✕
        </button>

        <div className="flex items-center gap-3 mb-4">
          <span className="text-2xl">⚡</span>
          <div>
            <h3 className="text-xl font-bold text-white">{item.title}</h3>
            <p className="text-xs text-indigo-400 font-semibold tracking-wide uppercase">
              Recommendation Evidence Analysis
            </p>
          </div>
        </div>

        <div className="bg-slate-800/80 rounded-xl p-4 mb-5 flex items-center justify-between border border-slate-700">
          <div>
            <p className="text-xs text-slate-400 font-medium">Overall Match Score</p>
            <p className="text-3xl font-extrabold text-indigo-400">{matchPercentage}%</p>
          </div>
          <div className="text-right">
            <p className="text-xs text-slate-400 font-medium">Algorithm Confidence</p>
            <span
              className={`inline-block px-3 py-1 text-xs font-bold rounded-full uppercase ${
                item.confidence === 'high'
                  ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40'
                  : 'bg-amber-500/20 text-amber-400 border border-amber-500/40'
              }`}
            >
              {item.confidence || 'High'} Confidence
            </span>
          </div>
        </div>

        <div className="space-y-3 mb-6">
          <h4 className="text-sm font-semibold text-slate-300">Model Component Scores</h4>

          <div>
            <div className="flex justify-between text-xs font-medium mb-1">
              <span className="text-slate-400">Content-Based Similarity (Genres/Overview/Embeddings)</span>
              <span className="text-indigo-300 font-bold">
                {Math.round((item.content_score || 0) * 100)}%
              </span>
            </div>
            <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
              <div
                className="bg-indigo-500 h-2 rounded-full transition-all duration-500"
                style={{ width: `${Math.min(100, Math.round((item.content_score || 0) * 100))}%` }}
              />
            </div>
          </div>

          <div>
            <div className="flex justify-between text-xs font-medium mb-1">
              <span className="text-slate-400">Collaborative Filtering (Similar User Ratings)</span>
              <span className="text-purple-300 font-bold">
                {Math.round((item.collaborative_score || 0) * 100)}%
              </span>
            </div>
            <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
              <div
                className="bg-purple-500 h-2 rounded-full transition-all duration-500"
                style={{ width: `${Math.min(100, Math.round((item.collaborative_score || 0) * 100))}%` }}
              />
            </div>
          </div>

          <div>
            <div className="flex justify-between text-xs font-medium mb-1">
              <span className="text-slate-400">Popularity & Rating Trends</span>
              <span className="text-cyan-300 font-bold">
                {Math.round((item.popularity_score || 0) * 100)}%
              </span>
            </div>
            <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
              <div
                className="bg-cyan-500 h-2 rounded-full transition-all duration-500"
                style={{ width: `${Math.min(100, Math.round((item.popularity_score || 0) * 100))}%` }}
              />
            </div>
          </div>
        </div>

        <div className="mb-6">
          <h4 className="text-sm font-semibold text-slate-300 mb-2">Primary Reason Codes</h4>
          <div className="flex flex-wrap gap-2">
            {item.reason_codes.map((code, idx) => (
              <span
                key={idx}
                className="bg-indigo-950 text-indigo-300 border border-indigo-700/50 px-2.5 py-1 text-xs rounded-lg font-medium"
              >
                #{code.replace(/_/g, ' ')}
              </span>
            ))}
          </div>
        </div>

        <div className="flex justify-end">
          <button
            onClick={onClose}
            className="bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold px-5 py-2 rounded-xl transition shadow-md"
          >
            Close Analysis
          </button>
        </div>
      </div>
    </div>
  );
};
