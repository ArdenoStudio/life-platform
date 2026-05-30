import hashlib
import re
from datetime import datetime, timezone
from typing import Any

import httpx
from pydantic import BaseModel, Field, ValidationError, model_validator

from app.schemas import (
    SourceImportAuditResponse,
    SourceImportCheck,
    SourceImportEndpoint,
    SourceImportExecutionResponse,
    SourceImportExecutionRun,
    SourceImportManifest,
    SourceImportPlanResponse,
    SourceImportRun,
)
from app.services.living_atlas_data import (
    DISTRICT_PROFILE_ROWS,
    DISTRICT_PROFILE_SOURCE_KEYS,
    DISTRICT_WEATHER_STATIONS,
    DISTRICTS,
    GAS_TARIFFS,
    OFFICIAL_COST_SOURCE_KEYS,
    OFFICIAL_IMPORT_CONTEXT_SOURCE_KEYS,
    OPTIONAL_IMPORT_CONTEXT_SOURCE_KEYS,
    TRANSPORT_OPTIONS,
    UTILITY_TARIFFS,
    WEATHER_RISK_SOURCE_KEYS,
    WEATHER_STATION_ROWS,
    source_refs,
    utc_now,
)


DISTRICT_DIRECT_IMPORT_URLS = {
    "population": "https://raw.githubusercontent.com/nuuuwan/lk_census_2024/main/data/Population-Preliminary-Report/Population-by-sex-and-age/data.json",
    "households": "https://raw.githubusercontent.com/nuuuwan/lk_census_2024/main/data/HH_GND_excel/Number-of-Households/data.json",
    "cooking_fuel": "https://raw.githubusercontent.com/nuuuwan/lk_census_2024/main/data/HH_GND_excel/Number-of-households-by-main-source-of-energyfuel-used-for-cooking/data.json",
    "country_regions": "https://raw.githubusercontent.com/nuuuwan/lk_admin_regions/main/data/ents/countrys.json",
    "province_regions": "https://raw.githubusercontent.com/nuuuwan/lk_admin_regions/main/data/ents/provinces.json",
    "district_regions": "https://raw.githubusercontent.com/nuuuwan/lk_admin_regions/main/data/ents/districts.json",
}

WEATHER_DIRECT_IMPORT_URLS = {
    "weather_stations": "https://raw.githubusercontent.com/nuuuwan/lk_weather_3h/main/data/weather_stations.json",
    "weather_alerts": "https://raw.githubusercontent.com/nuuuwan/lk_weather_3h/main/data/alert_data.json",
    "irrigation_levels": "https://raw.githubusercontent.com/nuuuwan/lk_irrigation/main/data/all.json",
}

OFFICIAL_COST_DIRECT_SOURCE_KEYS = [
    "pucsl-electricity",
    "nwsdb-water",
    "ntc-bus-fares",
    "cpc-fuel",
    "cbsl-economic-data",
    "sri-lanka-customs-tariff",
]

WEATHER_SOURCE_STATION_ALIASES = {
    "Mullaitivu": "Mullativu",
}


class DistrictProfileSeedRow(BaseModel):
    key: str = Field(min_length=1)
    region_id: str = Field(min_length=2)
    province: str = Field(min_length=1)
    population: int = Field(gt=0)
    households: int = Field(gt=0)
    area_sqkm: float = Field(gt=0)
    center_lat: float
    center_lng: float
    cooking_gas_share: float = Field(ge=0, le=1)
    elderly_share: float = Field(ge=0, le=1)

    @model_validator(mode="after")
    def coordinates_are_in_sri_lanka_bounds(self):
        if not 5.5 <= self.center_lat <= 10.2:
            raise ValueError("center_lat is outside Sri Lanka planning bounds")
        if not 79.0 <= self.center_lng <= 82.2:
            raise ValueError("center_lng is outside Sri Lanka planning bounds")
        if self.population / self.households < 1:
            raise ValueError("population must exceed household count")
        return self


class WeatherStationSeedRow(BaseModel):
    station_id: str = Field(min_length=1)
    station_name: str = Field(min_length=1)
    observed_at: datetime
    rainfall_mm: float = Field(ge=0)
    temperature_c: float = Field(ge=0, le=45)
    humidity_percent: float = Field(ge=0, le=100)


class TariffSeedRow(BaseModel):
    key: str = Field(min_length=1)
    label: str = Field(min_length=1)
    amount_lkr: float = Field(gt=0)
    unit: str = Field(min_length=1)
    source_key: str = Field(min_length=1)
    confidence: str = Field(pattern="^(high|medium|low)$")
    note: str = Field(min_length=1)


class TransportFareSeedRow(BaseModel):
    mode: str = Field(min_length=1)
    from_area: str = Field(min_length=1)
    to_area: str = Field(min_length=1)
    fare_lkr: float = Field(gt=0)
    confidence: str = Field(pattern="^(high|medium|low)$")
    source_key: str = Field(min_length=1)
    note: str = Field(min_length=1)

    @model_validator(mode="after")
    def route_has_two_ends(self):
        if self.from_area.strip().lower() == self.to_area.strip().lower():
            raise ValueError("transport fare route must have different from_area and to_area")
        return self


class OfficialCostParserEvidenceRow(BaseModel):
    source_key: str = Field(min_length=1)
    parser_key: str = Field(min_length=1)
    source_format: str = Field(pattern="^(html|pdf_text|text)$")
    observed_label: str = Field(min_length=1)
    evidence: dict[str, Any] = Field(default_factory=dict)


class IrrigationWaterLevelRow(BaseModel):
    station_name: str = Field(min_length=1)
    time_ut: int | float = Field(gt=0)
    water_level_m: float = Field(ge=-20, le=50)


class AdminRegionRow(BaseModel):
    id: str = Field(min_length=2)
    name: str = Field(min_length=1)
    area_sqkm: float = Field(gt=0)
    center_lat: float
    center_lng: float
    province_id: str | None = None

    @model_validator(mode="after")
    def coordinates_are_in_sri_lanka_bounds(self):
        if not 5.5 <= self.center_lat <= 10.2:
            raise ValueError("center_lat is outside Sri Lanka planning bounds")
        if not 79.0 <= self.center_lng <= 82.2:
            raise ValueError("center_lng is outside Sri Lanka planning bounds")
        return self


class DirectImportPayload(BaseModel):
    key: str
    url: str
    row_count: int
    sha256: str
    rows: list[dict]


class DirectImportDocument(BaseModel):
    key: str
    url: str
    item_count: int
    sha256: str
    data: Any


def _check(
    *,
    key: str,
    label: str,
    status: str,
    message: str,
    evidence: list[str] | None = None,
) -> SourceImportCheck:
    return SourceImportCheck(
        key=key,
        label=label,
        status=status,
        message=message,
        evidence=evidence or [],
    )


def _payload_from_rows(key: str, url: str, rows: list[dict]) -> DirectImportPayload:
    payload_bytes = str(rows).encode("utf-8")
    return DirectImportPayload(
        key=key,
        url=url,
        row_count=len(rows),
        sha256=hashlib.sha256(payload_bytes).hexdigest(),
        rows=rows,
    )


def _document_item_count(data: Any) -> int:
    if isinstance(data, list):
        return len(data)
    if isinstance(data, dict):
        return len(data)
    return 1


def _document_from_data(key: str, url: str, data: Any) -> DirectImportDocument:
    payload_bytes = str(data).encode("utf-8")
    return DirectImportDocument(
        key=key,
        url=url,
        item_count=_document_item_count(data),
        sha256=hashlib.sha256(payload_bytes).hexdigest(),
        data=data,
    )


OFFICIAL_COST_PARSER_FIXTURES = {
    "pucsl-electricity": {
        "parser_key": "pucsl-electricity-decision-index",
        "source_format": "html",
        "text": """
        Tariff Decision
        Decision on Electricity Tariffs - 2026 May
        Decision on Electricity Tariff - 2026 May
        Tariff Schedule - 2026 May
        Archives
        Decision on Electricity Tariff - 2026 April
        Tariff Schedule - 2026-April
        Decision on Electricity Tariff - 2025 October
        Tariff Schedule - 2025 October
        """,
    },
    "nwsdb-water": {
        "parser_key": "nwsdb-domestic-water-gazette",
        "source_format": "pdf_text",
        "text": """
        NATIONAL WATER SUPPLY AND DRAINAGE BOARD LAW, No. 2 OF 1974
        Notice under Section 84
        the following tariffs will be charged with effect from the 01st day of August, 2023
        Tariff TABLE 02 - (Category 10, 11, 13, 16, 18, 19)
        Tariff For Domestic Other Than Samurdhi Recipients & Tenement Garden
        No. of units Usage Charge Rs./Unit Monthly Service Charge Rs.
        00-05 60.00 300.00
        06-10 80.00 300.00
        11-15 100.00 300.00
        16-20 110.00 400.00
        21-25 130.00 500.00
        26-30 160.00 600.00
        31-40 180.00 1,500.00
        41-50 210.00 3,000.00
        51-75 240.00 3,500.00
        76-100 270.00 4,000.00
        Over 100 300.00 4,500.00
        tariff TABLE 03 - (Category 51, 52, 53)
        """,
    },
    "ntc-bus-fares": {
        "parser_key": "ntc-bus-fare-index",
        "source_format": "html",
        "text": """
        Bus Fares
        Interim Bus Fare revision March 2026
        will be effective from 24th of March 2026 (from 00.01 hrs.)
        Fare Stages (Effect From 2026-03-24)
        Normal
        Semi-Luxury
        Luxury
        Super Luxury
        Full Bus fare by Route wise (Effect from 2026-03-24)
        Normal Bus Fare PDF
        """,
    },
    "cpc-fuel": {
        "parser_key": "cpc-fuel-price-cards",
        "source_format": "html",
        "text": """
        Fuel Pricing
        Current market rates for all Ceylon Petroleum Corporation products
        Lanka Petrol 92 Octane
        White Oil
        Rs. 410.00 per Ltr
        Effect from: 02-05-2026 12.00 Midnight
        Lanka Auto Diesel
        White Oil
        Rs. 392.00 per Ltr
        Effect from: 02-05-2026 12.00 Midnight
        Lanka Kerosene
        White Oil
        Rs. 265.00 per Ltr
        Effect from: 02-05-2026 12.00 Midnight
        """,
    },
    "cbsl-economic-data": {
        "parser_key": "cbsl-exchange-rate-page",
        "source_format": "html",
        "text": """
        Exchange Rates
        Indicative Rate of the USD/LKR SPOT Exchange Rate Search (LKR per 1 USD)
        Indicative Exchange Rates Search (LKR per 1 world currency unit)
        Buying and Selling Exchange Rate (TT) Search
        Spreadsheets
        Daily Buying and Selling Exchange Rate 2005- Latest (Telegraphic Transfers)
        Monthly average spot exchange rates
        End month exchange rates- Spot
        Real Effective Exchange Rates (REER)
        """,
    },
    "sri-lanka-customs-tariff": {
        "parser_key": "customs-import-tariff-index",
        "source_format": "html",
        "text": """
        Customs Import Tariff - 2026
        Complete Customs Import Tariff for Sri Lanka, organised by HS Section and Chapter.
        Tariff ZIP 2026
        97 Chapters
        NOTICE
        The content in this website is for informational purposes only.
        The extracts taken from this web site shall not be used as evidence in any legal proceedings.
        Tariff Downloads
        Latest Tariff 2026 ZIP File (05.05.2026)
        Last updated on: 05/05/2026
        Chapters by Section
        Chapter 1 Live animals PDF
        Chapter 87 Vehicles other than railway or tramway rolling-stock PDF
        """,
    },
}


