from datetime import timedelta

from sqlalchemy import func, select

from app.db.models import AreaScoreSnapshot, DistrictProfileSnapshot, SourceDataRelease, SourceImportArtifact, WeatherRiskSnapshot
from app.db.session import SessionLocal
from app.schemas import SourceImportCheck, SourceImportExecutionResponse, SourceImportExecutionRun
from app.services.living_atlas_data import DISTRICTS, DISTRICT_PROFILE_ROWS, WEATHER_STATION_ROWS, utc_now
from app.services.source_imports import (
    build_district_profile_rows_from_census_payloads,
    build_weather_station_rows_from_alert_payload,
    official_cost_parser_evidence_from_reviewed_fixtures,
)


def test_official_cost_parser_fixtures_extract_review_evidence():
    evidence = official_cost_parser_evidence_from_reviewed_fixtures()
    by_source = {row.source_key: row for row in evidence}

    assert set(by_source) == {
        "cbsl-economic-data",
        "cpc-fuel",
        "ntc-bus-fares",
        "nwsdb-water",
        "pucsl-electricity",
        "sri-lanka-customs-tariff",
    }
    assert by_source["pucsl-electricity"].evidence["latest_decision"] == "2026 May"
    assert by_source["nwsdb-water"].evidence["domestic_block_count"] == 11
    assert by_source["ntc-bus-fares"].evidence["effective_from"] == "24th of March 2026"
    assert by_source["cpc-fuel"].evidence["products"][0]["product"] == "Lanka Petrol 92 Octane"
    assert len(by_source["cbsl-economic-data"].evidence["spreadsheet_labels"]) == 4
    assert by_source["sri-lanka-customs-tariff"].evidence["tariff_year"] == "2026"
    assert by_source["sri-lanka-customs-tariff"].evidence["legal_notice_present"] is True


def test_direct_district_profile_import_parser_normalizes_census_payloads():
    population_rows = []
    household_rows = []
    cooking_fuel_rows = []
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
    for seed in DISTRICT_PROFILE_ROWS:
        elderly_count = round(seed["population"] * seed["elderly_share"])
        gas_households = round(seed["households"] * seed["cooking_gas_share"])
        population_rows.append(
            {
                "region_id": seed["region_id"],
                "total": seed["population"],
                "age-60-to-64": 0,
                "age-65-and-over": elderly_count,
            }
        )
        household_rows.append({"region_id": seed["region_id"], "n_households": seed["households"]})
        cooking_fuel_rows.append({"region_id": seed["region_id"], "gas": gas_households})
        geography_row = {
            "id": seed["region_id"],
            "name": seed["key"],
            "area_sqkm": seed["area_sqkm"],
            "center_lat": seed["center_lat"],
            "center_lng": seed["center_lng"],
        }
        if seed["region_id"] == "LK":
            country_region_rows.append(geography_row)
        else:
            geography_row["province_id"] = province_names_to_id[seed["province"]]
            district_region_rows.append(geography_row)

    imported = build_district_profile_rows_from_census_payloads(
        population_rows,
        household_rows,
        cooking_fuel_rows,
        country_region_rows,
        province_region_rows,
        district_region_rows,
    )

    assert len(imported) == 26
    colombo = next(row for row in imported if row.key == "Colombo")
    assert colombo.population == 2375415
    assert colombo.households == 661822
    assert colombo.cooking_gas_share == 0.855


def test_direct_weather_import_parser_normalizes_alert_payloads():
    station_payload = {row["station_id"]: row["station_name"] for row in WEATHER_STATION_ROWS}
    station_payload["43410"] = "Mullativu"
    event_data = {}
    for seed in WEATHER_STATION_ROWS:
        station_name = "Mullativu" if seed["station_name"] == "Mullaitivu" else seed["station_name"]
        observed_at = seed["observed_at"]
        event_data.setdefault(station_name, {}).setdefault(observed_at[:10].replace("-", ""), {})[observed_at[11:16].replace(":", "")] = {
            "rain_mm": seed["rainfall_mm"],
            "temp_c": seed["temperature_c"],
            "rh": round(seed["humidity_percent"] / 100, 3),
        }

    imported = build_weather_station_rows_from_alert_payload(
        station_payload,
        {
            "url_source": "https://www.meteo.gov.lk",
            "event": "weather_report_3h",
            "event_measures": ["rain_mm", "temp_c", "rh"],
            "event_data": event_data,
        },
    )

    assert len(imported) == len(WEATHER_STATION_ROWS)
    ratnapura = next(row for row in imported if row.station_name == "Ratnapura")
    assert ratnapura.rainfall_mm == 25.5
    assert ratnapura.temperature_c == 24.6
    assert ratnapura.humidity_percent == 98.0


