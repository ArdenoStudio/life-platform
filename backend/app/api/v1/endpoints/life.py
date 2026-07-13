from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.schemas import (
    AffordabilityResponse,
    AreaScoreResponse,
    AtlasResponse,
    CostCommandResponse,
    I18nResponse,
    InsightsResponse,
    LifeOverviewResponse,
    PipelineResponse,
    PublicSourceReleaseResponse,
    RetailOffersResponse,
    SearchResult,
    SourceValidationResponse,
    TransportResponse,
    UtilitiesResponse,
    WeatherRiskResponse,
)
from app.services.life_service import LifeService
from app.services.living_atlas_data import DISTRICTS

router = APIRouter()

VALID_OVERVIEW_DISTRICTS = set(DISTRICTS) | {"Sri Lanka"}


def get_life_service() -> LifeService:
    return LifeService(get_settings())


@router.get("/overview", response_model=LifeOverviewResponse)
async def life_overview(
    district: str = Query("Sri Lanka"),
    profile: str = Query("family", pattern="^(single|family|commuter)$"),
    db: Session = Depends(get_db),
    service: LifeService = Depends(get_life_service),
):
    if district not in VALID_OVERVIEW_DISTRICTS:
        raise HTTPException(status_code=422, detail=f"Unknown district: {district}")
    return await service.overview(db, district=district, profile=profile)


@router.get("/domains")
async def life_domains(
    force_refresh: bool = Query(False),
    db: Session = Depends(get_db),
    service: LifeService = Depends(get_life_service),
):
    return {"items": await service.get_domain_signals(db, force_refresh=force_refresh)}


@router.get("/search", response_model=list[SearchResult])
async def life_search(
    q: str = Query(..., min_length=1, max_length=80),
    db: Session = Depends(get_db),
    service: LifeService = Depends(get_life_service),
):
    return await service.search(db, q)


@router.get("/affordability", response_model=AffordabilityResponse)
async def life_affordability(
    district: str = Query("Sri Lanka"),
    profile: str = Query("family", pattern="^(single|family|commuter)$"),
    db: Session = Depends(get_db),
    service: LifeService = Depends(get_life_service),
):
    domains = await service.get_domain_signals(db)
    return service.affordability_from_signals(db, domains, district=district, profile=profile)


@router.get("/trends")
def life_trends(
    domain: str | None = Query(None, pattern="^(food|fuel|property|vehicle|utilities|gas|transport|retail|indices|areas|weather)$"),
    days: int = Query(90, ge=1, le=3650),
    db: Session = Depends(get_db),
    service: LifeService = Depends(get_life_service),
):
    return service.trends(db, domain=domain, days=days)


@router.get("/pipeline", response_model=PipelineResponse)
async def life_pipeline(
    db: Session = Depends(get_db),
    service: LifeService = Depends(get_life_service),
):
    return await service.pipeline(db)


@router.get("/source-validation", response_model=SourceValidationResponse)
def life_source_validation(
    db: Session = Depends(get_db),
    service: LifeService = Depends(get_life_service),
):
    return service.source_validation(db)


@router.get("/source-release", response_model=PublicSourceReleaseResponse)
def life_source_release(
    db: Session = Depends(get_db),
    service: LifeService = Depends(get_life_service),
):
    return service.public_source_release(db)


@router.get("/cost-command", response_model=CostCommandResponse)
async def life_cost_command(
    district: str = Query("Sri Lanka"),
    profile: str = Query("family", pattern="^(single|family|commuter)$"),
    locale: str = Query("en", pattern="^(en|si|ta)$"),
    db: Session = Depends(get_db),
    service: LifeService = Depends(get_life_service),
):
    return await service.cost_command(db, district=district, profile=profile, locale=locale)


@router.get("/atlas", response_model=AtlasResponse)
def life_atlas(
    district: str = Query("Sri Lanka"),
    profile: str = Query("family", pattern="^(single|family|commuter)$"),
    locale: str = Query("en", pattern="^(en|si|ta)$"),
    db: Session = Depends(get_db),
    service: LifeService = Depends(get_life_service),
):
    return service.atlas(db, district=district, profile=profile, locale=locale)


@router.get("/areas/score", response_model=AreaScoreResponse)
def life_area_score(
    district: str = Query("Sri Lanka"),
    profile: str = Query("family", pattern="^(single|family|commuter)$"),
    locale: str = Query("en", pattern="^(en|si|ta)$"),
    db: Session = Depends(get_db),
    service: LifeService = Depends(get_life_service),
):
    return service.area_score(db, district=district, profile=profile, locale=locale)


@router.get("/utilities", response_model=UtilitiesResponse)
def life_utilities(
    district: str = Query("Sri Lanka"),
    db: Session = Depends(get_db),
    service: LifeService = Depends(get_life_service),
):
    return service.utilities(db, district=district)


@router.get("/transport", response_model=TransportResponse)
def life_transport(
    from_area: str = Query("Colombo", alias="from"),
    to_area: str = Query("Kandy", alias="to"),
    db: Session = Depends(get_db),
    service: LifeService = Depends(get_life_service),
):
    return service.transport(db, from_area=from_area, to_area=to_area)


@router.get("/retail/offers", response_model=RetailOffersResponse)
def life_retail_offers(
    q: str | None = Query(None, max_length=80),
    district: str = Query("Sri Lanka"),
    db: Session = Depends(get_db),
    service: LifeService = Depends(get_life_service),
):
    return service.retail_offers(db, query=q, district=district)


@router.get("/weather-risk", response_model=WeatherRiskResponse)
def life_weather_risk(
    district: str = Query("Sri Lanka"),
    db: Session = Depends(get_db),
    service: LifeService = Depends(get_life_service),
):
    return service.weather_risk(db, district=district)


@router.get("/insights", response_model=InsightsResponse)
async def life_insights(
    domain: str | None = Query(None, pattern="^(food|fuel|property|vehicle|utilities|gas|transport|retail|indices|areas|weather|sources)$"),
    db: Session = Depends(get_db),
    service: LifeService = Depends(get_life_service),
):
    return await service.insights(db, domain=domain)


@router.get("/i18n", response_model=I18nResponse)
def life_i18n(
    locale: str = Query("en", pattern="^(en|si|ta)$"),
    service: LifeService = Depends(get_life_service),
):
    return service.i18n(locale=locale)
