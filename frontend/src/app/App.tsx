import React from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import { RecommendationDashboard } from '../features/recommendations';

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-slate-950 font-sans text-slate-100">
        {/* Navigation Bar */}
        <nav className="border-b border-slate-800 bg-slate-900/80 backdrop-blur-md px-6 py-4 flex items-center justify-between sticky top-0 z-40">
          <div className="flex items-center gap-3">
            <span className="text-2xl">🎬</span>
            <span className="font-extrabold text-lg text-white tracking-wide">
              OTT Discovery Platform
            </span>
          </div>

          <div className="flex items-center gap-4 text-xs font-semibold">
            <Link
              to="/recommendations"
              className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-xl transition shadow-md shadow-indigo-600/30"
            >
              ⚡ Recommendation Engine (Member 2)
            </Link>
          </div>
        </nav>

        {/* Main Content Router */}
        <main>
          <Routes>
            <Route path="/" element={<RecommendationDashboard />} />
            <Route path="/recommendations" element={<RecommendationDashboard />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
