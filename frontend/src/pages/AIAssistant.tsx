import { useState, useRef, useEffect } from 'react';
import { aiService } from '../services/api';
import { Sparkles, Send, Bot, User, Loader2 } from 'lucide-react';

export default function AIAssistant() {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const endOfMessagesRef = useRef<HTMLDivElement>(null);

  const handleSubmit = async (e?: React.FormEvent) => {
    e?.preventDefault();
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

  useEffect(() => {
    if (response || loading) {
      endOfMessagesRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [response, loading]);

  const handleChipClick = (q: string) => {
    setQuery(q);
    // Note: To automatically submit on chip click, we'd wrap this in a setTimeout or use an effect, 
    // but giving the user a chance to review the query before sending is also good UX.
  };

  return (
    <div className="max-w-4xl mx-auto px-6 pt-32 pb-12 min-h-screen flex flex-col">
      <div className="mb-8 space-y-3 text-center">
        <h1 className="text-4xl md:text-5xl font-display font-bold text-white flex items-center justify-center gap-3">
          <Sparkles className="w-8 h-8 text-blue-500" /> AI Assistant
        </h1>
        <p className="text-neutral-400 text-lg">Grounded in the movie knowledge base.</p>
      </div>

      <div className="flex-1 bg-cinematic-surface border border-cinematic-border rounded-3xl overflow-hidden shadow-2xl flex flex-col relative">
        <div className="absolute inset-0 bg-gradient-to-b from-blue-900/5 to-transparent pointer-events-none" />
        
        <div className="flex-1 p-6 md:p-8 overflow-y-auto flex flex-col justify-end space-y-8 relative z-10 scrollbar-hide">
          {response || loading ? (
            <div className="space-y-8">
              {/* User Message */}
              <div className="flex justify-end animate-fade-in">
                <div className="flex gap-4 max-w-[85%] md:max-w-[75%] flex-row-reverse">
                  <div className="w-10 h-10 rounded-full bg-white/10 text-white flex items-center justify-center shrink-0 border border-white/5 shadow-sm">
                    <User className="w-5 h-5" />
                  </div>
                  <div className="bg-cinematic-base text-white px-6 py-4 rounded-3xl rounded-tr-sm border border-white/5 shadow-md">
                    <div className="text-lg font-light leading-relaxed">{query}</div>
                  </div>
                </div>
              </div>

              {/* AI Message */}
              <div className="flex animate-fade-in" style={{ animationDelay: '150ms' }}>
                <div className="flex gap-4 max-w-[95%] md:max-w-[85%]">
                  <div className="w-10 h-10 rounded-full bg-blue-600/20 text-blue-400 flex items-center justify-center shrink-0 border border-blue-500/20 shadow-sm relative">
                    <Bot className="w-5 h-5" />
                    {loading && (
                      <span className="absolute -top-1 -right-1 w-3 h-3 bg-blue-500 rounded-full animate-ping" />
                    )}
                  </div>
                  <div className="bg-blue-900/10 text-white px-6 py-5 rounded-3xl rounded-tl-sm border border-blue-500/10 shadow-md">
                    {loading ? (
                      <div className="flex items-center gap-3 text-neutral-400 h-6">
                        <Loader2 className="w-4 h-4 animate-spin text-blue-500" />
                        <span className="text-sm tracking-wide">Searching knowledge base...</span>
                      </div>
                    ) : (
                      <div className="prose prose-invert max-w-none prose-p:leading-relaxed prose-headings:font-display">
                        {/* 
                          Since the prompt format asks the AI NOT to use markdown asterisks and bullet points,
                          we just render the raw text. If it contains newlines, they will be preserved by whitespace-pre-wrap.
                        */}
                        <div className="whitespace-pre-wrap leading-loose font-light text-neutral-200">
                          {response}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center flex flex-col items-center justify-center h-full animate-fade-in">
              <div className="w-20 h-20 bg-blue-500/10 rounded-full flex items-center justify-center mb-6">
                <Sparkles className="w-10 h-10 text-blue-500 opacity-80" />
              </div>
              <h2 className="text-2xl font-display font-medium text-white mb-2">What are you in the mood for?</h2>
              <p className="text-neutral-400 mb-8 max-w-sm">I can find movies based on extremely specific scenarios, moods, and concepts.</p>
              
              <div className="flex flex-wrap justify-center gap-3 max-w-2xl">
                {[
                  "Recommend dark sci-fi movies", 
                  "Something like Interstellar but darker", 
                  "Find a psychological thriller",
                  "A funny movie for tonight"
                ].map(q => (
                  <button 
                    key={q} 
                    onClick={() => handleChipClick(q)} 
                    className="px-5 py-2.5 bg-cinematic-base rounded-full text-sm font-medium text-neutral-300 hover:text-white hover:bg-white/10 border border-white/5 transition-all hover:scale-105 active:scale-95"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          )}
          <div ref={endOfMessagesRef} />
        </div>

        {/* Composer */}
        <div className="p-4 md:p-6 bg-cinematic-surface border-t border-cinematic-border relative z-10">
          <form onSubmit={handleSubmit} className="relative max-w-3xl mx-auto group">
            <input 
              type="text" 
              value={query}
              onChange={e => setQuery(e.target.value)}
              placeholder="Ask anything..."
              className="w-full bg-cinematic-base border border-white/10 rounded-full py-4 pl-6 pr-16 text-white text-lg focus:outline-none focus:border-blue-500/50 focus:bg-white/5 transition-all placeholder:text-neutral-600 shadow-inner"
            />
            <button 
              type="submit" 
              disabled={loading || !query.trim()} 
              className="absolute right-2 top-1/2 -translate-y-1/2 w-11 h-11 flex items-center justify-center bg-white text-black rounded-full hover:bg-neutral-200 transition-colors disabled:opacity-50 disabled:bg-neutral-700 disabled:text-neutral-500"
            >
              <Send className="w-5 h-5 ml-0.5" />
            </button>
          </form>
          <div className="text-center mt-3">
             <span className="text-[10px] text-neutral-500 uppercase tracking-widest font-semibold">Powered by Hybrid Retrieval & Llama 3.1</span>
          </div>
        </div>
      </div>
    </div>
  );
}