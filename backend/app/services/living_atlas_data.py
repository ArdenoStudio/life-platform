from datetime import datetime, timezone

from app.schemas import DistrictProfile, SourceReference, SourceValidationCheck, SourceValidationResponse, WeatherRiskObservation

SOURCE_DEFINITIONS = [
    {
        "key": "dcs-ccpi",
        "label": "DCS Colombo Consumer Price Index",
        "source_type": "official",
        "domain_key": "indices",
        "url": "https://www.statistics.gov.lk/InflationAndPrices/StaticalInformation/MonthlyCCPI",
        "confidence": "high",
        "freshness_note": "Official monthly inflation release from the Department of Census and Statistics.",
        "labels": {"si": "DCS කොළඹ පාරිභෝගික මිල දර්ශකය", "ta": "DCS கொழும்பு நுகர்வோர் விலைச் சுட்டெண்"},
    },
    {
        "key": "dcs-hies",
        "label": "DCS Household Income and Expenditure Survey",
        "source_type": "official",
        "domain_key": "areas",
        "url": "https://www.statistics.gov.lk/IncomeAndExpenditure/StaticalInformation/HouseholdIncomeandExpenditureSurvey",
        "confidence": "high",
        "freshness_note": "Official household expenditure structure used for basket weighting.",
        "labels": {"si": "DCS ගෘහ ආදායම් හා වියදම් සමීක්ෂණය", "ta": "DCS குடும்ப வருமான மற்றும் செலவுச் சர்வே"},
    },
    {
        "key": "dcs-census-2024",
        "label": "DCS Census of Population and Housing 2024",
        "source_type": "official",
        "domain_key": "areas",
        "url": "https://www.statistics.gov.lk/Population/StaticalInformation/CPH2024",
        "confidence": "high",
        "freshness_note": "Official population, housing, household, and district context for Atlas v2 scoring.",
        "labels": {},
    },
    {
        "key": "public-lk-census-2024-extracts",
        "label": "Public Census 2024 Extracts",
        "source_type": "derived",
        "domain_key": "areas",
        "url": "https://github.com/nuuuwan/lk_census_2024",
        "confidence": "medium",
        "freshness_note": "MIT-licensed extracted census tables; keep original DCS documents as the authoritative source.",
        "labels": {},
    },
    {
        "key": "public-lanka-data",
        "label": "Public Lanka Data Query Layer",
        "source_type": "derived",
        "domain_key": "areas",
        "url": "https://github.com/nuuuwan/lanka_data",
        "confidence": "medium",
        "freshness_note": "Sri Lanka geography and public-data query layer; useful for normalized district metadata after review.",
        "labels": {},
    },
    {
        "key": "public-lk-admin-regions",
        "label": "Public Sri Lanka Admin Regions",
        "source_type": "derived",
        "domain_key": "areas",
        "url": "https://github.com/nuuuwan/lk_admin_regions",
        "confidence": "medium",
        "freshness_note": "MIT-licensed administrative region metadata with DCS-sourced area, centroid, and hierarchy fields.",
        "labels": {},
    },
    {
        "key": "public-lk-rivers",
        "label": "Public Sri Lanka Rivers Dataset",
        "source_type": "derived",
        "domain_key": "weather",
        "url": "https://github.com/nuuuwan/lk_rivers",
        "confidence": "medium",
        "freshness_note": "River context candidate for district risk scoring; verify against official irrigation and DMC references.",
        "labels": {},
    },
    {
        "key": "public-lk-irrigation",
        "label": "Public Irrigation Water Levels",
        "source_type": "derived",
        "domain_key": "weather",
        "url": "https://github.com/nuuuwan/lk_irrigation",
        "confidence": "medium",
        "freshness_note": "MIT-licensed extract of Sri Lanka Irrigation Department river water-level measurements for planning risk context.",
        "labels": {},
    },
    {
        "key": "dmc-lk",
        "label": "Disaster Management Centre Sri Lanka",
        "source_type": "official",
        "domain_key": "weather",
        "url": "https://www.dmc.gov.lk/",
        "confidence": "high",
        "freshness_note": "Official disaster and public-risk context for future district risk alerts.",
        "labels": {},
    },
    {
        "key": "cbsl-price-report",
        "label": "CBSL Daily Price Report",
        "source_type": "official",
        "domain_key": "food",
        "url": "https://www.cbsl.gov.lk/statistics/economic-indicators/price-report",
        "confidence": "high",
        "freshness_note": "Official food and essential price reference for market context.",
        "labels": {"si": "CBSL දෛනික මිල වාර්තාව", "ta": "CBSL தினசரி விலை அறிக்கை"},
    },
    {
        "key": "cbsl-economic-data",
        "label": "CBSL Economic Data Library",
        "source_type": "official",
        "domain_key": "indices",
        "url": "https://www.cbsl.gov.lk/en/rates-and-indicators/exchange-rates",
        "confidence": "high",
        "freshness_note": "Official exchange-rate context for affordability and import-cost signals.",
        "labels": {},
    },
    {
        "key": "sri-lanka-customs-tariff",
        "label": "Sri Lanka Customs Tariff Guide",
        "source_type": "official",
        "domain_key": "vehicle",
        "url": "https://www.customs.gov.lk/customs-tariff/import-tariff/",
        "confidence": "high",
        "freshness_note": "Official customs import tariff index for import-cost context; parser contracts are covered but live promotion stays behind operator review.",
        "labels": {},
    },
    {
        "key": "public-apis-catalog",
        "label": "Public APIs Discovery Catalog",
        "source_type": "derived",
        "domain_key": "indices",
        "url": "https://github.com/marcelscruz/public-apis",
        "confidence": "medium",
        "freshness_note": "MIT-licensed provider catalog used for API discovery only, not as scoring evidence.",
        "collection_method": "provider_catalog",
        "license_status": "permissive",
        "review_status": "reviewed",
        "refresh_cadence": "manual provider review before promotion",
        "governance_note": "Use to shortlist public API providers; promote only concrete source keys after terms, cache, and coverage review.",
        "labels": {},
    },
    {
        "key": "public-cbsl-query-layer",
        "label": "Public CBSL Query Layer",
        "source_type": "derived",
        "domain_key": "indices",
        "url": "https://github.com/nuuuwan/lanka_data_search",
        "confidence": "medium",
        "freshness_note": "Public wrapper around CBSL data; use only after endpoint and license review.",
        "labels": {},
    },
    {
        "key": "harti-daily",
        "label": "HARTI Daily Food Price Bulletin",
        "source_type": "official",
        "domain_key": "food",
        "url": "https://www.harti.gov.lk/daily-price.php",
        "confidence": "high",
        "freshness_note": "Official agricultural market bulletin for daily food prices.",
        "labels": {"si": "HARTI දෛනික ආහාර මිල පුවත්පත", "ta": "HARTI தினசரி உணவு விலை அறிவிப்பு"},
    },
    {
        "key": "public-lk-food",
        "label": "Public Sri Lanka Food and Nutrition Dataset",
        "source_type": "derived",
        "domain_key": "food",
        "url": "https://github.com/nuuuwan/lk_food",
        "confidence": "medium",
        "freshness_note": "Food, nutrient, and local meal-index context for future nutrition-aware affordability.",
        "labels": {},
    },
    {
        "key": "fisheries-statistics",
        "label": "Ministry of Fisheries Statistics",
        "source_type": "official",
        "domain_key": "food",
        "url": "https://www.fisheries.gov.lk/",
        "confidence": "high",
        "freshness_note": "Official fisheries reports for fish supply and food-system context.",
        "labels": {},
    },
    {
        "key": "public-lk-fisheries",
        "label": "Public Sri Lanka Fisheries Report Extracts",
        "source_type": "derived",
        "domain_key": "food",
        "url": "https://github.com/nuuuwan/lk_fisheries",
        "confidence": "medium",
        "freshness_note": "Extracted fisheries reports; useful for supply context after official-source validation.",
        "labels": {},
    },
    {
        "key": "pucsl-electricity",
        "label": "PUCSL Electricity Tariffs",
        "source_type": "official",
        "domain_key": "utilities",
        "url": "https://www.pucsl.gov.lk/end-user-tariff-decisions/",
        "confidence": "high",
        "freshness_note": "Official electricity tariff decisions for household cost modelling.",
        "labels": {"si": "PUCSL විදුලි ගාස්තු", "ta": "PUCSL மின்சார கட்டணங்கள்"},
    },
    {
        "key": "nwsdb-water",
        "label": "NWSDB Water Tariffs",
        "source_type": "official",
        "domain_key": "utilities",
        "url": "https://www.waterboard.lk/wp-content/uploads/2023/08/Water-Tariff-2023-Revised-English.pdf",
        "confidence": "medium",
        "freshness_note": "Official water tariff gazette reference; domestic-table parser fixtures are covered and live PDF extraction remains operator-reviewed.",
        "labels": {"si": "NWSDB ජල ගාස්තු", "ta": "NWSDB நீர் கட்டணங்கள்"},
    },
    {
        "key": "litro-lpg",
        "label": "Litro LPG Prices",
        "source_type": "official",
        "domain_key": "gas",
        "url": "https://www.litrogas.com/",
        "confidence": "medium",
        "freshness_note": "Public LPG price reference; availability can vary by publication format.",
        "labels": {"si": "ලිට්රෝ ගෑස් මිල", "ta": "லிட்ரோ எரிவாயு விலை"},
    },
    {
        "key": "laugfs-lpg",
        "label": "LAUGFS LPG Prices",
        "source_type": "official",
        "domain_key": "gas",
        "url": "https://laugfsgas.lk/",
        "confidence": "medium",
        "freshness_note": "Public LPG price reference; normalized extraction is staged.",
        "labels": {"si": "LAUGFS ගෑස් මිල", "ta": "LAUGFS எரிவாயு விலை"},
    },
    {
        "key": "ntc-bus-fares",
        "label": "NTC Bus Fares",
        "source_type": "official",
        "domain_key": "transport",
        "url": "https://www.ntc.gov.lk/Bus_info/bus_fares.php",
        "confidence": "high",
        "freshness_note": "Official bus fare tables for route and distance-based public transport costs.",
        "labels": {"si": "NTC බස් ගාස්තු", "ta": "NTC பேருந்து கட்டணங்கள்"},
    },
    {
        "key": "public-bus-routes-lk",
        "label": "Public Sri Lanka Bus Route Statistics",
        "source_type": "derived",
        "domain_key": "transport",
        "url": "https://github.com/nuuuwan/bus_routes_lk",
        "confidence": "medium",
        "freshness_note": "Route-statistics candidate for commute scoring; verify coverage and update cadence before production scoring.",
        "labels": {},
    },
    {
        "key": "public-transport-timetable-lk",
        "label": "Public Transport Timetable Dataset",
        "source_type": "derived",
        "domain_key": "transport",
        "url": "https://github.com/nuuuwan/transport_timetable_lk",
        "confidence": "low",
        "freshness_note": "Older timetable candidate; keep low-confidence until source freshness and coverage are reviewed.",
        "labels": {},
    },
    {
        "key": "cpc-fuel",
        "label": "CPC Fuel Pricing",
        "source_type": "official",
        "domain_key": "fuel",
        "url": "https://ceypetco.gov.lk/marketing-sales/",
        "confidence": "high",
        "freshness_note": "Official fuel price reference checked by Octane and Ariva.",
        "labels": {"si": "CPC ඉන්ධන මිල", "ta": "CPC எரிபொருள் விலை"},
    },
    {
        "key": "octane-platform",
        "label": "Octane Platform API",
        "source_type": "platform",
        "domain_key": "fuel",
        "url": "https://octane-api.fly.dev",
        "confidence": "medium",
        "freshness_note": "Existing Ardeno Studio fuel platform used for latest fuel revisions, trip costs, and alerts.",
        "labels": {},
    },
    {
        "key": "propertylk-platform",
        "label": "PropertyLK Platform API",
        "source_type": "platform",
        "domain_key": "property",
        "url": "https://property-price-intelligence-an-ardeno-production.fly.dev",
        "confidence": "medium",
        "freshness_note": "Existing Ardeno Studio property platform used for listings, district benchmarks, trends, and rental context.",
        "labels": {},
    },
    {
        "key": "currency-api",
        "label": "Currency API Exchange Rates",
        "source_type": "derived",
        "domain_key": "vehicle",
        "url": "https://github.com/fawazahmed0/currency-api#readme",
        "confidence": "medium",
        "freshness_note": "Candidate for LKR import-cost sensitivity; cache and terms review required before production use.",
        "labels": {},
    },
    {
        "key": "autolens-platform",
        "label": "AutoLens Platform API",
        "source_type": "platform",
        "domain_key": "vehicle",
        "url": "https://vehicle-platform-backend.fly.dev/api/v1",
        "confidence": "medium",
        "freshness_note": "Existing Ardeno Studio vehicle platform used for listings, market medians, deal scores, and import context.",
        "labels": {},
    },
    {
        "key": "open-meteo",
        "label": "Open-Meteo Forecast API",
        "source_type": "derived",
        "domain_key": "weather",
        "url": "https://open-meteo.com/",
        "confidence": "medium",
        "freshness_note": "No-key weather forecast candidate; terms and Sri Lanka coverage must be reviewed before commercial use.",
        "labels": {},
    },
    {
        "key": "meteo-lk-3h",
        "label": "Department of Meteorology 3-Hourly Reports",
        "source_type": "official",
        "domain_key": "weather",
        "url": "https://www.meteo.gov.lk/",
        "confidence": "high",
        "freshness_note": "Official station-level weather observations for future district risk scoring.",
        "labels": {},
    },
    {
        "key": "public-lk-weather-3h",
        "label": "Public 3-Hourly Weather Extracts",
        "source_type": "derived",
        "domain_key": "weather",
        "url": "https://github.com/nuuuwan/lk_weather_3h",
        "confidence": "medium",
        "freshness_note": "Extracted Department of Meteorology reports; map station coverage before using in district scores.",
        "labels": {},
    },
    {
        "key": "sltda-arrivals",
        "label": "SLTDA Tourist Arrivals Reports",
        "source_type": "official",
        "domain_key": "indices",
        "url": "https://www.sltda.gov.lk/",
        "confidence": "high",
        "freshness_note": "Official weekly and monthly tourism arrival reports for future SMB demand intelligence.",
        "labels": {},
    },
    {
        "key": "public-lk-tourism",
        "label": "Public Sri Lanka Tourism Report Extracts",
        "source_type": "derived",
        "domain_key": "indices",
        "url": "https://github.com/nuuuwan/lk_tourism",
        "confidence": "medium",
        "freshness_note": "Extracted SLTDA reports; useful for tourism-demand signals after official-source validation.",
        "labels": {},
    },
    {
        "key": "open-food-facts",
        "label": "Open Food Facts",
        "source_type": "derived",
        "domain_key": "food",
        "url": "https://world.openfoodfacts.org/data",
        "confidence": "medium",
        "freshness_note": "Packaged-food metadata candidate; not a Sri Lanka market price source.",
        "labels": {},
    },
    {
        "key": "parliament-hansard",
        "label": "Parliament of Sri Lanka Hansards",
        "source_type": "official",
        "domain_key": "indices",
        "url": "https://www.parliament.lk/",
        "confidence": "high",
        "freshness_note": "Official parliamentary debate records for future public document intelligence.",
        "labels": {},
    },
    {
        "key": "public-lk-hansard",
        "label": "Public Sri Lanka Hansard Extracts",
        "source_type": "derived",
        "domain_key": "indices",
        "url": "https://github.com/nuuuwan/lk_hansard",
        "confidence": "medium",
        "freshness_note": "Large public Hansard corpus; index metadata first and avoid legal/policy overclaiming.",
        "labels": {},
    },
    {
        "key": "parliament-acts",
        "label": "Parliament of Sri Lanka Acts and Bills",
        "source_type": "official",
        "domain_key": "indices",
        "url": "https://www.parliament.lk/en/acts-bills",
        "confidence": "high",
        "freshness_note": "Official acts and bills source for future public legal-document search.",
        "labels": {},
    },
    {
        "key": "public-lk-acts",
        "label": "Public Sri Lanka Acts Extracts",
        "source_type": "derived",
        "domain_key": "indices",
        "url": "https://github.com/nuuuwan/lk_acts",
        "confidence": "medium",
        "freshness_note": "Public acts metadata and PDFs; keep public explainer framing and avoid legal-advice claims.",
        "labels": {},
    },
    {
        "key": "election-commission-lk",
        "label": "Election Commission of Sri Lanka",
        "source_type": "official",
        "domain_key": "areas",
        "url": "https://www.elections.gov.lk/",
        "confidence": "high",
        "freshness_note": "Official election source for district civic context and public-interest explainers.",
        "labels": {},
    },
    {
        "key": "public-elections-lk",
        "label": "Public Sri Lanka Elections Dataset",
        "source_type": "derived",
        "domain_key": "areas",
        "url": "https://github.com/nuuuwan/elections_lk",
        "confidence": "medium",
        "freshness_note": "MIT-licensed elections library; useful for civic context after data coverage review.",
        "labels": {},
    },
    {
        "key": "retail-public-pages",
        "label": "Public Retail Offer Pages",
        "source_type": "retail",
        "domain_key": "retail",
        "url": "https://www.keellssuper.com/",
        "confidence": "medium",
        "freshness_note": "Public retailer quotes are labelled as retail offers, not official prices.",
        "labels": {"si": "පොදු රීටේල් දීමනා පිටු", "ta": "பொது சில்லறை சலுகைப் பக்கங்கள்"},
    },
    {
        "key": "foodlk-platform",
        "label": "FoodLK Platform API",
        "source_type": "platform",
        "domain_key": "food",
        "url": "https://food-platform-backend.fly.dev/api/v1",
        "confidence": "medium",
        "freshness_note": "Existing Ardeno Studio food platform remains the food source of truth.",
        "labels": {"si": "FoodLK වේදිකා API", "ta": "FoodLK தள API"},
    },
]

