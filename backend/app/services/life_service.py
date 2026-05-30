from datetime import datetime, timedelta, timezone
from typing import Any, Iterable

import httpx
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.adapters import (
    AreaScoreAdapter,
    FoodAdapter,
    FuelAdapter,
    GasAdapter,
    IndicesAdapter,
    PropertyAdapter,
    RetailAdapter,
    TransportAdapter,
    UtilitiesAdapter,
    VehicleAdapter,
    WeatherRiskAdapter,
)
from app.core.config import Settings
from app.db.models import (
    AreaScoreSnapshot,
    DistrictProfileSnapshot,
    Domain,
    DomainSnapshot,
    IntegrationRun,
    LifeIndexSnapshot,
    PublicInsightSnapshot,
    RetailOfferSnapshot,
    SourceDataRelease,
    SourceImportArtifact,
    SourceRegistry,
    TariffSnapshot,
    TransportFareSnapshot,
    WeatherRiskSnapshot,
    utc_now,
)
from app.schemas import (
    AffordabilityBreakdownItem,
    AffordabilityResponse,
    AreaScoreComponent,
    AreaScoreResponse,
    AtlasResponse,
    CostCommandItem,
    CostCommandResponse,
    DomainHighlight,
    DomainSignal,
    DistrictProfile,
    I18nResponse,
    InsightsResponse,
    LifeOverviewResponse,
    PipelineDomainStatus,
    PipelineResponse,
    PublicInsight,
    PublicSourceReleaseResponse,
    RetailOffer,
    RetailOffersResponse,
    SearchResult,
    SourceDataReleaseActionResponse,
    SourceDataReleasesResponse,
    SourceDataReleaseSummary,
    SourceImportAuditResponse,
    SourceImportArtifactsResponse,
    SourceImportArtifactSummary,
    SourceImportCheck,
    SourceImportExecutionResponse,
    SourceImportPlanResponse,
    SourceReference,
    SourceValidationResponse,
    TransportOption,
    TransportResponse,
    UtilitiesResponse,
    UtilityItem,
    WeatherRiskObservation,
    WeatherRiskResponse,
)
from app.services.living_atlas_data import (
    AREA_BASE,
    DISTRICTS,
    DOMAIN_TRANSLATIONS,
    FOOD_PROTEIN_BASKET,
    GAS_TARIFFS,
    I18N_LABELS,
    OFFICIAL_IMPORT_CONTEXT_SOURCE_KEYS,
    RETAIL_OFFERS,
    SOURCE_DEFINITIONS,
    TRANSPORT_OPTIONS,
    UTILITY_TARIFFS,
    DISTRICT_WEATHER_STATIONS,
    _weather_risk_score,
    _weather_severity,
    district_profiles,
    grade_for,
    source_governance,
    source_refs,
    source_validation_report,
    weather_risk_observations,
)


PROFILE_FACTORS = {
    "single": {"food_baskets": 2.1, "fuel_litres": 28, "housing": 0.55, "vehicle": 0.35, "utilities": 18000},
    "family": {"food_baskets": 4.33, "fuel_litres": 55, "housing": 1.0, "vehicle": 0.75, "utilities": 32000},
    "commuter": {"food_baskets": 2.6, "fuel_litres": 85, "housing": 0.7, "vehicle": 0.85, "utilities": 22000},
}


DISTRICT_RENT_BASE = {
    "Colombo": 95000,
    "Gampaha": 62000,
    "Kandy": 58000,
    "Galle": 56000,
    "Jaffna": 52000,
    "Matara": 48000,
    "Kurunegala": 46000,
    "Sri Lanka": 55000,
}


LOCALES = {"en", "si", "ta"}

COST_ITEM_LABELS = {
    "si": {
        "education": "අධ්‍යාපන සංචිතය",
        "food": "ආහාර සහ සිල්ලර",
        "fuel": "ඉන්ධන",
        "gas": "LPG ගෑස්",
        "health": "සෞඛ්‍ය සහ පුද්ගලික සත්කාර",
        "household_goods": "ගෘහ භාණ්ඩ",
        "housing": "නිවාස පීඩනය",
        "transport": "පොදු ප්‍රවාහන සංචිතය",
        "utilities": "උපයෝගිතා සහ සන්නිවේදන",
        "vehicle": "වාහන හිමිකම් සංචිතය",
    },
    "ta": {
        "education": "கல்வி இருப்பு",
        "food": "உணவு மற்றும் மளிகை",
        "fuel": "எரிபொருள்",
        "gas": "LPG எரிவாயு",
        "health": "சுகாதாரம் மற்றும் தனிப்பட்ட பராமரிப்பு",
        "household_goods": "வீட்டு பொருட்கள்",
        "housing": "வீட்டு அழுத்தம்",
        "transport": "பொது போக்குவரத்து இருப்பு",
        "utilities": "பயன்பாடுகள் மற்றும் தொடர்பாடல்",
        "vehicle": "வாகன உரிமை இருப்பு",
    },
}

AREA_COMPONENT_LABELS = {
    "si": {
        "density": "ජනඝනත්ව පීඩනය",
        "food": "ආහාර බාස්කට් පීඩනය",
        "household_energy": "ගෘහ බලශක්ති ආවරණය",
        "rent": "කුලී පීඩනය",
        "source": "මූලාශ්‍ර ආවරණය",
        "transport": "ප්‍රවාහන පීඩනය",
        "utilities": "උපයෝගිතා පීඩනය",
        "weather": "කාලගුණ හා අවදානම් පීඩනය",
    },
    "ta": {
        "density": "மக்கள் அடர்த்தி அழுத்தம்",
        "food": "உணவு கூடை அழுத்தம்",
        "household_energy": "குடும்ப ஆற்றல் கவரேஜ்",
        "rent": "வாடகை அழுத்தம்",
        "source": "மூலக் கவரேஜ்",
        "transport": "போக்குவரத்து அழுத்தம்",
        "utilities": "பயன்பாட்டு அழுத்தம்",
        "weather": "வானிலை மற்றும் ஆபத்து அழுத்தம்",
    },
}

PROFILE_LABELS = {
    "si": {"single": "තනි", "family": "පවුල", "commuter": "ගමන්කරන"},
    "ta": {"single": "ஒற்றை", "family": "குடும்பம்", "commuter": "பயணி"},
}

DOMAIN_SEARCH_HINTS = {
    "vehicle": {
        "alto",
        "aqua",
        "axio",
        "car",
        "cars",
        "civic",
        "fit",
        "hybrid",
        "honda",
        "jeep",
        "lancer",
        "mazda",
        "prado",
        "suzuki",
        "toyota",
        "van",
        "vehicle",
        "vehicles",
        "vezel",
        "wagon",
    },
    "food": {
        "beef",
        "big onion",
        "bread",
        "chicken",
        "coconut",
        "dhal",
        "egg",
        "fish",
        "food",
        "grocery",
        "milk",
        "onion",
        "rice",
        "samba",
        "sugar",
        "vegetable",
    },
    "fuel": {"diesel", "fuel", "kerosene", "octane", "petrol", "trip"},
    "property": {"apartment", "house", "land", "property", "rent", "rental", "sale"},
    "utilities": {"electricity", "pucsl", "tariff", "utility", "water"},
    "gas": {"gas", "laugfs", "litro", "lpg"},
    "transport": {"bus", "commute", "fare", "rail", "train", "transport"},
    "retail": {"offer", "offers", "retail", "supermarket"},
    "weather": {"dmc", "flood", "rain", "risk", "river", "weather"},
}


def normalize_locale(locale: str) -> str:
    return locale if locale in LOCALES else "en"


def localized_cost_label(locale: str, key: str, fallback: str) -> str:
    return COST_ITEM_LABELS.get(locale, {}).get(key, fallback)


def localized_area_label(locale: str, key: str, fallback: str) -> str:
    return AREA_COMPONENT_LABELS.get(locale, {}).get(key, fallback)


def localized_profile_label(locale: str, profile: str) -> str:
    return PROFILE_LABELS.get(locale, {}).get(profile, profile)


def atlas_narrative(locale: str, district: str, score: float, profile: str) -> str:
    profile_label = localized_profile_label(locale, profile)
    if locale == "si":
        return f"{district} {profile_label} පැතිකඩ සඳහා {score}/100ක් ලබා ගනී. කුලිය, ආහාර, ප්‍රවාහනය, උපයෝගිතා සහ මූලාශ්‍ර ආවරණය වෙන වෙනම පෙන්වයි."
    if locale == "ta":
        return f"{district} {profile_label} சுயவிவரத்திற்கு {score}/100 பெறுகிறது. வாடகை, உணவு, போக்குவரத்து, பயன்பாடுகள் மற்றும் மூலக் கவரேஜ் தனியாக காட்டப்படுகின்றன."
    return f"{district} scores {score}/100 for the {profile} profile, with rent, food, transport, utilities, and source coverage shown separately."


def clamp_score(value: float, *, lower: float = 35, upper: float = 92) -> float:
    return round(max(lower, min(upper, value)), 1)


def parse_source_datetime(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value, tz=timezone.utc)
    if isinstance(value, str):
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    return None


