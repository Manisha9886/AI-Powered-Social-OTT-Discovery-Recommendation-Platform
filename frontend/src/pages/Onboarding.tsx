import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { preferenceService } from '../services/api';
import { Check, ArrowRight, ArrowLeft, Sparkles, Film, Clock, Calendar, Loader2 } from 'lucide-react';

const GENRE_OPTIONS = [
  'Action', 'Adventure', 'Animation', 'Comedy', 'Crime', 'Documentary',
  'Drama', 'Family', 'Fantasy', 'History', 'Horror', 'Music',
  'Mystery', 'Romance', 'Science Fiction', 'Thriller', 'War', 'Western'
];

const DURATION_OPTIONS = [
  { key: 'short', label: 'Short', desc: 'Under 90 minutes' },
  { key: 'medium', label: 'Medium', desc: '90–120 minutes' },
  { key: 'long', label: 'Long', desc: 'Over 120 minutes' },
  { key: 'any', label: 'Any Duration', desc: 'No preference' }
];

const YEAR_OPTIONS = [
  { key: 'new', label: 'New Releases', desc: '2024–2026' },
  { key: 'recent', label: 'Recent', desc: '2020–2023' },
  { key: '2010s', label: '2010–2019', desc: 'Modern favorites' },
  { key: '2000s', label: '2000–2009', desc: 'Turn of the century' },
  { key: 'classics', label: 'Classics', desc: 'Before 2000' },
  { key: 'any', label: 'Any Year', desc: 'No preference' }
];

