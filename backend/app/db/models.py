from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Domain(Base):
    __tablename__ = "domains"

    key: Mapped[str] = mapped_column(String(32), primary_key=True)
    label: Mapped[str] = mapped_column(String(80))
    category: Mapped[str] = mapped_column(String(64), index=True)
    api_base: Mapped[str] = mapped_column(String(512))
    homepage_url: Mapped[str] = mapped_column(String(512))
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    snapshots: Mapped[list["DomainSnapshot"]] = relationship(back_populates="domain")
    runs: Mapped[list["IntegrationRun"]] = relationship(back_populates="domain")


class DomainSnapshot(Base):
    __tablename__ = "domain_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    domain_key: Mapped[str] = mapped_column(ForeignKey("domains.key"), index=True)
    status: Mapped[str] = mapped_column(String(32), index=True)
    health_score: Mapped[float] = mapped_column(Float, default=0)
    summary: Mapped[dict] = mapped_column(JSON, default=dict)
    metrics: Mapped[list] = mapped_column(JSON, default=list)
    highlights: Mapped[list] = mapped_column(JSON, default=list)
    source_updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True)

    domain: Mapped[Domain] = relationship(back_populates="snapshots")


class LifeIndexSnapshot(Base):
    __tablename__ = "life_index_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    profile: Mapped[str] = mapped_column(String(32), index=True)
    district: Mapped[str] = mapped_column(String(128), index=True)
    total_lkr: Mapped[float] = mapped_column(Float)
    confidence: Mapped[str] = mapped_column(String(32))
    breakdown: Mapped[dict] = mapped_column(JSON, default=dict)
    assumptions: Mapped[list] = mapped_column(JSON, default=list)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True)


class IntegrationRun(Base):
    __tablename__ = "integration_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    domain_key: Mapped[str] = mapped_column(ForeignKey("domains.key"), index=True)
    status: Mapped[str] = mapped_column(String(32), index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    http_status: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    payload_summary: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    domain: Mapped[Domain] = relationship(back_populates="runs")


class SourceImportArtifact(Base):
    __tablename__ = "source_import_artifacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_key: Mapped[str] = mapped_column(String(120), index=True)
    domain_key: Mapped[str] = mapped_column(ForeignKey("domains.key"), index=True)
    status: Mapped[str] = mapped_column(String(32), index=True)
    mode: Mapped[str] = mapped_column(String(32), index=True)
    accepted_for_scoring: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    rows_imported: Mapped[int] = mapped_column(Integer, default=0)
    source_keys: Mapped[list] = mapped_column(JSON, default=list)
    checks: Mapped[list] = mapped_column(JSON, default=list)
    normalized_records: Mapped[list] = mapped_column(JSON, default=list)
    payload_summary: Mapped[dict] = mapped_column(JSON, default=dict)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True)


class DistrictProfileSnapshot(Base):
    __tablename__ = "district_profile_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_artifact_id: Mapped[int | None] = mapped_column(ForeignKey("source_import_artifacts.id"), nullable=True, index=True)
    run_key: Mapped[str] = mapped_column(String(120), index=True)
    district: Mapped[str] = mapped_column(String(128), index=True)
    region_id: Mapped[str] = mapped_column(String(16), index=True)
    province: Mapped[str] = mapped_column(String(80), index=True)
    population: Mapped[int] = mapped_column(Integer)
    households: Mapped[int] = mapped_column(Integer)
    area_sqkm: Mapped[float] = mapped_column(Float)
    center_lat: Mapped[float] = mapped_column(Float)
    center_lng: Mapped[float] = mapped_column(Float)
    cooking_gas_share: Mapped[float] = mapped_column(Float)
    elderly_share: Mapped[float] = mapped_column(Float)
    confidence: Mapped[str] = mapped_column(String(32), default="high")
    source_keys: Mapped[list] = mapped_column(JSON, default=list)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True)


class WeatherRiskSnapshot(Base):
    __tablename__ = "weather_risk_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_artifact_id: Mapped[int | None] = mapped_column(ForeignKey("source_import_artifacts.id"), nullable=True, index=True)
    run_key: Mapped[str] = mapped_column(String(120), index=True)
    record_type: Mapped[str] = mapped_column(String(64), index=True)
    station_id: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    station_name: Mapped[str] = mapped_column(String(120), index=True)
    source_observed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    rainfall_mm: Mapped[float | None] = mapped_column(Float, nullable=True)
    temperature_c: Mapped[float | None] = mapped_column(Float, nullable=True)
    humidity_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    water_level_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    source_keys: Mapped[list] = mapped_column(JSON, default=list)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True)


class SourceDataRelease(Base):
    __tablename__ = "source_data_releases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    release_key: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    status: Mapped[str] = mapped_column(String(32), default="promoted", index=True)
    source_import_artifact_ids: Mapped[list] = mapped_column(JSON, default=list)
    run_keys: Mapped[list] = mapped_column(JSON, default=list)
    source_keys: Mapped[list] = mapped_column(JSON, default=list)
    checks: Mapped[list] = mapped_column(JSON, default=list)
    district_profile_snapshot_count: Mapped[int] = mapped_column(Integer, default=0)
    weather_risk_snapshot_count: Mapped[int] = mapped_column(Integer, default=0)
    area_score_snapshot_count: Mapped[int] = mapped_column(Integer, default=0)
    payload_summary: Mapped[dict] = mapped_column(JSON, default=dict)
    operator_notes: Mapped[list] = mapped_column(JSON, default=list)
    superseded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    superseded_by_release_key: Mapped[str | None] = mapped_column(String(160), nullable=True, index=True)
    rolled_back_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True)