def test_life_overview_returns_all_domains(client):
    response = client.get("/api/v1/life/overview")
    assert response.status_code == 200
    payload = response.json()
    assert payload["headline"].startswith("Ariva reads Sri Lanka")
    survival = payload["survival_index"]
    assert survival["district"] == "Sri Lanka"
    assert survival["profile"] == "family"
    assert survival["monthly_lkr"] > 0
    assert survival["daily_lkr"] > 0
    assert survival["confidence"] in {"high", "medium", "low"}
    assert survival["label"] == "Cost of Life"
    assert survival["disclaimer"]
    assert survival["index_score"] == 100
    assert survival["trend"] == "flat"
    assert {domain["key"] for domain in payload["domains"]} == {
        "food",
        "fuel",
        "property",
        "vehicle",
        "utilities",
        "gas",
        "transport",
        "retail",
        "indices",
        "areas",
        "weather",
    }
    assert payload["affordability"]["total_monthly_lkr"] > 0
    assert payload["source_health"]["total"] == 11
    source_keys = {source["key"] for domain in payload["domains"] for source in domain["sources"]}
    assert {
        "dcs-census-2024",
        "public-lk-census-2024-extracts",
        "public-lk-weather-3h",
        "public-lk-irrigation",
        "public-lk-food",
        "public-lk-fisheries",
        "public-lk-tourism",
        "currency-api",
        "sri-lanka-customs-tariff",
        "public-bus-routes-lk",
        "public-lk-hansard",
        "dmc-lk",
    }.issubset(source_keys)
    sources = {source["key"]: source for domain in payload["domains"] for source in domain["sources"]}
    assert sources["dcs-census-2024"]["review_status"] == "approved"
    assert sources["dcs-census-2024"]["license_status"] == "official_public"
    assert sources["public-lk-weather-3h"]["review_status"] == "reviewed"
    assert sources["public-lk-weather-3h"]["license_status"] == "permissive"
    assert sources["public-lk-weather-3h"]["refresh_cadence"] == "scheduled refresh plus manual trigger"
    assert sources["propertylk-platform"]["review_status"] == "approved"


def test_life_overview_survival_index_is_district_specific(client):
    national = client.get("/api/v1/life/overview?district=Sri%20Lanka&profile=commuter").json()["survival_index"]
    response = client.get("/api/v1/life/overview?district=Colombo&profile=commuter")
    assert response.status_code == 200
    payload = response.json()
    assert payload["headline"].startswith("Ariva reads living signals for Colombo")
    survival = payload["survival_index"]
    assert survival["district"] == "Colombo"
    assert survival["profile"] == "commuter"
    assert survival["index_score"] == national["index_score"]
    assert survival["monthly_lkr"] == national["monthly_lkr"]
    assert survival["monthly_lkr"] < payload["affordability"]["total_monthly_lkr"]
    assert survival["trend"] in {"up", "down", "flat"}
    assert round(survival["daily_lkr"], 0) == round(survival["monthly_lkr"] / 30.4, 0)


def test_life_overview_survival_index_uses_mvp_weights(client):
    response = client.get("/api/v1/life/overview?district=Kandy&profile=family")
    assert response.status_code == 200
    survival = response.json()["survival_index"]
    assert survival["label"] == "Cost of Life"
    assert "45%" in survival["disclaimer"]
    assert "20%" in survival["disclaimer"]
    assert "35%" in survival["disclaimer"]
    assert survival["index_score"] is not None
    assert survival["monthly_lkr"] > 0
    assert survival["monthly_lkr"] < response.json()["affordability"]["total_monthly_lkr"]


def test_life_domains_records_snapshots(client):
    response = client.get("/api/v1/life/domains?force_refresh=true")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload["items"]) == 11

    trends = client.get("/api/v1/life/trends?domain=food")
    assert trends.status_code == 200
    assert len(trends.json()["points"]) >= 1


def test_life_search_finds_domain_and_metric(client):
    client.get("/api/v1/life/overview")
    response = client.get("/api/v1/life/search?q=petrol")
    assert response.status_code == 200
    results = response.json()
    assert any(item["domain"] == "fuel" for item in results)


def test_life_search_routes_vehicle_and_food_intents(client):
    client.get("/api/v1/life/overview")

    vehicle_response = client.get("/api/v1/life/search?q=Toyota%20Axio")
    assert vehicle_response.status_code == 200
    vehicle_results = vehicle_response.json()
    assert vehicle_results[0]["domain"] == "vehicle"
    assert not any(item["domain"] == "food" for item in vehicle_results[:3])

    food_response = client.get("/api/v1/life/search?q=rice")
    assert food_response.status_code == 200
    food_results = food_response.json()
    assert food_results[0]["domain"] == "food"

    protein_response = client.get("/api/v1/life/search?q=protein")
    assert protein_response.status_code == 200
    protein_results = protein_response.json()
    assert protein_results[0]["label"] == "FoodLK: Protein basket"
    assert protein_results[0]["domain"] == "food"


def test_life_affordability_profiles(client):
    response = client.get("/api/v1/life/affordability?district=Colombo&profile=commuter")
    assert response.status_code == 200
    payload = response.json()
    assert payload["district"] == "Colombo"
    assert payload["profile"] == "commuter"
    assert any(item["key"] == "fuel" for item in payload["breakdown"])


def test_life_pipeline_degrades_without_breaking(client):
    response = client.get("/api/v1/life/pipeline")
    assert response.status_code == 200
    payload = response.json()
    assert payload["overall_status"] in {"healthy", "degraded", "offline"}
    assert len(payload["domains"]) == 11


def test_source_validation_gate_is_healthy(client):
    response = client.get("/api/v1/life/source-validation")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "healthy"
    checks = {check["key"]: check for check in payload["checks"]}
    assert checks["score-source-gate"]["status"] == "pass"
    assert checks["official-cost-source-coverage"]["status"] == "pass"
    assert checks["weather-risk-coverage"]["status"] == "pass"
    assert checks["district-profile-coverage"]["status"] == "pass"
    assert "open-meteo" not in checks["score-source-gate"]["source_keys"]
    assert "public-lanka-data" in checks["score-source-gate"]["source_keys"]
    assert "sri-lanka-customs-tariff" in checks["official-cost-source-coverage"]["source_keys"]
    sources = {source["key"]: source for source in payload["sources"]}
    assert all(sources[key]["review_status"] != "needs_review" for key in checks["score-source-gate"]["source_keys"])


