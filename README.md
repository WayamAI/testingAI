# WayamAI Testing Cloud

AI-powered software testing and quality engineering platform.

## Local development

1. Copy `.env.example` to `.env` and fill in `OLLAMA_API_KEY`.
2. Copy `.env.example` to `backend/.env` and `worker/.env` (same values).
3. Copy `.env.example` to `frontend/.env` keeping only the `VITE_*` keys.
4. Ensure MongoDB is reachable at `mongodb://localhost:27017` and Redis at
   `redis://localhost:6379`.
5. Run `./scripts/dev.sh`.
