import unittest
import os
import sys

# Add root directory to sys.path for test discovery
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from recommendation.popularity.recommender import PopularityRecommender
from recommendation.content_based.recommender import ContentBasedRecommender
from recommendation.collaborative.recommender import CollaborativeRecommender
from recommendation.hybrid.recommender import HybridRecommender
from recommendation.evaluation.metrics import precision_at_k, recall_at_k, average_precision, mean_average_precision
from recommendation.interface import recommend


class TestRecommendationEngine(unittest.TestCase):

    def test_popularity_recommender(self):
        pop_model = PopularityRecommender()
        loaded = pop_model.load_data()
        self.assertTrue(loaded, "PopularityRecommender failed to load data")
        
        recs = pop_model.recommend(top_n=5)
        self.assertGreater(len(recs), 0)
        self.assertIn("movie_id", recs[0])
        self.assertIn("popularity_score", recs[0])

    def test_content_based_recommender(self):
        cb_model = ContentBasedRecommender()
        loaded = cb_model.load_data()
        self.assertTrue(loaded, "ContentBasedRecommender failed to load data")
        
        # Fetch valid movie_id from dataset
        sample_movie_id = int(cb_model.movies_df.iloc[0]['movie_id'])
        recs = cb_model.recommend_similar_movies(movie_ids=[sample_movie_id], top_n=5)
        self.assertGreater(len(recs), 0)
        self.assertIn("content_score", recs[0])

    def test_hybrid_recommender(self):
        hybrid = HybridRecommender()
        hybrid.initialize()
        
        response = hybrid.recommend(user_id=1, top_n=5)
        self.assertEqual(response.user_id, 1)
        self.assertGreater(len(response.recommendations), 0)
        
        first_rec = response.recommendations[0]
        self.assertIsNotNone(first_rec.evidence)
        self.assertGreaterEqual(first_rec.final_score, 0.0)
        self.assertGreater(len(first_rec.reason_codes), 0)

    def test_recommendation_interface(self):
        res = recommend(user_id=101, filters={"top_n": 3})
        self.assertEqual(res["user_id"], 101)
        self.assertIn("recommendations", res)

    def test_evaluation_metrics(self):
        recommended = [1, 2, 3, 4, 5]
        relevant = {2, 4, 6}
        
        prec = precision_at_k(recommended, relevant, k=5)
        self.assertEqual(prec, 2 / 5)
        
        rec = recall_at_k(recommended, relevant, k=5)
        self.assertEqual(rec, 2 / 3)
        
        ap = average_precision(recommended, relevant, k=5)
        self.assertGreater(ap, 0.0)


if __name__ == "__main__":
    unittest.main()
