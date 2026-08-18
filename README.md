# AI-Powered Social OTT Discovery & Recommendation Platform

Welcome to the starter monorepo for the OTT Discovery & Recommendation Platform, built for a 10-day hackathon!

## 🚀 Project Overview

This platform is a social movie discovery application that combines traditional recommendation algorithms (popularity, content-based, collaborative filtering) with cutting-edge AI (LLMs and RAG). It allows users to discover movies, follow friends, rate/review content, and ask an interactive AI assistant for highly personalized, explainable recommendations.

### Key Features

- **Social & Profiles:** User authentication, social feeds, follow system, watchlists.
- **Hybrid Recommendation Engine:** Combines multiple ML approaches to generate candidate movies.
- **Explainable AI Assistant:** An LLM-powered chat that understands natural language constraints, elicits preferences when queries are ambiguous, and explains *why* a movie was recommended using RAG and evidence scores.
- **Mock Data Ready:** Start developing the frontend or AI layers immediately without waiting for the database or ML models to be trained.

---

## 🏗️ Architecture & Technology Stack

The project uses a **Modular Monolith** architecture for simplicity during the hackathon, while maintaining clear boundaries between domains so that four developers can work concurrently.

### Technology Stack

- **Frontend:** React, TypeScript, Vite, Tailwind CSS
- **Backend Orchestrator:** Python, FastAPI, Pydantic, SQLAlchemy
- **Database:** PostgreSQL, with pgvector if needed
- **Recommendation Module:** Python, pandas, scikit-learn
- **AI Module:** Python, LangChain (minimal), LLM Provider
- **Infrastructure:** Docker, Docker Compose

### High-Level Architecture

```text
                         USER
                           │
                           ▼
                  ┌─────────────────┐
                  │   APPLICATION   │
                  └────────┬────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
          USER/SOCIAL     MOVIES    AI ASSISTANT
              │            │            │
              │            │            ▼
              │            │           LLM
              │            │            │
              │            │            ▼
              │            │           RAG
              │            │            │
              │            │            ▼
              │            │      EXPLANATION
              │            │
              └────────────┼──────────────┐
                           ▼              │
                    USER PREFERENCE       │
                           │              │
                           ▼              │
                  RECOMMENDATION ENGINE   │
                           │              │
              ┌────────────┼───────────┐  │
              ▼            ▼           ▼  │
         Popularity     Content   Collaborative
              │            │           │
              └────────────┼───────────┘
                           ▼
                    Hybrid Ranking
                           │
                           ▼
                   Top-N Recommendations
                           │
                           ▼
                  Recommendation Evidence
                           │
                           └──────────► RAG + LLM
```

---

## 📁 Repository Structure

```text
.
├── ai/                 # AI, LLM, RAG, and Explainability module
├── backend/            # FastAPI backend, orchestration, API, auth, DB
├── data/               # Mock data and datasets (TMDB, MovieLens)
├── frontend/           # React frontend
├── recommendation/     # Recommendation engine algorithms
├── scripts/            # Helpful setup and data/mock scripts
├── docs/               # Architecture and technical documentation
├── docker-compose.yml
├── .env.example
├── CONTRIBUTING.md
└── README.md
```

---

# 👥 Team Roles & Ownership

This project is designed for **four developers working concurrently**.

The project is divided into four major technical domains. Each team member has **primary ownership** of one domain and is responsible for implementing, testing, documenting, and maintaining it.

### ⚠️ Important Collaboration Rule

Folder ownership does **not** mean that other developers are technically blocked from accessing the folder.

Everyone can **read the entire repository**.

However, developers should normally **write/modify code only within their primary ownership areas**, unless a cross-module change is required.

If a developer needs to modify another member's primary area:

1. Discuss the change with the owner.
2. Agree on the required change.
3. Create a feature branch.
4. Keep the modification focused.
5. Open a Pull Request.
6. Have the relevant owner review it before merging.

