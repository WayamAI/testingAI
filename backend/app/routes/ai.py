import logging
from fastapi import APIRouter, Depends
from app.schemas.ai import (
    GenerateTestsRequest, GenerateTestsResponse, AnalyzeFailureRequest, AnalyzeFailureResponse,
)
from app.engines.ai.base import TestGenInput, FailureContext
from app.engines.ai.factory import generate_test_cases_with_fallback, analyze_failure_with_fallback
from app.security.dependencies import get_current_user
from app.models.user import User
from app.models.ai_request import AIRequest
from app.database.mongo import get_database

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/ai", tags=["ai"])


@router.post("/generate-tests", response_model=GenerateTestsResponse)
async def generate_tests(payload: GenerateTestsRequest, user: User = Depends(get_current_user)):
    cases, source = await generate_test_cases_with_fallback(
        TestGenInput(requirement_text=payload.requirement_text)
    )
    db = get_database()
    record = AIRequest(
        organization_id=user.organization_id,
        kind="test_generation",
        input_summary=payload.requirement_text[:200],
        source=source,
        output_summary=f"{len(cases)} test cases generated",
        created_by=user.id,
    )
    try:
        await db.ai_requests.insert_one(record.model_dump(by_alias=True))
    except Exception as exc:
        logger.warning("Failed to persist AIRequest for test_generation: %s", exc)
    return GenerateTestsResponse(cases=cases, source=source)


@router.post("/analyze-failure", response_model=AnalyzeFailureResponse)
async def analyze_failure(payload: AnalyzeFailureRequest, user: User = Depends(get_current_user)):
    analysis, source = await analyze_failure_with_fallback(
        FailureContext(
            error_message=payload.error_message,
            stack_trace=payload.stack_trace,
            test_case_title=payload.test_case_title,
        )
    )
    db = get_database()
    record = AIRequest(
        organization_id=user.organization_id,
        kind="failure_analysis",
        input_summary=payload.error_message[:200],
        source=source,
        output_summary=analysis.root_cause[:200],
        created_by=user.id,
    )
    try:
        await db.ai_requests.insert_one(record.model_dump(by_alias=True))
    except Exception as exc:
        logger.warning("Failed to persist AIRequest for failure_analysis: %s", exc)
    return AnalyzeFailureResponse(analysis=analysis, source=source)