def _plain_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.replace("\u2013", "-").replace("\u2014", "-")).strip()


def _strip_html(value: str) -> str:
    without_scripts = re.sub(r"<(script|style)\b.*?</\1>", " ", value, flags=re.IGNORECASE | re.DOTALL)
    without_tags = re.sub(r"<[^>]+>", " ", without_scripts)
    return _plain_text(without_tags)


def _lines(value: str) -> list[str]:
    return [line.strip() for line in value.replace("\u2013", "-").replace("\u2014", "-").splitlines() if line.strip()]


def parse_pucsl_tariff_decision_text(text: str) -> OfficialCostParserEvidenceRow:
    normalized = _plain_text(text)
    decision = re.search(r"Decision on Electricity Tariffs? - (?P<label>\d{4}\s+[A-Za-z]+)", normalized)
    schedule = re.search(r"Tariff Schedule - (?P<label>\d{4}[-\s]?[A-Za-z]+)", normalized)
    archive_count = len(re.findall(r"Decision on Electricity Tariff", normalized))
    if not decision or not schedule:
        raise ValueError("PUCSL tariff decision text must expose latest decision and tariff schedule labels")
    return OfficialCostParserEvidenceRow(
        source_key="pucsl-electricity",
        parser_key="pucsl-electricity-decision-index",
        source_format="html",
        observed_label=f"Decision {decision.group('label')}",
        evidence={
            "latest_decision": decision.group("label"),
            "latest_schedule": schedule.group("label"),
            "archive_decision_count": archive_count,
        },
    )


def parse_nwsdb_water_tariff_text(text: str) -> OfficialCostParserEvidenceRow:
    normalized = _plain_text(text)
    if "NATIONAL WATER SUPPLY AND DRAINAGE BOARD LAW" not in normalized or "Notice under Section 84" not in normalized:
        raise ValueError("NWSDB tariff text must include statutory notice markers")
    effective = re.search(r"effect from the (?P<date>\d{2}(?:st|nd|rd|th) day of [A-Za-z]+, \d{4})", normalized, re.IGNORECASE)
    table_match = re.search(
        r"Tariff TABLE 02.*?No\. of units Usage Charge Rs\./Unit Monthly Service Charge Rs\.(?P<table>.*?)tariff TABLE 03",
        normalized,
        re.IGNORECASE,
    )
    if not effective or not table_match:
        raise ValueError("NWSDB tariff text must expose effective date and domestic tariff table")
    blocks = re.findall(r"(?P<block>\d{2,3}\s*-\s*\d{2,3}|Over\s+\d+)\s+(?P<usage>[\d,.]+)\s+(?P<service>[\d,.]+)", table_match.group("table"))
    if len(blocks) < 8:
        raise ValueError("NWSDB domestic tariff table must expose the expected block rows")
    return OfficialCostParserEvidenceRow(
        source_key="nwsdb-water",
        parser_key="nwsdb-domestic-water-gazette",
        source_format="pdf_text",
        observed_label=f"Domestic tariff effective {effective.group('date')}",
        evidence={
            "effective_from": effective.group("date"),
            "domestic_block_count": len(blocks),
            "first_block": {"range": blocks[0][0], "usage_lkr": blocks[0][1], "service_lkr": blocks[0][2]},
            "last_block": {"range": blocks[-1][0], "usage_lkr": blocks[-1][1], "service_lkr": blocks[-1][2]},
        },
    )


def parse_ntc_bus_fare_text(text: str) -> OfficialCostParserEvidenceRow:
    normalized = _plain_text(text)
    effective = re.search(r"Effect(?:ive)? from (?P<date>\d{4}-\d{2}-\d{2}|\d{1,2}(?:st|nd|rd|th)? of [A-Za-z]+ \d{4})", normalized, re.IGNORECASE)
    fare_labels = [label for label in ["Normal", "Semi-Luxury", "Luxury", "Super Luxury", "Full Bus fare"] if label in normalized]
    if "Bus Fares" not in normalized or not effective or len(fare_labels) < 4:
        raise ValueError("NTC fare text must expose effective date and fare document labels")
    return OfficialCostParserEvidenceRow(
        source_key="ntc-bus-fares",
        parser_key="ntc-bus-fare-index",
        source_format="html",
        observed_label=f"Bus fares effective {effective.group('date')}",
        evidence={"effective_from": effective.group("date"), "fare_document_labels": fare_labels},
    )


def parse_cpc_fuel_price_text(text: str) -> OfficialCostParserEvidenceRow:
    lines = _lines(text)
    prices: list[dict[str, str]] = []
    for index, line in enumerate(lines):
        if not line.startswith("Lanka "):
            continue
        window = lines[index + 1 : index + 6]
        price = next((item for item in window if item.startswith("Rs.")), None)
        effect = next((item.replace("Effect from:", "").strip() for item in window if item.startswith("Effect from:")), None)
        if price and effect:
            prices.append({"product": line, "price": price.replace("Rs.", "").replace("per Ltr", "").strip(), "effective_from": effect})
    if not prices:
        raise ValueError("CPC fuel text must expose product price cards")
    return OfficialCostParserEvidenceRow(
        source_key="cpc-fuel",
        parser_key="cpc-fuel-price-cards",
        source_format="html",
        observed_label=f"{len(prices)} CPC fuel price cards",
        evidence={"price_count": len(prices), "products": prices},
    )


def parse_cbsl_exchange_rate_text(text: str) -> OfficialCostParserEvidenceRow:
    normalized = _plain_text(text)
    required_markers = [
        "Indicative Rate of the USD/LKR SPOT Exchange Rate",
        "Indicative Exchange Rates Search",
        "Buying and Selling Exchange Rate (TT) Search",
    ]
    missing = [marker for marker in required_markers if marker not in normalized]
    spreadsheet_labels = [
        label
        for label in [
            "Daily Buying and Selling Exchange Rate",
            "Monthly average spot exchange rates",
            "End month exchange rates- Spot",
            "Real Effective Exchange Rates",
        ]
        if label in normalized
    ]
    if missing or len(spreadsheet_labels) < 3:
        raise ValueError("CBSL exchange-rate text must expose official rate sections and spreadsheets")
    return OfficialCostParserEvidenceRow(
        source_key="cbsl-economic-data",
        parser_key="cbsl-exchange-rate-page",
        source_format="html",
        observed_label="CBSL exchange-rate page contract",
        evidence={"rate_sections": required_markers, "spreadsheet_labels": spreadsheet_labels},
    )


def parse_customs_tariff_text(text: str) -> OfficialCostParserEvidenceRow:
    normalized = _plain_text(text)
    year = re.search(r"Customs Import Tariff - (?P<year>\d{4})", normalized)
    updated = re.search(r"Last updated on:\s*(?P<date>\d{2}/\d{2}/\d{4})", normalized)
    chapter_count = re.search(r"(?P<count>\d+)\s+Chapters", normalized)
    disclaimer_present = "informational purposes" in normalized and "legal proceedings" in normalized
    if not year or not updated or not chapter_count or not disclaimer_present:
        raise ValueError("Customs tariff text must expose year, update date, chapter count, and legal-use notice")
    return OfficialCostParserEvidenceRow(
        source_key="sri-lanka-customs-tariff",
        parser_key="customs-import-tariff-index",
        source_format="html",
        observed_label=f"Customs Import Tariff {year.group('year')}",
        evidence={
            "tariff_year": year.group("year"),
            "last_updated": updated.group("date"),
            "chapter_count": int(chapter_count.group("count")),
            "legal_notice_present": disclaimer_present,
        },
    )


OFFICIAL_COST_PARSERS = {
    "pucsl-electricity": parse_pucsl_tariff_decision_text,
    "nwsdb-water": parse_nwsdb_water_tariff_text,
    "ntc-bus-fares": parse_ntc_bus_fare_text,
    "cpc-fuel": parse_cpc_fuel_price_text,
    "cbsl-economic-data": parse_cbsl_exchange_rate_text,
    "sri-lanka-customs-tariff": parse_customs_tariff_text,
}


def official_cost_parser_evidence_from_reviewed_fixtures() -> list[OfficialCostParserEvidenceRow]:
    evidence_rows: list[OfficialCostParserEvidenceRow] = []
    for source_key, fixture in OFFICIAL_COST_PARSER_FIXTURES.items():
        parser = OFFICIAL_COST_PARSERS[source_key]
        evidence = parser(fixture["text"])
        if evidence.parser_key != fixture["parser_key"] or evidence.source_format != fixture["source_format"]:
            raise ValueError(f"{source_key} parser metadata does not match reviewed fixture contract")
        evidence_rows.append(evidence)
    return evidence_rows


def _official_cost_source_url_map() -> dict[str, str]:
    source_map = {source.key: source.url for source in source_refs()}
    return {
        source_key: source_map[source_key]
        for source_key in OFFICIAL_COST_DIRECT_SOURCE_KEYS
        if source_key in source_map
    }


def _official_cost_direct_documents_from_parser_fixtures() -> list[DirectImportDocument]:
    source_urls = _official_cost_source_url_map()
    return [
        _document_from_data(
            source_key,
            source_urls.get(source_key, f"reviewed-fixture://{source_key}"),
            {
                "text": fixture["text"],
                "source_format": fixture["source_format"],
                "content_type": "text/plain; reviewed-fixture=true",
                "fixture": True,
            },
        )
        for source_key, fixture in OFFICIAL_COST_PARSER_FIXTURES.items()
    ]


async def _fetch_official_cost_document(client: httpx.AsyncClient, source_key: str, url: str) -> DirectImportDocument:
    response = await client.get(url, timeout=20)
    response.raise_for_status()
    content_type = response.headers.get("content-type", "").lower()
    if "pdf" in content_type or response.content.startswith(b"%PDF"):
        text = ""
        source_format = "pdf_text"
    else:
        text = _strip_html(response.text)
        source_format = "html" if "html" in content_type or "<html" in response.text[:500].lower() else "text"
    return DirectImportDocument(
        key=source_key,
        url=url,
        item_count=1,
        sha256=hashlib.sha256(response.content).hexdigest(),
        data={
            "text": text,
            "source_format": source_format,
            "content_type": content_type or "unknown",
            "byte_count": len(response.content),
            "fixture": False,
        },
    )


async def _fetch_json_payload(client: httpx.AsyncClient, key: str, url: str) -> DirectImportPayload:
    response = await client.get(url, timeout=20)
    response.raise_for_status()
    rows = response.json()
    if not isinstance(rows, list):
        raise ValueError(f"{key} payload is not a JSON list")
    return DirectImportPayload(
        key=key,
        url=url,
        row_count=len(rows),
        sha256=hashlib.sha256(response.content).hexdigest(),
        rows=rows,
    )