This allows the team to work concurrently without creating unnecessary merge conflicts.

---

# 👤 Team Member 1 — Data Engineering & Movie Intelligence

### Primary Goal

Build and maintain the data foundation used by the recommendation and AI systems.

### Responsibilities

- TMDB API integration
- Movie metadata ingestion
- MovieLens dataset processing
- Data cleaning and preprocessing
- Feature engineering
- Movie metadata normalization
- Movie embeddings
- Movie search/data preparation
- Preparing data for recommendation models
- Preparing movie knowledge data for RAG
- Data quality checks

### Primary Ownership

```text
data/
```

Main working areas:

```text
data/
├── raw/
├── processed/
├── sample/
└── README.md
```

Supporting scripts:

```text
scripts/data/
```

### Frontend Responsibility

Frontend is shared across the team. Member 1 owns the UI related to movie discovery and movie information:

```text
frontend/src/features/movies/
```

Examples:

- Movie search
- Movie browsing
- Movie details
- Movie metadata
- Genre/category exploration

### Individual Evaluation Contribution

> I developed the movie-data pipeline, integrated external movie data sources, performed preprocessing and feature engineering, and prepared the data and embeddings used by the recommendation and RAG systems.

---

# 👤 Team Member 2 — Recommendation Intelligence

### Primary Goal

Develop, compare, evaluate, and maintain the recommendation engine.

### Responsibilities

- Popularity-based recommendation
- Content-based recommendation
- Collaborative filtering
- Candidate generation
- Hybrid recommendation
- Ranking and filtering
- Recommendation diversity
- Model comparison
- Recommendation evaluation
- Recommendation performance
- Recommendation evidence generation

### Primary Ownership

```text
recommendation/
```

Main working areas:

```text
recommendation/
├── data/
├── preprocessing/
├── popularity/
├── content_based/
├── collaborative/
├── hybrid/
├── embeddings/
├── evaluation/
├── schemas/
└── tests/
```

### Frontend Responsibility

Member 2 owns the recommendation-related UI:

```text
frontend/src/features/recommendations/
```

Examples:

- Recommendation dashboard
- Recommendation cards
- Recommendation scores
- Recommendation explanations/evidence display
- Model comparison or evaluation visualizations

### Individual Evaluation Contribution

> I developed and evaluated multiple recommendation approaches and implemented the hybrid ranking system used to generate personalized recommendations.

---

# 👤 Team Member 3 — LLM, RAG & Explainable AI

### Primary Goal

Develop the conversational AI and explainability layer.

### Responsibilities

- LLM integration
- Natural-language understanding
- User intent extraction
- Preference extraction
- Preference elicitation
- Conversational recommendation requests
- RAG pipeline
- Vector retrieval
- Prompt engineering
- Recommendation explanations
- Evidence generation
- Confidence estimation
- AI guardrails
- Hallucination prevention
- Grounded responses

### Primary Ownership

```text
ai/
```

Main working areas:

```text
ai/
├── llm/
├── rag/
├── embeddings/
├── prompts/
├── agents/
├── explainability/
├── schemas/
└── tests/
```

### Frontend Responsibility

Member 3 owns the AI-related UI:

```text
frontend/src/features/ai/
```

Examples:

- AI chat
- Natural-language recommendation requests
- Preference clarification
- "Why this movie?"
- Recommendation evidence
- Confidence
- AI-generated explanations

### Individual Evaluation Contribution

> I developed the conversational AI, RAG pipeline, preference elicitation, and grounded explainability layer for the recommendation system.

---

# 👤 Team Member 4 — Backend, Social Intelligence & System Orchestration

### Primary Goal

Build the application backend and coordinate communication between the data, recommendation, AI, database, and frontend components.

### Backend Responsibilities

- FastAPI application
- Authentication
- User management
- Movie APIs
- Ratings
- Reviews
- Watchlists
- Follow system
- Social feed
- User interactions
- API architecture

### Database Responsibilities

