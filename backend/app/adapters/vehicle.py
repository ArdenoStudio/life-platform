import httpx

from app.adapters.base import DomainAdapter, as_number, parse_dt, utc_now
from app.schemas import DomainSignal


class VehicleAdapter(DomainAdapter):
    key = "vehicle"
    label = "AutoLens"
    category = "Vehicle market"
    homepage_url = "https://vehicle-platform-one.vercel.app"

    @property
    def api_base(self) -> str:
        return self.settings.vehicle_api_base.rstrip("/")

    def sources(self):
        from app.services.living_atlas_data import source_refs

        return source_refs("vehicle")

    async def fetch(self, client: httpx.AsyncClient) -> DomainSignal:
        if self.settings.life_use_fixtures:
            return self.fixture_signal()
        try:
            stats = await self.get_json(client, "stats/summary")
            pipeline = await self.get_json(client, "pipeline/status")
        except Exception as exc:
            return self.degraded_fixture(str(exc))

        avg_price = as_number(stats.get("avg_price_lkr"))
        last_updated = parse_dt(stats.get("last_updated"))
        overall = str(pipeline.get("overall_status") or "ok")
        status = "healthy" if overall == "ok" else "degraded"

        return DomainSignal(
            key="vehicle",
            label=self.label,
            category=self.category,
            status=status,
            health_score=84 if status == "healthy" else 52,
            summary="Vehicle listings, market medians, deal scores, estimates, and import-context signals.",
            api_base=self.api_base,
            source_url=f"{self.api_base}/stats/summary",
            homepage_url=self.homepage_url,
            last_updated_at=last_updated,
            observed_at=utc_now(),
            freshness_note="Vehicle data is refreshed through scheduled listing scrapers and market-signal jobs.",
            metrics=[
                self.metric("Listings", stats.get("total_listings"), "listings"),
                self.metric("Average price", round(avg_price, 0) if avg_price else None, "LKR"),
                self.metric("Good deals", stats.get("good_deals_count"), "listings"),
                self.metric("Sources", stats.get("source_count"), "feeds"),
            ],
            highlights=[
                self.highlight("Vehicle pressure", "Vehicle affordability depends on market listings plus import/tax signals", "watch", "/domains/vehicle"),
            ],
            top_items=[stats],
            sources=self.sources(),
        )

    def fixture_signal(self, *, error: str | None = None) -> DomainSignal:
        now = utc_now()
        return DomainSignal(
            key="vehicle",
            label=self.label,
            category=self.category,
            status="healthy" if error is None else "degraded",
            health_score=82 if error is None else 42,
            summary="Vehicle market intelligence for listings, estimates, deal scores, and import signal context.",
            api_base=self.api_base,
            source_url=f"{self.api_base}/stats/summary",
            homepage_url=self.homepage_url,
            last_updated_at=now,
            observed_at=now,
            freshness_note="Vehicle fixture values approximate the scheduled listing market." if error is None else "Fallback vehicle fixture.",
            metrics=[
                self.metric("Listings", 9400, "listings"),
                self.metric("Average price", 8250000, "LKR"),
                self.metric("Good deals", 420, "listings"),
                self.metric("Sources", 7, "feeds"),
            ],
            highlights=[self.highlight("Mobility cost", "Fuel plus vehicle ownership belongs in one monthly-life view", "neutral", "/affordability")],
            top_items=[],
            sources=self.sources(),
            errors=[error] if error else [],
        )
