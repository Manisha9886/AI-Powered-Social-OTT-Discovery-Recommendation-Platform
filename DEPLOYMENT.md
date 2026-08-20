# Deployment Guide (Vercel + Render + Internal Postgres / SQLite)

This guide walks you through deploying the **AI-Powered Social OTT Discovery & Recommendation Platform** for free using:
1. **Render Internal PostgreSQL** (or embedded SQLite) — *College Wi-Fi Compatible (No Port 5432 blocks!)*
2. **Render** for FastAPI Backend Service
3. **Vercel** for React + Vite Frontend

---

## 🗄️ Step 1: Set Up Database on Render (College Wi-Fi Safe)

### Option A: Render Internal PostgreSQL (Recommended)
1. Log in to [render.com](https://render.com).
2. Click **New +** -> **PostgreSQL**.
3. Name: `ott-discovery-db`, Database: `ott_discovery`, Region: `Oregon`, Plan: `Free`.
4. Click **Create Database**.
5. Once created, copy the **Internal Database URL** (e.g., `postgres://user:pass@dpg-xxx-a/ott_discovery`).
   *(Note: Internal URLs connect privately within Render's cloud network, so college firewalls will NEVER block them!)*

### Option B: Built-in SQLite (Zero Setup)
- If you prefer no separate database setup, simply leave `DATABASE_URL` empty on Render. The backend will automatically fall back to embedded SQLite (`ott_discovery.db`).

---


## 🐍 Step 2: Deploy FastAPI Backend on Render

1. Go to [render.com](https://render.com) and log in with GitHub.
2. Click **New +** -> **Web Service**.
3. Connect your GitHub repository: `AI-Powered-Social-OTT-Discovery-Recommendation-Platform`.
4. Render will auto-detect `render.yaml` or allow manual entry:
   - **Name:** `ott-discovery-backend`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install --upgrade pip && pip install -r requirements.txt`
   - **Start Command:** `PYTHONPATH=. uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
5. Under **Environment Variables**, add the following keys:
   * `ENVIRONMENT` = `production`
   * `DATABASE_URL` = *(Your Neon or Supabase PostgreSQL connection string from Step 1)*
   * `JWT_SECRET` = *(Generate a random string or click generate)*
   * `TMDB_API_KEY` = *(Your TMDB API key if using real metadata)*
   * `PINECONE_API_KEY` = *(Optional: Your Pinecone key for vector search)*
   * `ALLOWED_ORIGINS` = `*` *(Or your Vercel URL once frontend is deployed)*
6. Click **Create Web Service**. Render will deploy your backend!
7. Once deployed, copy your Render backend URL (e.g. `https://ott-discovery-backend.onrender.com`).

---

## ⚡ Step 3: Deploy React Frontend on Vercel

1. Go to [vercel.com](https://vercel.com) and log in with GitHub.
2. Click **Add New...** -> **Project**.
3. Import your repository: `AI-Powered-Social-OTT-Discovery-Recommendation-Platform`.
4. In the configuration panel:
   - **Framework Preset:** `Vite`
   - **Root Directory:** Edit and select `frontend` directory.
5. Under **Environment Variables**, add:
   * `VITE_API_URL` = `https://ott-discovery-backend.onrender.com` *(Your backend URL from Step 2)*
6. Click **Deploy**. Vercel will build and launch your frontend!

---

## 🎯 Verification & Testing

1. Open your Vercel deployment URL (e.g. `https://ott-discovery-frontend.vercel.app`).
2. Test browsing movies, logging in/registering, adding items to watchlist, rating movies, and trying AI recommendations.
3. Check the backend health endpoint: `https://ott-discovery-backend.onrender.com/health` (should return `{"status": "ok"}`).
