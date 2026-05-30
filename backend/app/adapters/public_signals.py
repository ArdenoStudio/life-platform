import httpx

from app.adapters.base import DomainAdapter, utc_now
from app.schemas import DomainSignal
from app.services.living_atlas_data import GAS_TARIFFS, RETAIL_OFFERS, TRANSPORT_OPTIONS, UTILITY_TARIFFS, source_refs, weather_risk_observations


class StaticSignalAdapter(DomainAdapter):
    status = "healthy"
    health_score = 70
    source_domain: str

    @property
    def api_base(self) -> str:
        refs = source_refs(self.source_domain)
        return refs[0].url if refs else "https://ariva.local"

    async def fetch(self, client: httpx.AsyncClient) -> DomainSignal:
        return self.fixture_signal()


class UtilitiesAdapter(StaticSignalAdapter):
    key = "utilities"
    label = "Utilities"
    category = "Electricity, water, and household services"
    homepage_url = "https://www.pucsl.gov.lk/end-user-tariff-decisions/"
    source_domain = "utilities"

    def fixture_signal(self, *, error: str | None = None) -> DomainSignal:
        now = utc_now()
        electricity = next(item for item in UTILITY_TARIFFS if item["key"] == "electricity-family")
        water = next(item for item in UTILITY_TARIFFS if item["key"] == "water-domestic")
        refs = source_refs("utilities")
        return DomainSignal(
            key="utilities",
            label=self.label,
            category=self.category,
            status="healthy" if error is None else "degraded",
            health_score=72 if error is None else 40,
            summary="Electricity and water tariff intelligence for household planning, grounded in PUCSL and NWSDB source references.",
            api_base=self.api_base,
            source_url=refs[0].url,
            homepage_url=self.homepage_url,
            last_updated_at=now,
            observed_at=now,
            freshness_note="Official tariff pages are tracked; block-level extraction is staged for automation.",
            metrics=[
                self.metric("Electricity family block", electricity["amount_lkr"], "LKR/month"),
                self.metric("Water domestic", water["amount_lkr"], "LKR/month"),
                self.metric("Utility source confidence", 2, "official sources"),
            ],
            highlights=[
                self.highlight("Electricity pressure", "Family proxy near LKR 18,500/month", "watch", "/?page=cost"),
                self.highlight("Water tariff", "NWSDB reference staged", "neutral", "/sources"),
            ],
            top_items=UTILITY_TARIFFS,
            sources=refs,
            errors=[error] if error else [],
        )


class GasAdapter(StaticSignalAdapter):
    key = "gas"
    label = "LPG Gas"
    category = "Cooking gas and household energy"
    homepage_url = "https://www.litrogas.com/"
    source_domain = "gas"

    def fixture_signal(self, *, error: str | None = None) -> DomainSignal:
        now = utc_now()
        refs = source_refs("gas")
        primary = GAS_TARIFFS[0]
        return DomainSignal(
            key="gas",
            label=self.label,
            category=self.category,
            status="healthy" if error is None else "degraded",
            health_score=68 if error is None else 38,
            summary="LPG cylinder price references from public vendor sources for cooking-cost planning.",
            api_base=self.api_base,
            source_url=refs[0].url,
            homepage_url=self.homepage_url,
            last_updated_at=now,
            observed_at=now,
            freshness_note="LPG vendor publications are source-labelled; live extraction is treated as medium confidence.",
            metrics=[
                self.metric("LPG 12.5kg", primary["amount_lkr"], "LKR/cylinder"),
                self.metric("Tracked LPG sources", len(refs), "sources"),
            ],
            highlights=[
                self.highlight("Cooking energy", "12.5kg cylinder tracked as a household cost input", "neutral", "/?page=cost"),
                self.highlight("Source confidence", "Medium until automated vendor extraction is live", "watch", "/sources"),
            ],
            top_items=GAS_TARIFFS,
            sources=refs,
            errors=[error] if error else [],
        )