def test_public_source_release_reports_seed_fallback_without_internal_payload(client):
    response = client.get("/api/v1/life/source-release")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "seed_fallback"
    assert payload["active_release_key"] is None
    assert payload["observed_at"] is None
    assert payload["source_keys"] == []
    assert payload["district_profile_snapshot_count"] == 0
    assert payload["weather_risk_snapshot_count"] == 0
    assert payload["area_score_snapshot_count"] == 0
    assert "source_import_artifact_ids" not in payload
    assert "checks" not in payload
    assert "operator_notes" not in payload


def test_living_atlas_v2_public_endpoints(client):
    cost = client.get("/api/v1/life/cost-command?district=Colombo&profile=family&locale=si")
    assert cost.status_code == 200
    cost_payload = cost.json()
    assert cost_payload["locale"] == "si"
    assert cost_payload["total_monthly_lkr"] > 0
    assert any(item["key"] == "gas" for item in cost_payload["items"])
    utilities_item = next(item for item in cost_payload["items"] if item["key"] == "utilities")
    transport_item = next(item for item in cost_payload["items"] if item["key"] == "transport")
    vehicle_item = next(item for item in cost_payload["items"] if item["key"] == "vehicle")
    assert utilities_item["source_type"] == "official"
    assert utilities_item["source_keys"] == ["pucsl-electricity", "nwsdb-water"]
    assert transport_item["source_type"] == "official"
    assert "ntc-bus-fares" in transport_item["source_keys"]
    assert "sri-lanka-customs-tariff" in vehicle_item["source_keys"]
    assert cost_payload["items"][0]["label"] == "ආහාර සහ සිල්ලර"
    assert any(move["label"] == "Protein basket check" and "source-labelled protein servings" in move["value"] for move in cost_payload["savings_moves"])

    atlas = client.get("/api/v1/life/atlas?district=Kandy&locale=ta")
    assert atlas.status_code == 200
    atlas_payload = atlas.json()
    assert atlas_payload["locale"] == "ta"
    assert atlas_payload["selected"]["district"] == "Kandy"
    assert atlas_payload["selected_profile"]["population"] == 1461895
    assert atlas_payload["selected_profile"]["source_keys"] == [
        "dcs-census-2024",
        "public-lk-census-2024-extracts",
        "public-lk-admin-regions",
        "public-lanka-data",
    ]
    assert len(atlas_payload["district_scores"]) >= 26
    assert len(atlas_payload["district_profiles"]) >= 26
    assert "density_per_sqkm" in atlas_payload["heatmap"][0]
    assert "weather" in atlas_payload["heatmap"][0]
    assert atlas_payload["methodology"]
    assert "சுயவிவரத்திற்கு" in atlas_payload["narrative"]

    score = client.get("/api/v1/life/areas/score?district=Galle&profile=commuter&locale=si")
    assert score.status_code == 200
    assert score.json()["profile"] == "commuter"
    assert score.json()["components"][0]["label"] == "කුලී පීඩනය"
    assert score.json()["district_profile"]["households"] == 307704
    assert score.json()["components"][0]["source_keys"]

    fallback_score = client.get("/api/v1/life/areas/score?district=Unknown&profile=family")
    assert fallback_score.status_code == 200
    assert fallback_score.json()["district"] == "Sri Lanka"

    utilities = client.get("/api/v1/life/utilities?district=Colombo")
    assert utilities.status_code == 200
    assert utilities.json()["electricity"]

    transport = client.get("/api/v1/life/transport?from=Gampaha&to=Colombo")
    assert transport.status_code == 200
    assert transport.json()["from_area"] == "Gampaha"
    assert transport.json()["to_area"] == "Colombo"
    assert any(item["mode"] == "bus" for item in transport.json()["options"])

    retail = client.get("/api/v1/life/retail/offers?q=rice&district=Sri%20Lanka")
    assert retail.status_code == 200
    assert any("Rice" in item["item_name"] for item in retail.json()["offers"])

    weather = client.get("/api/v1/life/weather-risk?district=Ratnapura")
    assert weather.status_code == 200
    weather_payload = weather.json()
    assert weather_payload["selected"]["district"] == "Ratnapura"
    assert weather_payload["selected"]["severity"] == "risk"
    assert weather_payload["selected"]["source_keys"] == [
        "meteo-lk-3h",
        "public-lk-weather-3h",
        "dmc-lk",
        "public-lk-rivers",
        "public-lk-irrigation",
    ]
    assert len(weather_payload["observations"]) >= 26
    assert weather_payload["sources"][0]["owner"]
    assert weather_payload["sources"][0]["governance_note"]

    insights = client.get("/api/v1/life/insights?domain=indices")
    assert insights.status_code == 200
    assert insights.json()["insights"]

    food_insights = client.get("/api/v1/life/insights?domain=food")
    assert food_insights.status_code == 200
    food_payload = food_insights.json()
    protein_insight = next(item for item in food_payload["insights"] if item["id"] == "food-protein-affordability")
    assert "per 25g protein serving" in protein_insight["message"]
    food_source_keys = {source["key"] for source in food_payload["sources"]}
    assert {"foodlk-platform", "public-lk-food", "fisheries-statistics", "public-lk-fisheries"}.issubset(food_source_keys)

    weather_insights = client.get("/api/v1/life/insights?domain=weather")
    assert weather_insights.status_code == 200
    assert weather_insights.json()["insights"][0]["domain"] == "weather"


def test_life_i18n_has_three_locales(client):
    for locale in ["en", "si", "ta"]:
        response = client.get(f"/api/v1/life/i18n?locale={locale}")
        assert response.status_code == 200
        payload = response.json()
        assert payload["locale"] == locale
        assert payload["labels"]["today"]
        assert payload["domains"]["utilities"]
        assert payload["domains"]["weather"]
        assert payload["sources"]["dcs-ccpi"]
        assert payload["sources"]["dcs-census-2024"]
        assert payload["sources"]["public-lk-weather-3h"]


