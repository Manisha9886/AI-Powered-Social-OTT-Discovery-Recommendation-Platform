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
  explainRecommendation: (movieId: number, query: string, evidence: any) => 
    api.post('/ai/explain', { movie_id: movieId, user_query: query, evidence }),
};

export const recommendationService = {
  getRecommendations: (userId: number = 101) => api.get(`/recommendations?user_id=${userId}`),
};