- PostgreSQL schema
- SQLAlchemy models
- Database migrations
- Relationships
- Indexes

### System Orchestration Responsibilities

The backend coordinates the different modules:

```text
Frontend
    ↓
Backend
    ↓
User/Data
    ↓
Recommendation Engine
    ↓
AI/RAG
    ↓
Backend
    ↓
Frontend
```

The backend should **not implement the recommendation algorithms or LLM logic itself**. It should orchestrate calls to those modules.

### Primary Ownership

```text
backend/
```

Main working areas:

```text
backend/
├── app/
│   ├── api/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   ├── repositories/
│   ├── config/
│   └── core/
└── tests/
```

### Frontend Responsibility

Member 4 owns:

```text
frontend/src/features/auth/
frontend/src/features/profile/
frontend/src/features/social/
```

Examples:

- Login/signup
- User profile
- Watchlist
- Ratings/reviews
- Following
- Social feed

### Individual Evaluation Contribution

> I designed and implemented the backend, database, social features, APIs, and orchestration layer connecting the recommendation and AI systems with the application.

---

# 🎨 Frontend Ownership

There is **NO dedicated frontend developer**.

Frontend development is a **shared responsibility**.

Each developer owns the frontend features corresponding to their technical domain.

```text
frontend/src/features/
│
├── auth/              → Team Member 4
├── profile/           → Team Member 4
├── social/            → Team Member 4
│
├── movies/            → Team Member 1
│
├── recommendations/  → Team Member 2
│
└── ai/                → Team Member 3
```

Shared frontend infrastructure is collaborative:

```text
frontend/src/app/
frontend/src/components/
frontend/src/services/
frontend/src/types/
frontend/src/mocks/
```

Changes to shared frontend infrastructure should be discussed with the team before merging.

---

# 📋 Ownership Summary

| Area | Primary Owner | Collaboration |
|---|---|---|
| `data/` | Member 1 | Members 2 & 3 |
| `recommendation/` | Member 2 | Members 1 & 4 |
| `ai/` | Member 3 | Members 1, 2 & 4 |
| `backend/` | Member 4 | All members |
| `frontend/src/features/movies/` | Member 1 | Member 4 |
| `frontend/src/features/recommendations/` | Member 2 | Members 1 & 3 |
| `frontend/src/features/ai/` | Member 3 | Members 2 & 4 |
| `frontend/src/features/auth/` | Member 4 | Member 1 |
| `frontend/src/features/profile/` | Member 4 | Member 1 |
| `frontend/src/features/social/` | Member 4 | Member 1 |
| `frontend/src/components/` | Shared | All |
| `frontend/src/services/` | Shared | All |
| `frontend/src/types/` | Shared | All |
| `frontend/src/mocks/` | Shared | All |
| `docs/` | Shared | All |
| `scripts/` | Shared | Coordinate before modifying |
| `docker-compose.yml` | Member 4 | All |
| `.env.example` | Member 4 | All |

---

# 🔗 Module Communication

The modules should communicate through clearly defined interfaces.

### Data → Recommendation

```text
Data Pipeline
     ↓
Processed Movie/User Data
     ↓
Recommendation Engine
```

### Data → AI/RAG

```text
Movie Data
     ↓
Embeddings / Knowledge Documents
     ↓
RAG
```

### Recommendation → AI

```text
Recommendation Engine
     ↓
Recommendation Evidence
     ↓
AI/RAG
     ↓
Explanation
```

### Backend → Recommendation

```text
Backend
   ↓
User ID + Preferences + Filters
   ↓
Recommendation Engine
   ↓
Recommendations + Evidence
```

### Backend → AI

```text
Backend
   ↓
User Query / Recommendation Context
   ↓
AI Module
   ↓
Intent / Explanation / Response
```

---

# 📡 API Contracts

The modules should expose stable interfaces so that developers can work concurrently without depending on each other's internal implementation.

### Recommendation Interface

