export interface Movie {
  movie_id: number | string;
  title: string;
  release_year: number;
  overview?: string;
  genres: string[] | string | any;
  vote_average?: number;
  poster_path?: string;
}

export interface RecommendationEvidence {
  content_similarity?: number;
  collaborative_score?: number;
  popularity_score?: number;
  preference_match?: number;
  [key: string]: number | undefined; // Allow for dynamic evidence fields
}

export interface RecommendationItem {
  movie_id: number;
  title: string;
  final_score: number;
  evidence: RecommendationEvidence;
  reason_codes: string[];
  confidence: string;
}

export interface RecommendationResponse {
  user_id: number;
  recommendations: RecommendationItem[];
}