def query_tokens(query: str) -> set[str]:
    return {part for part in query.replace("/", " ").replace("-", " ").lower().split() if part}


def infer_search_domains(query: str) -> set[str]:
    normalized = " ".join(query.lower().split())
    tokens = query_tokens(normalized)
    matches: set[str] = set()
    for domain, hints in DOMAIN_SEARCH_HINTS.items():
        if tokens.intersection(hints) or any(" " in hint and hint in normalized for hint in hints):
            matches.add(domain)
    return matches


def food_protein_basket_signal() -> dict[str, Any]:
    weekly_lkr = sum(item["price_lkr"] * item["weekly_quantity"] for item in FOOD_PROTEIN_BASKET)
    protein_g = sum(item["protein_g_per_unit"] * item["weekly_quantity"] for item in FOOD_PROTEIN_BASKET)
    serving_count = max(round(protein_g / 25), 1)
    source_keys = sorted({source_key for item in FOOD_PROTEIN_BASKET for source_key in item["source_keys"]})
    return {
        "weekly_lkr": round(weekly_lkr, 0),
        "protein_g": round(protein_g, 0),
        "serving_count": serving_count,
        "cost_per_serving_lkr": round(weekly_lkr / serving_count, 0),
        "source_keys": source_keys,
        "items": FOOD_PROTEIN_BASKET,
    }


