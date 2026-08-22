"""Feature 2: Doc-Driven Tests — upload a PRD/spec/API-def, extract real
scenarios via AI (with a deterministic fallback), generate Playwright
tests from them. Independent of whether a repo is connected — if the
project has a workspace, generated tests are also written to disk there.
"""
from app.database.mongo import get_database
from app.engines.ai.base import DocScenarioInput
from app.engines.ai.factory import extract_scenarios_with_fallback, generate_tests_from_scenarios_with_fallback
from app.intake.workspace import workspace_path
from app.models.base import new_id
from app.models.doc_upload import DocUpload
from app.models.generated_test import GeneratedTest
from app.services.baseline_service import BASELINE_DIR_NAME
from app.services.playwright_codegen import validate_js_syntax
from app.services.document_parsing import extract_text


async def process_document(org_id: str, user_id: str, project_id: str, filename: str, content: bytes) -> dict:
    text = extract_text(filename, content)  # raises DocumentParseError with a specific reason

    scenarios, scenario_source = await extract_scenarios_with_fallback(DocScenarioInput(document_text=text))
    if not scenarios:
        return {
            "scenarios_extracted": 0, "tests_generated": 0, "source": scenario_source,
            "message": "No testable scenarios could be extracted from this document.", "tests": [],
        }

    generated, gen_source = await generate_tests_from_scenarios_with_fallback(scenarios)

    workspace = workspace_path(project_id)
    has_workspace = workspace.exists()
    baseline_dir = workspace / BASELINE_DIR_NAME if has_workspace else None
    if baseline_dir:
        baseline_dir.mkdir(exist_ok=True)

    db = get_database()
    scan_id = new_id()
    persisted: list[GeneratedTest] = []
    rejected = 0

    for item in generated:
        if not await validate_js_syntax(item.code):
            rejected += 1
            continue

        file_path = None
        if baseline_dir:
            filename_out = f"docdriven_{item.category}_{new_id()[:8]}.spec.js"
            full_path = baseline_dir / filename_out
            full_path.write_text(item.code)
            file_path = str(full_path.relative_to(workspace))

        record = GeneratedTest(
            organization_id=org_id, project_id=project_id, scan_id=scan_id,
            category=item.category, title=item.title, code=item.code,
            confidence=item.confidence, source=gen_source, file_path=file_path, origin="doc_driven",
        )
        await db.generated_tests.insert_one(record.model_dump(by_alias=True))
        persisted.append(record)

    upload_record = DocUpload(
        organization_id=org_id, project_id=project_id, filename=filename,
        extracted_char_count=len(text), scenarios_extracted=len(scenarios),
        tests_generated=len(persisted), source=gen_source,
    )
    await db.doc_uploads.insert_one(upload_record.model_dump(by_alias=True))

    return {
        "scenarios_extracted": len(scenarios),
        "tests_generated": len(persisted),
        "rejected_invalid_syntax": rejected,
        "source": gen_source,
        "scenario_source": scenario_source,
        "tests": [t.model_dump() for t in persisted],
    }


async def list_doc_uploads(org_id: str, project_id: str) -> list[DocUpload]:
    db = get_database()
    cursor = db.doc_uploads.find({"organization_id": org_id, "project_id": project_id}).sort("created_at", -1)
    return [DocUpload.model_validate(d) async for d in cursor]
