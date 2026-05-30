import httpx

from app.adapters.base import DomainAdapter, as_number, parse_dt, utc_now
from app.schemas import DomainSignal


class PropertyAdapter(DomainAdapter):
    key = "property"
    label = "PropertyLK"
    category = "Housing and property"
    homepage_url = "https://propertylk-one.vercel.app"

    @property
    def api_base(self) -> str:
        return self.settings.property_api_base.rstrip("/")

    def sources(self):
        from app.services.living_atlas_data import source_refs

        return source_refs("property")

    async def fetch(self, client: httpx.AsyncClient) -> DomainSignal:
        if self.settings.life_use_fixtures:
            return self.fixture_signal()
        try:
            stats = await self.get_json(client, "stats")
            pipeline = await self.get_json(client, "public/pipeline")
        except Exception as exc:
            return self.degraded_fixture(str(exc))

        avg_price = as_number(stats.get("avg_price_lkr"))
        last_updated = parse_dt(stats.get("last_updated"))
        overall = str(pipeline.get("overall_status") or "ok")
        status = "healthy" if overall == "ok" else "degraded"

        return DomainSignal(
            key="property",
            label=self.label,
            category=self.category,
            status=status,
            health_score=86 if status == "healthy" else 55,
            summary="Property listings, district benchmarks, heatmaps, trends, and rental-yield context.",
            api_base=self.api_base,
            source_url=f"{self.api_base}/stats",
            homepage_url=self.homepage_url,
            last_updated_at=last_updated,
            observed_at=utc_now(),
            freshness_note="Property data is a periodic listing-market snapshot, not a live transaction registry.",
            metrics=[
                self.metric("Listings", stats.get("total_listings"), "listings"),
                self.metric("Average price", round(avg_price, 0) if avg_price else None, "LKR"),
                self.metric("Districts", stats.get("districts_covered"), "districts"),
                self.metric("7-day listings", stats.get("listings_last_7_days"), "listings"),
            ],
            highlights=[
                self.highlight("Pipeline", f"Property pipeline {overall}", "good" if status == "healthy" else "watch", "/sources"),
            ],
            top_items=[stats],
            sources=self.sources(),
        )

    def fixture_signal(self, *, error: str | None = None) -> DomainSignal:
        now = utc_now()
        return DomainSignal(
            key="property",
            label=self.label,
            category=self.category,
            status="healthy" if error is None else "degraded",
            health_score=84 if error is None else 44,
            summary="Housing market intelligence for listings, district medians, deal scores, heatmaps, and rental context.",
            api_base=self.api_base,
            source_url=f"{self.api_base}/stats",
            homepage_url=self.homepage_url,
            last_updated_at=now,
            observed_at=now,
            freshness_note="Property fixture values approximate a listing-market snapshot." if error is None else "Fallback property fixture.",
            metrics=[
                self.metric("Listings", 18200, "listings"),
                self.metric("Average price", 44500000, "LKR"),
                self.metric("Districts", 25, "districts"),
                self.metric("7-day listings", 620, "listings"),
            ],
            highlights=[self.highlight("Housing pressure", "Rent and sale signals dominate monthly living decisions", "watch", "/affordability")],
            top_items=[],
            sources=self.sources(),
            errors=[error] if error else [],
        )