async def _fetch_json_document(client: httpx.AsyncClient, key: str, url: str) -> DirectImportDocument:
    response = await client.get(url, timeout=20)
    response.raise_for_status()
    data = response.json()
    return DirectImportDocument(
        key=key,
        url=url,
        item_count=_document_item_count(data),
        sha256=hashlib.sha256(response.content).hexdigest(),
        data=data,
    )


def _district_rows_by_region_id(rows: list[dict]) -> dict[str, dict]:
    region_ids = {row["region_id"] for row in DISTRICT_PROFILE_ROWS}
    return {
        str(row.get("region_id")): row
        for row in rows
        if str(row.get("region_id")) in region_ids
    }


def build_district_profile_rows_from_census_payloads(
    population_rows: list[dict],
    household_rows: list[dict],
    cooking_fuel_rows: list[dict],
    country_region_rows: list[dict] | None = None,
    province_region_rows: list[dict] | None = None,
    district_region_rows: list[dict] | None = None,
) -> list[DistrictProfileSeedRow]:
    population_by_region = _district_rows_by_region_id(population_rows)
    households_by_region = _district_rows_by_region_id(household_rows)
    cooking_by_region = _district_rows_by_region_id(cooking_fuel_rows)
    country_geography = {row.id: row for row in [AdminRegionRow(**item) for item in country_region_rows or []]}
    province_geography = {row.id: row for row in [AdminRegionRow(**item) for item in province_region_rows or []]}
    district_geography = {row.id: row for row in [AdminRegionRow(**item) for item in district_region_rows or []]}
    imported_rows: list[DistrictProfileSeedRow] = []
    missing: list[str] = []
    for seed in DISTRICT_PROFILE_ROWS:
        region_id = seed["region_id"]
        population_row = population_by_region.get(region_id)
        household_row = households_by_region.get(region_id)
        cooking_row = cooking_by_region.get(region_id)
        if region_id == "LK":
            geography_row = country_geography.get(region_id)
            province_name = "National"
        else:
            geography_row = district_geography.get(region_id)
            province_name = seed["province"]
            if geography_row and geography_row.province_id:
                province = province_geography.get(geography_row.province_id)
                province_name = province.name if province else province_name
        if not population_row or not household_row or not cooking_row or not geography_row:
            missing.append(region_id)
            continue

        population = int(population_row["total"])
        households = int(household_row["n_households"])
        gas_households = int(cooking_row["gas"])
        elderly_count = int(population_row["age-60-to-64"]) + int(population_row["age-65-and-over"])
        imported_rows.append(
            DistrictProfileSeedRow(
                key=seed["key"],
                region_id=region_id,
                province=province_name,
                population=population,
                households=households,
                area_sqkm=geography_row.area_sqkm,
                center_lat=geography_row.center_lat,
                center_lng=geography_row.center_lng,
                cooking_gas_share=round(gas_households / households, 3),
                elderly_share=round(elderly_count / population, 3),
            )
        )

    if missing:
        raise ValueError(f"missing direct census rows for: {', '.join(missing)}")
    return imported_rows


def _district_direct_payloads_from_seed_rows() -> list[DirectImportPayload]:
    population_rows = []
    household_rows = []
    cooking_rows = []
    country_region_rows = []
    province_region_rows = []
    district_region_rows = []
    province_names_to_id = {
        "Western": "LK-1",
        "Central": "LK-2",
        "Southern": "LK-3",
        "Northern": "LK-4",
        "Eastern": "LK-5",
        "North Western": "LK-6",
        "North Central": "LK-7",
        "Uva": "LK-8",
        "Sabaragamuwa": "LK-9",
    }
    for province_name, province_id in province_names_to_id.items():
        province_region_rows.append(
            {
                "id": province_id,
                "name": province_name,
                "area_sqkm": 1,
                "center_lat": 7.5,
                "center_lng": 80.5,
            }
        )
    for row in DISTRICT_PROFILE_ROWS:
        elderly_count = round(row["population"] * row["elderly_share"])
        gas_households = round(row["households"] * row["cooking_gas_share"])
        population_rows.append(
            {
                "region_id": row["region_id"],
                "region_name": row["key"],
                "region_ent_type": "country" if row["region_id"] == "LK" else "district",
                "total": row["population"],
                "age-60-to-64": 0,
                "age-65-and-over": elderly_count,
            }
        )
        household_rows.append(
            {
                "region_id": row["region_id"],
                "region_name": row["key"],
                "region_ent_type": "country" if row["region_id"] == "LK" else "district",
                "n_households": row["households"],
            }
        )
        cooking_rows.append(
            {
                "region_id": row["region_id"],
                "region_name": row["key"],
                "region_ent_type": "country" if row["region_id"] == "LK" else "district",
                "gas": gas_households,
            }
        )
        geography_row = {
            "id": row["region_id"],
            "name": row["key"],
            "area_sqkm": row["area_sqkm"],
            "center_lat": row["center_lat"],
            "center_lng": row["center_lng"],
        }
        if row["region_id"] == "LK":
            country_region_rows.append(geography_row)
        else:
            geography_row["province_id"] = province_names_to_id[row["province"]]
            district_region_rows.append(geography_row)
    return [
        _payload_from_rows("population", DISTRICT_DIRECT_IMPORT_URLS["population"], population_rows),
        _payload_from_rows("households", DISTRICT_DIRECT_IMPORT_URLS["households"], household_rows),
        _payload_from_rows("cooking_fuel", DISTRICT_DIRECT_IMPORT_URLS["cooking_fuel"], cooking_rows),
        _payload_from_rows("country_regions", DISTRICT_DIRECT_IMPORT_URLS["country_regions"], country_region_rows),
        _payload_from_rows("province_regions", DISTRICT_DIRECT_IMPORT_URLS["province_regions"], province_region_rows),
        _payload_from_rows("district_regions", DISTRICT_DIRECT_IMPORT_URLS["district_regions"], district_region_rows),
    ]