class TransportAdapter(StaticSignalAdapter):
    key = "transport"
    label = "Public Transport"
    category = "Bus fares and commute pressure"
    homepage_url = "https://www.ntc.gov.lk/Bus_info/bus_fares.php"
    source_domain = "transport"

    def fixture_signal(self, *, error: str | None = None) -> DomainSignal:
        now = utc_now()
        refs = source_refs("transport")
        commuter = next(item for item in TRANSPORT_OPTIONS if item["from_area"] == "Gampaha" and item["to_area"] == "Colombo")
        return DomainSignal(
            key="transport",
            label=self.label,
            category=self.category,
            status="healthy" if error is None else "degraded",
            health_score=76 if error is None else 42,
            summary="Public bus fare and commute-cost signals using NTC fare tables and route planning estimates.",
            api_base=self.api_base,
            source_url=refs[0].url,
            homepage_url=self.homepage_url,
            last_updated_at=now,
            observed_at=now,
            freshness_note="NTC fare tables are official; route-level estimates remain planning signals.",
            metrics=[
                self.metric("Gampaha-Colombo bus", commuter["fare_lkr"], "LKR/trip"),
                self.metric("Tracked corridors", len(TRANSPORT_OPTIONS), "routes"),
            ],
            highlights=[
                self.highlight("Commuter corridor", "Gampaha to Colombo route estimate available", "good", "/?page=atlas"),
                self.highlight("Private vehicle contrast", "Fuel-only route estimates included separately", "neutral", "/transport"),
            ],
            top_items=TRANSPORT_OPTIONS,
            sources=refs,
            errors=[error] if error else [],
        )


class RetailAdapter(StaticSignalAdapter):
    key = "retail"
    label = "Retail Offers"
    category = "Supermarkets and public retail quotes"
    homepage_url = "https://www.keellssuper.com/"
    source_domain = "retail"

    def fixture_signal(self, *, error: str | None = None) -> DomainSignal:
        now = utc_now()
        refs = source_refs("retail")
        cheapest = min(RETAIL_OFFERS, key=lambda item: item["price_lkr"])
        return DomainSignal(
            key="retail",
            label=self.label,
            category=self.category,
            status="healthy" if error is None else "degraded",
            health_score=64 if error is None else 36,
            summary="Public supermarket and retail offer signals labelled separately from official price sources.",
            api_base=self.api_base,
            source_url=refs[0].url,
            homepage_url=self.homepage_url,
            last_updated_at=now,
            observed_at=now,
            freshness_note="Retail pages can change or block access; Ariva labels these as medium-confidence retail quotes.",
            metrics=[
                self.metric("Tracked retail quotes", len(RETAIL_OFFERS), "offers"),
                self.metric("Lowest sample item", cheapest["price_lkr"], f"LKR/{cheapest['unit']}"),
            ],
            highlights=[
                self.highlight("Retail blend", "Supermarket quotes are visible but not treated as official prices", "watch", "/sources"),
                self.highlight("Substitution signal", "Compare retail and market prices before buying", "good", "/?page=intelligence"),
            ],
            top_items=RETAIL_OFFERS,
            sources=refs,
            errors=[error] if error else [],
        )


class IndicesAdapter(StaticSignalAdapter):
    key = "indices"
    label = "Official Indices"
    category = "Inflation and expenditure context"
    homepage_url = "https://www.statistics.gov.lk/InflationAndPrices/StaticalInformation/MonthlyCCPI"
    source_domain = "indices"

    def fixture_signal(self, *, error: str | None = None) -> DomainSignal:
        now = utc_now()
        refs = source_refs("indices")
        return DomainSignal(
            key="indices",
            label=self.label,
            category=self.category,
            status="healthy" if error is None else "degraded",
            health_score=88 if error is None else 45,
            summary="Official inflation and household-expenditure context for interpreting daily price movement.",
            api_base=self.api_base,
            source_url=refs[0].url,
            homepage_url=self.homepage_url,
            last_updated_at=now,
            observed_at=now,
            freshness_note="Monthly official index context; not a live retail price feed.",
            metrics=[
                self.metric("CCPI April 2026", 5.4, "% YoY"),
                self.metric("HIES food share", 35.1, "% household spend"),
                self.metric("HIES non-food share", 64.9, "% household spend"),
            ],
            highlights=[
                self.highlight("Inflation context", "Colombo urban inflation reported at 5.4% in April 2026", "watch", "/?page=intelligence"),
                self.highlight("Non-food pressure", "Housing, utilities, health, transport, and education dominate the wider basket", "neutral", "/?page=cost"),
            ],
            top_items=[
                {"label": "Food share", "value": 35.1, "unit": "%"},
                {"label": "Non-food share", "value": 64.9, "unit": "%"},
                {"label": "April 2026 CCPI", "value": 5.4, "unit": "% YoY"},
            ],
            sources=refs,
            errors=[error] if error else [],
        )