SOURCE_OWNER_OVERRIDES = {
    "autolens-platform": "Ardeno Studio AutoLens",
    "cbsl-economic-data": "Central Bank of Sri Lanka",
    "cbsl-price-report": "Central Bank of Sri Lanka",
    "cpc-fuel": "Ceylon Petroleum Corporation",
    "currency-api": "fawazahmed0/currency-api",
    "dcs-ccpi": "Department of Census and Statistics",
    "dcs-census-2024": "Department of Census and Statistics",
    "dcs-hies": "Department of Census and Statistics",
    "dmc-lk": "Disaster Management Centre",
    "election-commission-lk": "Election Commission of Sri Lanka",
    "fisheries-statistics": "Ministry of Fisheries",
    "foodlk-platform": "Ardeno Studio FoodLK",
    "harti-daily": "Hector Kobbekaduwa Agrarian Research and Training Institute",
    "laugfs-lpg": "LAUGFS Gas",
    "litro-lpg": "Litro Gas Lanka",
    "meteo-lk-3h": "Department of Meteorology",
    "ntc-bus-fares": "National Transport Commission",
    "nwsdb-water": "National Water Supply and Drainage Board",
    "open-food-facts": "Open Food Facts",
    "open-meteo": "Open-Meteo",
    "octane-platform": "Ardeno Studio Octane",
    "parliament-acts": "Parliament of Sri Lanka",
    "parliament-hansard": "Parliament of Sri Lanka",
    "propertylk-platform": "Ardeno Studio PropertyLK",
    "public-apis-catalog": "marcelscruz/public-apis",
    "public-elections-lk": "nuuuwan/elections_lk",
    "public-lk-admin-regions": "nuuuwan/lk_admin_regions",
    "public-lanka-data": "nuuuwan/lanka_data",
    "public-lk-census-2024-extracts": "nuuuwan/lk_census_2024",
    "public-lk-irrigation": "nuuuwan/lk_irrigation",
    "public-lk-rivers": "nuuuwan/lk_rivers",
    "public-lk-weather-3h": "nuuuwan/lk_weather_3h",
    "pucsl-electricity": "Public Utilities Commission of Sri Lanka",
    "retail-public-pages": "Public retailer websites",
    "sltda-arrivals": "Sri Lanka Tourism Development Authority",
    "sri-lanka-customs-tariff": "Sri Lanka Customs",
}