```text
recommend(user_id, filters)
        ↓
RecommendationResponse
```

Example:

```json
{
  "user_id": 101,
  "recommendations": [
    {
      "movie_id": 123,
      "title": "Arrival",
      "final_score": 0.92,
      "content_score": 0.91,
      "collaborative_score": 0.87,
      "popularity_score": 0.72,
      "reason_codes": [
        "GENRE_MATCH",
        "SIMILAR_TO_LIKED_MOVIES",
        "SIMILAR_USER_PREFERENCE"
      ],
      "confidence": "high"
    }
  ]
}
```

The recommendation algorithms can change internally without requiring changes to the frontend.

### AI Interface

```text
understand_query(query)
        ↓
QueryIntent
```

Example:

```json
{
  "intent": "movie_recommendation",
  "preferences": {
    "similar_to": ["Interstellar"],
    "genres": ["Science Fiction"],
    "max_runtime": 120
  },
  "missing_information": [],
  "constraints": {
    "max_runtime": 120
  }
}
```

If important information is missing:

```json
{
  "missing_information": [
    "genre_or_mood"
  ],
  "clarifying_question": "Would you prefer something exciting, funny, emotional, or suspenseful?"
}
```

---

# 🔍 Explainability Contract

The recommendation engine must produce evidence **before** the LLM generates an explanation.

Example:

```json
{
  "movie_id": 123,
  "final_score": 0.92,
  "evidence": {
    "content_similarity": 0.91,
    "collaborative_score": 0.87,
    "popularity_score": 0.72,
    "preference_match": 0.94,
    "runtime_constraint_satisfied": true
  }
}
```

The RAG/LLM layer uses this evidence together with verified movie information to generate the explanation.

Example:

```json
{
  "explanation": "This movie closely matches your preference for science fiction and is similar to movies you have rated highly.",
  "confidence": "high",
  "sources": [
    "TMDB metadata",
    "user preference profile",
    "recommendation model evidence"
  ]
}
```

The LLM must **not invent recommendation scores or evidence**.

---

# 🗄️ Database Ownership

The primary database owner is Team Member 4.

Initial entities include:

```text
Users
Movies
Ratings
Reviews
Watchlists
Follows
Interactions
Recommendations
```

The schema should contain:

- Primary keys
- Foreign keys
- Timestamps
- Relationships
- Appropriate indexes

Database migrations should be used for schema changes.

Other developers may request schema changes when their modules require additional data.

---

# 🧪 Mock Data & Concurrent Development

Mock data is an important part of the architecture because all four developers must be able to work concurrently.

The frontend must be able to run without the ML or LLM systems being completed.

Mock data should be available for:

- Users
- Movies
- Recommendations
- AI responses
- Reviews
- Ratings
- Social feed

For example:

```text
Frontend
    ↓
Mock API
    ↓
Mock Recommendation Response
```

Later:

```text
Frontend
    ↓
Backend
    ↓
Real Recommendation Engine
```

The frontend contract should remain the same.

---

# ⚙️ Development Modes

The project supports three development modes.

### 1. Full Mode

```text
Frontend
   ↓
Backend
   ↓
Recommendation
   ↓
AI/RAG
   ↓
Database
```

### 2. Mock Mode

```text
Frontend
   ↓
Mock Responses
```

### 3. Local ML/AI Mode

```text
Backend
   ↓
Local Recommendation Modules
   +
Local AI/RAG Modules
```

This allows developers to work independently even when another component is incomplete.

---

# 🚀 How to Run the Project

## Prerequisites

- Docker and Docker Compose
- Node.js v18+
- Python 3.10+
- Git

---

## Option 1: Full Docker Setup

Copy the environment file:

```bash
cp .env.example .env
```

Fill in the required API keys.

Then:

```bash
docker-compose up --build
```

Services:

- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- PostgreSQL: `localhost:5432`

---

## Option 2: Local Development

### Start Database

