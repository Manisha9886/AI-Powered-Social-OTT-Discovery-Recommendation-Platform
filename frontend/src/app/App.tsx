import { BrowserRouter, Routes, Route } from 'react-router-dom';
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

          </Routes>
        </div>
      </div>
    </BrowserRouter>
  );
}