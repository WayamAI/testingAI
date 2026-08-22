from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.mongo import ping_database
from app.middleware.error_handler import install_error_handlers
from app.routes.auth import router as auth_router
from app.routes.projects import router as projects_router
from app.routes.ai import router as ai_router
from app.routes.requirements import router as requirements_router
from app.routes.test_cases import router as test_cases_router
from app.routes.test_suites import router as test_suites_router
from app.routes.test_runs import router as test_runs_router
from app.routes.websocket_execution import router as ws_execution_router
from app.routes.defects import router as defects_router
from app.routes.quality import router as quality_router
from app.routes.dashboard import router as dashboard_router
from app.routes.intake import router as intake_router
from app.routes.security import router as security_router
from app.routes.api_testing import router as api_testing_router
from app.routes.defect_prediction import router as defect_prediction_router
from app.routes.baseline import router as baseline_router
from app.core.config import get_settings
from app.seed.seed_demo import seed_demo_data

app = FastAPI(title="WayamAI Testing Cloud API", version="0.1.0")

install_error_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(projects_router)
app.include_router(ai_router)
app.include_router(requirements_router)
app.include_router(test_cases_router)
app.include_router(test_suites_router)
app.include_router(test_runs_router)
app.include_router(ws_execution_router)
app.include_router(defects_router)
app.include_router(quality_router)
app.include_router(dashboard_router)
app.include_router(intake_router)
app.include_router(security_router)
app.include_router(api_testing_router)
app.include_router(defect_prediction_router)
app.include_router(baseline_router)


@app.on_event("startup")
async def on_startup():
    if get_settings().demo_mode:
        await seed_demo_data()


@app.get("/api/health")
async def health():
    db_ok = await ping_database()
    return {"status": "ok", "database": "connected" if db_ok else "unreachable"}