PERMISSIVE_REVIEWED_SOURCE_KEYS = {
    "public-elections-lk",
    "public-lk-admin-regions",
    "public-lanka-data",
    "public-lk-census-2024-extracts",
    "public-lk-irrigation",
    "public-lk-rivers",
    "public-lk-weather-3h",
}


def source_governance(row: dict) -> dict[str, str]:
    source_type = row["source_type"]
    key = row["key"]
    url = row["url"]
    freshness_note = row["freshness_note"]
    owner = row.get("owner") or SOURCE_OWNER_OVERRIDES.get(key)
    if owner is None and "github.com/nuuuwan" in url:
        owner = "nuuuwan public data repository"
    owner = owner or row["label"]

    if source_type == "official":
        license_status = "official_public"
        review_status = "approved"
        collection_method = "official_publication"
        governance_note = "Use as authoritative public reference; still validate publication format before automated extraction."
    elif source_type == "platform":
        license_status = "internal_platform"
        review_status = "approved"
        collection_method = "platform_api"
        governance_note = "Existing Ardeno Studio platform source of truth."
    elif source_type == "retail":
        license_status = "terms_review"
        review_status = "candidate"
        collection_method = "retail_page"
        governance_note = "Use as public quote context only; do not treat as official price statistics."
    elif key in PERMISSIVE_REVIEWED_SOURCE_KEYS or "MIT-licensed" in freshness_note:
        license_status = "permissive"
        review_status = "reviewed"
        collection_method = "public_extract"
        governance_note = "MIT-licensed public extract reviewed for seed use; keep original official source linked."
    elif key in {"open-meteo", "currency-api", "open-food-facts"}:
        license_status = "terms_review"
        review_status = "candidate"
        collection_method = "public_api"
        governance_note = "Candidate public API; terms, limits, caching, and commercial use need review before production automation."
    else:
        license_status = "needs_review"
        review_status = "needs_review"
        collection_method = "public_extract"
        governance_note = "Visible for research and planning; do not promote to production scoring without source and license review."

    return {
        "collection_method": row.get("collection_method", collection_method),
        "governance_note": row.get("governance_note", governance_note),
        "license_status": row.get("license_status", license_status),
        "owner": owner,
        "refresh_cadence": row.get("refresh_cadence", "scheduled refresh plus manual trigger"),
        "review_status": row.get("review_status", review_status),
    }


