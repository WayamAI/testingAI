from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.mongo import ping_database

app = FastAPI(title="WayamAI Testing Cloud API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health():
    db_ok = await ping_database()
    return {"status": "ok", "database": "connected" if db_ok else "unreachable"}
