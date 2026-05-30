import httpx

from app.adapters.base import DomainAdapter, as_number, parse_dt, utc_now
from app.schemas import DomainSignal


class FuelAdapter(DomainAdapter):
    key = "fuel"
    label = "Octane"
    category = "Fuel"
    homepage_url = "https://octane-smoky.vercel.app"

    @property
    def api_base(self) -> str:
        return self.settings.fuel_api_base.rstrip("/")

    def sources(self):
        from app.services.living_atlas_data import source_refs

        return source_refs("fuel")

    async def fetch(self, client: httpx.AsyncClient) -> DomainSignal:
        if self.settings.life_use_fixtures:
            return self.fixture_signal()
        try:
            latest = await self.get_json(client, "v1/prices/latest")
            health = await self.get_json(client, "v1/health")
        except Exception as exc:
            return self.degraded_fixture(str(exc))

        prices = latest.get("prices", [])
        by_fuel = {row.get("fuel_type"): row for row in prices if isinstance(row, dict)}
        petrol_92 = by_fuel.get("petrol_92", {})
        diesel = by_fuel.get("auto_diesel", {})
        kerosene = by_fuel.get("kerosene", {})
        source_updated = parse_dt(petrol_92.get("recorded_at") or diesel.get("recorded_at"))
        stale = bool(health.get("data", {}).get("stale"))
        status = "degraded" if stale or not prices else "healthy"

        return DomainSignal(
            key="fuel",
            label=self.label,
            category=self.category,
            status=status,
            health_score=58 if status == "degraded" else 92,
            summary="Fuel price intelligence from CPC/LIOC-style revision tracking, history, calculators, and alerts.",
            api_base=self.api_base,
            source_url=f"{self.api_base}/v1/prices/latest",
            homepage_url=self.homepage_url,
            last_updated_at=source_updated,
            observed_at=utc_now(),
            freshness_note="Fuel revisions are checked several times daily; displayed values show the latest recorded revision.",
            metrics=[
                self.metric("Petrol 92", as_number(petrol_92.get("price_lkr")), "LKR/L"),
                self.metric("Auto Diesel", as_number(diesel.get("price_lkr")), "LKR/L"),
                self.metric("Kerosene", as_number(kerosene.get("price_lkr")), "LKR/L"),
            ],
            highlights=[
                self.highlight("Revision status", "Latest CPC fuel revision loaded" if not stale else "Fuel data may be stale", "good" if not stale else "watch", "/domains/fuel"),
            ],
            top_items=prices[:6],
            sources=self.sources(),
        )

    def fixture_signal(self, *, error: str | None = None) -> DomainSignal:
        now = utc_now()
        return DomainSignal(
            key="fuel",
            label=self.label,
            category=self.category,
            status="healthy" if error is None else "degraded",
            health_score=90 if error is None else 45,
            summary="Fuel price tracking for petrol, diesel, kerosene, price history, and trip-cost context.",
            api_base=self.api_base,
            source_url=f"{self.api_base}/v1/prices/latest",
            homepage_url=self.homepage_url,
            last_updated_at=now,
            observed_at=now,
            freshness_note="Fuel fixture values keep Ariva usable offline." if error is None else "Fallback fuel fixture.",
            metrics=[
                self.metric("Petrol 92", 410, "LKR/L"),
                self.metric("Auto Diesel", 392, "LKR/L"),
                self.metric("Kerosene", 265, "LKR/L"),
            ],
            highlights=[self.highlight("Trip cost input", "Petrol and diesel rates ready for commute estimates", "neutral", "/affordability")],
            top_items=[
                {"fuel_type": "petrol_92", "price_lkr": 410, "source": "cpc"},
                {"fuel_type": "auto_diesel", "price_lkr": 392, "source": "cpc"},
            ],
            sources=self.sources(),
            errors=[error] if error else [],
        )