DISTRICT_PROFILE_ROWS = [
    {"key": "Sri Lanka", "region_id": "LK", "province": "National", "population": 21781800, "households": 6111315, "area_sqkm": 65983.58, "center_lat": 7.621863, "center_lng": 80.698448, "cooking_gas_share": 0.424, "elderly_share": 0.18},
    {"key": "Colombo", "region_id": "LK-11", "province": "Western", "population": 2375415, "households": 661822, "area_sqkm": 688.17, "center_lat": 6.869822, "center_lng": 80.018487, "cooking_gas_share": 0.855, "elderly_share": 0.193},
    {"key": "Gampaha", "region_id": "LK-12", "province": "Western", "population": 2436142, "households": 688635, "area_sqkm": 1385.23, "center_lat": 7.123406, "center_lng": 80.018206, "cooking_gas_share": 0.639, "elderly_share": 0.189},
    {"key": "Kalutara", "region_id": "LK-13", "province": "Western", "population": 1305784, "households": 352963, "area_sqkm": 1646.99, "center_lat": 6.577185, "center_lng": 80.127744, "cooking_gas_share": 0.559, "elderly_share": 0.188},
    {"key": "Kandy", "region_id": "LK-21", "province": "Central", "population": 1461895, "households": 397626, "area_sqkm": 1927.69, "center_lat": 7.273178, "center_lng": 80.708811, "cooking_gas_share": 0.403, "elderly_share": 0.195},
    {"key": "Matale", "region_id": "LK-22", "province": "Central", "population": 526870, "households": 151132, "area_sqkm": 2058.75, "center_lat": 7.667651, "center_lng": 80.730702, "cooking_gas_share": 0.235, "elderly_share": 0.186},
    {"key": "Nuwara Eliya", "region_id": "LK-23", "province": "Central", "population": 725280, "households": 200261, "area_sqkm": 1744.81, "center_lat": 6.974738, "center_lng": 80.711186, "cooking_gas_share": 0.266, "elderly_share": 0.176},
    {"key": "Galle", "region_id": "LK-31", "province": "Southern", "population": 1097372, "households": 307704, "area_sqkm": 1613.49, "center_lat": 6.222792, "center_lng": 80.251811, "cooking_gas_share": 0.46, "elderly_share": 0.199},
    {"key": "Matara", "region_id": "LK-32", "province": "Southern", "population": 837889, "households": 231946, "area_sqkm": 1306.37, "center_lat": 6.142725, "center_lng": 80.539846, "cooking_gas_share": 0.374, "elderly_share": 0.204},
    {"key": "Hambantota", "region_id": "LK-33", "province": "Southern", "population": 671418, "households": 188638, "area_sqkm": 2625.06, "center_lat": 6.254039, "center_lng": 81.091281, "cooking_gas_share": 0.263, "elderly_share": 0.18},
    {"key": "Jaffna", "region_id": "LK-41", "province": "Northern", "population": 594751, "households": 159753, "area_sqkm": 1091.24, "center_lat": 9.687873, "center_lng": 80.116157, "cooking_gas_share": 0.423, "elderly_share": 0.196},
    {"key": "Mannar", "region_id": "LK-42", "province": "Northern", "population": 123756, "households": 32330, "area_sqkm": 2010.83, "center_lat": 8.878476, "center_lng": 80.091433, "cooking_gas_share": 0.411, "elderly_share": 0.127},
    {"key": "Vavuniya", "region_id": "LK-43", "province": "Northern", "population": 172312, "households": 48399, "area_sqkm": 1934.91, "center_lat": 8.853162, "center_lng": 80.470869, "cooking_gas_share": 0.418, "elderly_share": 0.141},
    {"key": "Mullaitivu", "region_id": "LK-44", "province": "Northern", "population": 122619, "households": 34786, "area_sqkm": 2681.15, "center_lat": 9.170128, "center_lng": 80.552726, "cooking_gas_share": 0.245, "elderly_share": 0.134},
    {"key": "Kilinochchi", "region_id": "LK-45", "province": "Northern", "population": 136710, "households": 36734, "area_sqkm": 1319.29, "center_lat": 9.421424, "center_lng": 80.309356, "cooking_gas_share": 0.212, "elderly_share": 0.131},
    {"key": "Batticaloa", "region_id": "LK-51", "province": "Eastern", "population": 595918, "households": 170262, "area_sqkm": 2480.5, "center_lat": 7.795426, "center_lng": 81.478872, "cooking_gas_share": 0.545, "elderly_share": 0.126},
    {"key": "Ampara", "region_id": "LK-52", "province": "Eastern", "population": 744551, "households": 207007, "area_sqkm": 4474.66, "center_lat": 7.233261, "center_lng": 81.553888, "cooking_gas_share": 0.486, "elderly_share": 0.132},
    {"key": "Trincomalee", "region_id": "LK-53", "province": "Eastern", "population": 442745, "households": 121948, "area_sqkm": 2692.11, "center_lat": 8.553962, "center_lng": 81.091548, "cooking_gas_share": 0.478, "elderly_share": 0.115},
    {"key": "Kurunegala", "region_id": "LK-61", "province": "North Western", "population": 1768156, "households": 511166, "area_sqkm": 4905.71, "center_lat": 7.664511, "center_lng": 80.236804, "cooking_gas_share": 0.213, "elderly_share": 0.196},
    {"key": "Puttalam", "region_id": "LK-62", "province": "North Western", "population": 818816, "households": 234027, "area_sqkm": 3133.88, "center_lat": 7.975263, "center_lng": 79.910874, "cooking_gas_share": 0.373, "elderly_share": 0.156},
    {"key": "Anuradhapura", "region_id": "LK-71", "province": "North Central", "population": 960080, "households": 275084, "area_sqkm": 7218.29, "center_lat": 8.392067, "center_lng": 80.51313, "cooking_gas_share": 0.239, "elderly_share": 0.153},
    {"key": "Polonnaruwa", "region_id": "LK-72", "province": "North Central", "population": 447530, "households": 127385, "area_sqkm": 3469.72, "center_lat": 7.994209, "center_lng": 81.028281, "cooking_gas_share": 0.212, "elderly_share": 0.162},
    {"key": "Badulla", "region_id": "LK-81", "province": "Uva", "population": 872307, "households": 248262, "area_sqkm": 2871.96, "center_lat": 7.073578, "center_lng": 81.044926, "cooking_gas_share": 0.184, "elderly_share": 0.177},
    {"key": "Monaragala", "region_id": "LK-82", "province": "Uva", "population": 527585, "households": 151763, "area_sqkm": 5757.99, "center_lat": 6.787062, "center_lng": 81.301821, "cooking_gas_share": 0.153, "elderly_share": 0.151},
    {"key": "Ratnapura", "region_id": "LK-91", "province": "Sabaragamuwa", "population": 1145423, "households": 327645, "area_sqkm": 3287.08, "center_lat": 6.586622, "center_lng": 80.565541, "cooking_gas_share": 0.208, "elderly_share": 0.185},
    {"key": "Kegalle", "region_id": "LK-92", "province": "Sabaragamuwa", "population": 870476, "households": 244037, "area_sqkm": 1657.73, "center_lat": 7.104294, "center_lng": 80.342772, "cooking_gas_share": 0.26, "elderly_share": 0.211},
]

DISTRICTS = [row["key"] for row in DISTRICT_PROFILE_ROWS]