def _weather_observed_at_from_keys(date_key: str, time_key: str) -> datetime:
    compact_time = time_key.zfill(4)
    if len(compact_time) == 4:
        return datetime.strptime(f"{date_key}{compact_time}", "%Y%m%d%H%M").replace(tzinfo=timezone.utc)
    return datetime.strptime(f"{date_key}{compact_time}", "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)


def build_weather_station_rows_from_alert_payload(station_payload: dict, alert_payload: dict) -> list[WeatherStationSeedRow]:
    event_data = alert_payload.get("event_data")
    if not isinstance(station_payload, dict) or not isinstance(event_data, dict):
        raise ValueError("weather station and alert payloads must be JSON objects")

    source_station_id_by_name = {str(name): str(station_id) for station_id, name in station_payload.items()}
    seed_station_id_by_name = {row["station_name"]: str(row["station_id"]) for row in WEATHER_STATION_ROWS}
    imported_rows: list[WeatherStationSeedRow] = []
    missing: list[str] = []
    for seed in WEATHER_STATION_ROWS:
        station_name = seed["station_name"]
        source_station_name = WEATHER_SOURCE_STATION_ALIASES.get(station_name, station_name)
        station_dates = event_data.get(source_station_name)
        if not isinstance(station_dates, dict) or not station_dates:
            missing.append(station_name)
            continue
        latest_date = max(station_dates)
        station_times = station_dates[latest_date]
        if not isinstance(station_times, dict) or not station_times:
            missing.append(station_name)
            continue
        latest_time = max(station_times)
        measures = station_times[latest_time]
        if not isinstance(measures, dict):
            missing.append(station_name)
            continue
        humidity = float(measures["rh"])
        humidity_percent = humidity * 100 if humidity <= 1 else humidity
        imported_rows.append(
            WeatherStationSeedRow(
                station_id=seed_station_id_by_name.get(station_name) or source_station_id_by_name.get(source_station_name, source_station_name),
                station_name=station_name,
                observed_at=_weather_observed_at_from_keys(latest_date, latest_time),
                rainfall_mm=float(measures["rain_mm"]),
                temperature_c=float(measures["temp_c"]),
                humidity_percent=round(humidity_percent, 1),
            )
        )

    if missing:
        raise ValueError(f"missing direct weather rows for: {', '.join(missing)}")
    return imported_rows


def _latest_irrigation_water_levels(rows: list[dict]) -> list[IrrigationWaterLevelRow]:
    latest_by_station: dict[str, IrrigationWaterLevelRow] = {}
    errors: list[str] = []
    for index, row in enumerate(rows):
        try:
            level = IrrigationWaterLevelRow(**row)
        except ValidationError as exc:
            errors.append(f"row-{index}: {exc.errors()[0]['msg']}")
            if len(errors) >= 5:
                break
            continue
        current = latest_by_station.get(level.station_name)
        if current is None or level.time_ut > current.time_ut:
            latest_by_station[level.station_name] = level
    if errors:
        raise ValueError(f"invalid irrigation water-level rows: {'; '.join(errors)}")
    return sorted(latest_by_station.values(), key=lambda row: row.station_name)


def _weather_direct_documents_from_seed_rows() -> list[DirectImportDocument]:
    station_payload = {row["station_id"]: WEATHER_SOURCE_STATION_ALIASES.get(row["station_name"], row["station_name"]) for row in WEATHER_STATION_ROWS}
    event_data: dict[str, dict[str, dict[str, dict[str, float]]]] = {}
    for row in WEATHER_STATION_ROWS:
        station = WeatherStationSeedRow(**row)
        source_station_name = WEATHER_SOURCE_STATION_ALIASES.get(station.station_name, station.station_name)
        date_key = station.observed_at.strftime("%Y%m%d")
        time_key = station.observed_at.strftime("%H%M")
        event_data.setdefault(source_station_name, {}).setdefault(date_key, {})[time_key] = {
            "rain_mm": station.rainfall_mm,
            "temp_c": station.temperature_c,
            "rh": round(station.humidity_percent / 100, 3),
        }

    irrigation_rows = [
        {"station_name": "Nagalagam Street", "time_ut": utc_now().timestamp(), "water_level_m": 0.61},
        {"station_name": "Peradeniya", "time_ut": utc_now().timestamp(), "water_level_m": 1.73},
        {"station_name": "Thawalama", "time_ut": utc_now().timestamp(), "water_level_m": 2.63},
        {"station_name": "Ratnapura", "time_ut": utc_now().timestamp(), "water_level_m": 1.04},
        {"station_name": "Panadugama", "time_ut": utc_now().timestamp(), "water_level_m": 3.1},
    ]
    return [
        _document_from_data("weather_stations", WEATHER_DIRECT_IMPORT_URLS["weather_stations"], station_payload),
        _document_from_data(
            "weather_alerts",
            WEATHER_DIRECT_IMPORT_URLS["weather_alerts"],
            {
                "url_source": "https://www.meteo.gov.lk",
                "event": "weather_report_3h",
                "event_measures": ["rain_mm", "temp_c", "rh"],
                "event_data": event_data,
            },
        ),
        _document_from_data("irrigation_levels", WEATHER_DIRECT_IMPORT_URLS["irrigation_levels"], irrigation_rows),
    ]


def _district_direct_execution_from_payloads(
    payloads: list[DirectImportPayload],
    *,
    live_fetch: bool,
) -> SourceImportExecutionRun:
    payload_map = {payload.key: payload for payload in payloads}
    required_payload_keys = sorted(DISTRICT_DIRECT_IMPORT_URLS)
    missing_payloads = sorted(set(required_payload_keys) - set(payload_map))
    imported_rows: list[DistrictProfileSeedRow] = []
    parser_error = None
    if not missing_payloads:
        try:
            imported_rows = build_district_profile_rows_from_census_payloads(
                payload_map["population"].rows,
                payload_map["households"].rows,
                payload_map["cooking_fuel"].rows,
                payload_map["country_regions"].rows,
                payload_map["province_regions"].rows,
                payload_map["district_regions"].rows,
            )
        except (KeyError, TypeError, ValueError, ValidationError) as exc:
            parser_error = str(exc)

    seed_by_region = {row["region_id"]: row for row in DISTRICT_PROFILE_ROWS}
    imported_by_region = {row.region_id: row for row in imported_rows}
    population_mismatches = []
    household_mismatches = []
    gas_share_mismatches = []
    elderly_share_mismatches = []
    province_mismatches = []
    area_mismatches = []
    center_mismatches = []
    for region_id, seed in seed_by_region.items():
        imported = imported_by_region.get(region_id)
        if imported is None:
            continue
        if imported.province != seed["province"]:
            province_mismatches.append(f"{seed['key']}: {imported.province} != {seed['province']}")
        if imported.population != seed["population"]:
            population_mismatches.append(f"{seed['key']}: {imported.population} != {seed['population']}")
        if imported.households != seed["households"]:
            household_mismatches.append(f"{seed['key']}: {imported.households} != {seed['households']}")
        if abs(imported.area_sqkm - seed["area_sqkm"]) > 0.01:
            area_mismatches.append(f"{seed['key']}: {imported.area_sqkm:.2f} != {seed['area_sqkm']:.2f}")
        if abs(imported.center_lat - seed["center_lat"]) > 0.000001 or abs(imported.center_lng - seed["center_lng"]) > 0.000001:
            center_mismatches.append(f"{seed['key']}: {imported.center_lat:.6f},{imported.center_lng:.6f} != {seed['center_lat']:.6f},{seed['center_lng']:.6f}")
        if abs(imported.cooking_gas_share - seed["cooking_gas_share"]) > 0.002:
            gas_share_mismatches.append(f"{seed['key']}: {imported.cooking_gas_share:.3f} != {seed['cooking_gas_share']:.3f}")
        if abs(imported.elderly_share - seed["elderly_share"]) > 0.002:
            elderly_share_mismatches.append(f"{seed['key']}: {imported.elderly_share:.3f} != {seed['elderly_share']:.3f}")

    checks = [
        _check(
            key="live-fetch",
            label="Live fetch",
            status="pass" if live_fetch else "watch",
            message="Fetched raw nuuuwan census JSON over HTTPS."
            if live_fetch
            else "Live fetch disabled; parser contract ran against bundled reviewed seed-shaped payloads.",
            evidence=[
                f"{payload.key}: rows={payload.row_count}, sha256={payload.sha256[:12]}"
                for payload in payloads
            ],
        ),
        _check(
            key="payload-presence",
            label="Payload presence",
            status="fail" if missing_payloads else "pass",
            message="All required direct census payloads are available." if not missing_payloads else "One or more required direct census payloads is missing.",
            evidence=[f"missing: {', '.join(missing_payloads) or 'none'}"],
        ),
        _check(
            key="typed-row-import",
            label="Typed row import",
            status="fail" if parser_error else "pass",
            message="Direct census payloads normalize into DistrictProfileSeedRow records."
            if not parser_error
            else "Direct census payloads failed typed row normalization.",
            evidence=[parser_error] if parser_error else [f"{len(imported_rows)} typed district profile rows"],
        ),
        _check(
            key="coverage",
            label="Coverage",
            status="fail" if len(imported_rows) != len(DISTRICT_PROFILE_ROWS) else "pass",
            message="Direct import covers Sri Lanka plus all 25 districts."
            if len(imported_rows) == len(DISTRICT_PROFILE_ROWS)
            else "Direct import coverage does not match current district profile coverage.",
            evidence=[f"imported rows: {len(imported_rows)}", f"expected rows: {len(DISTRICT_PROFILE_ROWS)}"],
        ),
        _check(
            key="seed-reconciliation",
            label="Seed reconciliation",
            status="fail"
            if population_mismatches
            or household_mismatches
            or province_mismatches
            or area_mismatches
            or center_mismatches
            or gas_share_mismatches
            or elderly_share_mismatches
            else "pass",
            message="Direct census fields reconcile with the reviewed seed values within tolerance."
            if not population_mismatches
            and not household_mismatches
            and not province_mismatches
            and not area_mismatches
            and not center_mismatches
            and not gas_share_mismatches
            and not elderly_share_mismatches
            else "Direct census fields differ from reviewed seed values.",
            evidence=[
                f"population mismatches: {len(population_mismatches)}",
                f"household mismatches: {len(household_mismatches)}",
                f"province mismatches: {len(province_mismatches)}",
                f"area mismatches: {len(area_mismatches)}",
                f"center mismatches: {len(center_mismatches)}",
                f"gas-share mismatches: {len(gas_share_mismatches)}",
                f"elderly-share mismatches: {len(elderly_share_mismatches)}",
                *population_mismatches[:3],
                *household_mismatches[:3],
                *province_mismatches[:3],
                *area_mismatches[:3],
                *center_mismatches[:3],
                *gas_share_mismatches[:3],
                *elderly_share_mismatches[:3],
            ],
        ),
        _check(
            key="field-source-boundary",
            label="Field source boundary",
            status="pass" if live_fetch else "watch",
            message="All district profile fields have direct source payload lineage for this live run."
            if live_fetch
            else "Offline contract mode uses seed-shaped payloads; run live_fetch=true before promotion.",
            evidence=[
                "census payload fields: population, households, cooking_gas_share, elderly_share",
                "admin-region payload fields: province, area_sqkm, center_lat, center_lng",
            ],
        ),
    ]
    status = _status_for(checks)
    normalized_records = [
        {"record_type": "district_profile", **row.model_dump(mode="json")}
        for row in imported_rows
    ]
    return SourceImportExecutionRun(
        key="district-profile-direct-run",
        label="District profile direct import run",
        domain_key="areas",
        status=status,
        mode="live_fetch" if live_fetch else "offline_contract",
        rows_imported=len(imported_rows),
        accepted_for_scoring=status == "pass",
        source_keys=DISTRICT_PROFILE_SOURCE_KEYS,
        fetched_urls=[payload.url for payload in payloads],
        storage_target="DistrictProfile response rows and area_score_snapshots after promotion review",
        action="Direct district profile importer is ready for promotion review."
        if status != "fail"
        else "Fix direct census importer failures before any promotion.",
        normalized_records=normalized_records,
        checks=checks,
    )


def _weather_direct_execution_from_documents(
    documents: list[DirectImportDocument],
    *,
    live_fetch: bool,
) -> SourceImportExecutionRun:
    document_map = {document.key: document for document in documents}
    required_document_keys = sorted(WEATHER_DIRECT_IMPORT_URLS)
    missing_documents = sorted(set(required_document_keys) - set(document_map))
    imported_rows: list[WeatherStationSeedRow] = []
    latest_levels: list[IrrigationWaterLevelRow] = []
    parser_error = None
    if not missing_documents:
        try:
            imported_rows = build_weather_station_rows_from_alert_payload(
                document_map["weather_stations"].data,
                document_map["weather_alerts"].data,
            )
            irrigation_rows = document_map["irrigation_levels"].data
            if not isinstance(irrigation_rows, list):
                raise ValueError("irrigation_levels payload must be a JSON list")
            latest_levels = _latest_irrigation_water_levels(irrigation_rows)
        except (KeyError, TypeError, ValueError, ValidationError) as exc:
            parser_error = str(exc)

    seed_by_station = {row["station_name"]: WeatherStationSeedRow(**row) for row in WEATHER_STATION_ROWS}
    imported_by_station = {row.station_name: row for row in imported_rows}
    rainfall_mismatches = []
    temperature_mismatches = []
    humidity_mismatches = []
    observed_at_mismatches = []
    for station_name, seed in seed_by_station.items():
        imported = imported_by_station.get(station_name)
        if imported is None:
            continue
        if abs(imported.rainfall_mm - seed.rainfall_mm) > 0.01:
            rainfall_mismatches.append(f"{station_name}: {imported.rainfall_mm:g} != {seed.rainfall_mm:g}")
        if abs(imported.temperature_c - seed.temperature_c) > 0.01:
            temperature_mismatches.append(f"{station_name}: {imported.temperature_c:g} != {seed.temperature_c:g}")
        if abs(imported.humidity_percent - seed.humidity_percent) > 0.1:
            humidity_mismatches.append(f"{station_name}: {imported.humidity_percent:g} != {seed.humidity_percent:g}")
        if imported.observed_at != seed.observed_at:
            observed_at_mismatches.append(f"{station_name}: {imported.observed_at.isoformat()} != {seed.observed_at.isoformat()}")

    imported_station_names = {row.station_name for row in imported_rows}
    mapped_station_names = {station_name for station_name, _coverage in DISTRICT_WEATHER_STATIONS.values()}
    missing_mapped_stations = sorted(mapped_station_names - imported_station_names)
    missing_districts = sorted(set(DISTRICTS) - set(DISTRICT_WEATHER_STATIONS))
    latest_level_at = max((datetime.fromtimestamp(level.time_ut, tz=timezone.utc) for level in latest_levels), default=None)
    required_level_count = 25 if live_fetch else 3
    river_context_status = "fail" if len(latest_levels) < required_level_count else "pass"
    normalized_records = [
        {"record_type": "weather_station", **row.model_dump(mode="json")}
        for row in imported_rows
    ]
    normalized_records.extend(
        {
            "record_type": "irrigation_water_level",
            **level.model_dump(mode="json"),
            "observed_at": datetime.fromtimestamp(level.time_ut, tz=timezone.utc).isoformat(),
        }
        for level in latest_levels
    )

    checks = [
        _check(
            key="live-fetch",
            label="Live fetch",
            status="pass" if live_fetch else "watch",
            message="Fetched raw weather and irrigation JSON over HTTPS."
            if live_fetch
            else "Live fetch disabled; parser contract ran against bundled reviewed seed-shaped weather payloads.",
            evidence=[
                f"{document.key}: items={document.item_count}, sha256={document.sha256[:12]}"
                for document in documents
            ],
        ),
        _check(
            key="payload-presence",
            label="Payload presence",
            status="fail" if missing_documents else "pass",
            message="All required direct weather/risk payloads are available." if not missing_documents else "One or more required direct weather/risk payloads is missing.",
            evidence=[f"missing: {', '.join(missing_documents) or 'none'}"],
        ),
        _check(
            key="typed-station-import",
            label="Typed station import",
            status="fail" if parser_error else "pass",
            message="Direct weather payloads normalize into WeatherStationSeedRow records and current irrigation rows."
            if not parser_error
            else "Direct weather/risk payloads failed typed normalization.",
            evidence=[parser_error] if parser_error else [f"{len(imported_rows)} weather station rows", f"{len(latest_levels)} current irrigation stations"],
        ),
        _check(
            key="district-station-coverage",
            label="District station coverage",
            status="fail" if missing_districts or missing_mapped_stations or len(DISTRICT_WEATHER_STATIONS) != 26 else "pass",
            message="Every displayed district maps to a direct, proxy, or national station row."
            if not missing_districts and not missing_mapped_stations and len(DISTRICT_WEATHER_STATIONS) == 26
            else "Weather district mapping is incomplete.",
            evidence=[
                f"mappings: {len(DISTRICT_WEATHER_STATIONS)}",
                f"imported stations: {len(imported_station_names)}",
                f"missing districts: {', '.join(missing_districts) or 'none'}",
                f"missing station rows: {', '.join(missing_mapped_stations) or 'none'}",
            ],
        ),
        _check(
            key="seed-reconciliation",
            label="Seed reconciliation",
            status="fail"
            if rainfall_mismatches
            or temperature_mismatches
            or humidity_mismatches
            or observed_at_mismatches
            else "pass",
            message="Direct weather station fields reconcile with the reviewed seed values within tolerance."
            if not rainfall_mismatches
            and not temperature_mismatches
            and not humidity_mismatches
            and not observed_at_mismatches
            else "Direct weather station fields differ from reviewed seed values.",
            evidence=[
                f"rainfall mismatches: {len(rainfall_mismatches)}",
                f"temperature mismatches: {len(temperature_mismatches)}",
                f"humidity mismatches: {len(humidity_mismatches)}",
                f"observed_at mismatches: {len(observed_at_mismatches)}",
                *rainfall_mismatches[:3],
                *temperature_mismatches[:3],
                *humidity_mismatches[:3],
                *observed_at_mismatches[:3],
            ],
        ),
        _check(
            key="river-water-context",
            label="River water context",
            status=river_context_status,
            message="Current irrigation water-level feed has enough station coverage for planning risk context."
            if river_context_status == "pass"
            else "Irrigation water-level feed does not have enough current station coverage for planning risk context.",
            evidence=[
                f"latest irrigation stations: {len(latest_levels)}",
                f"required stations: {required_level_count}",
                f"latest time_ut: {latest_level_at.isoformat() if latest_level_at else 'unavailable'}",
            ],
        ),
        _check(
            key="field-source-boundary",
            label="Field source boundary",
            status="pass" if live_fetch else "watch",
            message="Weather score inputs have direct weather-station and irrigation water-level payload lineage for this live run."
            if live_fetch
            else "Offline contract mode uses seed-shaped payloads; run live_fetch=true before promotion.",
            evidence=[
                "weather payload fields: observed_at, rainfall_mm, temperature_c, humidity_percent",
                "irrigation payload fields: station_name, time_ut, water_level_m",
                "alert boundary: planning score only; DMC warning automation remains a separate promotion gate",
            ],
        ),
    ]
    status = _status_for(checks)
    return SourceImportExecutionRun(
        key="weather-risk-direct-run",
        label="Weather and risk direct import run",
        domain_key="weather",
        status=status,
        mode="live_fetch" if live_fetch else "offline_contract",
        rows_imported=len(imported_rows) + len(latest_levels),
        accepted_for_scoring=status == "pass",
        source_keys=WEATHER_RISK_SOURCE_KEYS,
        fetched_urls=[document.url for document in documents],
        storage_target="WeatherRiskObservation response rows and weather component scores after promotion review",
        action="Direct weather/risk importer is ready for planning-score promotion review; keep emergency alerting behind DMC warning ingestion."
        if status != "fail"
        else "Fix direct weather/risk importer failures before any promotion.",
        normalized_records=normalized_records,
        checks=checks,
    )


def _official_cost_direct_execution_from_documents(
    documents: list[DirectImportDocument],
    *,
    live_fetch: bool,
    fetch_errors: list[str] | None = None,
) -> SourceImportExecutionRun:
    document_map = {document.key: document for document in documents}
    required_source_keys = OFFICIAL_COST_DIRECT_SOURCE_KEYS
    missing_documents = sorted(set(required_source_keys) - set(document_map))
    fetch_errors = fetch_errors or []
    parser_evidence_rows: list[OfficialCostParserEvidenceRow] = []
    parser_warnings: list[str] = []
    normalized_records: list[dict[str, Any]] = []

    for source_key in required_source_keys:
        document = document_map.get(source_key)
        if document is None:
            continue
        data = document.data if isinstance(document.data, dict) else {}
        text = str(data.get("text") or "")
        if not text:
            parser_warnings.append(f"{source_key}: fetched {data.get('content_type', 'unknown')} but no extracted text is available")
            normalized_records.append(
                {
                    "record_type": "official_cost_fetch_evidence",
                    "source_key": source_key,
                    "url": document.url,
                    "content_type": data.get("content_type", "unknown"),
                    "byte_count": data.get("byte_count"),
                    "sha256": document.sha256,
                    "parser_status": "watch",
                    "note": "Fetched source document; text extraction still needs operator-reviewed tooling.",
                }
            )
            continue
        try:
            evidence = OFFICIAL_COST_PARSERS[source_key](text)
        except (KeyError, TypeError, ValueError, ValidationError) as exc:
            parser_warnings.append(f"{source_key}: {exc}")
            normalized_records.append(
                {
                    "record_type": "official_cost_fetch_evidence",
                    "source_key": source_key,
                    "url": document.url,
                    "content_type": data.get("content_type", "unknown"),
                    "byte_count": data.get("byte_count"),
                    "sha256": document.sha256,
                    "parser_status": "watch",
                    "note": str(exc),
                }
            )
            continue
        parser_evidence_rows.append(evidence)
        normalized_records.append(
            {
                "record_type": "official_cost_parser_evidence",
                "source_key": evidence.source_key,
                "parser_key": evidence.parser_key,
                "source_format": evidence.source_format,
                "observed_label": evidence.observed_label,
                "evidence": evidence.evidence,
                "url": document.url,
                "content_type": data.get("content_type", "unknown"),
                "byte_count": data.get("byte_count"),
                "sha256": document.sha256,
                "fixture": bool(data.get("fixture")),
            }
        )

    checks = [
        _check(
            key="live-fetch",
            label="Live fetch",
            status="watch" if live_fetch and fetch_errors else "pass" if live_fetch else "watch",
            message="Fetched available official tariff/import source documents over HTTPS; one or more source needs retry."
            if live_fetch and fetch_errors
            else "Fetched official tariff/import source documents over HTTPS."
            if live_fetch
            else "Live fetch disabled; parser contract ran against reviewed official-source snippets.",
            evidence=[
                f"{document.key}: items={document.item_count}, sha256={document.sha256[:12]}, type={document.data.get('content_type', 'unknown') if isinstance(document.data, dict) else 'unknown'}"
                for document in documents
            ],
        ),
        _check(
            key="payload-presence",
            label="Payload presence",
            status="watch" if missing_documents or fetch_errors else "pass",
            message="All required official cost/import source documents are represented." if not missing_documents else "One or more official cost/import source document is missing.",
            evidence=[
                f"missing: {', '.join(missing_documents) or 'none'}",
                *fetch_errors,
            ],
        ),
        _check(
            key="source-specific-parser-evidence",
            label="Source-specific parser evidence",
            status="watch" if missing_documents or fetch_errors or parser_warnings else "pass",
            message="Official cost/import parser evidence was produced for every required source."
            if not missing_documents and not fetch_errors and not parser_warnings
            else "Official cost/import run produced review evidence, but one or more source still needs extraction or parser review.",
            evidence=fetch_errors
            or parser_warnings
            or [
                f"{row.source_key}: {row.parser_key} -> {row.observed_label}"
                for row in parser_evidence_rows
            ],
        ),
        _check(
            key="promotion-boundary",
            label="Promotion boundary",
            status="watch",
            message="Official cost/import direct runs are review-only until live source extraction and operator notes are approved.",
            evidence=[
                "accepted_for_scoring=false for this run family",
                "tariff/import rows remain planning signals",
                "operator review must approve effective dates before unattended promotion",
            ],
        ),
    ]
    status = _status_for(checks)
    return SourceImportExecutionRun(
        key="official-cost-direct-run",
        label="Official cost and import context direct run",
        domain_key="utilities",
        status=status,
        mode="live_fetch" if live_fetch else "offline_contract",
        rows_imported=len(normalized_records),
        accepted_for_scoring=False,
        source_keys=OFFICIAL_COST_DIRECT_SOURCE_KEYS,
        fetched_urls=[document.url for document in documents],
        storage_target="Review-only official cost parser evidence; tariff_snapshots and transport_fare_snapshots stay seed-backed until promotion review",
        action="Review official cost/import parser evidence and add operator notes before enabling any tariff/import promotion.",
        normalized_records=normalized_records,
        checks=checks,
    )


def _status_for(checks: list[SourceImportCheck]) -> str:
    if any(check.status == "fail" for check in checks):
        return "fail"
    if any(check.status == "watch" for check in checks):
        return "watch"
    return "pass"


def _source_gate_checks(source_keys: list[str]) -> list[SourceImportCheck]:
    source_map = {source.key: source for source in source_refs()}
    missing = sorted(key for key in source_keys if key not in source_map)
    unreviewed = sorted(
        key
        for key in source_keys
        if key in source_map and source_map[key].review_status in {"candidate", "needs_review"}
    )
    needs_license_review = sorted(
        key
        for key in source_keys
        if key in source_map and source_map[key].license_status in {"needs_review", "terms_review"}
    )
    return [
        _check(
            key="source-registry-presence",
            label="Source registry presence",
            status="fail" if missing else "pass",
            message="Every importer source key exists in source_registry." if not missing else "Importer has missing source keys.",
            evidence=[f"missing: {', '.join(missing) or 'none'}"],
        ),
        _check(
            key="source-review-gate",
            label="Source review gate",
            status="fail" if unreviewed or needs_license_review else "pass",
            message="Importer source keys are approved or reviewed for seed use."
            if not unreviewed and not needs_license_review
            else "Importer includes candidate, terms-review, or unreviewed source keys.",
            evidence=[
                f"unreviewed/candidate: {', '.join(unreviewed) or 'none'}",
                f"license review needed: {', '.join(needs_license_review) or 'none'}",
            ],
        ),
    ]


def _readiness_source_gate_checks(
    source_keys: list[str],
    *,
    source_map: dict,
    allow_candidate_sources: bool = False,
) -> list[SourceImportCheck]:
    missing = sorted(key for key in source_keys if key not in source_map)
    candidate_or_review = sorted(
        key
        for key in source_keys
        if key in source_map
        and (
            source_map[key].review_status in {"candidate", "needs_review"}
            or source_map[key].license_status in {"needs_review", "terms_review"}
        )
    )
    if missing:
        review_status = "fail"
        review_message = "Direct import manifest has missing source registry keys."
    elif candidate_or_review and not allow_candidate_sources:
        review_status = "fail"
        review_message = "Direct import manifest includes sources that are not cleared for scoring."
    elif candidate_or_review:
        review_status = "watch"
        review_message = "Candidate providers remain isolated until terms, limits, and coverage are reviewed."
    else:
        review_status = "pass"
        review_message = "Manifest sources exist and are reviewed for the current import role."

    return [
        _check(
            key="manifest-source-presence",
            label="Manifest source presence",
            status="fail" if missing else "pass",
            message="Every manifest source key exists in source_registry." if not missing else "Manifest has missing source keys.",
            evidence=[f"missing: {', '.join(missing) or 'none'}"],
        ),
        _check(
            key="manifest-source-review",
            label="Manifest source review",
            status=review_status,
            message=review_message,
            evidence=[f"candidate or terms-review: {', '.join(candidate_or_review) or 'none'}"],
        ),
    ]


def _endpoint(
    source_map: dict,
    *,
    key: str,
    label: str,
    source_key: str,
    method: str,
    status: str = "ready",
    required: bool = True,
    note: str,
) -> SourceImportEndpoint:
    source = source_map.get(source_key)
    if source is None:
        return SourceImportEndpoint(
            key=key,
            label=label,
            source_key=source_key,
            url="",
            method=method,
            required=required,
            status="blocked",
            note="Missing source registry entry.",
        )
    return SourceImportEndpoint(
        key=key,
        label=label,
        source_key=source_key,
        url=source.url,
        method=method,
        required=required,
        status=status,
        note=note,
    )


def _district_profile_importer() -> SourceImportRun:
    errors: list[str] = []
    for index, row in enumerate(DISTRICT_PROFILE_ROWS):
        try:
            DistrictProfileSeedRow(**row)
        except ValidationError as exc:
            errors.append(f"{row.get('key', f'row-{index}')}: {exc.errors()[0]['msg']}")

    keys = [row["key"] for row in DISTRICT_PROFILE_ROWS]
    duplicates = sorted({key for key in keys if keys.count(key) > 1})
    expected_keys = set(DISTRICTS)
    missing = sorted(expected_keys - set(keys))
    extra = sorted(set(keys) - expected_keys)
    national_rows = [row for row in DISTRICT_PROFILE_ROWS if row["key"] == "Sri Lanka"]
    district_rows = [row for row in DISTRICT_PROFILE_ROWS if row["key"] != "Sri Lanka"]
    district_population_total = sum(row["population"] for row in district_rows)
    national_population = national_rows[0]["population"] if national_rows else 0
    population_delta = abs(national_population - district_population_total)
    population_delta_ratio = population_delta / national_population if national_population else 1

    checks = [
        _check(
            key="typed-row-validation",
            label="Typed row validation",
            status="fail" if errors else "pass",
            message="All district profile rows satisfy the typed import contract."
            if not errors
            else "One or more district profile rows failed typed validation.",
            evidence=errors[:5] or [f"{len(DISTRICT_PROFILE_ROWS)} rows validated"],
        ),
        _check(
            key="coverage",
            label="Coverage",
            status="fail" if duplicates or missing or extra or len(keys) != 26 else "pass",
            message="District importer covers Sri Lanka plus all 25 districts exactly once."
            if not duplicates and not missing and not extra and len(keys) == 26
            else "District importer coverage is incomplete or duplicated.",
            evidence=[
                f"rows: {len(keys)}",
                f"duplicates: {', '.join(duplicates) or 'none'}",
                f"missing: {', '.join(missing) or 'none'}",
                f"extra: {', '.join(extra) or 'none'}",
            ],
        ),
        _check(
            key="national-total-reconciliation",
            label="National total reconciliation",
            status="watch" if population_delta_ratio > 0.01 else "pass",
            message="District population rows reconcile with the national row within 1%."
            if population_delta_ratio <= 0.01
            else "District population total differs from the national row by more than 1%.",
            evidence=[
                f"national: {national_population}",
                f"district total: {district_population_total}",
                f"delta ratio: {population_delta_ratio:.4f}",
            ],
        ),
        *_source_gate_checks(DISTRICT_PROFILE_SOURCE_KEYS),
    ]
    status = _status_for(checks)
    return SourceImportRun(
        key="district-profile-seed-import",
        label="District profile seed import",
        domain_key="areas",
        status=status,
        rows_checked=len(DISTRICT_PROFILE_ROWS),
        accepted_for_scoring=status == "pass",
        source_keys=DISTRICT_PROFILE_SOURCE_KEYS,
        storage_target="DistrictProfile response rows and area_score_snapshots",
        collection_method="reviewed_seed_extract",
        action="Replace with direct DCS/public-data importer before production automation." if status == "pass" else "Fix importer checks before score promotion.",
        checks=checks,
    )


def _weather_risk_importer() -> SourceImportRun:
    errors: list[str] = []
    for index, row in enumerate(WEATHER_STATION_ROWS):
        try:
            WeatherStationSeedRow(**row)
        except ValidationError as exc:
            errors.append(f"{row.get('station_name', f'row-{index}')}: {exc.errors()[0]['msg']}")

    station_names = [row["station_name"] for row in WEATHER_STATION_ROWS]
    duplicate_stations = sorted({name for name in station_names if station_names.count(name) > 1})
    mapped_station_names = [station_name for station_name, _coverage in DISTRICT_WEATHER_STATIONS.values()]
    missing_mapped_stations = sorted(set(mapped_station_names) - set(station_names))
    missing_districts = sorted(set(DISTRICTS) - set(DISTRICT_WEATHER_STATIONS))
    coverage_values = [coverage for _station_name, coverage in DISTRICT_WEATHER_STATIONS.values()]
    direct_count = coverage_values.count("direct")
    proxy_count = coverage_values.count("proxy")
    national_count = coverage_values.count("national")
    latest_observed = max(WeatherStationSeedRow(**row).observed_at for row in WEATHER_STATION_ROWS) if not errors else None

    checks = [
        _check(
            key="typed-row-validation",
            label="Typed row validation",
            status="fail" if errors else "pass",
            message="All weather station rows satisfy the typed import contract."
            if not errors
            else "One or more weather station rows failed typed validation.",
            evidence=errors[:5] or [f"{len(WEATHER_STATION_ROWS)} station rows validated"],
        ),
        _check(
            key="station-identity",
            label="Station identity",
            status="fail" if duplicate_stations else "pass",
            message="Station names are unique within the reviewed seed payload."
            if not duplicate_stations
            else "Weather station rows include duplicate station names.",
            evidence=[f"duplicates: {', '.join(duplicate_stations) or 'none'}"],
        ),
        _check(
            key="district-station-coverage",
            label="District station coverage",
            status="fail" if missing_districts or missing_mapped_stations or len(DISTRICT_WEATHER_STATIONS) != 26 else "pass",
            message="Every displayed district maps to a direct, proxy, or national station row."
            if not missing_districts and not missing_mapped_stations and len(DISTRICT_WEATHER_STATIONS) == 26
            else "Weather district mapping is incomplete.",
            evidence=[
                f"mappings: {len(DISTRICT_WEATHER_STATIONS)}",
                f"direct: {direct_count}",
                f"proxy: {proxy_count}",
                f"national: {national_count}",
                f"missing districts: {', '.join(missing_districts) or 'none'}",
                f"missing station rows: {', '.join(missing_mapped_stations) or 'none'}",
            ],
        ),
        _check(
            key="freshness-window",
            label="Freshness window",
            status="pass",
            message="Seed weather observations carry explicit observed_at timestamps and are labelled as planning data.",
            evidence=[f"latest observed_at: {latest_observed.isoformat() if latest_observed else 'unavailable'}"],
        ),
        *_source_gate_checks(WEATHER_RISK_SOURCE_KEYS),
    ]
    status = _status_for(checks)
    return SourceImportRun(
        key="weather-risk-seed-import",
        label="Weather risk seed import",
        domain_key="weather",
        status=status,
        rows_checked=len(WEATHER_STATION_ROWS) + len(DISTRICT_WEATHER_STATIONS),
        accepted_for_scoring=status == "pass",
        source_keys=WEATHER_RISK_SOURCE_KEYS,
        storage_target="WeatherRiskObservation response rows and weather component scores",
        collection_method="reviewed_seed_extract",
        action="Promote the direct weather/risk run after release review; keep DMC warning automation separate before operational alerting."
        if status == "pass"
        else "Fix importer checks before score promotion.",
        checks=checks,
    )


def _official_cost_importer() -> SourceImportRun:
    tariff_errors: list[str] = []
    fare_errors: list[str] = []
    parser_errors: list[str] = []
    tariff_rows = [*UTILITY_TARIFFS, *GAS_TARIFFS]
    fare_rows = TRANSPORT_OPTIONS
    try:
        parser_evidence_rows = official_cost_parser_evidence_from_reviewed_fixtures()
    except (KeyError, TypeError, ValueError, ValidationError) as exc:
        parser_evidence_rows = []
        parser_errors.append(str(exc))

    for index, row in enumerate(tariff_rows):
        try:
            TariffSeedRow(**row)
        except ValidationError as exc:
            tariff_errors.append(f"{row.get('key', f'tariff-{index}')}: {exc.errors()[0]['msg']}")

    for index, row in enumerate(fare_rows):
        try:
            TransportFareSeedRow(**row)
        except ValidationError as exc:
            fare_errors.append(f"{row.get('mode', f'fare-{index}')}: {exc.errors()[0]['msg']}")

    tariff_source_keys = sorted({row["source_key"] for row in tariff_rows})
    fare_source_keys = sorted({row["source_key"] for row in fare_rows})
    missing_required_sources = sorted(set(OFFICIAL_COST_SOURCE_KEYS) - set(tariff_source_keys) - set(fare_source_keys))
    duplicate_tariff_keys = sorted({row["key"] for row in tariff_rows if [item["key"] for item in tariff_rows].count(row["key"]) > 1})
    duplicate_routes = sorted(
        {
            f"{row['mode']}:{row['from_area']}->{row['to_area']}"
            for row in fare_rows
            if [
                f"{item['mode']}:{item['from_area']}->{item['to_area']}"
                for item in fare_rows
            ].count(f"{row['mode']}:{row['from_area']}->{row['to_area']}") > 1
        }
    )

    checks = [
        _check(
            key="typed-tariff-validation",
            label="Typed tariff validation",
            status="fail" if tariff_errors or duplicate_tariff_keys else "pass",
            message="Utility and LPG tariff planning rows satisfy the typed seed contract."
            if not tariff_errors and not duplicate_tariff_keys
            else "One or more tariff planning rows failed validation or has a duplicate key.",
            evidence=tariff_errors[:5]
            or [
                f"{len(tariff_rows)} tariff rows validated",
                f"duplicate keys: {', '.join(duplicate_tariff_keys) or 'none'}",
            ],
        ),
        _check(
            key="typed-fare-validation",
            label="Typed fare validation",
            status="fail" if fare_errors or duplicate_routes else "pass",
            message="Transport fare planning rows satisfy the typed seed contract."
            if not fare_errors and not duplicate_routes
            else "One or more transport fare planning rows failed validation or has a duplicate route.",
            evidence=fare_errors[:5]
            or [
                f"{len(fare_rows)} transport rows validated",
                f"duplicate routes: {', '.join(duplicate_routes) or 'none'}",
            ],
        ),
        _check(
            key="official-source-coverage",
            label="Official source coverage",
            status="fail" if missing_required_sources else "pass",
            message="Current utility, LPG, transport, and fuel planning rows point to registered official sources."
            if not missing_required_sources
            else "One or more official source references is not represented in the current cost seed rows.",
            evidence=[
                f"tariff source keys: {', '.join(tariff_source_keys)}",
                f"fare source keys: {', '.join(fare_source_keys)}",
                f"missing required: {', '.join(missing_required_sources) or 'none'}",
            ],
        ),
        _check(
            key="source-specific-parser-fixtures",
            label="Source-specific parser fixtures",
            status="fail" if parser_errors else "pass",
            message="Reviewed official snippets exercise source-specific parser contracts for tariff, fare, fuel, exchange-rate, and customs pages."
            if not parser_errors
            else "One or more reviewed official parser fixture failed.",
            evidence=parser_errors
            or [
                f"{row.source_key}: {row.parser_key} -> {row.observed_label}"
                for row in parser_evidence_rows
            ],
        ),
        *_source_gate_checks(OFFICIAL_COST_SOURCE_KEYS),
        *_source_gate_checks(OFFICIAL_IMPORT_CONTEXT_SOURCE_KEYS),
    ]
    status = _status_for(checks)
    return SourceImportRun(
        key="official-cost-seed-import",
        label="Official cost seed import",
        domain_key="utilities",
        status=status,
        rows_checked=len(tariff_rows) + len(fare_rows) + len(parser_evidence_rows),
        accepted_for_scoring=status == "pass",
        source_keys=OFFICIAL_COST_SOURCE_KEYS + OFFICIAL_IMPORT_CONTEXT_SOURCE_KEYS,
        storage_target="tariff_snapshots and transport_fare_snapshots",
        collection_method="reviewed_official_seed_rows",
        action="Parser fixtures are covered; promote direct tariff/import fetches only after live source review and operator release evidence."
        if status == "pass"
        else "Fix official cost seed rows before public cost outputs rely on them.",
        checks=checks,
    )


def _district_profile_direct_manifest(source_map: dict) -> SourceImportManifest:
    source_keys = DISTRICT_PROFILE_SOURCE_KEYS
    checks = [
        *_readiness_source_gate_checks(source_keys, source_map=source_map),
        _check(
            key="parser-contract",
            label="Parser contract",
            status="pass",
            message="The guarded direct importer fetches raw census and admin-region payloads, validates typed district rows, and records reconciliation evidence.",
            evidence=[
                "contract: DistrictProfileSeedRow",
                "required rows: Sri Lanka plus 25 districts",
                "required fields: region_id, province, population, households, area, centroid, gas share, elderly share",
                "execution gate: POST /api/v1/internal/source-import-run?live_fetch=true",
                "promotion gate: POST /api/v1/internal/source-import-run?live_fetch=true&promote=true",
            ],
        ),
        _check(
            key="storage-target",
            label="Storage target",
            status="pass",
            message="The target response and snapshot paths are already defined.",
            evidence=["DistrictProfile response rows", "area_score_snapshots", "source_registry"],
        ),
    ]
    status = _status_for(checks)
    return SourceImportManifest(
        key="district-profile-direct-import",
        label="District profile direct import",
        domain_key="areas",
        status=status,
        promotion_status="direct_ready",
        accepted_for_direct_run=True,
        source_keys=source_keys,
        retrieval_mode="guarded live fetch from reviewed raw GitHub extracts plus official publication review",
        parser_contract="Normalize DCS CPH2024 district rows and lk_admin_regions geography into DistrictProfileSeedRow, then diff against reviewed seed values before replacing seeds.",
        storage_target="DistrictProfile response rows and area_score_snapshots",
        refresh_cadence="manual release review plus scheduled link/provenance audit",
        next_action="Run live_fetch=true during release review, inspect checksum/reconciliation evidence, then use promote=true to persist scoring snapshots.",
        endpoints=[
            _endpoint(
                source_map,
                key="dcs-cph2024-page",
                label="DCS CPH2024 publication page",
                source_key="dcs-census-2024",
                method="GET/manual document review",
                note="Authoritative source; parser must tolerate HTML, spreadsheet, or PDF publication changes.",
            ),
            _endpoint(
                source_map,
                key="nuuuwan-census-extract",
                label="nuuuwan/lk_census_2024",
                source_key="public-lk-census-2024-extracts",
                method="GitHub metadata/raw file review",
                note="Reviewed MIT extract used as a reproducibility and diff source, not the authority of record.",
            ),
            _endpoint(
                source_map,
                key="nuuuwan-lanka-data",
                label="nuuuwan/lanka_data",
                source_key="public-lanka-data",
                method="GitHub metadata/raw file review",
                note="Reviewed district metadata/query layer for normalized geography joins.",
            ),
            _endpoint(
                source_map,
                key="nuuuwan-admin-regions",
                label="nuuuwan/lk_admin_regions",
                source_key="public-lk-admin-regions",
                method="GitHub metadata/raw file review",
                note="Reviewed MIT admin-region extract used for district province, area, and centroid lineage.",
            ),
        ],
        checks=checks,
    )


def _weather_risk_direct_manifest(source_map: dict) -> SourceImportManifest:
    source_keys = WEATHER_RISK_SOURCE_KEYS
    checks = [
        *_readiness_source_gate_checks(source_keys, source_map=source_map),
        _check(
            key="parser-contract",
            label="Parser contract",
            status="pass",
            message="The guarded direct importer fetches raw weather-station and irrigation water-level payloads, validates typed rows, and records reconciliation evidence.",
            evidence=[
                "contract: WeatherStationSeedRow",
                "required mappings: district to direct/proxy/national station",
                "execution gate: POST /api/v1/internal/source-import-run?live_fetch=true",
                "promotion gate: POST /api/v1/internal/source-import-run?live_fetch=true&promote=true",
                "alert boundary: planning signal only until DMC warnings are ingested directly",
            ],
        ),
        _check(
            key="storage-target",
            label="Storage target",
            status="pass",
            message="The weather response, Atlas weather component, and source registry targets are defined.",
            evidence=["WeatherRiskObservation response rows", "Atlas weather score component", "source_registry"],
        ),
    ]
    status = _status_for(checks)
    return SourceImportManifest(
        key="weather-risk-direct-import",
        label="Weather and risk direct import",
        domain_key="weather",
        status=status,
        promotion_status="direct_ready",
        accepted_for_direct_run=True,
        source_keys=source_keys,
        retrieval_mode="guarded live fetch from reviewed raw GitHub extracts plus official weather/risk publication review",
        parser_contract="Normalize lk_weather_3h station observations into WeatherStationSeedRow, validate lk_irrigation water-level context, map districts to direct/proxy stations, and keep DMC alerts separate from planning scores.",
        storage_target="WeatherRiskObservation response rows and Atlas weather score component",
        refresh_cadence="scheduled refresh plus manual trigger after direct-run promotion review",
        next_action="Run live_fetch=true during release review, inspect weather/irrigation checksum and reconciliation evidence, then use promote=true to persist planning-score snapshots while DMC warning ingestion remains separate.",
        endpoints=[
            _endpoint(
                source_map,
                key="meteo-3h-page",
                label="Department of Meteorology 3-hourly reports",
                source_key="meteo-lk-3h",
                method="GET/manual document review",
                note="Authoritative observation source; direct parser must capture observed_at and station identity.",
            ),
            _endpoint(
                source_map,
                key="nuuuwan-weather-extract",
                label="nuuuwan/lk_weather_3h",
                source_key="public-lk-weather-3h",
                method="GitHub metadata/raw file review",
                note="Reviewed MIT extract used to validate station parsing and coverage.",
            ),
            _endpoint(
                source_map,
                key="dmc-risk-page",
                label="Disaster Management Centre",
                source_key="dmc-lk",
                method="GET/manual warning review",
                note="Authoritative emergency context; keep separate from planning score until direct warning parser exists.",
            ),
            _endpoint(
                source_map,
                key="nuuuwan-rivers-extract",
                label="nuuuwan/lk_rivers",
                source_key="public-lk-rivers",
                method="GitHub metadata/raw file review",
                note="Reviewed river context extract for district risk enrichment after official irrigation validation.",
            ),
            _endpoint(
                source_map,
                key="nuuuwan-irrigation-extract",
                label="nuuuwan/lk_irrigation",
                source_key="public-lk-irrigation",
                method="GitHub metadata/raw file review",
                note="Reviewed MIT extract used for live irrigation water-level context in planning scores.",
            ),
        ],
        checks=checks,
    )


def _public_api_discovery_manifest(source_map: dict) -> SourceImportManifest:
    source_keys = ["public-apis-catalog", "currency-api", "open-food-facts", "open-meteo"]
    checks = [
        *_readiness_source_gate_checks(source_keys, source_map=source_map, allow_candidate_sources=True),
        _check(
            key="provider-promotion-boundary",
            label="Provider promotion boundary",
            status="watch",
            message="public-apis is a provider shortlist; concrete APIs need terms, cache, rate-limit, and Sri Lanka coverage review before direct ingestion.",
            evidence=[
                "catalog role: discovery only",
                "candidate APIs stay isolated from score-source dependencies",
                "promotion requires a concrete source key and parser contract",
            ],
        ),
    ]
    status = _status_for(checks)
    return SourceImportManifest(
        key="public-api-provider-discovery",
        label="Public API provider discovery",
        domain_key="indices",
        status=status,
        promotion_status="candidate",
        accepted_for_direct_run=False,
        source_keys=source_keys,
        retrieval_mode="manual provider shortlist review",
        parser_contract="Do not ingest the catalog itself; use it to justify a concrete provider source key with reviewed terms and a typed adapter.",
        storage_target="source_registry candidate rows and docs/source-roadmap.md",
        refresh_cadence="manual provider review before promotion",
        next_action="Review candidate provider terms and promote only source-specific importers, starting with exchange-rate and weather forecast fallbacks.",
        endpoints=[
            _endpoint(
                source_map,
                key="public-apis-catalog",
                label="marcelscruz/public-apis",
                source_key="public-apis-catalog",
                method="GitHub metadata/manual catalog review",
                note="Discovery catalog only; not a primary data source.",
            ),
            _endpoint(
                source_map,
                key="currency-api",
                label="Currency API exchange rates",
                source_key="currency-api",
                method="GitHub metadata/API terms review",
                status="watch",
                note="Candidate import-cost sensitivity feed; terms and cache policy must be cleared first.",
            ),
            _endpoint(
                source_map,
                key="open-food-facts",
                label="Open Food Facts",
                source_key="open-food-facts",
                method="API terms/coverage review",
                status="watch",
                note="Candidate packaged-food metadata feed; not a market-price source.",
            ),
            _endpoint(
                source_map,
                key="open-meteo",
                label="Open-Meteo forecast API",
                source_key="open-meteo",
                method="API terms/coverage review",
                status="watch",
                note="Candidate forecast fallback; keep out of scoring until forecast accuracy and terms are reviewed.",
            ),
        ],
        checks=checks,
    )


def _official_cost_direct_manifest(source_map: dict) -> SourceImportManifest:
    source_keys = OFFICIAL_COST_SOURCE_KEYS + OFFICIAL_IMPORT_CONTEXT_SOURCE_KEYS + OPTIONAL_IMPORT_CONTEXT_SOURCE_KEYS
    try:
        parser_evidence_rows = official_cost_parser_evidence_from_reviewed_fixtures()
        parser_errors: list[str] = []
    except (KeyError, TypeError, ValueError, ValidationError) as exc:
        parser_evidence_rows = []
        parser_errors = [str(exc)]
    checks = [
        *_readiness_source_gate_checks(source_keys, source_map=source_map, allow_candidate_sources=True),
        _check(
            key="source-specific-parser-fixtures",
            label="Source-specific parser fixtures",
            status="fail" if parser_errors else "pass",
            message="Reviewed official snippets exercise source-specific parser contracts for tariff, fare, fuel, exchange-rate, and customs pages."
            if not parser_errors
            else "One or more reviewed official parser fixture failed.",
            evidence=parser_errors
            or [
                f"{row.source_key}: {row.parser_key} -> {row.observed_label}"
                for row in parser_evidence_rows
            ],
        ),
        _check(
            key="live-promotion-boundary",
            label="Live promotion boundary",
            status="watch",
            message="Source-specific parser contracts exist, but unattended tariff/import promotion still needs live fetch evidence and operator review.",
            evidence=[
                "contracts covered: PUCSL decisions, NWSDB domestic water table, NTC fare index, CPC fuel price cards, CBSL exchange-rate page, Customs tariff index",
                "execution boundary: source-labelled planning rows can be snapshotted now",
                "promotion boundary: no direct tariff/import parser promotes without operator release evidence",
            ],
        ),
        _check(
            key="storage-target",
            label="Storage target",
            status="pass",
            message="The target storage and public response paths already exist for official cost context.",
            evidence=["tariff_snapshots", "transport_fare_snapshots", "CostCommandResponse", "UtilitiesResponse", "TransportResponse"],
        ),
    ]
    status = _status_for(checks)
    return SourceImportManifest(
        key="official-cost-tariff-import",
        label="Official tariff and import context import",
        domain_key="utilities",
        status=status,
        promotion_status="needs_parser",
        accepted_for_direct_run=False,
        source_keys=source_keys,
        retrieval_mode="official publication review plus candidate API terms review",
        parser_contract="Use source-specific parser contracts for PUCSL decisions, NWSDB domestic water tables, NTC fare indexes, CPC fuel price cards, CBSL exchange-rate page structure, and Customs tariff index metadata before promotion.",
        storage_target="tariff_snapshots, transport_fare_snapshots, and public cost-command source trails",
        refresh_cadence="scheduled refresh plus manual trigger after parser review",
        next_action="Run POST /api/v1/internal/source-import-run?include_official_cost=true for reviewed parser evidence, then use live_fetch=true for source fetch checks; keep promotion disabled until PDF/text extraction evidence and operator release notes are approved.",
        endpoints=[
            _endpoint(
                source_map,
                key="pucsl-electricity-tariffs",
                label="PUCSL electricity tariff decisions",
                source_key="pucsl-electricity",
                method="GET/manual table review",
                note="Authoritative electricity tariff source; parser must capture block/unit charges and effective date.",
            ),
            _endpoint(
                source_map,
                key="nwsdb-water-tariffs",
                label="NWSDB water tariff reference",
                source_key="nwsdb-water",
                method="GET/manual tariff review",
                note="Authoritative water tariff source; parser must separate domestic blocks from non-domestic tariffs.",
            ),
            _endpoint(
                source_map,
                key="ntc-bus-fares",
                label="NTC bus fare tables",
                source_key="ntc-bus-fares",
                method="GET/manual table review",
                note="Authoritative public bus fare source; route estimates must remain labelled planning signals.",
            ),
            _endpoint(
                source_map,
                key="cpc-fuel-prices",
                label="CPC fuel prices",
                source_key="cpc-fuel",
                method="GET/manual price review",
                note="Authoritative fuel price source; shared by fuel and private-vehicle commute estimates.",
            ),
            _endpoint(
                source_map,
                key="cbsl-exchange-context",
                label="CBSL exchange-rate and economic data",
                source_key="cbsl-economic-data",
                method="GET/manual data library review",
                note="Official exchange-rate context for import-cost sensitivity; do not replace with a third-party API silently.",
            ),
            _endpoint(
                source_map,
                key="customs-tariff-guide",
                label="Sri Lanka Customs tariff guide",
                source_key="sri-lanka-customs-tariff",
                method="GET/manual tariff-heading review",
                note="Official import-duty context; public UI must not present this as a tax quote.",
            ),
            _endpoint(
                source_map,
                key="currency-api-fallback",
                label="Currency API exchange-rate fallback",
                source_key="currency-api",
                method="API terms/cache review",
                status="watch",
                required=False,
                note="Candidate fallback only; keep isolated until commercial terms and cache policy are reviewed.",
            ),
        ],
        checks=checks,
    )


def source_import_audit_report() -> SourceImportAuditResponse:
    importers = [_district_profile_importer(), _weather_risk_importer(), _official_cost_importer()]
    if any(importer.status == "fail" for importer in importers):
        status = "offline"
        summary = "One or more source import families failed typed audit checks."
    elif any(importer.status == "watch" for importer in importers):
        status = "degraded"
        summary = "Source import families are usable with warnings; keep confidence caveats visible."
    else:
        status = "healthy"
        summary = "Typed source import audits passed for current district and weather seed families."

    source_map = {source.key: source for source in source_refs()}
    source_keys = sorted({key for importer in importers for key in importer.source_keys if key in source_map})
    return SourceImportAuditResponse(
        generated_at=utc_now(),
        status=status,
        summary=summary,
        importers=importers,
        sources=[source_map[key] for key in source_keys],
    )


def source_import_plan_report() -> SourceImportPlanResponse:
    source_map = {source.key: source for source in source_refs()}
    manifests = [
        _district_profile_direct_manifest(source_map),
        _weather_risk_direct_manifest(source_map),
        _official_cost_direct_manifest(source_map),
        _public_api_discovery_manifest(source_map),
    ]
    if any(manifest.status == "fail" for manifest in manifests):
        status = "offline"
        summary = "One or more direct import manifests is blocked by missing or uncleared source definitions."
    elif any(manifest.status == "watch" for manifest in manifests):
        status = "degraded"
        summary = "Direct import manifests are defined, but seed importers remain active until parser and terms watch items are resolved."
    else:
        status = "healthy"
        summary = "Direct import manifests are ready for automated source jobs."

    source_keys = sorted({key for manifest in manifests for key in manifest.source_keys if key in source_map})
    return SourceImportPlanResponse(
        generated_at=utc_now(),
        status=status,
        summary=summary,
        manifests=manifests,
        sources=[source_map[key] for key in source_keys],
    )


async def source_import_execution_report(*, live_fetch: bool = False, include_official_cost: bool = False) -> SourceImportExecutionResponse:
    runs: list[SourceImportExecutionRun] = []
    if live_fetch:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            try:
                district_payloads = [
                    await _fetch_json_payload(client, key, url)
                    for key, url in DISTRICT_DIRECT_IMPORT_URLS.items()
                ]
                runs.append(_district_direct_execution_from_payloads(district_payloads, live_fetch=True))
            except (httpx.HTTPError, ValueError) as exc:
                runs.append(
                    SourceImportExecutionRun(
                        key="district-profile-direct-run",
                        label="District profile direct import run",
                        domain_key="areas",
                        status="fail",
                        mode="live_fetch",
                        rows_imported=0,
                        accepted_for_scoring=False,
                        source_keys=DISTRICT_PROFILE_SOURCE_KEYS,
                        fetched_urls=list(DISTRICT_DIRECT_IMPORT_URLS.values()),
                        storage_target="DistrictProfile response rows and area_score_snapshots after full field-source promotion",
                        action="Fix direct district-profile source fetch before running the importer again.",
                        checks=[
                            _check(
                                key="live-fetch",
                                label="Live fetch",
                                status="fail",
                                message="Failed to fetch one or more raw district-profile payloads.",
                                evidence=[str(exc)],
                            )
                        ],
                    )
                )
            try:
                weather_documents = [
                    await _fetch_json_document(client, key, url)
                    for key, url in WEATHER_DIRECT_IMPORT_URLS.items()
                ]
                runs.append(_weather_direct_execution_from_documents(weather_documents, live_fetch=True))
            except (httpx.HTTPError, ValueError) as exc:
                runs.append(
                    SourceImportExecutionRun(
                        key="weather-risk-direct-run",
                        label="Weather and risk direct import run",
                        domain_key="weather",
                        status="fail",
                        mode="live_fetch",
                        rows_imported=0,
                        accepted_for_scoring=False,
                        source_keys=WEATHER_RISK_SOURCE_KEYS,
                        fetched_urls=list(WEATHER_DIRECT_IMPORT_URLS.values()),
                        storage_target="WeatherRiskObservation response rows and weather component scores after promotion review",
                        action="Fix direct weather/risk source fetch before running the importer again.",
                        checks=[
                            _check(
                                key="live-fetch",
                                label="Live fetch",
                                status="fail",
                                message="Failed to fetch one or more raw weather/risk payloads.",
                                evidence=[str(exc)],
                            )
                        ],
                    )
                )
            if include_official_cost:
                source_urls = _official_cost_source_url_map()
                official_cost_documents: list[DirectImportDocument] = []
                fetch_errors: list[str] = []
                for source_key in OFFICIAL_COST_DIRECT_SOURCE_KEYS:
                    url = source_urls.get(source_key)
                    if not url:
                        fetch_errors.append(f"{source_key}: missing source URL")
                        continue
                    try:
                        official_cost_documents.append(await _fetch_official_cost_document(client, source_key, url))
                    except (httpx.HTTPError, ValueError) as exc:
                        fetch_errors.append(f"{source_key}: {exc.__class__.__name__}: {exc}")
                runs.append(
                    _official_cost_direct_execution_from_documents(
                        official_cost_documents,
                        live_fetch=True,
                        fetch_errors=fetch_errors,
                    )
                )
    else:
        runs = [
            _district_direct_execution_from_payloads(_district_direct_payloads_from_seed_rows(), live_fetch=False),
            _weather_direct_execution_from_documents(_weather_direct_documents_from_seed_rows(), live_fetch=False),
        ]
        if include_official_cost:
            runs.append(
                _official_cost_direct_execution_from_documents(
                    _official_cost_direct_documents_from_parser_fixtures(),
                    live_fetch=False,
                )
            )

    if any(run.status == "fail" for run in runs):
        status = "offline"
        summary = "One or more source import execution runs failed."
    elif any(run.status == "watch" for run in runs):
        status = "degraded"
        summary = "Source import execution is runnable but still has promotion watch items."
    else:
        status = "healthy"
        summary = "Source import execution passed and is ready for promotion review."

    source_map = {source.key: source for source in source_refs()}
    source_keys = sorted({key for run in runs for key in run.source_keys if key in source_map})
    return SourceImportExecutionResponse(
        generated_at=utc_now(),
        status=status,
        summary=summary,
        runs=runs,
        sources=[source_map[key] for key in source_keys],
    )
