import numpy as np
from typing import List, Set, Dict, Any


def precision_at_k(recommended: List[int], relevant: Set[int], k: int) -> float:
    """Compute Precision@K."""
    if not recommended or k <= 0:
        return 0.0
    rec_k = recommended[:k]
    hits = sum(1 for item in rec_k if item in relevant)
    return hits / float(k)


def recall_at_k(recommended: List[int], relevant: Set[int], k: int) -> float:
    """Compute Recall@K."""
    if not relevant or k <= 0:
        return 0.0
    rec_k = recommended[:k]
    hits = sum(1 for item in rec_k if item in relevant)
    return hits / float(len(relevant))


def average_precision(recommended: List[int], relevant: Set[int], k: int) -> float:
    """Compute Average Precision at K (AP@K)."""
    if not recommended or not relevant or k <= 0:
        return 0.0

    rec_k = recommended[:k]
    score = 0.0
    num_hits = 0.0

    for i, item in enumerate(rec_k):
        if item in relevant:
            num_hits += 1.0
            score += num_hits / (i + 1.0)

    return score / min(len(relevant), k)


def mean_average_precision(
    user_recommendations: Dict[int, List[int]],
    user_relevance: Dict[int, Set[int]],
    k: int = 10
) -> float:
    """Compute Mean Average Precision at K (MAP@K) across all users."""
    ap_scores = []
    for user_id, recs in user_recommendations.items():
        relevant = user_relevance.get(user_id, set())
        ap = average_precision(recs, relevant, k)
        ap_scores.append(ap)
    return float(np.mean(ap_scores)) if ap_scores else 0.0


def catalog_coverage(recommended_lists: List[List[int]], total_catalog_items: int) -> float:
    """Compute Catalog Coverage (percentage of total catalog recommended across all users)."""
    if total_catalog_items <= 0:
        return 0.0
    unique_recommended = set(item for sublist in recommended_lists for item in sublist)
    return len(unique_recommended) / float(total_catalog_items)


def genre_diversity_score(genre_lists: List[List[str]]) -> float:
    """
    Compute Genre Diversity score based on unique genre ratio across recommendations.
    High diversity means recommendations span a rich variety of genres.
    """
    if not genre_lists:
        return 0.0
    all_genres = [g for sublist in genre_lists for g in sublist]
    if not all_genres:
        return 0.0
    unique_genres = set(all_genres)
    return len(unique_genres) / float(len(all_genres))