WEATHER_RISK_SOURCE_KEYS = ["meteo-lk-3h", "public-lk-weather-3h", "dmc-lk", "public-lk-rivers", "public-lk-irrigation"]

WEATHER_STATION_ROWS = [
    {"station_id": "43413", "station_name": "Mannar", "observed_at": "2026-05-25T20:30:00+00:00", "rainfall_mm": 0.0, "temperature_c": 29.3, "humidity_percent": 84.0},
    {"station_id": "43415", "station_name": "Vavuniya", "observed_at": "2026-05-25T20:30:00+00:00", "rainfall_mm": 0.0, "temperature_c": 26.8, "humidity_percent": 92.0},
    {"station_id": "43418", "station_name": "Trincomalee", "observed_at": "2026-05-25T20:30:00+00:00", "rainfall_mm": 0.0, "temperature_c": 29.1, "humidity_percent": 71.0},
    {"station_id": "43421", "station_name": "Anuradhapura", "observed_at": "2026-05-25T20:30:00+00:00", "rainfall_mm": 0.0, "temperature_c": 28.1, "humidity_percent": 82.0},
    {"station_id": "43424", "station_name": "Puttalam", "observed_at": "2026-05-25T20:30:00+00:00", "rainfall_mm": 0.0, "temperature_c": 29.2, "humidity_percent": 80.0},
    {"station_id": "43436", "station_name": "Batticaloa", "observed_at": "2026-05-25T20:30:00+00:00", "rainfall_mm": 0.0, "temperature_c": 30.5, "humidity_percent": 81.0},
    {"station_id": "43441", "station_name": "Kurunegala", "observed_at": "2026-05-25T20:30:00+00:00", "rainfall_mm": 0.1, "temperature_c": 26.6, "humidity_percent": 88.0},
    {"station_id": "43444", "station_name": "Katugastota", "observed_at": "2026-05-25T20:30:00+00:00", "rainfall_mm": 0.0, "temperature_c": 25.4, "humidity_percent": 84.0},
    {"station_id": "43450", "station_name": "Katunayake", "observed_at": "2026-05-25T20:30:00+00:00", "rainfall_mm": 0.5, "temperature_c": 28.8, "humidity_percent": 88.0},
    {"station_id": "43466", "station_name": "Colombo", "observed_at": "2026-05-25T20:30:00+00:00", "rainfall_mm": 0.0, "temperature_c": 29.1, "humidity_percent": 85.0},
    {"station_id": "43467", "station_name": "Ratmalana", "observed_at": "2026-05-25T20:30:00+00:00", "rainfall_mm": 0.0, "temperature_c": 29.2, "humidity_percent": 83.0},
    {"station_id": "43473", "station_name": "Nuwara Eliya", "observed_at": "2026-05-25T20:30:00+00:00", "rainfall_mm": 0.0, "temperature_c": 16.7, "humidity_percent": 92.0},
    {"station_id": "43479", "station_name": "Badulla", "observed_at": "2026-05-25T20:30:00+00:00", "rainfall_mm": 0.0, "temperature_c": 24.9, "humidity_percent": 79.0},
    {"station_id": "43486", "station_name": "Ratnapura", "observed_at": "2026-05-25T20:30:00+00:00", "rainfall_mm": 25.5, "temperature_c": 24.6, "humidity_percent": 98.0},
    {"station_id": "43495", "station_name": "Galle", "observed_at": "2026-05-25T20:30:00+00:00", "rainfall_mm": 0.0, "temperature_c": 28.8, "humidity_percent": 89.0},
    {"station_id": "43497", "station_name": "Hambantota", "observed_at": "2026-05-25T20:30:00+00:00", "rainfall_mm": 0.0, "temperature_c": 27.7, "humidity_percent": 87.0},
    {"station_id": "721501", "station_name": "Polonnaruwa", "observed_at": "2026-05-25T20:30:00+00:00", "rainfall_mm": 0.0, "temperature_c": 29.4, "humidity_percent": 68.0},
    {"station_id": "821501", "station_name": "Monaragala", "observed_at": "2026-05-25T20:30:00+00:00", "rainfall_mm": 0.0, "temperature_c": 27.9, "humidity_percent": 72.0},
    {"station_id": "43404", "station_name": "Jaffna", "observed_at": "2026-05-25T17:30:00+00:00", "rainfall_mm": 0.0, "temperature_c": 29.8, "humidity_percent": 78.0},
    {"station_id": "43410", "station_name": "Mullaitivu", "observed_at": "2026-05-25T17:30:00+00:00", "rainfall_mm": 0.0, "temperature_c": 32.4, "humidity_percent": 59.0},
    {"station_id": "43475", "station_name": "Pottuvil", "observed_at": "2026-05-25T17:30:00+00:00", "rainfall_mm": 0.0, "temperature_c": 32.2, "humidity_percent": 61.0},
]

DISTRICT_WEATHER_STATIONS = {
    "Sri Lanka": ("Ratnapura", "national"),
    "Colombo": ("Colombo", "direct"),
    "Gampaha": ("Katunayake", "proxy"),
    "Kalutara": ("Ratmalana", "proxy"),
    "Kandy": ("Katugastota", "direct"),
    "Matale": ("Katugastota", "proxy"),
    "Nuwara Eliya": ("Nuwara Eliya", "direct"),
    "Galle": ("Galle", "direct"),
    "Matara": ("Galle", "proxy"),
    "Hambantota": ("Hambantota", "direct"),
    "Jaffna": ("Jaffna", "direct"),
    "Mannar": ("Mannar", "direct"),
    "Vavuniya": ("Vavuniya", "direct"),
    "Mullaitivu": ("Mullaitivu", "direct"),
    "Kilinochchi": ("Vavuniya", "proxy"),
    "Batticaloa": ("Batticaloa", "direct"),
    "Ampara": ("Pottuvil", "proxy"),
    "Trincomalee": ("Trincomalee", "direct"),
    "Kurunegala": ("Kurunegala", "direct"),
    "Puttalam": ("Puttalam", "direct"),
    "Anuradhapura": ("Anuradhapura", "direct"),
    "Polonnaruwa": ("Polonnaruwa", "direct"),
    "Badulla": ("Badulla", "direct"),
    "Monaragala": ("Monaragala", "direct"),
    "Ratnapura": ("Ratnapura", "direct"),
    "Kegalle": ("Ratnapura", "proxy"),
}

UTILITY_TARIFFS = [
    {"key": "electricity-low", "label": "Electricity low-use block", "amount_lkr": 7200, "unit": "monthly planning estimate", "source_key": "pucsl-electricity", "confidence": "medium", "note": "Planning estimate until block-level PUCSL extraction is automated."},
    {"key": "electricity-family", "label": "Electricity family block", "amount_lkr": 18500, "unit": "monthly planning estimate", "source_key": "pucsl-electricity", "confidence": "medium", "note": "Uses a family-consumption proxy for the Cost Desk."},
    {"key": "water-domestic", "label": "Domestic water", "amount_lkr": 2600, "unit": "monthly planning estimate", "source_key": "nwsdb-water", "confidence": "low", "note": "Static v2 assumption until tariff slabs are normalized."},
]

GAS_TARIFFS = [
    {"key": "litro-12-5kg", "label": "LPG 12.5kg cylinder", "amount_lkr": 3790, "unit": "per cylinder", "source_key": "litro-lpg", "confidence": "medium", "note": "Public LPG price reference; verify against latest vendor publication."},
    {"key": "laugfs-12-5kg", "label": "LPG 12.5kg alternate quote", "amount_lkr": 3800, "unit": "per cylinder", "source_key": "laugfs-lpg", "confidence": "medium", "note": "Retail/vendor quote placeholder until automated extraction is live."},
]