class WeatherRiskAdapter(StaticSignalAdapter):
    key = "weather"
    label = "Weather and Risk"
    category = "Weather observations, rain pressure, and public risk context"
    homepage_url = "https://www.dmc.gov.lk/"
    source_domain = "weather"

    @property
    def api_base(self) -> str:
        return "https://www.meteo.gov.lk/"

    def fixture_signal(self, *, error: str | None = None) -> DomainSignal:
        now = utc_now()
        refs = source_refs("weather")
        primary = next((source for source in refs if source.key == "dmc-lk"), refs[0])
        observations = weather_risk_observations()
        highest = max(observations, key=lambda item: item.risk_score)
        direct_count = sum(1 for item in observations if item.coverage == "direct")
        sorted_items = sorted(observations, key=lambda item: item.risk_score, reverse=True)
        return DomainSignal(
            key="weather",
            label=self.label,
            category=self.category,
            status="healthy" if error is None else "degraded",
            health_score=74 if error is None else 41,
            summary="District weather and public-risk planning signals from Met Department extracts, DMC context, river datasets, and Open-Meteo candidates.",
            api_base=self.api_base,
            source_url=primary.url,
            homepage_url=self.homepage_url,
            last_updated_at=highest.observed_at,
            observed_at=now,
            freshness_note="Reviewed seed from public 3-hour weather extracts; operational alerts still need direct DMC/Irrigation ingestion.",
            metrics=[
                self.metric("Highest 3h rain", highest.rainfall_mm, "mm", f"{highest.district} via {highest.station_name} station"),
                self.metric("Highest risk score", highest.risk_score, "/100", highest.note),
                self.metric("Direct station districts", direct_count, "districts"),
                self.metric("Risk rows", len(observations), "districts"),
            ],
            highlights=[
                self.highlight("Rain watch", f"{highest.district} has the highest reviewed rain pressure at {highest.rainfall_mm:g}mm.", highest.severity, "/?page=intelligence"),
                self.highlight("Coverage caveat", "Proxy station rows are labelled until district-level DMC and Irrigation ingestion is automated.", "watch", "/sources"),
            ],
            top_items=[item.model_dump(mode="json") for item in sorted_items[:8]],
            sources=refs,
            errors=[error] if error else [],
        )


class AreaScoreAdapter(StaticSignalAdapter):
    key = "areas"
    label = "District Life Scores"
    category = "District affordability and livability"
    homepage_url = "https://www.statistics.gov.lk/IncomeAndExpenditure/StaticalInformation/HouseholdIncomeandExpenditureSurvey"
    source_domain = "areas"

    def fixture_signal(self, *, error: str | None = None) -> DomainSignal:
        now = utc_now()
        refs = source_refs("areas")
        return DomainSignal(
            key="areas",
            label=self.label,
            category=self.category,
            status="healthy" if error is None else "degraded",
            health_score=74 if error is None else 40,
            summary="District life scoring that blends affordability, rent pressure, food pressure, transport, utilities, and source coverage.",
            api_base=self.api_base,
            source_url=refs[0].url,
            homepage_url=self.homepage_url,
            last_updated_at=now,
            observed_at=now,
            freshness_note="Derived Ariva score; inputs are labelled and weighted for public planning, not formal statistics.",
            metrics=[
                self.metric("Districts scored", 26, "districts"),
                self.metric("Score components", 7, "signals"),
            ],
            highlights=[
                self.highlight("Atlas mode", "District heat panels ready for public comparison", "good", "/?page=atlas"),
                self.highlight("Derived score", "Methodology is transparent and source-labelled", "neutral", "/sources"),
            ],
            top_items=[
                {"label": "Affordability", "weight": 0.32},
                {"label": "Food pressure", "weight": 0.22},
                {"label": "Transport pressure", "weight": 0.18},
            ],
            sources=refs,
            errors=[error] if error else [],
        )