export default function Onboarding() {
  const navigate = useNavigate();

  const [step, setStep] = useState(1);
  const [selectedGenres, setSelectedGenres] = useState<string[]>([]);
  const [selectedDurations, setSelectedDurations] = useState<string[]>([]);
  const [selectedYears, setSelectedYears] = useState<string[]>([]);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    // Pre-populate if user already has preferences
    preferenceService.getPreferences().then(res => {
      if (res.data) {
        if (res.data.genres) setSelectedGenres(res.data.genres);
        if (res.data.duration) setSelectedDurations(res.data.duration);
        if (res.data.release_year) setSelectedYears(res.data.release_year);
      }
    }).catch(() => {});
  }, []);

  const toggleGenre = (genre: string) => {
    setSelectedGenres(prev => 
      prev.includes(genre) ? prev.filter(g => g !== genre) : [...prev, genre]
    );
  };

  const toggleDuration = (key: string) => {
    if (key === 'any') {
      setSelectedDurations(['any']);
      return;
    }
    setSelectedDurations(prev => {
      const filtered = prev.filter(d => d !== 'any');
      return filtered.includes(key) ? filtered.filter(d => d !== key) : [...filtered, key];
    });
  };

  const toggleYear = (key: string) => {
    if (key === 'any') {
      setSelectedYears(['any']);
      return;
    }
    setSelectedYears(prev => {
      const filtered = prev.filter(y => y !== 'any');
      return filtered.includes(key) ? filtered.filter(y => y !== key) : [...filtered, key];
    });
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await preferenceService.savePreferences({
        genres: selectedGenres,
        duration: selectedDurations.length ? selectedDurations : ['any'],
        release_year: selectedYears.length ? selectedYears : ['any']
      });
      navigate('/recommendations');
    } catch (err) {
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-6 py-20 min-h-screen flex flex-col justify-center">
      {/* Progress Bar Indicator */}
      <div className="mb-12">
        <div className="flex items-center justify-between text-xs font-semibold text-neutral-400 uppercase tracking-widest mb-3">
          <span className={step >= 1 ? 'text-white' : ''}>1. Genres</span>
          <span className={step >= 2 ? 'text-white' : ''}>2. Duration</span>
          <span className={step >= 3 ? 'text-white' : ''}>3. Release Year</span>
          <span className={step >= 4 ? 'text-white' : ''}>4. Summary</span>
        </div>
        <div className="w-full bg-white/10 h-1.5 rounded-full overflow-hidden">
          <div 
            className="bg-netflix-red h-full transition-all duration-500"
            style={{ width: `${(step / 4) * 100}%` }}
          />
        </div>
      </div>

      {/* STEP 1: GENRES */}
      {step === 1 && (
        <div className="space-y-8 animate-fade-in">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-xs font-medium text-blue-400 mb-3">
              <Film className="w-3.5 h-3.5" /> Step 1 of 4
            </div>
            <h1 className="text-4xl md:text-5xl font-display font-bold text-white mb-2">What do you enjoy watching?</h1>
            <p className="text-neutral-400 text-base">Select the genres you love. You can choose multiple.</p>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
            {GENRE_OPTIONS.map(genre => {
              const selected = selectedGenres.includes(genre);
              return (
                <button
                  key={genre}
                  onClick={() => toggleGenre(genre)}
                  className={`p-4 rounded-xl text-left border font-medium text-sm transition-all duration-300 flex items-center justify-between ${
                    selected 
                      ? 'bg-netflix-red/20 border-netflix-red text-white shadow-lg scale-[1.02]' 
                      : 'bg-cinematic-surface border-cinematic-border text-neutral-300 hover:border-white/20'
                  }`}
                >
                  <span>{genre}</span>
                  {selected && <Check className="w-4 h-4 text-netflix-red" />}
                </button>
              );
            })}
          </div>

          <div className="flex justify-end pt-4">
            <button
              disabled={selectedGenres.length === 0}
              onClick={() => setStep(2)}
              className="px-8 py-3.5 bg-white text-black font-semibold rounded-full hover:bg-neutral-200 disabled:opacity-40 disabled:cursor-not-allowed transition-all flex items-center gap-2 shadow-lg"
            >
              Continue <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* STEP 2: DURATION */}
      {step === 2 && (
        <div className="space-y-8 animate-fade-in">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-xs font-medium text-blue-400 mb-3">
              <Clock className="w-3.5 h-3.5" /> Step 2 of 4
            </div>
            <h1 className="text-4xl md:text-5xl font-display font-bold text-white mb-2">How long do you like your movies?</h1>
            <p className="text-neutral-400 text-base">Choose preferred runtime ranges.</p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {DURATION_OPTIONS.map(opt => {
              const selected = selectedDurations.includes(opt.key);
              return (
                <button
                  key={opt.key}
                  onClick={() => toggleDuration(opt.key)}
                  className={`p-6 rounded-2xl text-left border transition-all duration-300 flex items-center justify-between ${
                    selected 
                      ? 'bg-netflix-red/20 border-netflix-red text-white shadow-lg scale-[1.02]' 
                      : 'bg-cinematic-surface border-cinematic-border text-neutral-300 hover:border-white/20'
                  }`}
                >
                  <div>
                    <h3 className="font-bold text-lg text-white mb-1">{opt.label}</h3>
                    <p className="text-xs text-neutral-400">{opt.desc}</p>
                  </div>
                  {selected && <Check className="w-5 h-5 text-netflix-red shrink-0" />}
                </button>
              );
            })}
          </div>

          <div className="flex justify-between pt-4">
            <button
              onClick={() => setStep(1)}
              className="px-6 py-3 bg-white/10 hover:bg-white/20 text-white font-medium rounded-full transition-all flex items-center gap-2"
            >
              <ArrowLeft className="w-4 h-4" /> Back
            </button>
            <button
              onClick={() => setStep(3)}
              className="px-8 py-3.5 bg-white text-black font-semibold rounded-full hover:bg-neutral-200 transition-all flex items-center gap-2 shadow-lg"
            >
              Continue <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* STEP 3: RELEASE YEAR */}
      {step === 3 && (
        <div className="space-y-8 animate-fade-in">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-xs font-medium text-blue-400 mb-3">
              <Calendar className="w-3.5 h-3.5" /> Step 3 of 4
            </div>
            <h1 className="text-4xl md:text-5xl font-display font-bold text-white mb-2">What era of movies do you prefer?</h1>
            <p className="text-neutral-400 text-base">Select your favorite movie eras.</p>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
            {YEAR_OPTIONS.map(opt => {
              const selected = selectedYears.includes(opt.key);
              return (
                <button
                  key={opt.key}
                  onClick={() => toggleYear(opt.key)}
                  className={`p-5 rounded-2xl text-left border transition-all duration-300 flex items-center justify-between ${
                    selected 
                      ? 'bg-netflix-red/20 border-netflix-red text-white shadow-lg scale-[1.02]' 
                      : 'bg-cinematic-surface border-cinematic-border text-neutral-300 hover:border-white/20'
                  }`}
                >
                  <div>
                    <h3 className="font-bold text-base text-white mb-1">{opt.label}</h3>
                    <p className="text-xs text-neutral-400">{opt.desc}</p>
                  </div>
                  {selected && <Check className="w-4 h-4 text-netflix-red shrink-0" />}
                </button>
              );
            })}
          </div>

          <div className="flex justify-between pt-4">
            <button
              onClick={() => setStep(2)}
              className="px-6 py-3 bg-white/10 hover:bg-white/20 text-white font-medium rounded-full transition-all flex items-center gap-2"
            >
              <ArrowLeft className="w-4 h-4" /> Back
            </button>
            <button
              onClick={() => setStep(4)}
              className="px-8 py-3.5 bg-white text-black font-semibold rounded-full hover:bg-neutral-200 transition-all flex items-center gap-2 shadow-lg"
            >
              Review Summary <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* STEP 4: SUMMARY */}
      {step === 4 && (
        <div className="space-y-8 animate-fade-in">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-xs font-medium text-emerald-400 mb-3">
              <Sparkles className="w-3.5 h-3.5" /> Step 4 of 4
            </div>
            <h1 className="text-4xl md:text-5xl font-display font-bold text-white mb-2">Your Movie Preferences</h1>
            <p className="text-neutral-400 text-base">Review your choices before discovering recommendations.</p>
          </div>

          <div className="bg-cinematic-surface border border-cinematic-border rounded-2xl p-6 md:p-8 space-y-6 shadow-xl">
            <div>
              <h3 className="text-xs font-semibold uppercase tracking-widest text-neutral-400 mb-3 flex items-center gap-2">
                <Film className="w-4 h-4 text-blue-400" /> Selected Genres
              </h3>
              <div className="flex flex-wrap gap-2">
                {selectedGenres.map(g => (
                  <span key={g} className="px-3 py-1 bg-netflix-red/20 border border-netflix-red/40 text-white text-xs font-medium rounded-full">
                    {g}
                  </span>
                ))}
              </div>
            </div>

            <div className="pt-4 border-t border-white/5">
              <h3 className="text-xs font-semibold uppercase tracking-widest text-neutral-400 mb-3 flex items-center gap-2">
                <Clock className="w-4 h-4 text-emerald-400" /> Duration Preference
              </h3>
              <div className="flex flex-wrap gap-2">
                {(selectedDurations.length ? selectedDurations : ['any']).map(d => (
                  <span key={d} className="px-3 py-1 bg-white/10 border border-white/15 text-white text-xs font-medium rounded-full capitalize">
                    {d}
                  </span>
                ))}
              </div>
            </div>

            <div className="pt-4 border-t border-white/5">
              <h3 className="text-xs font-semibold uppercase tracking-widest text-neutral-400 mb-3 flex items-center gap-2">
                <Calendar className="w-4 h-4 text-purple-400" /> Release Year Preference
              </h3>
              <div className="flex flex-wrap gap-2">
                {(selectedYears.length ? selectedYears : ['any']).map(y => (
                  <span key={y} className="px-3 py-1 bg-white/10 border border-white/15 text-white text-xs font-medium rounded-full capitalize">
                    {y}
                  </span>
                ))}
              </div>
            </div>
          </div>

          <div className="flex justify-between pt-4">
            <button
              onClick={() => setStep(3)}
              className="px-6 py-3 bg-white/10 hover:bg-white/20 text-white font-medium rounded-full transition-all flex items-center gap-2"
            >
              <ArrowLeft className="w-4 h-4" /> Back
            </button>
            <button
              onClick={handleSave}
              disabled={saving}
              className="px-8 py-3.5 bg-netflix-red hover:bg-red-700 text-white font-semibold rounded-full transition-all flex items-center gap-2 shadow-xl hover:scale-105"
            >
              {saving ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Save Preferences & Discover Movies'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