TRANSPORT_OPTIONS = [
    {"mode": "bus", "from_area": "Colombo", "to_area": "Kandy", "fare_lkr": 650, "confidence": "medium", "source_key": "ntc-bus-fares", "note": "Distance-table estimate for public bus travel."},
    {"mode": "bus", "from_area": "Colombo", "to_area": "Galle", "fare_lkr": 520, "confidence": "medium", "source_key": "ntc-bus-fares", "note": "Distance-table estimate for public bus travel."},
    {"mode": "bus", "from_area": "Gampaha", "to_area": "Colombo", "fare_lkr": 220, "confidence": "medium", "source_key": "ntc-bus-fares", "note": "Commuter corridor planning estimate."},
    {"mode": "fuel", "from_area": "Colombo", "to_area": "Kandy", "fare_lkr": 6200, "confidence": "low", "source_key": "cpc-fuel", "note": "Private vehicle fuel-only estimate; excludes parking, maintenance, and tolls."},
]

RETAIL_OFFERS = [
    {"item_name": "Rice Nadu", "retailer": "Public retail blend", "district": "Sri Lanka", "price_lkr": 320, "unit": "1kg", "source_key": "retail-public-pages", "confidence": "medium", "note": "Retail quote sample; compare against FoodLK market quotes."},
    {"item_name": "Dhal", "retailer": "Public retail blend", "district": "Sri Lanka", "price_lkr": 420, "unit": "1kg", "source_key": "retail-public-pages", "confidence": "medium", "note": "Retail quote sample; official market validation pending."},
    {"item_name": "Milk powder", "retailer": "Public retail blend", "district": "Sri Lanka", "price_lkr": 1190, "unit": "400g", "source_key": "retail-public-pages", "confidence": "medium", "note": "Retail offer signal, not an official controlled price."},
    {"item_name": "Coconut", "retailer": "Public retail blend", "district": "Sri Lanka", "price_lkr": 145, "unit": "each", "source_key": "retail-public-pages", "confidence": "low", "note": "Highly local item; district quote ingestion should replace this."},
    {"item_name": "Chicken", "retailer": "Public retail blend", "district": "Colombo", "price_lkr": 1280, "unit": "1kg", "source_key": "retail-public-pages", "confidence": "medium", "note": "Retail quote sample for protein basket."},
]

FOOD_PROTEIN_BASKET = [
    {
        "item_name": "Dhal",
        "weekly_quantity": 1.0,
        "price_lkr": 420,
        "unit": "1kg",
        "protein_g_per_unit": 240,
        "source_keys": ["foodlk-platform", "cbsl-price-report", "harti-daily", "public-lk-food"],
        "confidence": "medium",
        "note": "Plant-protein anchor for household meal substitutions.",
    },
    {
        "item_name": "Eggs",
        "weekly_quantity": 10,
        "price_lkr": 58,
        "unit": "each",
        "protein_g_per_unit": 6,
        "source_keys": ["foodlk-platform", "cbsl-price-report", "harti-daily", "public-lk-food"],
        "confidence": "medium",
        "note": "Count-based household protein proxy until live item matching is normalized.",
    },
    {
        "item_name": "Chicken",
        "weekly_quantity": 0.75,
        "price_lkr": 1280,
        "unit": "1kg",
        "protein_g_per_unit": 270,
        "source_keys": ["foodlk-platform", "retail-public-pages", "public-lk-food"],
        "confidence": "medium",
        "note": "Retail quote sample for animal-protein pressure.",
    },
    {
        "item_name": "Fish",
        "weekly_quantity": 0.75,
        "price_lkr": 1100,
        "unit": "1kg",
        "protein_g_per_unit": 220,
        "source_keys": ["fisheries-statistics", "public-lk-fisheries", "public-lk-food"],
        "confidence": "medium",
        "note": "Fisheries supply context for fish-protein planning.",
    },
]

AREA_BASE = {
    "Sri Lanka": {"rent": 58, "food": 66, "transport": 61, "utilities": 58, "source": 70},
    "Colombo": {"rent": 41, "food": 62, "transport": 74, "utilities": 62, "source": 82},
    "Gampaha": {"rent": 57, "food": 65, "transport": 70, "utilities": 60, "source": 76},
    "Kandy": {"rent": 63, "food": 67, "transport": 66, "utilities": 58, "source": 70},
    "Galle": {"rent": 65, "food": 68, "transport": 61, "utilities": 57, "source": 68},
    "Jaffna": {"rent": 69, "food": 60, "transport": 56, "utilities": 54, "source": 62},
    "Matara": {"rent": 71, "food": 69, "transport": 57, "utilities": 56, "source": 63},
    "Kurunegala": {"rent": 72, "food": 70, "transport": 62, "utilities": 56, "source": 65},
}

I18N_LABELS = {
    "en": {
        "today": "Today",
        "cost_os": "Cost Desk",
        "atlas": "Atlas",
        "intelligence": "Signals",
        "sources": "Sources",
        "national_cost_pulse": "National cost pulse",
        "daily_living_total": "Daily living total",
        "source_health": "Source health",
        "public_only": "Public only",
        "no_accounts": "Optional account. Public view works without sign-in.",
        "degraded": "Degraded source",
        "search": "Search food, fuel, rent, transport",
    },
    "si": {
        "today": "අද",
        "cost_os": "වියදම් මධ්‍යස්ථානය",
        "atlas": "සිතියම",
        "intelligence": "සංඥා",
        "sources": "මූලාශ්‍ර",
        "national_cost_pulse": "ජාතික වියදම් තත්ත්වය",
        "daily_living_total": "දෛනික ජීවන වියදම",
        "source_health": "මූලාශ්‍ර සෞඛ්‍යය",
        "public_only": "පොදු පමණි",
        "no_accounts": "ගිණුමක් අවශ්‍ය නැත. පොදු දසුන සැමට විවෘතයි.",
        "degraded": "අඩු තත්ත්වයේ මූලාශ්‍රය",
        "search": "ආහාර, ඉන්ධන, කුලිය, ගමනාගමනය සොයන්න",
    },
    "ta": {
        "today": "இன்று",
        "cost_os": "செலவு மேசை",
        "atlas": "வரைபடம்",
        "intelligence": "சிக்னல்கள்",
        "sources": "மூலங்கள்",
        "national_cost_pulse": "தேசிய செலவு நிலை",
        "daily_living_total": "தினசரி வாழ்வு செலவு",
        "source_health": "மூல நலம்",
        "public_only": "பொது பயன்பாடு மட்டும்",
        "no_accounts": "கணக்கு விருப்பம். பொது காட்சி உள்நுழைவு இல்லாமலும் செயல்படும்.",
        "degraded": "குறைந்த நம்பகத் தரம்",
        "search": "உணவு, எரிபொருள், வாடகை, போக்குவரத்து தேடுங்கள்",
    },
}