class LifeService:
    _cache: dict[str, tuple[datetime, list[DomainSignal]]] = {}

    def __init__(self, settings: Settings):
        self.settings = settings
        self.adapters = [
            FoodAdapter(settings),
            FuelAdapter(settings),
            PropertyAdapter(settings),
            VehicleAdapter(settings),
            UtilitiesAdapter(settings),
            GasAdapter(settings),
            TransportAdapter(settings),
            RetailAdapter(settings),
            IndicesAdapter(settings),
            WeatherRiskAdapter(settings),
            AreaScoreAdapter(settings),
        ]

    async def get_domain_signals(self, db: Session, *, force_refresh: bool = False) -> list[DomainSignal]:
        cache_key = "domains"
        now = utc_now()
        cached = self._cache.get(cache_key)
        if cached and not force_refresh:
            cached_at, payload = cached
            if (now - cached_at).total_seconds() < self.settings.life_cache_seconds:
                return payload

        await self.ensure_domains(db)
        self.ensure_sources(db)
        timeout = httpx.Timeout(self.settings.upstream_timeout_seconds)
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            signals = [await self._fetch_adapter(adapter, client, db) for adapter in self.adapters]

        self._cache[cache_key] = (now, signals)
        self.store_domain_snapshots(db, signals)
        return signals

    async def _fetch_adapter(self, adapter, client: httpx.AsyncClient, db: Session) -> DomainSignal:
        run = IntegrationRun(domain_key=adapter.key, status="running")
        db.add(run)
        db.commit()
        db.refresh(run)
        try:
            signal = await adapter.fetch(client)
            run.status = "completed" if signal.status != "offline" else "failed"
            run.finished_at = utc_now()
            run.payload_summary = {
                "status": signal.status,
                "health_score": signal.health_score,
                "metrics_count": len(signal.metrics),
                "errors": signal.errors,
            }
            db.commit()
            return signal
        except Exception as exc:
            run.status = "failed"
            run.finished_at = utc_now()
            run.error_message = str(exc)
            db.commit()
            return adapter.degraded_fixture(str(exc))

    async def ensure_domains(self, db: Session) -> None:
        self.ensure_domains_sync(db)

    def ensure_domains_sync(self, db: Session) -> None:
        changed = False
        for adapter in self.adapters:
            existing = db.get(Domain, adapter.key)
            if existing is None:
                db.add(
                    Domain(
                        key=adapter.key,
                        label=adapter.label,
                        category=adapter.category,
                        api_base=adapter.api_base,
                        homepage_url=adapter.homepage_url,
                        enabled=True,
                    )
                )
                changed = True
            else:
                existing.label = adapter.label
                existing.category = adapter.category
                existing.api_base = adapter.api_base
                existing.homepage_url = adapter.homepage_url
                existing.updated_at = utc_now()
                changed = True
        if changed:
            db.commit()

    def ensure_sources(self, db: Session) -> None:
        changed = False
        now = utc_now()
        for row in SOURCE_DEFINITIONS:
            governance = source_governance(row)
            existing = db.get(SourceRegistry, row["key"])
            if existing is None:
                db.add(
                    SourceRegistry(
                        key=row["key"],
                        label=row["label"],
                        source_type=row["source_type"],
                        domain_key=row["domain_key"],
                        url=row["url"],
                        confidence=row["confidence"],
                        freshness_note=row["freshness_note"],
                        owner=governance["owner"],
                        collection_method=governance["collection_method"],
                        license_status=governance["license_status"],
                        review_status=governance["review_status"],
                        refresh_cadence=governance["refresh_cadence"],
                        governance_note=governance["governance_note"],
                        status="healthy",
                        locale_labels=row.get("labels", {}),
                        last_checked_at=now,
                    )
                )
                changed = True
            else:
                existing.label = row["label"]
                existing.source_type = row["source_type"]
                existing.domain_key = row["domain_key"]
                existing.url = row["url"]
                existing.confidence = row["confidence"]
                existing.freshness_note = row["freshness_note"]
                existing.owner = governance["owner"]
                existing.collection_method = governance["collection_method"]
                existing.license_status = governance["license_status"]
                existing.review_status = governance["review_status"]
                existing.refresh_cadence = governance["refresh_cadence"]
                existing.governance_note = governance["governance_note"]
                existing.locale_labels = row.get("labels", {})
                existing.updated_at = now
                changed = True
        if changed:
            db.commit()

    def store_domain_snapshots(self, db: Session, signals: Iterable[DomainSignal]) -> None:
        for signal in signals:
            db.add(
                DomainSnapshot(
                    domain_key=signal.key,
                    status=signal.status,
                    health_score=signal.health_score,
                    summary={"text": signal.summary, "freshness_note": signal.freshness_note, "errors": signal.errors},
                    metrics=[metric.model_dump() for metric in signal.metrics],
                    highlights=[highlight.model_dump() for highlight in signal.highlights],
                    source_updated_at=signal.last_updated_at,
                    observed_at=signal.observed_at,
                )
            )
        db.commit()

    async def overview(self, db: Session, *, district: str = "Sri Lanka", profile: str = "family") -> LifeOverviewResponse:
        domains = await self.get_domain_signals(db)
        affordability = self.affordability_from_signals(db, domains, district=district, profile=profile)
        health = self.source_health(domains)
        movers = self.top_movers(domains)
        freshness_note = "Live-powered summaries with short caching; each domain exposes its own source freshness."
        return LifeOverviewResponse(
            generated_at=utc_now(),
            headline="Ariva reads Sri Lanka living signals across food, fuel, property, vehicles, and daily costs.",
            freshness_note=freshness_note,
            domains=domains,
            affordability=affordability,
            top_movers=movers,
            source_health=health,
        )

    def affordability_from_signals(
        self,
        db: Session,
        domains: list[DomainSignal],
        *,
        district: str = "Sri Lanka",
        profile: str = "family",
    ) -> AffordabilityResponse:
        if profile not in PROFILE_FACTORS:
            profile = "family"
        factors = PROFILE_FACTORS[profile]
        domain_map = {domain.key: domain for domain in domains}

        food_basket = self._metric_value(domain_map.get("food"), "Essentials basket") or 8650
        petrol_92 = self._metric_value(domain_map.get("fuel"), "Petrol 92") or 410
        avg_property_price = self._metric_value(domain_map.get("property"), "Average price")
        avg_vehicle_price = self._metric_value(domain_map.get("vehicle"), "Average price")

        rent_base = DISTRICT_RENT_BASE.get(district, DISTRICT_RENT_BASE.get("Sri Lanka", 55000))
        if avg_property_price and avg_property_price > 1_000_000:
            # A conservative monthly rental proxy when a rental endpoint is not available.
            rent_base = max(rent_base, min(avg_property_price * 0.0022, 185000))

        vehicle_monthly = 0
        if avg_vehicle_price and avg_vehicle_price > 500_000:
            vehicle_monthly = min(max(avg_vehicle_price * 0.0045, 22000), 85000)
        else:
            vehicle_monthly = 28000

        food_monthly = food_basket * factors["food_baskets"]
        fuel_monthly = petrol_92 * factors["fuel_litres"]
        housing_monthly = rent_base * factors["housing"]
        vehicle_monthly = vehicle_monthly * factors["vehicle"]
        utility_seed_total = sum(item["amount_lkr"] for item in UTILITY_TARIFFS if item["key"] in {"electricity-family", "water-domestic"})
        utility_profile_factor = 1.0 if profile == "family" else 0.68 if profile == "single" else 0.78
        utilities_monthly = max(utility_seed_total * utility_profile_factor, factors["utilities"] * 0.72)
        commuter_bus_fare = next(
            (item["fare_lkr"] for item in TRANSPORT_OPTIONS if item["mode"] == "bus" and item["from_area"] == "Gampaha" and item["to_area"] == "Colombo"),
            220,
        )
        public_transport_monthly = commuter_bus_fare * (44 if profile == "commuter" else 28 if profile == "single" else 40)

        breakdown = [
            AffordabilityBreakdownItem(
                key="food",
                label="Food and groceries",
                monthly_lkr=round(food_monthly, 0),
                confidence="medium",
                source_domains=["food"],
                note="Derived from FoodLK essentials basket multiplied by household profile.",
            ),
            AffordabilityBreakdownItem(
                key="housing",
                label="Housing pressure",
                monthly_lkr=round(housing_monthly, 0),
                confidence="low",
                source_domains=["property"],
                note="Uses a rental proxy until district rental-yield signals are normalized centrally.",
            ),
            AffordabilityBreakdownItem(
                key="fuel",
                label="Fuel",
                monthly_lkr=round(fuel_monthly, 0),
                confidence="high",
                source_domains=["fuel"],
                note="Uses latest Petrol 92 rate and profile-specific litres per month.",
            ),
            AffordabilityBreakdownItem(
                key="vehicle",
                label="Vehicle ownership reserve",
                monthly_lkr=round(vehicle_monthly, 0),
                confidence="low",
                source_domains=["vehicle"],
                note="Planning reserve derived from vehicle market average with CBSL/customs import-cost context; not a loan or tax quote.",
            ),
            AffordabilityBreakdownItem(
                key="utilities",
                label="Utilities and communications",
                monthly_lkr=round(utilities_monthly, 0),
                confidence="medium",
                source_domains=["utilities"],
                note="Uses source-labelled PUCSL electricity and NWSDB water planning rows; telecom remains outside the v1 model.",
            ),
            AffordabilityBreakdownItem(
                key="transport",
                label="Public transport buffer",
                monthly_lkr=round(public_transport_monthly, 0),
                confidence="medium",
                source_domains=["transport"],
                note="Uses NTC bus-fare planning rows for commute buffering; rail and route freshness remain staged.",
            ),
        ]
        total = round(sum(item.monthly_lkr for item in breakdown), 0)
        confidence = "medium" if all(domain.status != "offline" for domain in domains) else "low"
        response = AffordabilityResponse(
            district=district,
            profile=profile,
            total_monthly_lkr=total,
            confidence=confidence,
            generated_at=utc_now(),
            breakdown=breakdown,
            assumptions=[
                "This is a planning index, not financial advice or a formal cost-of-living statistic.",
                "Food and fuel use upstream price signals; housing and vehicle costs are conservative v1 proxies.",
                "Utility and transport rows are source-labelled planning inputs; direct tariff/import extraction still requires operator review.",
            ],
        )
        db.add(
            LifeIndexSnapshot(
                profile=profile,
                district=district,
                total_lkr=total,
                confidence=confidence,
                breakdown={item.key: item.model_dump() for item in breakdown},
                assumptions=response.assumptions,
                observed_at=response.generated_at,
            )
        )
        db.commit()
        return response

    def source_health(self, domains: list[DomainSignal]) -> dict[str, int | float]:
        healthy = sum(1 for domain in domains if domain.status == "healthy")
        degraded = sum(1 for domain in domains if domain.status == "degraded")
        offline = sum(1 for domain in domains if domain.status == "offline")
        avg_score = round(sum(domain.health_score for domain in domains) / max(len(domains), 1), 1)
        return {"healthy": healthy, "degraded": degraded, "offline": offline, "total": len(domains), "average_score": avg_score}

    def top_movers(self, domains: list[DomainSignal]) -> list[DomainHighlight]:
        rows: list[DomainHighlight] = []
        for domain in domains:
            rows.extend(domain.highlights[:2])
        return rows[:8]

    async def search(self, db: Session, query: str) -> list[SearchResult]:
        domains = await self.get_domain_signals(db)
        q = query.strip().lower()
        if not q:
            return []
        hinted_domains = infer_search_domains(q)
        results: list[SearchResult] = []
        tokens = query_tokens(q)
        if tokens.intersection({"protein", "nutrition", "meal", "meals", "fish", "egg", "eggs", "dhal", "chicken"}):
            protein = food_protein_basket_signal()
            results.append(
                SearchResult(
                    domain="food",
                    label="FoodLK: Protein basket",
                    description=(
                        f"LKR {protein['weekly_lkr']:,.0f}/week for about {protein['serving_count']} "
                        f"protein servings from reviewed food, nutrition, and fisheries context."
                    ),
                    href="/?page=intelligence",
                    score=118,
                )
            )
        for domain in domains:
            domain_is_hinted = domain.key in hinted_domains
            haystacks = [domain.label, domain.category, domain.summary, *(h.label for h in domain.highlights)]
            if any(q in str(value).lower() for value in haystacks):
                results.append(
                    SearchResult(
                        domain=domain.key,
                        label=domain.label,
                        description=domain.summary,
                        href=f"/domains/{domain.key}",
                        score=110 if domain_is_hinted else 90,
                    )
                )
            elif domain_is_hinted:
                results.append(
                    SearchResult(
                        domain=domain.key,
                        label=domain.label,
                        description=domain.summary,
                        href=f"/domains/{domain.key}",
                        score=95,
                    )
                )
            for metric in domain.metrics:
                if q in metric.label.lower():
                    results.append(
                        SearchResult(
                            domain=domain.key,
                            label=f"{domain.label}: {metric.label}",
                            description=f"{metric.value} {metric.unit or ''}".strip(),
                            href=f"/domains/{domain.key}",
                            score=100 if domain_is_hinted else 80,
                        )
                    )
            for item in domain.top_items:
                label = str(item.get("label") or item.get("item_name") or item.get("fuel_type") or item.get("title") or "")
                if label and q in label.lower():
                    results.append(
                        SearchResult(
                            domain=domain.key,
                            label=label,
                            description=f"Found in {domain.label}",
                            href=f"/domains/{domain.key}",
                            score=90 if domain_is_hinted else 70,
                        )
                    )
        deduped: dict[tuple[str, str], SearchResult] = {}
        for result in results:
            key = (result.domain, result.label)
            if key not in deduped or result.score > deduped[key].score:
                deduped[key] = result
        return sorted(deduped.values(), key=lambda result: result.score, reverse=True)[:20]

    def trends(self, db: Session, domain: str | None = None, days: int = 90) -> dict[str, Any]:
        cutoff = utc_now() - timedelta(days=days)
        query = select(DomainSnapshot).where(DomainSnapshot.observed_at >= cutoff).order_by(DomainSnapshot.observed_at.asc())
        if domain:
            query = query.where(DomainSnapshot.domain_key == domain)
        snapshots = db.scalars(query).all()
        return {
            "domain": domain or "all",
            "days": days,
            "points": [
                {
                    "domain": snapshot.domain_key,
                    "observed_at": snapshot.observed_at.isoformat(),
                    "health_score": snapshot.health_score,
                    "status": snapshot.status,
                    "metrics": snapshot.metrics,
                }
                for snapshot in snapshots
            ],
        }

    async def pipeline(self, db: Session) -> PipelineResponse:
        domains = await self.get_domain_signals(db)
        health = self.source_health(domains)
        if health["offline"]:
            overall = "offline"
        elif health["degraded"]:
            overall = "degraded"
        else:
            overall = "healthy"
        recent_runs = db.scalars(select(IntegrationRun).order_by(desc(IntegrationRun.started_at)).limit(20)).all()
        return PipelineResponse(
            generated_at=utc_now(),
            overall_status=overall,
            domains=[
                PipelineDomainStatus(
                    domain=domain.key,
                    label=domain.label,
                    status=domain.status,
                    health_score=domain.health_score,
                    last_updated_at=domain.last_updated_at,
                    freshness_note=domain.freshness_note,
                    errors=domain.errors,
                )
                for domain in domains
            ],
            recent_runs=[
                {
                    "id": run.id,
                    "domain": run.domain_key,
                    "status": run.status,
                    "started_at": run.started_at.isoformat() if run.started_at else None,
                    "finished_at": run.finished_at.isoformat() if run.finished_at else None,
                    "error_message": run.error_message,
                }
                for run in recent_runs
            ],
        )

    async def cost_command(
        self,
        db: Session,
        *,
        district: str = "Sri Lanka",
        profile: str = "family",
        locale: str = "en",
    ) -> CostCommandResponse:
        locale = normalize_locale(locale)
        profile = profile if profile in PROFILE_FACTORS else "family"
        domains = await self.get_domain_signals(db)
        affordability = self.affordability_from_signals(db, domains, district=district, profile=profile)
        gas_monthly = GAS_TARIFFS[0]["amount_lkr"] * (1.15 if profile == "family" else 0.65)
        health_monthly = 12500 if profile == "single" else 28500 if profile == "family" else 17000
        education_monthly = 32000 if profile == "family" else 5500
        household_goods = 14500 if profile == "family" else 7800
        protein = food_protein_basket_signal()

        extra_items = [
            CostCommandItem(
                key="gas",
                label=localized_cost_label(locale, "gas", "LPG gas"),
                monthly_lkr=round(gas_monthly, 0),
                weekly_lkr=round(gas_monthly / 4.33, 0),
                confidence="medium",
                source_type="official",
                source_keys=["litro-lpg", "laugfs-lpg"],
                note="Cooking-gas planning input from public LPG price references.",
            ),
            CostCommandItem(
                key="health",
                label=localized_cost_label(locale, "health", "Health and personal care"),
                monthly_lkr=round(health_monthly, 0),
                weekly_lkr=round(health_monthly / 4.33, 0),
                confidence="low",
                source_type="derived",
                source_keys=["dcs-hies"],
                note="Derived from household expenditure structure until health-price sources are normalized.",
            ),
            CostCommandItem(
                key="education",
                label=localized_cost_label(locale, "education", "Education buffer"),
                monthly_lkr=round(education_monthly, 0),
                weekly_lkr=round(education_monthly / 4.33, 0),
                confidence="low",
                source_type="derived",
                source_keys=["dcs-hies"],
                note="Family profile includes stronger education pressure; public-only planning signal.",
            ),
            CostCommandItem(
                key="household_goods",
                label=localized_cost_label(locale, "household_goods", "Household goods"),
                monthly_lkr=round(household_goods, 0),
                weekly_lkr=round(household_goods / 4.33, 0),
                confidence="low",
                source_type="derived",
                source_keys=["dcs-hies", "retail-public-pages"],
                note="Durable and household goods reserve from HIES structure plus retail-offer queue.",
            ),
        ]
        base_items = [
            CostCommandItem(
                key=item.key,
                label=localized_cost_label(locale, item.key, item.label),
                monthly_lkr=item.monthly_lkr,
                weekly_lkr=round(item.monthly_lkr / 4.33, 0),
                confidence=item.confidence,
                source_type=self._cost_item_source_type(item.key),
                source_keys=self._cost_item_source_keys(item.key, item.source_domains),
                note=item.note,
            )
            for item in affordability.breakdown
        ]
        items = base_items + extra_items
        total = round(sum(item.monthly_lkr for item in items), 0)
        snapshot_source_map = {
            "food": "foodlk-platform",
            "fuel": "cpc-fuel",
            "property": "dcs-hies",
            "vehicle": "autolens-platform",
            "utilities": "pucsl-electricity",
            "gas": "litro-lpg",
            "transport": "ntc-bus-fares",
        }
        for item in items:
            source_key = snapshot_source_map.get(item.source_keys[0], item.source_keys[0]) if item.source_keys else "dcs-hies"
            db.add(
                TariffSnapshot(
                    domain_key=item.key,
                    source_key=source_key,
                    district=district,
                    category=item.label,
                    amount_lkr=item.monthly_lkr,
                    unit="LKR/month",
                    confidence=item.confidence,
                    payload=item.model_dump(mode="json"),
                )
            )
        db.commit()
        return CostCommandResponse(
            generated_at=utc_now(),
            locale=locale,
            district=district,
            profile=profile,
            total_monthly_lkr=total,
            daily_lkr=round(total / 30.4, 0),
            items=items,
            savings_moves=[
                DomainHighlight(label="Swap retail vs market", value="Compare supermarket quotes with FoodLK market quotes before basket buys.", severity="good", href="/?page=intelligence"),
                DomainHighlight(
                    label="Protein basket check",
                    value=f"LKR {protein['weekly_lkr']:,.0f}/week for about {protein['serving_count']} source-labelled protein servings.",
                    severity="watch",
                    href="/?page=intelligence",
                ),
                DomainHighlight(label="Commute mode check", value="Compare NTC bus fares with private fuel-only trip costs.", severity="watch", href="/?page=atlas"),
                DomainHighlight(label="Gas cadence", value="Track LPG cylinder replacement as a monthly reserve, not a surprise expense.", severity="neutral", href="/?page=cost"),
            ],
            sources=self.public_sources(),
            assumptions=[
                "This is a public planning estimate, not a personal finance account.",
                "All filters are query-driven and shareable; no user profile is stored.",
                "Official, retail, platform, and derived inputs are labelled separately; tariff/import parsers stay behind operator review.",
            ],
        )

    def _cost_item_source_type(self, key: str) -> str:
        if key in {"fuel", "gas", "transport", "utilities"}:
            return "official"
        if key in {"food", "property", "vehicle"}:
            return "platform"
        return "derived"

    def _cost_item_source_keys(self, key: str, fallback: list[str]) -> list[str]:
        source_keys = {
            "food": ["foodlk-platform", "cbsl-price-report", "harti-daily"],
            "fuel": ["octane-platform", "cpc-fuel"],
            "property": ["propertylk-platform", "dcs-hies"],
            "vehicle": ["autolens-platform", *OFFICIAL_IMPORT_CONTEXT_SOURCE_KEYS],
            "utilities": ["pucsl-electricity", "nwsdb-water"],
            "transport": ["ntc-bus-fares", "cpc-fuel"],
        }
        return source_keys.get(key, fallback)

    def utilities(self, db: Session, *, district: str = "Sri Lanka") -> UtilitiesResponse:
        self.ensure_sources(db)
        now = utc_now()
        items = [
            UtilityItem(**item)
            for item in UTILITY_TARIFFS
        ]
        gas = [UtilityItem(**item) for item in GAS_TARIFFS]
        for item in items + gas:
            db.add(
                TariffSnapshot(
                    domain_key="utilities" if item.key.startswith(("electricity", "water")) else "gas",
                    source_key=item.source_key,
                    district=district,
                    category=item.label,
                    amount_lkr=item.amount_lkr,
                    unit=item.unit,
                    confidence=item.confidence,
                    payload=item.model_dump(mode="json"),
                    observed_at=now,
                )
            )
        db.commit()
        return UtilitiesResponse(
            generated_at=now,
            district=district,
            electricity=[item for item in items if item.key.startswith("electricity")],
            water=[item for item in items if item.key.startswith("water")],
            gas=gas,
            sources=self.public_sources("utilities") + self.public_sources("gas"),
        )

    def transport(self, db: Session, *, from_area: str = "Colombo", to_area: str = "Kandy") -> TransportResponse:
        self.ensure_sources(db)
        now = utc_now()
        options = [
            TransportOption(**item)
            for item in TRANSPORT_OPTIONS
            if {item["from_area"].lower(), item["to_area"].lower()} == {from_area.lower(), to_area.lower()}
        ]
        if not options:
            options = [TransportOption(**item) for item in TRANSPORT_OPTIONS[:2]]
        for option in options:
            db.add(
                TransportFareSnapshot(
                    source_key=option.source_key,
                    mode=option.mode,
                    from_area=option.from_area,
                    to_area=option.to_area,
                    fare_lkr=option.fare_lkr,
                    confidence=option.confidence,
                    payload=option.model_dump(mode="json"),
                    observed_at=now,
                )
            )
        db.commit()
        return TransportResponse(
            generated_at=now,
            from_area=from_area,
            to_area=to_area,
            options=options,
            sources=self.public_sources("transport") + self.public_sources("fuel"),
        )

    def retail_offers(self, db: Session, *, query: str | None = None, district: str = "Sri Lanka") -> RetailOffersResponse:
        self.ensure_sources(db)
        now = utc_now()
        q = (query or "").strip().lower()
        rows = [
            item
            for item in RETAIL_OFFERS
            if (not q or q in item["item_name"].lower()) and item["district"] in {district, "Sri Lanka"}
        ]
        if not rows and q:
            rows = [item for item in RETAIL_OFFERS if q in item["item_name"].lower()]
        offers = [RetailOffer(**item) for item in rows]
        for offer in offers:
            db.add(
                RetailOfferSnapshot(
                    source_key=offer.source_key,
                    item_name=offer.item_name,
                    retailer=offer.retailer,
                    district=offer.district,
                    price_lkr=offer.price_lkr,
                    unit=offer.unit,
                    confidence=offer.confidence,
                    payload=offer.model_dump(mode="json"),
                    observed_at=now,
                )
            )
        db.commit()
        return RetailOffersResponse(
            generated_at=now,
            query=query,
            district=district,
            offers=offers,
            sources=self.public_sources("retail"),
        )

    def _district_profile_from_snapshot(self, row: DistrictProfileSnapshot) -> DistrictProfile:
        density = round(row.population / row.area_sqkm, 1)
        return DistrictProfile(
            key=row.district,
            region_id=row.region_id,
            province=row.province,
            population=row.population,
            households=row.households,
            area_sqkm=row.area_sqkm,
            density_per_sqkm=density,
            center_lat=row.center_lat,
            center_lng=row.center_lng,
            cooking_gas_share=row.cooking_gas_share,
            elderly_share=row.elderly_share,
            confidence=row.confidence,
            source_keys=row.source_keys,
            note=f"Promoted from direct source-import artifact {row.source_artifact_id or 'unlinked'} observed at {row.observed_at.isoformat()}.",
        )

    def _complete_source_release_filters(self) -> tuple[Any, ...]:
        required_weather_stations = {station_name for station_name, _coverage in DISTRICT_WEATHER_STATIONS.values()}
        return (
            SourceDataRelease.district_profile_snapshot_count >= len(DISTRICTS),
            SourceDataRelease.weather_risk_snapshot_count >= len(required_weather_stations),
            SourceDataRelease.area_score_snapshot_count >= len(DISTRICTS) * len(PROFILE_FACTORS),
        )

    def _active_source_data_release(self, db: Session) -> SourceDataRelease | None:
        return db.scalar(
            select(SourceDataRelease)
            .where(
                SourceDataRelease.status == "promoted",
                *self._complete_source_release_filters(),
            )
            .order_by(desc(SourceDataRelease.observed_at), desc(SourceDataRelease.id))
            .limit(1)
        )

    def _latest_promoted_release_observed_at(self, db: Session) -> datetime | None:
        active_release = self._active_source_data_release(db)
        return active_release.observed_at if active_release else None

    def _district_profiles(self, db: Session, *, source_observed_at: datetime | None = None) -> list[DistrictProfile]:
        latest_at = source_observed_at or self._latest_promoted_release_observed_at(db)
        if latest_at is None:
            return district_profiles()
        latest_at = db.scalar(
            select(DistrictProfileSnapshot.observed_at)
            .where(DistrictProfileSnapshot.observed_at == latest_at)
            .order_by(desc(DistrictProfileSnapshot.observed_at), desc(DistrictProfileSnapshot.id))
            .limit(1)
        )
        if latest_at is None:
            return district_profiles()
        rows = db.scalars(
            select(DistrictProfileSnapshot)
            .where(DistrictProfileSnapshot.observed_at == latest_at)
            .order_by(DistrictProfileSnapshot.id)
        ).all()
        by_district = {row.district: row for row in rows}
        if not set(DISTRICTS).issubset(by_district):
            return district_profiles()
        return [self._district_profile_from_snapshot(by_district[district]) for district in DISTRICTS]

    def _district_profile_for(self, db: Session, district: str, *, source_observed_at: datetime | None = None) -> DistrictProfile:
        normalized = " ".join((district or "Sri Lanka").replace("-", " ").split()).lower()
        profiles = self._district_profiles(db, source_observed_at=source_observed_at)
        for profile in profiles:
            if profile.key.lower() == normalized:
                return profile
        return profiles[0]

    def _weather_observation_from_snapshot(self, district: str, row: WeatherRiskSnapshot, coverage: str) -> WeatherRiskObservation:
        rainfall = float(row.rainfall_mm or 0)
        humidity = float(row.humidity_percent or 0)
        score = _weather_risk_score(rainfall, humidity, coverage)
        severity = _weather_severity(rainfall, humidity, score)
        if coverage == "national":
            note = "National watch uses the highest-pressure promoted station row until district-level alert ingestion is automated."
        elif coverage == "proxy":
            note = f"{district} uses nearest promoted station proxy {row.station_name}; treat as planning context, not a local warning."
        else:
            note = f"{district} uses the directly mapped {row.station_name} station from the promoted source-import snapshot."
        return WeatherRiskObservation(
            district=district,
            station_id=row.station_id or row.station_name,
            station_name=row.station_name,
            observed_at=row.source_observed_at or row.observed_at,
            rainfall_mm=rainfall,
            temperature_c=float(row.temperature_c or 0),
            humidity_percent=humidity,
            risk_score=score,
            severity=severity,
            coverage=coverage,
            confidence="medium" if coverage == "direct" else "low",
            source_keys=row.source_keys or WEATHER_RISK_SOURCE_KEYS,
            note=note,
        )

    def _weather_risk_observations(self, db: Session, *, source_observed_at: datetime | None = None) -> list[WeatherRiskObservation]:
        latest_at = source_observed_at or self._latest_promoted_release_observed_at(db)
        if latest_at is None:
            return weather_risk_observations()
        latest_at = db.scalar(
            select(WeatherRiskSnapshot.observed_at)
            .where(WeatherRiskSnapshot.record_type == "weather_station")
            .where(WeatherRiskSnapshot.observed_at == latest_at)
            .order_by(desc(WeatherRiskSnapshot.observed_at), desc(WeatherRiskSnapshot.id))
            .limit(1)
        )
        if latest_at is None:
            return weather_risk_observations()
        rows = db.scalars(
            select(WeatherRiskSnapshot)
            .where(WeatherRiskSnapshot.record_type == "weather_station", WeatherRiskSnapshot.observed_at == latest_at)
            .order_by(WeatherRiskSnapshot.id)
        ).all()
        by_station = {row.station_name: row for row in rows}
        required_stations = {station_name for station_name, _coverage in DISTRICT_WEATHER_STATIONS.values()}
        if not required_stations.issubset(by_station):
            return weather_risk_observations()
        return [
            self._weather_observation_from_snapshot(district, by_station[station_name], coverage)
            for district, (station_name, coverage) in DISTRICT_WEATHER_STATIONS.items()
        ]

    def _weather_risk_for(self, db: Session, district: str, *, source_observed_at: datetime | None = None) -> WeatherRiskObservation:
        normalized = " ".join((district or "Sri Lanka").replace("-", " ").split()).lower()
        observations = self._weather_risk_observations(db, source_observed_at=source_observed_at)
        for item in observations:
            if item.district.lower() == normalized:
                return item
        return observations[0]

    def weather_risk(self, db: Session, *, district: str = "Sri Lanka") -> WeatherRiskResponse:
        self.ensure_sources(db)
        observations = self._weather_risk_observations(db)
        selected = self._weather_risk_for(db, district)
        return WeatherRiskResponse(
            generated_at=utc_now(),
            district=selected.district,
            selected=selected,
            observations=observations,
            methodology=[
                "Weather rows are reviewed seed observations from the public 3-hour Met Department extract, with DMC and river sources kept visible for risk context.",
                "Direct station districts use their mapped station; other districts are marked as proxy until district-level weather and river ingestion is automated.",
                "This is a planning signal, not an emergency alert. Use official DMC, Department of Meteorology, and Irrigation Department channels for warnings.",
            ],
            sources=self.public_sources("weather"),
        )

    def area_score(
        self,
        db: Session,
        *,
        district: str = "Sri Lanka",
        profile: str = "family",
        locale: str = "en",
        persist: bool = True,
        source_observed_at: datetime | None = None,
    ) -> AreaScoreResponse:
        self.ensure_sources(db)
        locale = normalize_locale(locale)
        district_profile = self._district_profile_for(db, district, source_observed_at=source_observed_at)
        resolved_district = district_profile.key
        weather = self._weather_risk_for(db, resolved_district, source_observed_at=source_observed_at)
        density = district_profile.density_per_sqkm
        if resolved_district == "Sri Lanka":
            base = dict(AREA_BASE.get(district, AREA_BASE["Sri Lanka"]))
        else:
            rent_score = clamp_score(88 - (density / 80), lower=38, upper=82)
            food_score = clamp_score(77 - (district_profile.elderly_share * 38) - (district_profile.cooking_gas_share * 5), lower=56, upper=78)
            transport_score = clamp_score(52 + min(density / 130, 22), lower=48, upper=78)
            utilities_score = clamp_score(50 + (district_profile.cooking_gas_share * 30), lower=48, upper=82)
            density_score = clamp_score(88 - (density / 95), lower=42, upper=88)
            source_score = 92
            base = {
                "density": density_score,
                "food": food_score,
                "rent": rent_score,
                "source": source_score,
                "transport": transport_score,
                "utilities": utilities_score,
            }
        base.setdefault("density", clamp_score(88 - (density / 95), lower=42, upper=88))
        base["weather"] = clamp_score(92 - (weather.risk_score * 0.55), lower=42, upper=88)
        if profile not in PROFILE_FACTORS:
            profile = "family"
        weights = {"rent": 0.24, "food": 0.2, "transport": 0.16, "utilities": 0.12, "density": 0.09, "weather": 0.08, "source": 0.11}
        if profile == "commuter":
            weights = {"rent": 0.2, "food": 0.17, "transport": 0.26, "utilities": 0.09, "density": 0.09, "weather": 0.08, "source": 0.11}
        source_keys = district_profile.source_keys
        components = [
            AreaScoreComponent(key="rent", label=localized_area_label(locale, "rent", "Rent pressure"), score=base["rent"], value=f"{base['rent']}/100", weight=weights["rent"], confidence="medium", source_keys=source_keys + ["property"], note="Density is used as a sourced rent-pressure proxy until district rental yields are normalized."),
            AreaScoreComponent(key="food", label=localized_area_label(locale, "food", "Food basket pressure"), score=base["food"], value=f"{base['food']}/100", weight=weights["food"], confidence="medium", source_keys=source_keys + ["foodlk-platform"], note="Food pressure blends household structure with existing food price signals."),
            AreaScoreComponent(key="transport", label=localized_area_label(locale, "transport", "Transport pressure"), score=base["transport"], value=f"{base['transport']}/100", weight=weights["transport"], confidence="medium", source_keys=source_keys + ["ntc-bus-fares"], note="Dense districts receive stronger public-transport access but also stronger commute pressure."),
            AreaScoreComponent(key="utilities", label=localized_area_label(locale, "utilities", "Utility pressure"), score=base["utilities"], value=f"{base['utilities']}/100", weight=weights["utilities"], confidence="medium", source_keys=source_keys + ["pucsl-electricity", "nwsdb-water"], note="Cooking gas share is used as a household-energy access proxy."),
            AreaScoreComponent(key="density", label=localized_area_label(locale, "density", "Density pressure"), score=base["density"], value=f"{district_profile.density_per_sqkm:,.0f}/sqkm", weight=weights["density"], confidence="high", source_keys=source_keys, note="Population divided by district area from sourced census and admin-region data."),
            AreaScoreComponent(key="weather", label=localized_area_label(locale, "weather", "Weather and risk pressure"), score=base["weather"], value=f"{weather.severity} / {weather.rainfall_mm:g}mm rain", weight=weights["weather"], confidence=weather.confidence, source_keys=weather.source_keys, note=weather.note),
            AreaScoreComponent(key="source", label=localized_area_label(locale, "source", "Source coverage"), score=base["source"], value=f"{base['source']}/100", weight=weights["source"], confidence="high", source_keys=source_keys, note="District profile has official census facts plus reviewed public extracts."),
        ]
        score = round(sum(component.score * component.weight for component in components), 1)
        response = AreaScoreResponse(
            generated_at=utc_now(),
            district=resolved_district,
            profile=profile,
            score=score,
            grade=grade_for(score),
            confidence="medium",
            components=components,
            district_profile=district_profile,
            sources=self.public_sources("areas") + self.public_sources("indices") + self.public_sources("weather"),
        )
        if persist:
            db.add(
                AreaScoreSnapshot(
                    district=resolved_district,
                    profile=profile,
                    score=score,
                    grade=response.grade,
                    confidence=response.confidence,
                    components=[component.model_dump(mode="json") for component in components],
                    observed_at=response.generated_at,
                )
            )
            db.commit()
        return response

    def atlas(self, db: Session, *, district: str = "Sri Lanka", profile: str = "family", locale: str = "en") -> AtlasResponse:
        locale = normalize_locale(locale)
        selected = self.area_score(db, district=district, profile=profile, locale=locale)
        district_scores = [self.area_score(db, district=item, profile=profile, locale=locale, persist=False) for item in DISTRICTS]
        profiles = self._district_profiles(db)
        profile_map = {item.key: item for item in profiles}
        heatmap = [
            {
                "district": item.district,
                "province": profile_map[item.district].province if item.district in profile_map else "Unknown",
                "score": item.score,
                "grade": item.grade,
                "population": profile_map[item.district].population if item.district in profile_map else 0,
                "density_per_sqkm": profile_map[item.district].density_per_sqkm if item.district in profile_map else 0,
                "rent": next(component.score for component in item.components if component.key == "rent"),
                "food": next(component.score for component in item.components if component.key == "food"),
                "transport": next(component.score for component in item.components if component.key == "transport"),
                "weather": next(component.score for component in item.components if component.key == "weather"),
            }
            for item in district_scores
        ]
        national = next((item.score for item in district_scores if item.district == "Sri Lanka"), selected.score)
        return AtlasResponse(
            generated_at=utc_now(),
            locale=locale,
            district=district,
            profile=profile if profile in PROFILE_FACTORS else "family",
            national_score=national,
            selected=selected,
            district_scores=district_scores,
            heatmap=heatmap,
            narrative=atlas_narrative(locale, selected.district, selected.score, profile),
            selected_profile=selected.district_profile,
            district_profiles=profiles,
            methodology=[
                "District facts use Census 2024 population and household extracts plus public Lanka Data administrative region metadata.",
                "Scores are planning signals, not official rankings; density, household energy, transport, weather/risk, and source coverage are labelled separately.",
                "Missing or unreviewed source data lowers confidence instead of being treated as official truth.",
            ],
            sources=self.public_sources(),
        )

    async def insights(self, db: Session, *, domain: str | None = None) -> InsightsResponse:
        domains = await self.get_domain_signals(db)
        now = utc_now()
        source_map = {source.key: source for source in self.public_sources()}
        highest_weather = max(self._weather_risk_observations(db), key=lambda item: item.risk_score)
        protein = food_protein_basket_signal()
        rows = [
            PublicInsight(
                id="cost-non-food-pressure",
                domain="indices",
                title="Non-food costs are the bigger monthly load",
                message="HIES context shows the household basket is broader than food, so utilities, transport, health, education, and household goods are first-class Ariva inputs.",
                severity="watch",
                confidence="high",
                source_keys=["dcs-hies"],
                observed_at=now,
            ),
            PublicInsight(
                id="food-substitution",
                domain="food",
                title="Food basket needs substitutions, not just cheapest sorting",
                message="Retail and market quote comparison should highlight reasonable substitutes when staples move quickly.",
                severity="watch",
                confidence="medium",
                source_keys=["foodlk-platform", "cbsl-price-report", "harti-daily"],
                observed_at=now,
            ),
            PublicInsight(
                id="food-protein-affordability",
                domain="food",
                title="Protein affordability needs a basket view",
                message=(
                    f"The reviewed protein basket is about LKR {protein['weekly_lkr']:,.0f}/week, "
                    f"or roughly LKR {protein['cost_per_serving_lkr']:,.0f} per 25g protein serving, "
                    "using food-price, nutrition, and fisheries context with visible confidence."
                ),
                severity="watch",
                confidence="medium",
                source_keys=protein["source_keys"],
                observed_at=now,
            ),
            PublicInsight(
                id="source-degraded-visible",
                domain="sources",
                title="Source confidence is part of the product",
                message="When retail pages block access or official formats change, the domain should degrade visibly without breaking the dashboard.",
                severity="good",
                confidence="high",
                source_keys=list(source_map)[:4],
                observed_at=now,
            ),
            PublicInsight(
                id="weather-risk-watch",
                domain="weather",
                title="Weather risk is now a public planning input",
                message=f"{highest_weather.district} has the highest reviewed weather pressure in the seed model, with {highest_weather.rainfall_mm:g}mm rain at {highest_weather.station_name}.",
                severity=highest_weather.severity,
                confidence=highest_weather.confidence,
                source_keys=highest_weather.source_keys,
                observed_at=now,
            ),
        ]
        for signal in domains:
            if signal.status != "healthy":
                rows.append(
                    PublicInsight(
                        id=f"{signal.key}-degraded",
                        domain=signal.key,
                        title=f"{signal.label} needs attention",
                        message=f"{signal.label} is currently {signal.status}; Ariva is still serving degraded public signals with visible freshness.",
                        severity="watch",
                        confidence="medium",
                        source_keys=[source.key for source in signal.sources] or [signal.key],
                        observed_at=now,
                    )
                )
        filtered = [row for row in rows if domain is None or row.domain == domain]
        for item in filtered:
            db.add(
                PublicInsightSnapshot(
                    insight_key=item.id,
                    domain_key=item.domain,
                    title=item.title,
                    severity=item.severity,
                    message=item.message,
                    confidence=item.confidence,
                    source_keys=item.source_keys,
                    observed_at=item.observed_at,
                )
            )
        db.commit()
        keys = {key for item in filtered for key in item.source_keys}
        return InsightsResponse(
            generated_at=now,
            domain=domain,
            insights=filtered,
            sources=[source for source in self.public_sources() if source.key in keys],
        )

    def i18n(self, *, locale: str = "en") -> I18nResponse:
        if locale not in {"en", "si", "ta"}:
            locale = "en"
        source_labels = {
            row["key"]: row.get("labels", {}).get(locale, row["label"])
            for row in SOURCE_DEFINITIONS
        }
        return I18nResponse(
            locale=locale,
            labels=I18N_LABELS[locale],
            domains=DOMAIN_TRANSLATIONS[locale],
            sources=source_labels,
        )

    def public_sources(self, domain: str | None = None) -> list[SourceReference]:
        return source_refs(domain)

    def source_validation(self, db: Session) -> SourceValidationResponse:
        self.ensure_sources(db)
        return source_validation_report()

    def public_source_release(self, db: Session) -> PublicSourceReleaseResponse:
        release = self._active_source_data_release(db)
        if release is None:
            return PublicSourceReleaseResponse(
                generated_at=utc_now(),
                status="seed_fallback",
                note="Atlas and weather responses are using reviewed seed data because no complete promoted source release is active.",
            )
        return PublicSourceReleaseResponse(
            generated_at=utc_now(),
            status="promoted",
            active_release_key=release.release_key,
            observed_at=release.observed_at,
            source_keys=release.source_keys,
            district_profile_snapshot_count=release.district_profile_snapshot_count,
            weather_risk_snapshot_count=release.weather_risk_snapshot_count,
            area_score_snapshot_count=release.area_score_snapshot_count,
            note="Atlas and weather responses are using the latest complete promoted source release.",
        )

    def source_import_audit(self, db: Session, *, persist: bool = True) -> SourceImportAuditResponse:
        from app.services.source_imports import source_import_audit_report

        self.ensure_domains_sync(db)
        self.ensure_sources(db)
        audit = source_import_audit_report()
        if persist:
            now = utc_now()
            for importer in audit.importers:
                db.add(
                    IntegrationRun(
                        domain_key=importer.domain_key,
                        status="failed" if importer.status == "fail" else "completed",
                        started_at=audit.generated_at,
                        finished_at=now,
                        error_message=importer.action if importer.status == "fail" else None,
                        payload_summary={
                            "importer_key": importer.key,
                            "audit_status": importer.status,
                            "accepted_for_scoring": importer.accepted_for_scoring,
                            "rows_checked": importer.rows_checked,
                            "checks": [
                                {
                                    "key": check.key,
                                    "status": check.status,
                                    "message": check.message,
                                }
                                for check in importer.checks
                            ],
                        },
                    )
                )
            db.commit()
        return audit

    def source_import_plan(self, db: Session, *, persist: bool = True) -> SourceImportPlanResponse:
        from app.services.source_imports import source_import_plan_report

        self.ensure_domains_sync(db)
        self.ensure_sources(db)
        plan = source_import_plan_report()
        if persist:
            now = utc_now()
            for manifest in plan.manifests:
                db.add(
                    IntegrationRun(
                        domain_key=manifest.domain_key,
                        status="failed" if manifest.status == "fail" else "completed",
                        started_at=plan.generated_at,
                        finished_at=now,
                        error_message=manifest.next_action if manifest.status == "fail" else None,
                        payload_summary={
                            "manifest_key": manifest.key,
                            "readiness_status": manifest.status,
                            "promotion_status": manifest.promotion_status,
                            "accepted_for_direct_run": manifest.accepted_for_direct_run,
                            "endpoint_statuses": [
                                {
                                    "key": endpoint.key,
                                    "status": endpoint.status,
                                    "source_key": endpoint.source_key,
                                }
                                for endpoint in manifest.endpoints
                            ],
                            "checks": [
                                {
                                    "key": check.key,
                                    "status": check.status,
                                    "message": check.message,
                                }
                                for check in manifest.checks
                            ],
                        },
                    )
                )
            db.commit()
        return plan

    def _promote_canonical_snapshots_from_run(
        self,
        db: Session,
        run,
        *,
        artifact: SourceImportArtifact,
        observed_at: datetime,
        created_at: datetime,
    ) -> int:
        snapshot_count = 0
        for record in run.normalized_records or []:
            record_type = record.get("record_type")
            if run.key == "district-profile-direct-run" and record_type == "district_profile":
                db.add(
                    DistrictProfileSnapshot(
                        source_artifact_id=artifact.id,
                        run_key=run.key,
                        district=record["key"],
                        region_id=record["region_id"],
                        province=record["province"],
                        population=int(record["population"]),
                        households=int(record["households"]),
                        area_sqkm=float(record["area_sqkm"]),
                        center_lat=float(record["center_lat"]),
                        center_lng=float(record["center_lng"]),
                        cooking_gas_share=float(record["cooking_gas_share"]),
                        elderly_share=float(record["elderly_share"]),
                        confidence="high",
                        source_keys=run.source_keys,
                        payload=record,
                        observed_at=observed_at,
                        created_at=created_at,
                    )
                )
                snapshot_count += 1
            elif run.key == "weather-risk-direct-run" and record_type in {"weather_station", "irrigation_water_level"}:
                source_observed_at = parse_source_datetime(record.get("observed_at") or record.get("time_ut"))
                db.add(
                    WeatherRiskSnapshot(
                        source_artifact_id=artifact.id,
                        run_key=run.key,
                        record_type=record_type,
                        station_id=record.get("station_id"),
                        station_name=record["station_name"],
                        source_observed_at=source_observed_at,
                        rainfall_mm=float(record["rainfall_mm"]) if record.get("rainfall_mm") is not None else None,
                        temperature_c=float(record["temperature_c"]) if record.get("temperature_c") is not None else None,
                        humidity_percent=float(record["humidity_percent"]) if record.get("humidity_percent") is not None else None,
                        water_level_m=float(record["water_level_m"]) if record.get("water_level_m") is not None else None,
                        source_keys=run.source_keys,
                        payload=record,
                        observed_at=observed_at,
                        created_at=created_at,
                    )
                )
                snapshot_count += 1
        return snapshot_count

    def _promote_area_score_snapshots(self, db: Session, *, observed_at: datetime) -> int:
        snapshot_count = 0
        for district in DISTRICTS:
            for profile in PROFILE_FACTORS:
                score = self.area_score(db, district=district, profile=profile, persist=False, source_observed_at=observed_at)
                db.add(
                    AreaScoreSnapshot(
                        district=score.district,
                        profile=score.profile,
                        score=score.score,
                        grade=score.grade,
                        confidence=score.confidence,
                        components=[component.model_dump(mode="json") for component in score.components],
                        observed_at=observed_at,
                    )
                )
                snapshot_count += 1
        return snapshot_count

    def _source_import_artifact_for_run(self, run, *, observed_at: datetime, created_at: datetime) -> SourceImportArtifact:
        normalized_records = run.normalized_records or []
        checks = [check.model_dump(mode="json") for check in run.checks]
        return SourceImportArtifact(
            run_key=run.key,
            domain_key=run.domain_key,
            status=run.status,
            mode=run.mode,
            accepted_for_scoring=run.accepted_for_scoring,
            rows_imported=run.rows_imported,
            source_keys=run.source_keys,
            checks=checks,
            normalized_records=normalized_records,
            payload_summary={
                "label": run.label,
                "storage_target": run.storage_target,
                "action": run.action,
                "fetched_urls": run.fetched_urls,
                "fetched_url_count": len(run.fetched_urls),
                "normalized_record_count": len(normalized_records),
                "raw_payload_stored": False,
                "promoted_records": run.promoted_records,
                "promotion_note": run.promotion_note,
            },
            observed_at=observed_at,
            created_at=created_at,
        )

    def _source_data_release_for_execution(
        self,
        execution: SourceImportExecutionResponse,
        *,
        artifact_ids: list[int],
        canonical_snapshot_counts: dict[str, int],
        area_score_snapshot_count: int,
        created_at: datetime,
    ) -> SourceDataRelease:
        release_key = f"direct-source-{execution.generated_at.strftime('%Y%m%dT%H%M%S%fZ')}"
        source_keys = sorted({key for run in execution.runs for key in run.source_keys})
        checks = [
            {**check.model_dump(mode="json"), "run_key": run.key}
            for run in execution.runs
            for check in run.checks
        ]
        operator_notes = [
            self._source_data_release_note(
                action="promote",
                note="Created by guarded live source-import promotion.",
                created_at=created_at,
                source="system",
            )
        ]
        return SourceDataRelease(
            release_key=release_key,
            status="promoted",
            source_import_artifact_ids=artifact_ids,
            run_keys=[run.key for run in execution.runs],
            source_keys=source_keys,
            checks=checks,
            district_profile_snapshot_count=canonical_snapshot_counts.get("district-profile-direct-run", 0),
            weather_risk_snapshot_count=canonical_snapshot_counts.get("weather-risk-direct-run", 0),
            area_score_snapshot_count=area_score_snapshot_count,
            payload_summary={
                "summary": execution.summary,
                "status": execution.status,
                "mode": "live_fetch",
                "promotion_gate": "live_fetch=true&persist=true&healthy&accepted_for_scoring",
                "artifact_count": len(artifact_ids),
            },
            operator_notes=operator_notes,
            observed_at=execution.generated_at,
            created_at=created_at,
        )

    def _source_data_release_note(
        self,
        *,
        action: str,
        note: str,
        created_at: datetime,
        source: str,
        target_release_key: str | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "action": action,
            "note": note,
            "source": source,
            "created_at": created_at.isoformat(),
        }
        if target_release_key:
            payload["target_release_key"] = target_release_key
        return payload

    def _append_source_data_release_note(
        self,
        release: SourceDataRelease,
        *,
        action: str,
        note: str,
        created_at: datetime,
        source: str,
        target_release_key: str | None = None,
    ) -> None:
        release.operator_notes = [
            *(release.operator_notes or []),
            self._source_data_release_note(
                action=action,
                note=note,
                created_at=created_at,
                source=source,
                target_release_key=target_release_key,
            ),
        ]

    def _source_data_release_summary(self, row: SourceDataRelease) -> SourceDataReleaseSummary:
        return SourceDataReleaseSummary(
            id=row.id,
            release_key=row.release_key,
            status=row.status,
            source_import_artifact_ids=row.source_import_artifact_ids,
            run_keys=row.run_keys,
            source_keys=row.source_keys,
            checks=[SourceImportCheck(**check) for check in row.checks],
            district_profile_snapshot_count=row.district_profile_snapshot_count,
            weather_risk_snapshot_count=row.weather_risk_snapshot_count,
            area_score_snapshot_count=row.area_score_snapshot_count,
            payload_summary=row.payload_summary,
            operator_notes=row.operator_notes or [],
            superseded_at=row.superseded_at,
            superseded_by_release_key=row.superseded_by_release_key,
            rolled_back_at=row.rolled_back_at,
            observed_at=row.observed_at,
            created_at=row.created_at,
        )

    def _supersede_current_source_data_releases(
        self,
        db: Session,
        *,
        replacement_release_key: str,
        created_at: datetime,
    ) -> int:
        rows = db.scalars(
            select(SourceDataRelease).where(
                SourceDataRelease.status == "promoted",
                SourceDataRelease.release_key != replacement_release_key,
            )
        ).all()
        for row in rows:
            row.status = "superseded"
            row.superseded_at = created_at
            row.superseded_by_release_key = replacement_release_key
            self._append_source_data_release_note(
                row,
                action="supersede",
                note=f"Superseded by {replacement_release_key}.",
                created_at=created_at,
                source="system",
                target_release_key=replacement_release_key,
            )
        return len(rows)

    async def source_import_run(
        self,
        db: Session,
        *,
        live_fetch: bool = False,
        promote: bool = False,
        persist: bool = True,
        include_official_cost: bool = False,
    ) -> SourceImportExecutionResponse:
        from app.services.source_imports import source_import_execution_report

        self.ensure_domains_sync(db)
        self.ensure_sources(db)
        execution = await source_import_execution_report(live_fetch=live_fetch, include_official_cost=include_official_cost)
        promoted_records = 0
        promotion_allowed = persist and promote and live_fetch and execution.status == "healthy" and all(run.accepted_for_scoring for run in execution.runs)
        if persist:
            now = utc_now()
            canonical_snapshot_counts: dict[str, int] = {}
            artifacts_by_key: dict[str, SourceImportArtifact] = {}
            artifact_ids: list[int] = []
            release_key: str | None = None
            for run in execution.runs:
                artifact = self._source_import_artifact_for_run(run, observed_at=execution.generated_at, created_at=now)
                db.add(artifact)
                db.flush()
                artifacts_by_key[run.key] = artifact
                artifact_ids.append(artifact.id)
                canonical_count = 0
                if promotion_allowed:
                    canonical_count = self._promote_canonical_snapshots_from_run(
                        db,
                        run,
                        artifact=artifact,
                        observed_at=execution.generated_at,
                        created_at=now,
                    )
                canonical_snapshot_counts[run.key] = canonical_count
                artifact.payload_summary = {**artifact.payload_summary, "canonical_snapshot_count": canonical_count}
            if promotion_allowed:
                db.flush()
                promoted_records = self._promote_area_score_snapshots(db, observed_at=execution.generated_at)
                release = self._source_data_release_for_execution(
                    execution,
                    artifact_ids=artifact_ids,
                    canonical_snapshot_counts=canonical_snapshot_counts,
                    area_score_snapshot_count=promoted_records,
                    created_at=now,
                )
                db.add(release)
                db.flush()
                release_key = release.release_key
                superseded_count = self._supersede_current_source_data_releases(
                    db,
                    replacement_release_key=release.release_key,
                    created_at=now,
                )
                release.payload_summary = {
                    **release.payload_summary,
                    "superseded_release_count": superseded_count,
                }
                for run in execution.runs:
                    run.promoted_records = promoted_records
                    run.promotion_note = (
                        f"Promoted {canonical_snapshot_counts.get(run.key, 0)} canonical source snapshots "
                        f"and {promoted_records} area score snapshots in release {release.release_key}."
                    )
                    artifact = artifacts_by_key[run.key]
                    artifact.payload_summary = {
                        **artifact.payload_summary,
                        "promoted_records": run.promoted_records,
                        "promotion_note": run.promotion_note,
                        "source_data_release_key": release.release_key,
                    }
            for run in execution.runs:
                db.add(
                    IntegrationRun(
                        domain_key=run.domain_key,
                        status="failed" if run.status == "fail" else "completed",
                        started_at=execution.generated_at,
                        finished_at=now,
                        error_message=run.action if run.status == "fail" else None,
                        payload_summary={
                            "execution_key": run.key,
                            "execution_status": run.status,
                            "mode": run.mode,
                            "rows_imported": run.rows_imported,
                            "accepted_for_scoring": run.accepted_for_scoring,
                            "promoted_records": run.promoted_records,
                            "fetched_url_count": len(run.fetched_urls),
                            "source_import_artifact_stored": True,
                            "source_data_release_key": release_key,
                            "normalized_record_count": len(run.normalized_records or []),
                            "canonical_snapshot_count": canonical_snapshot_counts.get(run.key, 0),
                            "checks": [
                                {
                                    "key": check.key,
                                    "status": check.status,
                                    "message": check.message,
                                }
                                for check in run.checks
                            ],
                        },
                    )
                )
            db.commit()
        return execution

    def source_import_artifacts(
        self,
        db: Session,
        *,
        run_key: str | None = None,
        limit: int = 20,
        include_records: bool = False,
    ) -> SourceImportArtifactsResponse:
        statement = select(SourceImportArtifact).order_by(desc(SourceImportArtifact.created_at), desc(SourceImportArtifact.id)).limit(limit)
        if run_key:
            statement = (
                select(SourceImportArtifact)
                .where(SourceImportArtifact.run_key == run_key)
                .order_by(desc(SourceImportArtifact.created_at), desc(SourceImportArtifact.id))
                .limit(limit)
            )
        rows = db.scalars(statement).all()
        return SourceImportArtifactsResponse(
            generated_at=utc_now(),
            artifacts=[
                SourceImportArtifactSummary(
                    id=row.id,
                    run_key=row.run_key,
                    domain_key=row.domain_key,
                    status=row.status,
                    mode=row.mode,
                    accepted_for_scoring=row.accepted_for_scoring,
                    rows_imported=row.rows_imported,
                    source_keys=row.source_keys,
                    checks=[SourceImportCheck(**check) for check in row.checks],
                    normalized_record_count=row.payload_summary.get("normalized_record_count", len(row.normalized_records or [])),
                    normalized_records=row.normalized_records if include_records else [],
                    payload_summary=row.payload_summary,
                    observed_at=row.observed_at,
                    created_at=row.created_at,
                )
                for row in rows
            ],
        )

    def source_data_releases(self, db: Session, *, limit: int = 20) -> SourceDataReleasesResponse:
        rows = db.scalars(
            select(SourceDataRelease)
            .order_by(desc(SourceDataRelease.observed_at), desc(SourceDataRelease.id))
            .limit(limit)
        ).all()
        active_release = self._active_source_data_release(db)
        return SourceDataReleasesResponse(
            generated_at=utc_now(),
            active_release_key=active_release.release_key if active_release else None,
            releases=[self._source_data_release_summary(row) for row in rows],
        )

    def add_source_data_release_note(
        self,
        db: Session,
        *,
        release_key: str,
        note: str | None,
    ) -> SourceDataReleaseActionResponse:
        release = db.scalar(select(SourceDataRelease).where(SourceDataRelease.release_key == release_key))
        if release is None:
            raise ValueError("Source data release not found")
        normalized_note = (note or "").strip()
        if not normalized_note:
            raise ValueError("A release note is required")
        now = utc_now()
        self._append_source_data_release_note(
            release,
            action="note",
            note=normalized_note,
            created_at=now,
            source="operator",
        )
        db.commit()
        db.refresh(release)
        active_release = self._active_source_data_release(db)
        return SourceDataReleaseActionResponse(
            generated_at=utc_now(),
            action="note",
            message=f"Added operator note to source data release {release.release_key}.",
            active_release_key=active_release.release_key if active_release else None,
            release=self._source_data_release_summary(release),
        )

    def rollback_source_data_release(
        self,
        db: Session,
        *,
        release_key: str,
        note: str | None,
        reactivate_previous: bool = True,
    ) -> SourceDataReleaseActionResponse:
        release = db.scalar(select(SourceDataRelease).where(SourceDataRelease.release_key == release_key))
        if release is None:
            raise ValueError("Source data release not found")
        if release.status != "promoted":
            raise ValueError("Only the currently promoted source data release can be rolled back")

        now = utc_now()
        release.status = "rolled_back"
        release.rolled_back_at = now
        self._append_source_data_release_note(
            release,
            action="rollback",
            note=(note or "Rolled back by operator.").strip(),
            created_at=now,
            source="operator",
        )

        reactivated: SourceDataRelease | None = None
        if reactivate_previous:
            reactivated = db.scalar(
                select(SourceDataRelease)
                .where(
                    SourceDataRelease.status == "superseded",
                    SourceDataRelease.observed_at < release.observed_at,
                    *self._complete_source_release_filters(),
                )
                .order_by(desc(SourceDataRelease.observed_at), desc(SourceDataRelease.id))
                .limit(1)
            )
            if reactivated is not None:
                reactivated.status = "promoted"
                reactivated.superseded_at = None
                reactivated.superseded_by_release_key = None
                self._append_source_data_release_note(
                    reactivated,
                    action="reactivate",
                    note=f"Reactivated after rollback of {release.release_key}.",
                    created_at=now,
                    source="system",
                    target_release_key=release.release_key,
                )

        db.commit()
        db.refresh(release)
        if reactivated is not None:
            db.refresh(reactivated)
        active_release = self._active_source_data_release(db)
        return SourceDataReleaseActionResponse(
            generated_at=utc_now(),
            action="rollback",
            message=(
                f"Rolled back {release.release_key} and reactivated {reactivated.release_key}."
                if reactivated is not None
                else f"Rolled back {release.release_key}; no previous complete release was reactivated."
            ),
            active_release_key=active_release.release_key if active_release else None,
            release=self._source_data_release_summary(release),
            reactivated_release=self._source_data_release_summary(reactivated) if reactivated is not None else None,
        )

    def _metric_value(self, domain: DomainSignal | None, label: str) -> float | None:
        if domain is None:
            return None
        for metric in domain.metrics:
            if metric.label == label:
                try:
                    return float(metric.value) if metric.value is not None else None
                except (TypeError, ValueError):
                    return None
        return None
