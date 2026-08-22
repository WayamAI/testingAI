"""Feature 7: Self-Healing Tests — scoped strictly to selector-not-found
failures. Live-scans the real DOM, lets the AI pick only an index into
that real candidate list (never inventing a selector — enforced in
app/engines/ai/ollama_provider.py), validates the pick against the live
page a second time, and requires an explicit human approval action before
any write-back to a real file. Never auto-applies.
"""
from app.database.mongo import get_database
from app.engines.ai.base import SelfHealInput
from app.engines.ai.factory import pick_self_heal_candidate_with_fallback
from app.intake.workspace import workspace_path
from app.models.self_heal_attempt import SelfHealAttempt
from app.services.dom_scan_service import DomScanError, scan_live_dom, validate_selector_live


class NoCandidatesFound(Exception):
    pass


class AttemptNotFound(Exception):
    pass


class InvalidApproval(Exception):
    pass


async def propose_heal(
    org_id: str, project_id: str, url: str, original_selector: str, failure_context: str
) -> SelfHealAttempt:
    candidates = await scan_live_dom(url)
    if not candidates:
        raise NoCandidatesFound(f"No interactive elements found on {url} to propose as a replacement.")

    pick, source = await pick_self_heal_candidate_with_fallback(
        SelfHealInput(original_selector=original_selector, failure_context=failure_context, candidates=candidates)
    )
    chosen = next(c for c in candidates if c.index == pick.candidate_index)

    try:
        live_count = await validate_selector_live(url, chosen.selector_hint)
    except DomScanError:
        live_count = -1  # validation itself failed — surfaced honestly, not treated as success

    db = get_database()
    record = SelfHealAttempt(
        organization_id=org_id, project_id=project_id, url=url,
        original_selector=original_selector, failure_context=failure_context,
        proposed_selector=chosen.selector_hint, candidate_index=pick.candidate_index,
        ai_confidence=pick.confidence, ai_reasoning=pick.reasoning, source=source,
        live_validation_count=live_count, status="proposed",
    )
    await db.self_heal_attempts.insert_one(record.model_dump(by_alias=True))
    return record


async def approve_heal(
    org_id: str, attempt_id: str, target_file: str | None, target_line: int | None
) -> SelfHealAttempt:
    db = get_database()
    doc = await db.self_heal_attempts.find_one({"_id": attempt_id, "organization_id": org_id})
    if not doc:
        raise AttemptNotFound("Self-heal attempt not found.")
    attempt = SelfHealAttempt.model_validate(doc)

    if attempt.status != "proposed":
        raise InvalidApproval(f"Attempt is already '{attempt.status}' — only a pending proposal can be approved.")
    if attempt.live_validation_count != 1:
        raise InvalidApproval(
            f"Live validation found {attempt.live_validation_count} matching element(s) for the proposed "
            "selector (expected exactly 1) — re-propose before approving."
        )

    applied = False
    if target_file and target_line:
        workspace = workspace_path(attempt.project_id)
        full_path = (workspace / target_file).resolve()
        if not str(full_path).startswith(str(workspace.resolve())):
            raise InvalidApproval("target_file escapes the project workspace — rejected.")
        if not full_path.exists():
            raise InvalidApproval(f"target_file {target_file} does not exist in the workspace.")

        lines = full_path.read_text().splitlines(keepends=True)
        if not (1 <= target_line <= len(lines)):
            raise InvalidApproval(f"target_line {target_line} is out of range for {target_file}.")
        line = lines[target_line - 1]
        if attempt.original_selector not in line:
            raise InvalidApproval(
                f"Line {target_line} of {target_file} does not contain the original selector "
                f"'{attempt.original_selector}' — refusing to write back a mismatched patch."
            )
        lines[target_line - 1] = line.replace(attempt.original_selector, attempt.proposed_selector)
        full_path.write_text("".join(lines))
        applied = True

    await db.self_heal_attempts.update_one(
        {"_id": attempt_id, "organization_id": org_id},
        {"$set": {"status": "approved", "target_file": target_file, "target_line": target_line, "applied": applied}},
    )
    updated = await db.self_heal_attempts.find_one({"_id": attempt_id, "organization_id": org_id})
    return SelfHealAttempt.model_validate(updated)


async def reject_heal(org_id: str, attempt_id: str) -> SelfHealAttempt:
    db = get_database()
    doc = await db.self_heal_attempts.find_one({"_id": attempt_id, "organization_id": org_id})
    if not doc:
        raise AttemptNotFound("Self-heal attempt not found.")
    await db.self_heal_attempts.update_one(
        {"_id": attempt_id, "organization_id": org_id}, {"$set": {"status": "rejected"}}
    )
    updated = await db.self_heal_attempts.find_one({"_id": attempt_id, "organization_id": org_id})
    return SelfHealAttempt.model_validate(updated)


async def list_attempts(org_id: str, project_id: str) -> list[SelfHealAttempt]:
    db = get_database()
    cursor = db.self_heal_attempts.find({"organization_id": org_id, "project_id": project_id}).sort("created_at", -1)
    return [SelfHealAttempt.model_validate(d) async for d in cursor]
