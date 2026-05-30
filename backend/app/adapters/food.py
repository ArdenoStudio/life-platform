from datetime import datetime

import httpx

from app.adapters.base import DomainAdapter, as_number, parse_dt, utc_now
from app.schemas import DomainSignal
from app.services.living_atlas_data import FOOD_PROTEIN_BASKET


def protein_basket_total() -> float:
    return sum(item["price_lkr"] * item["weekly_quantity"] for item in FOOD_PROTEIN_BASKET)


class FoodAdapter(DomainAdapter):
    key = "food"
    label = "FoodLK"
    category = "Food and groceries"
    homepage_url = "https://food-platform-one.vercel.app"

    @property
    def api_base(self) -> str:
        return self.settings.food_api_base.rstrip("/")

    def sources(self):
        from app.services.living_atlas_data import source_refs

        return source_refs("food")

    async def fetch(self, client: httpx.AsyncClient) -> DomainSignal:
        if self.settings.life_use_fixtures:
            return self.fixture_signal()
        try:
            hub, freshness, basket = await self._fetch_live(client)
        except Exception as exc:
            return self.degraded_fixture(str(exc))

        coverage = hub.get("coverage", {})
        confidence = freshness.get("confidence", {})
        pipeline = freshness.get("pipeline", {})
        basket_summary = basket.get("summary", {})
        last_updated = parse_dt(freshness.get("freshness", {}).get("last_scrape_at"))
        score = as_number(confidence.get("score"))
        if score is None:
            ratio = as_number(pipeline.get("source_health_ratio"))
            score = (ratio or 0.6) * 100 if ratio is not None and ratio <= 1 else 65

        status = "healthy" if score >= 70 else "degraded"
        total_basket = as_number(basket_summary.get("total_lkr"))
        protein_basket = protein_basket_total()
        return DomainSignal(
            key="food",
            label=self.label,
            category=self.category,
            status=status,
            health_score=max(0, min(float(score), 100)),
            summary="Retail grocery offers and official market quotes with basket estimates and source transparency.",
            api_base=self.api_base,
            source_url=f"{self.api_base}/hub/summary",
            homepage_url=self.homepage_url,
            last_updated_at=last_updated,
            observed_at=utc_now(),
            freshness_note=confidence.get("note") or "Food uses scheduled source refreshes and manual runs.",
            metrics=[
                self.metric("Retail offers", coverage.get("offers_count"), "offers"),
                self.metric("Market quotes", coverage.get("market_quotes_count"), "quotes"),
                self.metric("Sources", coverage.get("sources_count"), "feeds"),
                self.metric("Essentials basket", round(total_basket, 0) if total_basket else None, "LKR"),
                self.metric("Protein basket", round(protein_basket, 0), "LKR/week"),
            ],
            highlights=[
                self.highlight("Source health", f"{pipeline.get('healthy_sources', 0)}/{pipeline.get('total_sources', 0)} healthy", "good" if status == "healthy" else "watch", "/sources"),
                self.highlight("Basket signal", f"LKR {total_basket:,.0f}" if total_basket else "Pending basket", "neutral", "/affordability"),
                self.highlight("Protein basket", f"LKR {protein_basket:,.0f}/week", "watch", "/?page=intelligence"),
            ],
            top_items=basket.get("items", [])[:6],
            sources=self.sources(),
        )

    async def _fetch_live(self, client: httpx.AsyncClient) -> tuple[dict, dict, dict]:
        hub = await self.get_json(client, "hub/summary")
        freshness = await self.get_json(client, "platform/freshness")
        basket = await self.get_json(client, "basket/estimate", preset="essentials")
        return hub, freshness, basket

    def fixture_signal(self, *, error: str | None = None) -> DomainSignal:
        now = utc_now()
        return DomainSignal(
            key="food",
            label=self.label,
            category=self.category,
            status="healthy" if error is None else "degraded",
            health_score=82 if error is None else 42,
            summary="Food and grocery price intelligence across supermarkets, official market quotes, and household baskets.",
            api_base=self.api_base,
            source_url=f"{self.api_base}/hub/summary",
            homepage_url=self.homepage_url,
            last_updated_at=now,
            observed_at=now,
            freshness_note="Scheduled food refreshes; fixture-backed in this environment." if error is None else "Fallback food fixture.",
            metrics=[
                self.metric("Retail offers", 240, "offers"),
                self.metric("Market quotes", 59500, "quotes"),
                self.metric("Sources", 10, "feeds"),
                self.metric("Essentials basket", 8650, "LKR"),
                self.metric("Protein basket", round(protein_basket_total(), 0), "LKR/week"),
            ],
            highlights=[
                self.highlight("Food basket", "Essentials basket near LKR 8,650", "neutral", "/affordability"),
                self.highlight("Coverage", "Retail + market source blend", "good", "/sources"),
                self.highlight("Protein basket", f"LKR {protein_basket_total():,.0f}/week", "watch", "/?page=intelligence"),
            ],
            top_items=[
                {"label": "Rice", "price_lkr": 320, "source": "market"},
                {"label": "Dhal", "price_lkr": 420, "source": "retail"},
                {"label": "Big onion", "price_lkr": 290, "source": "market"},
            ],
            sources=self.sources(),
            errors=[error] if error else [],
        )
