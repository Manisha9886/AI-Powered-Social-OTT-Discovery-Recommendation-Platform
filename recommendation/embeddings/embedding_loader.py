import os
import json
import numpy as np
from typing import Tuple, List, Optional


def load_movie_embeddings(data_dir: str) -> Tuple[Optional[np.ndarray], Optional[List[int]]]:
    """
    Load pre-computed movie vector embeddings and corresponding movie IDs.
    """
    embeddings_path = os.path.join(data_dir, "movie_embeddings.npy")
    ids_path = os.path.join(data_dir, "movie_embedding_ids.json")

    if not os.path.exists(embeddings_path) or not os.path.exists(ids_path):
        return None, None

    try:
        embeddings = np.load(embeddings_path)
        with open(ids_path, "r", encoding="utf-8") as f:
            movie_ids = [int(x) for x in json.load(f)]
        return embeddings, movie_ids
    except Exception as e:
        print(f"Embedding Loader Error: {e}")
        return None, None