class SourceRegistry(Base):
    __tablename__ = "source_registry"

    key: Mapped[str] = mapped_column(String(80), primary_key=True)
    label: Mapped[str] = mapped_column(String(160))
    source_type: Mapped[str] = mapped_column(String(32), index=True)
    domain_key: Mapped[str | None] = mapped_column(String(32), index=True, nullable=True)
    url: Mapped[str] = mapped_column(String(512))
    confidence: Mapped[str] = mapped_column(String(32), default="medium")
    freshness_note: Mapped[str] = mapped_column(Text)
    owner: Mapped[str] = mapped_column(String(160), default="Unknown")
    collection_method: Mapped[str] = mapped_column(String(80), default="manual_review")
    license_status: Mapped[str] = mapped_column(String(80), default="needs_review")
    review_status: Mapped[str] = mapped_column(String(80), default="needs_review")
    refresh_cadence: Mapped[str] = mapped_column(String(160), default="scheduled or manual refresh")
    governance_note: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(32), default="healthy", index=True)
    locale_labels: Mapped[dict] = mapped_column(JSON, default=dict)
    last_checked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class TariffSnapshot(Base):
    __tablename__ = "tariff_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    domain_key: Mapped[str] = mapped_column(String(32), index=True)
    source_key: Mapped[str] = mapped_column(ForeignKey("source_registry.key"), index=True)
    district: Mapped[str] = mapped_column(String(128), index=True)
    category: Mapped[str] = mapped_column(String(128), index=True)
    amount_lkr: Mapped[float] = mapped_column(Float)
    unit: Mapped[str] = mapped_column(String(64))
    confidence: Mapped[str] = mapped_column(String(32))
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True)


class RetailOfferSnapshot(Base):
    __tablename__ = "retail_offer_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_key: Mapped[str] = mapped_column(ForeignKey("source_registry.key"), index=True)
    item_name: Mapped[str] = mapped_column(String(160), index=True)
    retailer: Mapped[str] = mapped_column(String(120), index=True)
    district: Mapped[str] = mapped_column(String(128), index=True)
    price_lkr: Mapped[float] = mapped_column(Float)
    unit: Mapped[str] = mapped_column(String(64))
    confidence: Mapped[str] = mapped_column(String(32))
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True)


class TransportFareSnapshot(Base):
    __tablename__ = "transport_fare_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_key: Mapped[str] = mapped_column(ForeignKey("source_registry.key"), index=True)
    mode: Mapped[str] = mapped_column(String(64), index=True)
    from_area: Mapped[str] = mapped_column(String(128), index=True)
    to_area: Mapped[str] = mapped_column(String(128), index=True)
    fare_lkr: Mapped[float] = mapped_column(Float)
    confidence: Mapped[str] = mapped_column(String(32))
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True)


class AreaScoreSnapshot(Base):
    __tablename__ = "area_score_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    district: Mapped[str] = mapped_column(String(128), index=True)
    profile: Mapped[str] = mapped_column(String(32), index=True)
    score: Mapped[float] = mapped_column(Float)
    grade: Mapped[str] = mapped_column(String(8))
    confidence: Mapped[str] = mapped_column(String(32))
    components: Mapped[list] = mapped_column(JSON, default=list)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True)


class PublicInsightSnapshot(Base):
    __tablename__ = "public_insight_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    insight_key: Mapped[str] = mapped_column(String(120), index=True)
    domain_key: Mapped[str] = mapped_column(String(32), index=True)
    title: Mapped[str] = mapped_column(String(180))
    severity: Mapped[str] = mapped_column(String(32), index=True)
    message: Mapped[str] = mapped_column(Text)
    confidence: Mapped[str] = mapped_column(String(32))
    source_keys: Mapped[list] = mapped_column(JSON, default=list)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True)


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    auth_sub: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    display_name: Mapped[str | None] = mapped_column(String(160), nullable=True)
    photo_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    default_locale: Mapped[str] = mapped_column(String(8), default="en")
    district: Mapped[str] = mapped_column(String(128), default="Sri Lanka")
    profile: Mapped[str] = mapped_column(String(32), default="family")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class SavedItem(Base):
    __tablename__ = "saved_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    auth_sub: Mapped[str] = mapped_column(String(160), index=True)
    domain_key: Mapped[str] = mapped_column(String(32), index=True)
    label: Mapped[str] = mapped_column(String(180))
    query: Mapped[str | None] = mapped_column(String(160), nullable=True)
    href: Mapped[str | None] = mapped_column(String(512), nullable=True)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True)


class AlertRule(Base):
    __tablename__ = "alert_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    auth_sub: Mapped[str] = mapped_column(String(160), index=True)
    domain_key: Mapped[str | None] = mapped_column(String(32), index=True, nullable=True)
    label: Mapped[str] = mapped_column(String(180))
    metric_label: Mapped[str | None] = mapped_column(String(120), nullable=True)
    condition: Mapped[str] = mapped_column(String(40), index=True)
    threshold_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    last_triggered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Notification(Base):
    __tablename__ = "notifications"
    __table_args__ = (UniqueConstraint("auth_sub", "idempotency_key", name="uq_notifications_auth_idempotency"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    auth_sub: Mapped[str] = mapped_column(String(160), index=True)
    alert_rule_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(180))
    message: Mapped[str] = mapped_column(Text)
    severity: Mapped[str] = mapped_column(String(32), default="neutral", index=True)
    source_domain: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)
    idempotency_key: Mapped[str] = mapped_column(String(240))
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True)
