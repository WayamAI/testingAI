from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.database.mongo import get_database
from app.services import execution_service, testing_service
from app.models.test_run import TestRun

router = APIRouter()


@router.websocket("/ws/executions/{run_id}")
async def execution_socket(websocket: WebSocket, run_id: str):
    await websocket.accept()
    db = get_database()
    run_doc = await db.test_runs.find_one({"_id": run_id})
    if not run_doc:
        await websocket.send_json({"type": "error", "message": "Run not found"})
        await websocket.close()
        return

    run = TestRun.model_validate(run_doc)
    suite = await testing_service.get_test_suite(run.organization_id, run.suite_id)
    if not suite:
        await websocket.send_json({"type": "error", "message": "Test suite not found"})
        await websocket.close()
        return

    case_ids = suite.test_case_ids

    async def on_event(event):
        try:
            await websocket.send_json(event.model_dump())
        except Exception:
            pass

    try:
        await execution_service.execute_and_persist(run.organization_id, run.project_id, run, case_ids, on_event)
    except WebSocketDisconnect:
        pass
    except Exception as exc:
        try:
            await websocket.send_json({"type": "error", "message": str(exc)})
        except Exception:
            pass
    finally:
        try:
            await websocket.close()
        except Exception:
            pass