def test_living_atlas_tables_exist(client):
    response = client.get("/api/v1/life/cost-command")
    assert response.status_code == 200
    pipeline = client.get("/api/v1/life/pipeline")
    assert pipeline.status_code == 200


def test_me_endpoints_require_auth(client):
    response = client.get("/api/v1/me/profile")
    assert response.status_code == 401


def test_hybrid_account_profile_saved_items_alerts_and_notifications(client):
    headers = {"Authorization": "Bearer life-test-token"}

    profile = client.get("/api/v1/me/profile", headers=headers)
    assert profile.status_code == 200
    assert profile.json()["district"] == "Sri Lanka"

    updated = client.put(
        "/api/v1/me/profile",
        headers=headers,
        json={"district": "Colombo", "profile": "commuter", "default_locale": "si"},
    )
    assert updated.status_code == 200
    assert updated.json()["district"] == "Colombo"
    assert updated.json()["profile"] == "commuter"
    assert updated.json()["default_locale"] == "si"

    saved = client.post(
        "/api/v1/me/saved-items",
        headers=headers,
        json={"domain_key": "food", "label": "Rice watch", "query": "rice", "href": "/intelligence", "payload": {"unit": "1kg"}},
    )
    assert saved.status_code == 201
    saved_id = saved.json()["id"]
    assert client.get("/api/v1/me/saved-items", headers=headers).json()[0]["label"] == "Rice watch"

    alert = client.post(
        "/api/v1/me/alerts",
        headers=headers,
        json={
            "domain_key": "fuel",
            "label": "Petrol 92 ceiling",
            "metric_label": "Petrol 92",
            "condition": "above",
            "threshold_value": 100,
        },
    )
    assert alert.status_code == 201
    assert alert.json()["enabled"] is True

    pulse = client.get("/api/v1/me/life-pulse", headers=headers)
    assert pulse.status_code == 200
    payload = pulse.json()
    assert payload["profile"]["district"] == "Colombo"
    assert payload["saved_items"][0]["id"] == saved_id
    assert payload["unread_count"] == 1
    assert payload["notifications"][0]["source_domain"] == "fuel"

    notification_id = payload["notifications"][0]["id"]
    read = client.patch(f"/api/v1/me/notifications/{notification_id}", headers=headers, json={"read": True})
    assert read.status_code == 200
    assert read.json()["read_at"] is not None

    delete_saved = client.delete(f"/api/v1/me/saved-items/{saved_id}", headers=headers)
    assert delete_saved.status_code == 204


def test_internal_alert_evaluation_is_token_protected_and_idempotent(client):
    headers = {"Authorization": "Bearer life-test-token"}
    client.get("/api/v1/me/profile", headers=headers)
    client.post(
        "/api/v1/me/alerts",
        headers=headers,
        json={
            "domain_key": "fuel",
            "label": "Fuel watch",
            "metric_label": "Petrol 92",
            "condition": "above",
            "threshold_value": 100,
        },
    )

    forbidden = client.post("/api/v1/internal/alerts/evaluate")
    assert forbidden.status_code in {401, 403}

    internal_headers = {"Authorization": "Bearer internal-test-token"}
    first = client.post("/api/v1/internal/alerts/evaluate", headers=internal_headers)
    assert first.status_code == 200
    assert first.json()["users_checked"] == 1
    assert first.json()["notifications_created"] == 1

    second = client.post("/api/v1/internal/alerts/evaluate", headers=internal_headers)
    assert second.status_code == 200
    assert second.json()["notifications_created"] == 0


