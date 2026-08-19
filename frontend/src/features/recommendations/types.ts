export interface RecommendationEvidence {
  content_similarity: number;
  collaborative_score: number;
  popularity_score: number;
  preference_match: number;
  runtime_constraint_satisfied: boolean;
}

export interface RecommendationItem {
  movie_id: number;
  title: string;
  final_score: number;
  content_score: number;
  collaborative_score: number;
  popularity_score: number;
  genres: string[];
  poster_path?: string | null;
  vote_average: number;
  release_year?: number | null;
  runtime?: number | null;
  overview?: string;
  reason_codes: string[];
  confidence: 'high' | 'medium' | 'low' | string;
  evidence?: RecommendationEvidence | null;
}

export interface RecommendationFilters {
  genres?: string[];
  max_runtime?: number;
  min_vote_average?: number;
  strategy?: 'hybrid' | 'popularity' | 'content_based' | 'collaborative';
}

export interface RecommendationResponse {
  user_id: number;
  recommendations: RecommendationItem[];
  strategy_used: string;
  total_count: number;
}