```bash
docker-compose up -d db
```

### Start Backend

```bash
cd backend
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

Linux/macOS:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
pip install -e ../recommendation
pip install -e ../ai
```

Start FastAPI:

```bash
uvicorn app.main:app --reload
```

### Start Frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

---

## Option 3: Frontend Mock Mode

If the backend or ML/AI components are not ready, the frontend can use mock responses.

Set:

```text
VITE_USE_MOCKS=true
```

Mock data is located in:

```text
frontend/src/mocks/
```

This allows frontend development to continue independently.

---

# 📖 API Documentation

Once the backend is running, visit:

```text
http://localhost:8000/docs
```

FastAPI automatically provides interactive OpenAPI documentation.

---

# 🧪 Testing

Each major module should contain its own tests.

### Backend

Test:

- Authentication
- User endpoints
- Movie endpoints
- Recommendation endpoints
- AI endpoints

### Recommendation

Test:

- Popularity recommender
- Content-based recommender
- Collaborative filtering
- Hybrid ranking
- Evaluation metrics

### AI

Test:

- Intent extraction
- Preference extraction
- RAG retrieval
- Explanation generation
- Response schemas

### Frontend

Test:

- Component rendering
- Recommendation components
- AI chat
- Basic user flows

---

# 📅 10-Day Development Principle

The team should work **concurrently**, not sequentially.

Do NOT follow:

```text
Backend → ML → AI → Frontend
```

Instead:

```text
                 DAY 1
                   │
      ┌────────────┼────────────┐
      ▼            ▼            ▼
    DATA          ML          AI/RAG
      │            │            │
      └────────────┼────────────┘
                   │
                   ▼
                BACKEND
                   │
                   ▼
              INTEGRATION
                   │
                   ▼
                  MVP
```

All four developers should begin their respective modules immediately.

Use:

```text
API Contracts
+
Mock Data
+
Stable Schemas
+
Independent Modules
```

to prevent one developer from blocking another.

---

# 🎯 Development Principle

The objective is to build a **working MVP first**, then improve individual components.

### Prioritize

- Clear architecture
- Parallel development
- Stable interfaces
- Working recommendation pipeline
- Working AI/RAG pipeline
- Explainability
- User experience
- Evaluation
- Integration

### Avoid

- Unnecessary microservices
- Kubernetes
- Complex cloud infrastructure
- Huge deep-learning models
- Over-engineered agent workflows
- Unnecessary abstractions
- Features outside the current architecture

The goal is to have a **functional, demonstrable system within 10 days**, while ensuring that every team member has a substantial and independently defensible technical contribution.

---

# 📌 Quick Ownership Reference

```text
┌────────────────────────────────────────────────────────────┐
│                    TEAM MEMBER 1                           │
│             DATA ENGINEERING & MOVIE INTELLIGENCE          │
│                                                            │
│  data/                                                     │
│  frontend/src/features/movies/                             │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│                    TEAM MEMBER 2                           │
│                  RECOMMENDATION INTELLIGENCE               │
│                                                            │
│  recommendation/                                           │
│  frontend/src/features/recommendations/                    │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│                    TEAM MEMBER 3                           │
│                  LLM + RAG + EXPLAINABILITY                │
│                                                            │
│  ai/                                                       │
│  frontend/src/features/ai/                                 │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│                    TEAM MEMBER 4                           │
│           BACKEND + SOCIAL + ORCHESTRATION                 │
│                                                            │
│  backend/                                                  │
│  frontend/src/features/auth/                               │
│  frontend/src/features/profile/                            │
│  frontend/src/features/social/                             │
└────────────────────────────────────────────────────────────┘

                    SHARED BY ALL

  frontend/src/components/
  frontend/src/services/
  frontend/src/types/
  frontend/src/mocks/
  docs/
  Git collaboration
  Integration
```

**Everyone can read the entire repository. Primary ownership defines who is responsible for maintaining and approving changes in that area.**
