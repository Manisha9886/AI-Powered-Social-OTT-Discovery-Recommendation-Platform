import json
import os

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed')
LOOKUP_PATH = os.path.join(PROCESSED_DIR, 'movie_lookup.json')

def is_valid_image_url(url):
    if not url:
        return False
    if url.startswith('/'):
        return True
    if any(domain in url for domain in ['image.tmdb.org', 'media-amazon.com', 'ssl-images-amazon.com', 'wikimedia.org']):
        return True
    if any(url.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.webp']):
        return True
    return False

def sanitize():
    with open(LOOKUP_PATH, 'r', encoding='utf-8') as f:
        movies = json.load(f)

    cleaned = 0
    for mid, mdata in movies.items():
        poster = mdata.get("poster_path")
        if poster and not is_valid_image_url(poster):
            mdata["poster_path"] = None
            cleaned += 1

    with open(LOOKUP_PATH, 'w', encoding='utf-8') as f:
        json.dump(movies, f, indent=2)

    print(f"Sanitized {cleaned} invalid website links to null in movie_lookup.json!")

if __name__ == "__main__":
    sanitize()
