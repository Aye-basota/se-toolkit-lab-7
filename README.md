# Telegram Bot for LMS

A Telegram bot that lets users interact with a Learning Management System backend through chat. Supports slash commands and natural language queries routed through an LLM.

## Features

- `/start`, `/help`, `/health`, `/labs`, `/scores` commands
- Natural language intent routing via LLM
- Inline keyboard buttons
- Multi-step reasoning (chained API calls)
- Containerized with Docker, deployed alongside backend

## Tech stack

- Python 3.12+, aiogram
- FastAPI backend integration
- LLM API for intent recognition
- Docker, Docker Compose
- Caddy reverse proxy

## Quick start

```bash
# Set up environment
cp .env.bot.example .env.bot.secret
cp .env.docker.example .env.docker.secret

# Deploy
docker compose up --build
```

## Project structure

- `bot/` — Telegram bot handlers and services
- `backend/` — FastAPI + PostgreSQL
- `frontend/` — React dashboard