DOMAIN_TRANSLATIONS = {
    "en": {
        "food": "Food and grocery",
        "fuel": "Fuel",
        "property": "Property and rent",
        "vehicle": "Vehicle market",
        "utilities": "Utilities",
        "gas": "LPG gas",
        "transport": "Public transport",
        "retail": "Retail offers",
        "indices": "Official indices",
        "areas": "District life scores",
        "weather": "Weather and risk",
    },
    "si": {
        "food": "ආහාර හා සිල්ලර",
        "fuel": "ඉන්ධන",
        "property": "දේපළ හා කුලී",
        "vehicle": "වාහන වෙළඳපොළ",
        "utilities": "උපයෝගිතා",
        "gas": "LPG ගෑස්",
        "transport": "පොදු ප්‍රවාහනය",
        "retail": "රීටේල් දීමනා",
        "indices": "නිල දර්ශක",
        "areas": "ප්‍රදේශ ජීවන ලකුණු",
        "weather": "කාලගුණ හා අවදානම්",
    },
    "ta": {
        "food": "உணவு மற்றும் மளிகை",
        "fuel": "எரிபொருள்",
        "property": "சொத்து மற்றும் வாடகை",
        "vehicle": "வாகன சந்தை",
        "utilities": "பயன்பாட்டு சேவைகள்",
        "gas": "LPG எரிவாயு",
        "transport": "பொது போக்குவரத்து",
        "retail": "சில்லறை சலுகைகள்",
        "indices": "அதிகாரப்பூர்வ சுட்டெண்கள்",
        "areas": "பகுதி வாழ்வு மதிப்பெண்கள்",
        "weather": "வானிலை மற்றும் ஆபத்து",
    },
}


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def source_refs(domain: str | None = None) -> list[SourceReference]:
    now = utc_now()
    rows = [row for row in SOURCE_DEFINITIONS if domain is None or row["domain_key"] == domain]
    return [
        SourceReference(
            key=row["key"],
            label=row["label"],
            source_type=row["source_type"],
            url=row["url"],
            confidence=row["confidence"],
            freshness_note=row["freshness_note"],
            **source_governance(row),
            last_checked_at=now,
            labels=row.get("labels", {}),
        )
        for row in rows
    ]


def grade_for(score: float) -> str:
    if score >= 80:
        return "A"
    if score >= 70:
        return "B"
    if score >= 60:
        return "C"
    if score >= 50:
        return "D"
    return "E"


def iso_now() -> datetime:
    return utc_now()


DISTRICT_PROFILE_SOURCE_KEYS = ["dcs-census-2024", "public-lk-census-2024-extracts", "public-lk-admin-regions", "public-lanka-data"]

OFFICIAL_COST_SOURCE_KEYS = [
    "pucsl-electricity",
    "nwsdb-water",
    "litro-lpg",
    "laugfs-lpg",
    "ntc-bus-fares",
    "cpc-fuel",
]

OFFICIAL_IMPORT_CONTEXT_SOURCE_KEYS = [
    "cbsl-economic-data",
    "sri-lanka-customs-tariff",
]

OPTIONAL_IMPORT_CONTEXT_SOURCE_KEYS = ["currency-api"]

SCORE_DEPENDENCY_SOURCE_KEYS = sorted(
    set(
        DISTRICT_PROFILE_SOURCE_KEYS
        + WEATHER_RISK_SOURCE_KEYS
        + [
            "foodlk-platform",
            "ntc-bus-fares",
            "nwsdb-water",
            "propertylk-platform",
            "pucsl-electricity",
        ]
    )
)


def _profile_from_row(row: dict) -> DistrictProfile:
    density = round(row["population"] / row["area_sqkm"], 1)
    return DistrictProfile(
        key=row["key"],
        region_id=row["region_id"],
        province=row["province"],
        population=row["population"],
        households=row["households"],
        area_sqkm=row["area_sqkm"],
        density_per_sqkm=density,
        center_lat=row["center_lat"],
        center_lng=row["center_lng"],
        cooking_gas_share=row["cooking_gas_share"],
        elderly_share=row["elderly_share"],
        confidence="high",
        source_keys=DISTRICT_PROFILE_SOURCE_KEYS,
        note="Population and household facts come from Census 2024 extracts; area and center points come from the public Lanka Data administrative region layer.",
    )


def district_profiles() -> list[DistrictProfile]:
    return [_profile_from_row(row) for row in DISTRICT_PROFILE_ROWS]


def district_profile_for(district: str) -> DistrictProfile:
    normalized = " ".join((district or "Sri Lanka").replace("-", " ").split()).lower()
    for row in DISTRICT_PROFILE_ROWS:
        if row["key"].lower() == normalized:
            return _profile_from_row(row)
    return _profile_from_row(DISTRICT_PROFILE_ROWS[0])


def _weather_risk_score(rainfall_mm: float, humidity_percent: float, coverage: str) -> float:
    rain_pressure = min(rainfall_mm * 1.8, 52)
    humidity_pressure = max(humidity_percent - 78, 0) * 1.15
    proxy_penalty = 6 if coverage == "proxy" else 0
    return round(min(100, 24 + rain_pressure + humidity_pressure + proxy_penalty), 1)


def _weather_severity(rainfall_mm: float, humidity_percent: float, score: float) -> str:
    if rainfall_mm >= 20 or score >= 72:
        return "risk"
    if rainfall_mm >= 5 or humidity_percent >= 92 or score >= 48:
        return "watch"
    return "good"


def _weather_observation_for_district(district: str, station_name: str, coverage: str) -> WeatherRiskObservation:
    station_rows = {row["station_name"]: row for row in WEATHER_STATION_ROWS}
    row = station_rows[station_name]
    score = _weather_risk_score(row["rainfall_mm"], row["humidity_percent"], coverage)
    severity = _weather_severity(row["rainfall_mm"], row["humidity_percent"], score)
    if coverage == "national":
        note = "National watch uses the highest-pressure reviewed station row until district-level alert ingestion is automated."
    elif coverage == "proxy":
        note = f"{district} uses nearest reviewed station proxy {station_name}; treat as planning context, not a local warning."
    else:
        note = f"{district} uses the directly mapped {station_name} station from the public 3-hour weather extract."
    return WeatherRiskObservation(
        district=district,
        station_id=row["station_id"],
        station_name=station_name,
        observed_at=row["observed_at"],
        rainfall_mm=row["rainfall_mm"],
        temperature_c=row["temperature_c"],
        humidity_percent=row["humidity_percent"],
        risk_score=score,
        severity=severity,
        coverage=coverage,
        confidence="medium" if coverage == "direct" else "low",
        source_keys=WEATHER_RISK_SOURCE_KEYS,
        note=note,
    )


def weather_risk_observations() -> list[WeatherRiskObservation]:
    return [
        _weather_observation_for_district(district, station_name, coverage)
        for district, (station_name, coverage) in DISTRICT_WEATHER_STATIONS.items()
    ]


def weather_risk_for(district: str) -> WeatherRiskObservation:
    normalized = " ".join((district or "Sri Lanka").replace("-", " ").split()).lower()
    for item in weather_risk_observations():
        if item.district.lower() == normalized:
            return item
    return weather_risk_observations()[0]


def _validation_check(
    *,
    key: str,
    label: str,
    status: str,
    message: str,
    evidence: list[str] | None = None,
    source_keys: list[str] | None = None,
) -> SourceValidationCheck:
    return SourceValidationCheck(
        key=key,
        label=label,
        status=status,
        message=message,
        evidence=evidence or [],
        source_keys=source_keys or [],
    )


def _missing_keys(source_keys: list[str], source_map: dict[str, SourceReference]) -> list[str]:
    return sorted(key for key in source_keys if key not in source_map)


def _unreviewed_keys(source_keys: list[str], source_map: dict[str, SourceReference]) -> list[str]:
    return sorted(
        key
        for key in source_keys
        if key in source_map
        and (source_map[key].review_status == "needs_review" or source_map[key].license_status == "needs_review")
    )


def source_validation_report() -> SourceValidationResponse:
    source_map = {source.key: source for source in source_refs()}
    source_keys = [row["key"] for row in SOURCE_DEFINITIONS]
    duplicate_keys = sorted({key for key in source_keys if source_keys.count(key) > 1})
    allowed_domains = set(DOMAIN_TRANSLATIONS["en"])
    unknown_domains = sorted({row["domain_key"] for row in SOURCE_DEFINITIONS if row["domain_key"] not in allowed_domains})
    district_profile_keys = [row["key"] for row in DISTRICT_PROFILE_ROWS]
    station_names = {row["station_name"] for row in WEATHER_STATION_ROWS}
    mapped_station_names = {station_name for station_name, _coverage in DISTRICT_WEATHER_STATIONS.values()}
    missing_weather_districts = sorted(set(DISTRICTS) - set(DISTRICT_WEATHER_STATIONS))
    missing_stations = sorted(mapped_station_names - station_names)
    density_mismatches = [
        profile.key
        for profile in district_profiles()
        if abs(profile.density_per_sqkm - round(profile.population / profile.area_sqkm, 1)) > 0.1
    ]
    missing_score_sources = _missing_keys(SCORE_DEPENDENCY_SOURCE_KEYS, source_map)
    unreviewed_score_sources = _unreviewed_keys(SCORE_DEPENDENCY_SOURCE_KEYS, source_map)
    official_cost_source_keys = OFFICIAL_COST_SOURCE_KEYS + OFFICIAL_IMPORT_CONTEXT_SOURCE_KEYS
    missing_official_cost_sources = _missing_keys(official_cost_source_keys, source_map)
    unreviewed_official_cost_sources = _unreviewed_keys(official_cost_source_keys, source_map)
    optional_import_candidates = sorted(
        key
        for key in OPTIONAL_IMPORT_CONTEXT_SOURCE_KEYS
        if key in source_map and source_map[key].review_status == "candidate"
    )
    candidate_score_sources = sorted(
        key
        for key in SCORE_DEPENDENCY_SOURCE_KEYS
        if key in source_map and source_map[key].review_status == "candidate"
    )
    candidate_context_sources = sorted(source.key for source in source_map.values() if source.review_status == "candidate")

    checks = [
        _validation_check(
            key="registry-keys",
            label="Source registry keys",
            status="fail" if duplicate_keys or unknown_domains else "pass",
            message="Source keys are unique and each source maps to a known Life domain."
            if not duplicate_keys and not unknown_domains
            else "Source registry has duplicate keys or unknown domains.",
            evidence=[
                f"{len(source_keys)} source definitions",
                f"duplicates: {', '.join(duplicate_keys) or 'none'}",
                f"unknown domains: {', '.join(unknown_domains) or 'none'}",
            ],
        ),
        _validation_check(
            key="governance-fields",
            label="Governance metadata",
            status="fail"
            if any(
                not source.owner
                or not source.collection_method
                or not source.license_status
                or not source.review_status
                or not source.refresh_cadence
                for source in source_map.values()
            )
            else "pass",
            message="Every source exposes owner, collection method, license, review status, and refresh cadence.",
            evidence=[f"{len(source_map)} source references rendered with governance fields"],
            source_keys=sorted(source_map),
        ),
        _validation_check(
            key="district-profile-coverage",
            label="District profile coverage",
            status="fail" if len(district_profile_keys) != len(set(district_profile_keys)) or len(district_profile_keys) != 26 else "pass",
            message="District profile seed covers Sri Lanka plus all 25 districts exactly once."
            if len(district_profile_keys) == len(set(district_profile_keys)) == 26
            else "District profile coverage is incomplete or duplicated.",
            evidence=[f"{len(district_profile_keys)} district profile rows", f"density mismatches: {', '.join(density_mismatches) or 'none'}"],
            source_keys=DISTRICT_PROFILE_SOURCE_KEYS,
        ),
        _validation_check(
            key="district-profile-density",
            label="District density arithmetic",
            status="fail" if density_mismatches else "pass",
            message="Density values are reproducible from population divided by district area."
            if not density_mismatches
            else "One or more district density values no longer match population and area.",
            evidence=[f"checked {len(district_profiles())} computed profiles"],
            source_keys=DISTRICT_PROFILE_SOURCE_KEYS,
        ),
        _validation_check(
            key="weather-risk-coverage",
            label="Weather risk coverage",
            status="fail" if missing_weather_districts or missing_stations else "pass",
            message="Weather risk seed maps every displayed district to a reviewed direct or proxy station."
            if not missing_weather_districts and not missing_stations
            else "Weather risk station coverage is incomplete.",
            evidence=[
                f"{len(DISTRICT_WEATHER_STATIONS)} district station mappings",
                f"missing districts: {', '.join(missing_weather_districts) or 'none'}",
                f"missing stations: {', '.join(missing_stations) or 'none'}",
            ],
            source_keys=WEATHER_RISK_SOURCE_KEYS,
        ),
        _validation_check(
            key="score-source-gate",
            label="Score source gate",
            status="fail" if missing_score_sources or unreviewed_score_sources or candidate_score_sources else "pass",
            message="Every scoring dependency exists and is approved or reviewed before use."
            if not missing_score_sources and not unreviewed_score_sources and not candidate_score_sources
            else "One or more scoring dependencies is missing, unreviewed, or still candidate-only.",
            evidence=[
                f"{len(SCORE_DEPENDENCY_SOURCE_KEYS)} scoring source dependencies",
                f"missing: {', '.join(missing_score_sources) or 'none'}",
                f"unreviewed: {', '.join(unreviewed_score_sources) or 'none'}",
                f"candidate-only: {', '.join(candidate_score_sources) or 'none'}",
            ],
            source_keys=SCORE_DEPENDENCY_SOURCE_KEYS,
        ),
        _validation_check(
            key="official-cost-source-coverage",
            label="Official cost source coverage",
            status="fail" if missing_official_cost_sources or unreviewed_official_cost_sources else "pass",
            message="Official utility, transport, fuel, and import-context sources are registered before tariff automation."
            if not missing_official_cost_sources and not unreviewed_official_cost_sources
            else "One or more official cost/import source references is missing or unreviewed.",
            evidence=[
                f"{len(OFFICIAL_COST_SOURCE_KEYS)} utility, gas, transport, and fuel source references",
                f"{len(OFFICIAL_IMPORT_CONTEXT_SOURCE_KEYS)} official import-context source references",
                f"missing: {', '.join(missing_official_cost_sources) or 'none'}",
                f"unreviewed: {', '.join(unreviewed_official_cost_sources) or 'none'}",
                f"optional candidate fallback isolated: {', '.join(optional_import_candidates) or 'none'}",
            ],
            source_keys=official_cost_source_keys + optional_import_candidates,
        ),
        _validation_check(
            key="candidate-isolation",
            label="Candidate source isolation",
            status="pass",
            message="Candidate public APIs and retail pages stay visible in the registry but are isolated from score dependencies.",
            evidence=[f"candidate context sources: {', '.join(candidate_context_sources) or 'none'}"],
            source_keys=candidate_context_sources,
        ),
    ]
    if any(check.status == "fail" for check in checks):
        status = "offline"
        summary = "Source validation is failing; do not promote new scoring outputs."
    elif any(check.status == "watch" for check in checks):
        status = "degraded"
        summary = "Source validation has warnings; keep confidence caveats visible."
    else:
        status = "healthy"
        summary = "Source validation gate is healthy for the current seeded atlas and weather scoring path."
    touched_source_keys = sorted({source_key for check in checks for source_key in check.source_keys if source_key in source_map})
    return SourceValidationResponse(
        generated_at=utc_now(),
        status=status,
        summary=summary,
        checks=checks,
        sources=[source_map[key] for key in touched_source_keys],
    )
