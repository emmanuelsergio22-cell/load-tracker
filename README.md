# Adaptive Training Load Tracker

An API that takes free-text daily logs (training done, how you feel, what you ate) and uses Claude to turn them into a structured training load recommendation — adjusting for soreness, fatigue, and nutrition, with context from your recent history.

**Live API:** https://athletes-load-tracker.onrender.com/docs
*(free-tier instance — first request after inactivity can take 50+ seconds to spin up)*

## What it does

Most training logs force you into rigid fields (RPE score, sleep hours, macros). This instead takes plain language — "5-a-side, 60 mins, felt sharp" / "tired but good mood" / "chicken, rice, protein shake" — and:

1. Parses it into structured data (soreness, fatigue, sleep quality, nutrition quality) using Claude.
2. Pulls similar past days from a vector store, so the recommendation accounts for recent history, not just today in isolation.
3. Returns a load recommendation (reduce / maintain / increase) with reasoning, and logs the entry.

## Tech stack

- **FastAPI** — HTTP API layer (`POST /log`)
- **Anthropic API (Claude Haiku)** — parses free text into structured JSON
- **ChromaDB** — vector store for similarity search against past entries
- **SQLite** — persists every logged day
- **Render** — deployment (free tier)

## API