def test_internal_source_refresh_runs_validation_pipeline_and_optional_alerts(client):
    headers = {"Authorization": "Bearer life-test-token"}
    client.get("/api/v1/me/profile", headers=headers)
    client.post(
        "/api/v1/me/alerts",
        headers=headers,
        json={
            "domain_key": "fuel",
            "label": "Fuel source refresh watch",
            "metric_label": "Petrol 92",
            "condition": "above",
            "threshold_value": 100,
        },
    )

    forbidden = client.post("/api/v1/internal/source-refresh")
    assert forbidden.status_code in {401, 403}

    internal_headers = {"Authorization": "Bearer internal-test-token"}
    response = client.post("/api/v1/internal/source-refresh?force_refresh=true&evaluate_alerts=true", headers=internal_headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload["refresh_status"] == "healthy"
    assert payload["domains_refreshed"] == 11
    assert payload["source_validation"]["status"] == "healthy"
    assert payload["import_audit"]["status"] == "healthy"
    assert payload["import_plan"]["status"] == "degraded"
    assert {item["key"] for item in payload["import_audit"]["importers"]} == {
        "district-profile-seed-import",
        "official-cost-seed-import",
        "weather-risk-seed-import",
    }
    assert {item["key"] for item in payload["import_plan"]["manifests"]} == {
        "district-profile-direct-import",
        "official-cost-tariff-import",
        "weather-risk-direct-import",
        "public-api-provider-discovery",
    }
    assert payload["pipeline"]["recent_runs"]
    assert payload["alert_evaluation"]["users_checked"] == 1
    assert payload["alert_evaluation"]["notifications_created"] == 1
    assert any("notification" in action.lower() for action in payload["actions"])
    assert any("source-import-plan" in action for action in payload["actions"])


def test_internal_source_import_audit_is_token_protected_and_records_evidence(client):
    forbidden = client.post("/api/v1/internal/source-import-audit")
    assert forbidden.status_code in {401, 403}

    internal_headers = {"Authorization": "Bearer internal-test-token"}
    response = client.post("/api/v1/internal/source-import-audit", headers=internal_headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "healthy"
    importers = {item["key"]: item for item in payload["importers"]}
    assert importers["district-profile-seed-import"]["accepted_for_scoring"] is True
    assert importers["weather-risk-seed-import"]["accepted_for_scoring"] is True
    assert importers["official-cost-seed-import"]["accepted_for_scoring"] is True
    assert importers["official-cost-seed-import"]["storage_target"] == "tariff_snapshots and transport_fare_snapshots"
    assert "sri-lanka-customs-tariff" in importers["official-cost-seed-import"]["source_keys"]
    assert "cbsl-economic-data" in importers["official-cost-seed-import"]["source_keys"]
    official_checks = {check["key"]: check for check in importers["official-cost-seed-import"]["checks"]}
    assert official_checks["source-specific-parser-fixtures"]["status"] == "pass"
    assert any("customs-import-tariff-index" in item for item in official_checks["source-specific-parser-fixtures"]["evidence"])
    assert all(check["status"] == "pass" for item in importers.values() for check in item["checks"])

    pipeline = client.get("/api/v1/life/pipeline")
    assert pipeline.status_code == 200
    recent_runs = pipeline.json()["recent_runs"]
    assert any(run["domain"] == "areas" and run["status"] == "completed" for run in recent_runs)
    assert any(run["domain"] == "weather" and run["status"] == "completed" for run in recent_runs)


def test_internal_source_import_plan_is_token_protected_and_records_readiness(client):
    forbidden = client.post("/api/v1/internal/source-import-plan")
    assert forbidden.status_code in {401, 403}

    internal_headers = {"Authorization": "Bearer internal-test-token"}
    response = client.post("/api/v1/internal/source-import-plan", headers=internal_headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "degraded"
    manifests = {item["key"]: item for item in payload["manifests"]}
    assert manifests["district-profile-direct-import"]["promotion_status"] == "direct_ready"
    assert manifests["district-profile-direct-import"]["accepted_for_direct_run"] is True
    assert manifests["weather-risk-direct-import"]["promotion_status"] == "direct_ready"
    assert manifests["weather-risk-direct-import"]["accepted_for_direct_run"] is True
    assert manifests["official-cost-tariff-import"]["promotion_status"] == "needs_parser"
    assert manifests["official-cost-tariff-import"]["accepted_for_direct_run"] is False
    assert manifests["official-cost-tariff-import"]["status"] == "watch"
    official_manifest_checks = {check["key"]: check for check in manifests["official-cost-tariff-import"]["checks"]}
    assert official_manifest_checks["source-specific-parser-fixtures"]["status"] == "pass"
    assert official_manifest_checks["live-promotion-boundary"]["status"] == "watch"
    assert manifests["public-api-provider-discovery"]["promotion_status"] == "candidate"
    assert "public-apis-catalog" in manifests["public-api-provider-discovery"]["source_keys"]
    assert any(endpoint["source_key"] == "public-lk-admin-regions" for endpoint in manifests["district-profile-direct-import"]["endpoints"])
    assert any(endpoint["source_key"] == "public-lk-irrigation" for endpoint in manifests["weather-risk-direct-import"]["endpoints"])
    assert any(endpoint["source_key"] == "sri-lanka-customs-tariff" for endpoint in manifests["official-cost-tariff-import"]["endpoints"])
    assert any(endpoint["source_key"] == "public-apis-catalog" for endpoint in manifests["public-api-provider-discovery"]["endpoints"])
    assert any(check["status"] == "watch" for item in manifests.values() for check in item["checks"])
    source_keys = {source["key"] for source in payload["sources"]}
    assert {"public-apis-catalog", "public-lk-weather-3h", "public-lk-irrigation", "public-lk-admin-regions", "public-lanka-data", "sri-lanka-customs-tariff"}.issubset(source_keys)

    pipeline = client.get("/api/v1/life/pipeline")
    assert pipeline.status_code == 200
    recent_runs = pipeline.json()["recent_runs"]
    assert any(run["domain"] == "areas" and run["status"] == "completed" for run in recent_runs)
    assert any(run["domain"] == "weather" and run["status"] == "completed" for run in recent_runs)
    assert any(run["domain"] == "indices" and run["status"] == "completed" for run in recent_runs)


def test_internal_source_import_run_is_token_protected_and_records_execution(client):
    forbidden = client.post("/api/v1/internal/source-import-run")
    assert forbidden.status_code in {401, 403}

    internal_headers = {"Authorization": "Bearer internal-test-token"}
    no_persist = client.post("/api/v1/internal/source-import-run?live_fetch=false&persist=false", headers=internal_headers)
    assert no_persist.status_code == 200
    with SessionLocal() as db:
        assert db.scalar(select(func.count()).select_from(SourceImportArtifact)) == 0

    response = client.post("/api/v1/internal/source-import-run?live_fetch=false", headers=internal_headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "degraded"
    runs = {item["key"]: item for item in payload["runs"]}
    run = runs["district-profile-direct-run"]
    assert run["mode"] == "offline_contract"
    assert run["rows_imported"] == 26
    assert run["accepted_for_scoring"] is False
    checks = {check["key"]: check for check in run["checks"]}
    assert checks["typed-row-import"]["status"] == "pass"
    assert checks["coverage"]["status"] == "pass"
    assert checks["seed-reconciliation"]["status"] == "pass"
    assert checks["field-source-boundary"]["status"] == "watch"
    weather_run = runs["weather-risk-direct-run"]
    assert weather_run["mode"] == "offline_contract"
    assert weather_run["rows_imported"] >= len(WEATHER_STATION_ROWS)
    assert weather_run["accepted_for_scoring"] is False
    weather_checks = {check["key"]: check for check in weather_run["checks"]}
    assert weather_checks["typed-station-import"]["status"] == "pass"
    assert weather_checks["seed-reconciliation"]["status"] == "pass"
    assert weather_checks["river-water-context"]["status"] == "pass"
    assert weather_checks["field-source-boundary"]["status"] == "watch"

    pipeline = client.get("/api/v1/life/pipeline")
    assert pipeline.status_code == 200
    recent_runs = pipeline.json()["recent_runs"]
    assert any(run["domain"] == "areas" and run["status"] == "completed" for run in recent_runs)

    with SessionLocal() as db:
        artifacts = db.scalars(select(SourceImportArtifact).order_by(SourceImportArtifact.run_key)).all()
        assert db.scalar(select(func.count()).select_from(DistrictProfileSnapshot)) == 0
        assert db.scalar(select(func.count()).select_from(WeatherRiskSnapshot)) == 0
        assert db.scalar(select(func.count()).select_from(SourceDataRelease)) == 0
    assert len(artifacts) == 2
    artifacts_by_key = {artifact.run_key: artifact for artifact in artifacts}
    district_artifact = artifacts_by_key["district-profile-direct-run"]
    assert district_artifact.mode == "offline_contract"
    assert district_artifact.rows_imported == 26
    assert len(district_artifact.normalized_records) == 26
    assert district_artifact.normalized_records[0]["record_type"] == "district_profile"
    assert district_artifact.payload_summary["raw_payload_stored"] is False
    assert district_artifact.payload_summary["normalized_record_count"] == 26
    weather_artifact = artifacts_by_key["weather-risk-direct-run"]
    assert weather_artifact.rows_imported >= len(WEATHER_STATION_ROWS)
    assert {record["record_type"] for record in weather_artifact.normalized_records} == {"weather_station", "irrigation_water_level"}
    assert weather_artifact.payload_summary["raw_payload_stored"] is False
    assert len(str(weather_artifact.normalized_records)) < 50000

    artifact_forbidden = client.get("/api/v1/internal/source-import-artifacts")
    assert artifact_forbidden.status_code in {401, 403}

    artifact_response = client.get("/api/v1/internal/source-import-artifacts", headers=internal_headers)
    assert artifact_response.status_code == 200
    artifact_payload = artifact_response.json()
    assert len(artifact_payload["artifacts"]) == 2
    assert all(item["normalized_records"] == [] for item in artifact_payload["artifacts"])
    assert {item["run_key"] for item in artifact_payload["artifacts"]} == {
        "district-profile-direct-run",
        "weather-risk-direct-run",
    }

    district_detail = client.get(
        "/api/v1/internal/source-import-artifacts?run_key=district-profile-direct-run&include_records=true",
        headers=internal_headers,
    )
    assert district_detail.status_code == 200
    district_detail_payload = district_detail.json()
    assert len(district_detail_payload["artifacts"]) == 1
    assert district_detail_payload["artifacts"][0]["normalized_record_count"] == 26
    assert len(district_detail_payload["artifacts"][0]["normalized_records"]) == 26


def test_official_cost_source_import_run_is_review_only(client):
    internal_headers = {"Authorization": "Bearer internal-test-token"}
    response = client.post(
        "/api/v1/internal/source-import-run?live_fetch=false&include_official_cost=true",
        headers=internal_headers,
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "degraded"
    runs = {item["key"]: item for item in payload["runs"]}
    official_run = runs["official-cost-direct-run"]
    assert official_run["mode"] == "offline_contract"
    assert official_run["accepted_for_scoring"] is False
    assert official_run["rows_imported"] == 6
    assert "sri-lanka-customs-tariff" in official_run["source_keys"]
    official_checks = {check["key"]: check for check in official_run["checks"]}
    assert official_checks["source-specific-parser-evidence"]["status"] == "pass"
    assert official_checks["promotion-boundary"]["status"] == "watch"

    blocked_promotion = client.post(
        "/api/v1/internal/source-import-run?live_fetch=true&promote=true&include_official_cost=true",
        headers=internal_headers,
    )
    assert blocked_promotion.status_code == 400

    artifact_response = client.get(
        "/api/v1/internal/source-import-artifacts?run_key=official-cost-direct-run&include_records=true",
        headers=internal_headers,
    )
    assert artifact_response.status_code == 200
    artifacts = artifact_response.json()["artifacts"]
    assert len(artifacts) == 1
    assert artifacts[0]["accepted_for_scoring"] is False
    assert artifacts[0]["normalized_record_count"] == 6
    assert {record["record_type"] for record in artifacts[0]["normalized_records"]} == {"official_cost_parser_evidence"}
    assert any(record["source_key"] == "sri-lanka-customs-tariff" for record in artifacts[0]["normalized_records"])


def test_internal_source_import_run_promotes_live_direct_snapshots(client, monkeypatch):
    district_records = []
    for row in DISTRICT_PROFILE_ROWS:
        record = {"record_type": "district_profile", **row}
        if record["key"] == "Kandy":
            record["population"] = record["population"] + 123
        district_records.append(record)
    weather_records = []
    for row in WEATHER_STATION_ROWS:
        record = {"record_type": "weather_station", **row}
        record["observed_at"] = row["observed_at"].isoformat() if hasattr(row["observed_at"], "isoformat") else row["observed_at"]
        if record["station_name"] == "Ratnapura":
            record["rainfall_mm"] = 33.3
        weather_records.append(record)

    async def fake_execution_report(*, live_fetch: bool = False, include_official_cost: bool = False):
        assert live_fetch is True
        assert include_official_cost is False
        check = SourceImportCheck(key="field-source-boundary", label="Field source boundary", status="pass", message="Direct lineage pass.", evidence=[])
        return SourceImportExecutionResponse(
            generated_at=utc_now(),
            status="healthy",
            summary="Direct import execution passed and is ready for promotion review.",
            runs=[
                SourceImportExecutionRun(
                    key="district-profile-direct-run",
                    label="District profile direct import run",
                    domain_key="areas",
                    status="pass",
                    mode="live_fetch",
                    rows_imported=26,
                    accepted_for_scoring=True,
                    source_keys=["dcs-census-2024", "public-lk-census-2024-extracts", "public-lk-admin-regions", "public-lanka-data"],
                    fetched_urls=["https://example.test/district.json"],
                    storage_target="DistrictProfile response rows and area_score_snapshots after promotion review",
                    action="Ready.",
                    normalized_records=district_records,
                    checks=[check],
                ),
                SourceImportExecutionRun(
                    key="weather-risk-direct-run",
                    label="Weather and risk direct import run",
                    domain_key="weather",
                    status="pass",
                    mode="live_fetch",
                    rows_imported=len(weather_records),
                    accepted_for_scoring=True,
                    source_keys=["meteo-lk-3h", "public-lk-weather-3h", "dmc-lk", "public-lk-rivers", "public-lk-irrigation"],
                    fetched_urls=["https://example.test/weather.json"],
                    storage_target="WeatherRiskObservation response rows and weather component scores after promotion review",
                    action="Ready.",
                    normalized_records=weather_records,
                    checks=[check],
                ),
            ],
            sources=[],
        )

    monkeypatch.setattr("app.services.source_imports.source_import_execution_report", fake_execution_report)
    internal_headers = {"Authorization": "Bearer internal-test-token"}
    offline_promotion = client.post("/api/v1/internal/source-import-run?live_fetch=false&promote=true", headers=internal_headers)
    assert offline_promotion.status_code == 400

    response = client.post("/api/v1/internal/source-import-run?live_fetch=true&promote=true", headers=internal_headers)
    assert response.status_code == 200
    payload = response.json()
    promoted_count = len(DISTRICTS) * 3
    assert payload["status"] == "healthy"
    assert {run["promoted_records"] for run in payload["runs"]} == {promoted_count}
    assert all("Promoted" in run["promotion_note"] and "release direct-source-" in run["promotion_note"] for run in payload["runs"])

    with SessionLocal() as db:
        snapshot_count = db.scalar(select(func.count()).select_from(AreaScoreSnapshot))
        district_snapshot_count = db.scalar(select(func.count()).select_from(DistrictProfileSnapshot))
        weather_snapshot_count = db.scalar(select(func.count()).select_from(WeatherRiskSnapshot))
        releases = db.scalars(select(SourceDataRelease)).all()
    assert snapshot_count == promoted_count
    assert district_snapshot_count == len(DISTRICT_PROFILE_ROWS)
    assert weather_snapshot_count == len(WEATHER_STATION_ROWS)
    assert len(releases) == 1
    assert releases[0].district_profile_snapshot_count == len(DISTRICT_PROFILE_ROWS)
    assert releases[0].weather_risk_snapshot_count == len(WEATHER_STATION_ROWS)
    assert releases[0].area_score_snapshot_count == promoted_count
    assert releases[0].status == "promoted"

    releases_forbidden = client.get("/api/v1/internal/source-data-releases")
    assert releases_forbidden.status_code in {401, 403}
    releases_response = client.get("/api/v1/internal/source-data-releases", headers=internal_headers)
    assert releases_response.status_code == 200
    releases_payload = releases_response.json()
    assert len(releases_payload["releases"]) == 1
    assert releases_payload["releases"][0]["district_profile_snapshot_count"] == len(DISTRICT_PROFILE_ROWS)
    assert releases_payload["releases"][0]["area_score_snapshot_count"] == promoted_count

    public_release = client.get("/api/v1/life/source-release")
    assert public_release.status_code == 200
    public_payload = public_release.json()
    assert public_payload["status"] == "promoted"
    assert public_payload["active_release_key"].startswith("direct-source-")
    assert public_payload["observed_at"] is not None
    assert public_payload["district_profile_snapshot_count"] == len(DISTRICT_PROFILE_ROWS)
    assert public_payload["weather_risk_snapshot_count"] == len(WEATHER_STATION_ROWS)
    assert public_payload["area_score_snapshot_count"] == promoted_count
    assert {
        "dcs-census-2024",
        "public-lk-census-2024-extracts",
        "public-lk-admin-regions",
        "public-lanka-data",
        "public-lk-weather-3h",
        "public-lk-irrigation",
    }.issubset(set(public_payload["source_keys"]))
    assert "source_import_artifact_ids" not in public_payload
    assert "checks" not in public_payload
    assert "operator_notes" not in public_payload

    atlas = client.get("/api/v1/life/atlas?district=Kandy")
    assert atlas.status_code == 200
    assert atlas.json()["selected_profile"]["population"] == 1462018

    weather = client.get("/api/v1/life/weather-risk?district=Ratnapura")
    assert weather.status_code == 200
    assert weather.json()["selected"]["rainfall_mm"] == 33.3


def test_source_data_release_lifecycle_supersedes_and_rolls_back(client, monkeypatch):
    base_time = utc_now()
    kandy_population = next(row["population"] for row in DISTRICT_PROFILE_ROWS if row["key"] == "Kandy")

    def execution_for(version: int, *, rainfall: float) -> SourceImportExecutionResponse:
        generated_at = base_time + timedelta(minutes=version)
        district_records = []
        for row in DISTRICT_PROFILE_ROWS:
            record = {"record_type": "district_profile", **row}
            if record["key"] == "Kandy":
                record["population"] = kandy_population + (version * 100)
            district_records.append(record)
        weather_records = []
        for row in WEATHER_STATION_ROWS:
            record = {"record_type": "weather_station", **row}
            record["observed_at"] = row["observed_at"].isoformat() if hasattr(row["observed_at"], "isoformat") else row["observed_at"]
            if record["station_name"] == "Ratnapura":
                record["rainfall_mm"] = rainfall
            weather_records.append(record)
        check = SourceImportCheck(key="field-source-boundary", label="Field source boundary", status="pass", message="Direct lineage pass.", evidence=[])
        return SourceImportExecutionResponse(
            generated_at=generated_at,
            status="healthy",
            summary=f"Direct import execution v{version} passed and is ready for promotion review.",
            runs=[
                SourceImportExecutionRun(
                    key="district-profile-direct-run",
                    label="District profile direct import run",
                    domain_key="areas",
                    status="pass",
                    mode="live_fetch",
                    rows_imported=26,
                    accepted_for_scoring=True,
                    source_keys=["dcs-census-2024", "public-lk-census-2024-extracts", "public-lk-admin-regions", "public-lanka-data"],
                    fetched_urls=[f"https://example.test/district-v{version}.json"],
                    storage_target="DistrictProfile response rows and area_score_snapshots after promotion review",
                    action="Ready.",
                    normalized_records=district_records,
                    checks=[check],
                ),
                SourceImportExecutionRun(
                    key="weather-risk-direct-run",
                    label="Weather and risk direct import run",
                    domain_key="weather",
                    status="pass",
                    mode="live_fetch",
                    rows_imported=len(weather_records),
                    accepted_for_scoring=True,
                    source_keys=["meteo-lk-3h", "public-lk-weather-3h", "dmc-lk", "public-lk-rivers", "public-lk-irrigation"],
                    fetched_urls=[f"https://example.test/weather-v{version}.json"],
                    storage_target="WeatherRiskObservation response rows and weather component scores after promotion review",
                    action="Ready.",
                    normalized_records=weather_records,
                    checks=[check],
                ),
            ],
            sources=[],
        )

    executions = [execution_for(1, rainfall=22.2), execution_for(2, rainfall=44.4)]

    async def fake_execution_report(*, live_fetch: bool = False, include_official_cost: bool = False):
        assert live_fetch is True
        assert include_official_cost is False
        return executions.pop(0)

    monkeypatch.setattr("app.services.source_imports.source_import_execution_report", fake_execution_report)
    internal_headers = {"Authorization": "Bearer internal-test-token"}

    first_promotion = client.post("/api/v1/internal/source-import-run?live_fetch=true&promote=true", headers=internal_headers)
    assert first_promotion.status_code == 200
    first_releases = client.get("/api/v1/internal/source-data-releases", headers=internal_headers).json()
    first_key = first_releases["active_release_key"]
    assert first_key is not None

    second_promotion = client.post("/api/v1/internal/source-import-run?live_fetch=true&promote=true", headers=internal_headers)
    assert second_promotion.status_code == 200
    second_releases = client.get("/api/v1/internal/source-data-releases", headers=internal_headers).json()
    second_key = second_releases["active_release_key"]
    release_by_key = {release["release_key"]: release for release in second_releases["releases"]}
    assert second_key is not None and second_key != first_key
    assert release_by_key[second_key]["status"] == "promoted"
    assert release_by_key[second_key]["payload_summary"]["superseded_release_count"] == 1
    assert release_by_key[first_key]["status"] == "superseded"
    assert release_by_key[first_key]["superseded_by_release_key"] == second_key

    atlas_before_rollback = client.get("/api/v1/life/atlas?district=Kandy")
    assert atlas_before_rollback.status_code == 200
    assert atlas_before_rollback.json()["selected_profile"]["population"] == kandy_population + 200

    note_response = client.post(
        f"/api/v1/internal/source-data-releases/{second_key}/notes",
        headers=internal_headers,
        json={"note": "Operator reviewed the second direct-import batch."},
    )
    assert note_response.status_code == 200
    assert note_response.json()["release"]["operator_notes"][-1]["action"] == "note"

    rollback_forbidden = client.post(f"/api/v1/internal/source-data-releases/{second_key}/rollback")
    assert rollback_forbidden.status_code in {401, 403}

    rollback_response = client.post(
        f"/api/v1/internal/source-data-releases/{second_key}/rollback",
        headers=internal_headers,
        json={"note": "Weather row outlier review failed; restore previous promoted batch.", "reactivate_previous": True},
    )
    assert rollback_response.status_code == 200
    rollback_payload = rollback_response.json()
    assert rollback_payload["active_release_key"] == first_key
    assert rollback_payload["release"]["status"] == "rolled_back"
    assert rollback_payload["reactivated_release"]["release_key"] == first_key
    assert rollback_payload["reactivated_release"]["status"] == "promoted"

    releases_after_rollback = client.get("/api/v1/internal/source-data-releases", headers=internal_headers).json()
    release_by_key = {release["release_key"]: release for release in releases_after_rollback["releases"]}
    assert releases_after_rollback["active_release_key"] == first_key
    assert release_by_key[second_key]["status"] == "rolled_back"
    assert release_by_key[first_key]["status"] == "promoted"

    atlas_after_rollback = client.get("/api/v1/life/atlas?district=Kandy")
    assert atlas_after_rollback.status_code == 200
    assert atlas_after_rollback.json()["selected_profile"]["population"] == kandy_population + 100

    weather_after_rollback = client.get("/api/v1/life/weather-risk?district=Ratnapura")
    assert weather_after_rollback.status_code == 200
    assert weather_after_rollback.json()["selected"]["rainfall_mm"] == 22.2
