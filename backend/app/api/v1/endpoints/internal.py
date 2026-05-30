from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.auth import require_internal_token
from app.core.config import get_settings
from app.db.session import get_db
from app.db.models import utc_now
from app.schemas import (
    AlertEvaluationResponse,
    SourceDataReleaseActionRequest,
    SourceDataReleaseActionResponse,
    SourceDataReleasesResponse,
    SourceImportAuditResponse,
    SourceImportArtifactsResponse,
    SourceImportExecutionResponse,
    SourceImportPlanResponse,
    SourceRefreshResponse,
)
from app.services.account_service import AccountService
from app.services.life_service import LifeService

router = APIRouter()


def get_account_service() -> AccountService:
    return AccountService()


def get_life_service() -> LifeService:
    return LifeService(get_settings())


@router.post("/alerts/evaluate", response_model=AlertEvaluationResponse)
async def evaluate_alerts(
    force_refresh: bool = Query(False),
    _: None = Depends(require_internal_token),
    db: Session = Depends(get_db),
    account_service: AccountService = Depends(get_account_service),
    life_service: LifeService = Depends(get_life_service),
):
    domains = await life_service.get_domain_signals(db, force_refresh=force_refresh)
    return account_service.evaluate_all_users(db, domains)


@router.post("/source-refresh", response_model=SourceRefreshResponse)
async def refresh_sources(
    force_refresh: bool = Query(True),
    evaluate_alerts: bool = Query(False),
    _: None = Depends(require_internal_token),
    db: Session = Depends(get_db),
    account_service: AccountService = Depends(get_account_service),
    life_service: LifeService = Depends(get_life_service),
):
    domains = await life_service.get_domain_signals(db, force_refresh=force_refresh)
    validation = life_service.source_validation(db)
    import_audit = life_service.source_import_audit(db)
    import_plan = life_service.source_import_plan(db)
    pipeline = await life_service.pipeline(db)
    alert_evaluation = account_service.evaluate_all_users(db, domains) if evaluate_alerts else None
    degraded_domains = [domain.key for domain in domains if domain.status == "degraded"]
    offline_domains = [domain.key for domain in domains if domain.status == "offline"]
    if offline_domains:
        refresh_status = "offline"
    elif degraded_domains or validation.status != "healthy" or import_audit.status != "healthy":
        refresh_status = "degraded"
    else:
        refresh_status = "healthy"

    actions = []
    if validation.status != "healthy":
        actions.append("Review /life/source-validation before promoting new scoring inputs.")
    if import_audit.status != "healthy":
        actions.append("Review /internal/source-import-audit before promoting seeded import families.")
    if import_plan.status != "healthy":
        actions.append("Review /internal/source-import-plan before replacing seed importers with direct source jobs.")
    if degraded_domains:
        actions.append(f"Inspect degraded domains: {', '.join(degraded_domains)}.")
    if offline_domains:
        actions.append(f"Escalate offline domains: {', '.join(offline_domains)}.")
    if alert_evaluation is None:
        actions.append("Alert evaluation skipped for this refresh run.")
    elif alert_evaluation.notifications_created:
        actions.append(f"Created {alert_evaluation.notifications_created} notification(s) from refreshed signals.")
    else:
        actions.append("Alert evaluation completed without new notifications.")
    if not actions:
        actions.append("Refresh completed with no operator action required.")

    return SourceRefreshResponse(
        generated_at=utc_now(),
        refresh_status=refresh_status,
        domains_refreshed=len(domains),
        degraded_domains=degraded_domains,
        offline_domains=offline_domains,
        pipeline=pipeline,
        source_validation=validation,
        import_audit=import_audit,
        import_plan=import_plan,
        alert_evaluation=alert_evaluation,
        actions=actions,
    )


@router.post("/source-import-audit", response_model=SourceImportAuditResponse)
def audit_source_imports(
    persist: bool = Query(True),
    _: None = Depends(require_internal_token),
    db: Session = Depends(get_db),
    life_service: LifeService = Depends(get_life_service),
):
    return life_service.source_import_audit(db, persist=persist)


@router.post("/source-import-plan", response_model=SourceImportPlanResponse)
def source_import_plan(
    persist: bool = Query(True),
    _: None = Depends(require_internal_token),
    db: Session = Depends(get_db),
    life_service: LifeService = Depends(get_life_service),
):
    return life_service.source_import_plan(db, persist=persist)


@router.post("/source-import-run", response_model=SourceImportExecutionResponse)
async def run_source_import(
    live_fetch: bool = Query(False),
    promote: bool = Query(False),
    persist: bool = Query(True),
    include_official_cost: bool = Query(False),
    _: None = Depends(require_internal_token),
    db: Session = Depends(get_db),
    life_service: LifeService = Depends(get_life_service),
):
    if promote and not live_fetch:
        raise HTTPException(status_code=400, detail="promote=true requires live_fetch=true")
    if promote and not persist:
        raise HTTPException(status_code=400, detail="promote=true requires persist=true")
    if promote and include_official_cost:
        raise HTTPException(status_code=400, detail="official cost/import direct run is review-only and cannot be promoted")
    return await life_service.source_import_run(
        db,
        live_fetch=live_fetch,
        promote=promote,
        persist=persist,
        include_official_cost=include_official_cost,
    )


@router.get("/source-import-artifacts", response_model=SourceImportArtifactsResponse)
def list_source_import_artifacts(
    run_key: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    include_records: bool = Query(False),
    _: None = Depends(require_internal_token),
    db: Session = Depends(get_db),
    life_service: LifeService = Depends(get_life_service),
):
    return life_service.source_import_artifacts(db, run_key=run_key, limit=limit, include_records=include_records)


@router.get("/source-data-releases", response_model=SourceDataReleasesResponse)
def list_source_data_releases(
    limit: int = Query(20, ge=1, le=100),
    _: None = Depends(require_internal_token),
    db: Session = Depends(get_db),
    life_service: LifeService = Depends(get_life_service),
):
    return life_service.source_data_releases(db, limit=limit)


@router.post("/source-data-releases/{release_key}/notes", response_model=SourceDataReleaseActionResponse)
def add_source_data_release_note(
    release_key: str,
    payload: SourceDataReleaseActionRequest = Body(...),
    _: None = Depends(require_internal_token),
    db: Session = Depends(get_db),
    life_service: LifeService = Depends(get_life_service),
):
    try:
        return life_service.add_source_data_release_note(db, release_key=release_key, note=payload.note)
    except ValueError as exc:
        status_code = 404 if "not found" in str(exc).lower() else 400
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc


@router.post("/source-data-releases/{release_key}/rollback", response_model=SourceDataReleaseActionResponse)
def rollback_source_data_release(
    release_key: str,
    payload: SourceDataReleaseActionRequest | None = Body(None),
    _: None = Depends(require_internal_token),
    db: Session = Depends(get_db),
    life_service: LifeService = Depends(get_life_service),
):
    request = payload or SourceDataReleaseActionRequest()
    try:
        return life_service.rollback_source_data_release(
            db,
            release_key=release_key,
            note=request.note,
            reactivate_previous=request.reactivate_previous,
        )
    except ValueError as exc:
        status_code = 404 if "not found" in str(exc).lower() else 400
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc
