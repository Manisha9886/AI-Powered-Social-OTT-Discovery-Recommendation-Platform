# Contributing Guidelines

Welcome to the hackathon! Since we have 4 developers working concurrently for 10 days, following these guidelines is crucial to avoid merge conflicts and blocked work.

## 🌿 Branching Strategy

We use a simplified Git Flow.

- `main`: The stable, deployable version of the project.
- `develop`: The active integration branch. All feature branches merge here.

### Feature Branches
Create a feature branch from `develop` for your work. Name it based on your domain:

- `feature/data/TMDB-ingestion`
- `feature/recommendation/collaborative-filtering`
- `feature/ai-rag/intent-extraction`
- `feature/backend-social/auth-endpoints`
- `feature/frontend/movie-card-ui`

```bash
git checkout develop
git pull
git checkout -b feature/<domain>/<short-description>
```

### Pull Requests
- DO NOT push directly to `main` or `develop`.
- Open a Pull Request (PR) against the `develop` branch.
- Request a review from at least one other team member if it affects shared interfaces.

## 🏗️ Modularity & Boundaries (CRITICAL)

To allow parallel development, we MUST respect interface boundaries.

1. **Frontend:** Do not import Python code. Communicate ONLY via the FastAPI REST endpoints.
2. **Backend (FastAPI):** Orchestrates the other modules.
3. **Recommendation Module (`recommendation/`):** Must expose a clean interface in `recommendation/interface.py` (e.g., `recommend(user_id, filters)`). The backend will call this.
4. **AI Module (`ai/`):** Must expose a clean interface in `ai/interface.py` (e.g., `understand_query()`, `explain_recommendation()`).

If you need a feature from another module that isn't built yet, **use a mock**. The `data/sample/` folder contains mock JSON files. You can load these in your code temporarily so you are not blocked.

## 🎯 Day 1 Tasks by Role

- **Member 1 (Data):** Set up TMDB API scripts to download a sample of 1000 movies into `data/sample/movies.json`.
- **Member 2 (Recommendation):** Implement the `recommendation/interface.py` returning mock scores based on `data/sample/movies.json`.
- **Member 3 (AI/RAG):** Implement `ai/interface.py` that parses a hardcoded query and returns a mock intent/explanation.
- **Member 4 (Backend):** Create the FastAPI routers, hook them up to the mock `recommendation` and `ai` interfaces, and verify the `/docs` Swagger UI works.
