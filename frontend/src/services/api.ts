import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL 
  ? `${import.meta.env.VITE_API_URL}/api/v1` 
  : (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1');

export const api = axios.create({
  baseURL: API_BASE,
});

// Interceptor to attach JWT token if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const movieService = {
  getMovies: (page = 1, pageSize = 24) => api.get(`/movies?page=${page}&page_size=${pageSize}`),
  getMovie: (id: string | number) => api.get(`/movies/${id}`),
  getOverview: (id: string | number) => api.get(`/movies/${id}/overview`),
};

export const preferenceService = {
  getPreferences: () => api.get('/preferences/me'),
  savePreferences: (data: { genres: string[]; duration: string[]; release_year: string[] }) => 
    api.post('/preferences/me', data),
};

export const aiService = {
  recommend: (query: string) => api.post('/ai/recommend', { query }),
  explainRecommendation: (movieId: number, query: string, evidence: any) => 
    api.post('/ai/explain', { movie_id: movieId, user_query: query, evidence }),
  understandQuery: (query: string) => api.post('/ai/understand', { query }),
};

export const recommendationService = {
  getRecommendations: (userId: number = 101) => api.get(`/recommendations?user_id=${userId}`),
};

export const authService = {
  signup: (data: any) => api.post('/auth/signup', data),
  login: (data: any) => api.post('/auth/login', data),
  getMe: () => api.get('/auth/me'),
};

export const watchlistService = {
  getWatchlist: () => api.get('/watchlist'),
  addToWatchlist: (movieId: number, status = 'plan_to_watch') => 
    api.post('/watchlist', { movie_id: movieId, status }),
  removeFromWatchlist: (movieId: number) => api.delete(`/watchlist/${movieId}`),
};

export const ratingService = {
  getRatings: () => api.get('/ratings'),
  rateMovie: (movieId: number, rating: number, review?: string) => 
    api.post('/ratings', { movie_id: movieId, rating, review }),
};