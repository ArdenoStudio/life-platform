from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

DomainKey = Literal["food", "fuel", "property", "vehicle", "utilities", "gas", "transport", "retail", "indices", "areas", "weather"]
SourceStatus = Literal["healthy", "degraded", "offline"]
SourceType = Literal["official", "retail", "platform", "derived"]
Confidence = Literal["high", "medium", "low"]
LocaleCode = Literal["en", "si", "ta"]


class SourceReference(BaseModel):
    key: str
    label: str
    source_type: SourceType
    url: str
    confidence: Confidence
    freshness_note: str
    owner: str
    collection_method: str
    license_status: Literal["official_public", "permissive", "terms_review", "internal_platform", "needs_review"]
    review_status: Literal["approved", "reviewed", "candidate", "needs_review"]
    refresh_cadence: str
    governance_note: str
    last_checked_at: datetime | None = None
    labels: dict[str, str] = Field(default_factory=dict)


class SourceValidationCheck(BaseModel):
    key: str
    label: str
    status: Literal["pass", "watch", "fail"]
    message: str
    evidence: list[str] = Field(default_factory=list)
    source_keys: list[str] = Field(default_factory=list)


class SourceValidationResponse(BaseModel):
    generated_at: datetime
    status: SourceStatus
    summary: str
    checks: list[SourceValidationCheck]
    sources: list[SourceReference]


class SourceImportCheck(BaseModel):
    key: str
    label: str
    status: Literal["pass", "watch", "fail"]
    message: str
    evidence: list[str] = Field(default_factory=list)


class SourceImportRun(BaseModel):
    key: str
    label: str
    domain_key: DomainKey
    status: Literal["pass", "watch", "fail"]
    rows_checked: int
    accepted_for_scoring: bool
    source_keys: list[str]
    storage_target: str
    collection_method: str
    action: str
    checks: list[SourceImportCheck]


class SourceImportAuditResponse(BaseModel):
    generated_at: datetime
    status: SourceStatus
    summary: str
    importers: list[SourceImportRun]
    sources: list[SourceReference]


class SourceImportEndpoint(BaseModel):
    key: str
    label: str
    source_key: str | None = None
    url: str
    method: str
    required: bool = True
    status: Literal["ready", "watch", "blocked"]
    note: str


class SourceImportManifest(BaseModel):
    key: str
    label: str
    domain_key: DomainKey
    status: Literal["pass", "watch", "fail"]
    promotion_status: Literal["seed_audited", "direct_ready", "needs_parser", "blocked_by_terms", "candidate"]
    accepted_for_direct_run: bool
    source_keys: list[str]
    retrieval_mode: str
    parser_contract: str
    storage_target: str
    refresh_cadence: str
    next_action: str
    endpoints: list[SourceImportEndpoint]
    checks: list[SourceImportCheck]


class SourceImportPlanResponse(BaseModel):
    generated_at: datetime
    status: SourceStatus
    summary: str
    manifests: list[SourceImportManifest]
    sources: list[SourceReference]


class SourceImportExecutionRun(BaseModel):
    key: str
    label: str
    domain_key: DomainKey
    status: Literal["pass", "watch", "fail"]
    mode: Literal["offline_contract", "live_fetch"]
    rows_imported: int
    accepted_for_scoring: bool
    source_keys: list[str]
    fetched_urls: list[str]
    storage_target: str
    action: str
    normalized_records: list[dict[str, Any]] = Field(default_factory=list)
    promoted_records: int = 0
    promotion_note: str | None = None
    checks: list[SourceImportCheck]


class SourceImportExecutionResponse(BaseModel):
    generated_at: datetime
    status: SourceStatus
    summary: str
    runs: list[SourceImportExecutionRun]
    sources: list[SourceReference]


class SourceImportArtifactSummary(BaseModel):
    id: int
    run_key: str
    domain_key: DomainKey
    status: Literal["pass", "watch", "fail"]
    mode: Literal["offline_contract", "live_fetch"]
    accepted_for_scoring: bool
    rows_imported: int
    source_keys: list[str]
    checks: list[SourceImportCheck]
    normalized_record_count: int
    normalized_records: list[dict[str, Any]] = Field(default_factory=list)
    payload_summary: dict[str, Any]
    observed_at: datetime
    created_at: datetime


class SourceImportArtifactsResponse(BaseModel):
    generated_at: datetime
    artifacts: list[SourceImportArtifactSummary]


class SourceDataReleaseSummary(BaseModel):
    id: int
    release_key: str
    status: Literal["promoted", "superseded", "rolled_back", "failed"]
    source_import_artifact_ids: list[int]
    run_keys: list[str]
    source_keys: list[str]
    checks: list[SourceImportCheck]
    district_profile_snapshot_count: int
    weather_risk_snapshot_count: int
    area_score_snapshot_count: int
    payload_summary: dict[str, Any]
    operator_notes: list[dict[str, Any]] = Field(default_factory=list)
    superseded_at: datetime | None = None
    superseded_by_release_key: str | None = None
    rolled_back_at: datetime | None = None
    observed_at: datetime
    created_at: datetime


class SourceDataReleasesResponse(BaseModel):
    generated_at: datetime
    active_release_key: str | None = None
    releases: list[SourceDataReleaseSummary]


class SourceDataReleaseActionRequest(BaseModel):
    note: str | None = Field(default=None, max_length=500)
    reactivate_previous: bool = True


class SourceDataReleaseActionResponse(BaseModel):
    generated_at: datetime
    action: Literal["rollback", "note"]
    message: str
    active_release_key: str | None = None
    release: SourceDataReleaseSummary
    reactivated_release: SourceDataReleaseSummary | None = None


class PublicSourceReleaseResponse(BaseModel):
    generated_at: datetime
    status: Literal["promoted", "seed_fallback"]
    active_release_key: str | None = None
    observed_at: datetime | None = None
    source_keys: list[str] = Field(default_factory=list)
    district_profile_snapshot_count: int = 0
    weather_risk_snapshot_count: int = 0
    area_score_snapshot_count: int = 0
    note: str


class DomainMetric(BaseModel):
    label: str
    value: float | int | str | None
    unit: str | None = None
    change: float | None = None
    trend: Literal["up", "down", "flat", "unknown"] = "unknown"
    description: str | None = None


class DomainHighlight(BaseModel):
    label: str
    value: str
    severity: Literal["good", "watch", "risk", "neutral"] = "neutral"
    href: str | None = None


class DomainSignal(BaseModel):
    key: DomainKey
    label: str
    category: str
    status: SourceStatus
    health_score: float = Field(ge=0, le=100)
    summary: str
    api_base: str
    source_url: str
    homepage_url: str
    last_updated_at: datetime | None = None
    observed_at: datetime
    freshness_note: str
    metrics: list[DomainMetric] = Field(default_factory=list)
    highlights: list[DomainHighlight] = Field(default_factory=list)
    top_items: list[dict] = Field(default_factory=list)
    sources: list[SourceReference] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)


class AffordabilityBreakdownItem(BaseModel):
    key: str
    label: str
    monthly_lkr: float
    confidence: Confidence
    source_domains: list[str]
    note: str


class AffordabilityResponse(BaseModel):
    district: str
    profile: Literal["single", "family", "commuter"]
    total_monthly_lkr: float
    confidence: Confidence
    generated_at: datetime
    breakdown: list[AffordabilityBreakdownItem]
    assumptions: list[str]


class LifeOverviewResponse(BaseModel):
    generated_at: datetime
    headline: str
    freshness_note: str
    domains: list[DomainSignal]
    affordability: AffordabilityResponse
    top_movers: list[DomainHighlight]
    source_health: dict[str, int | float]


class SearchResult(BaseModel):
    domain: str
    label: str
    description: str
    href: str | None = None
    score: int


class PipelineDomainStatus(BaseModel):
    domain: str
    label: str
    status: str
    health_score: float
    last_updated_at: datetime | None
    freshness_note: str
    errors: list[str]


class PipelineResponse(BaseModel):
    generated_at: datetime
    overall_status: SourceStatus
    domains: list[PipelineDomainStatus]
    recent_runs: list[dict]


class CostCommandItem(BaseModel):
    key: str
    label: str
    monthly_lkr: float
    weekly_lkr: float
    confidence: Confidence
    source_type: SourceType
    source_keys: list[str]
    note: str


class CostCommandResponse(BaseModel):
    generated_at: datetime
    locale: LocaleCode
    district: str
    profile: Literal["single", "family", "commuter"]
    total_monthly_lkr: float
    daily_lkr: float
    items: list[CostCommandItem]
    savings_moves: list[DomainHighlight]
    sources: list[SourceReference]
    assumptions: list[str]


class AreaScoreComponent(BaseModel):
    key: str
    label: str
    score: float = Field(ge=0, le=100)
    value: str
    weight: float
    confidence: Confidence
    source_keys: list[str] = Field(default_factory=list)
    note: str | None = None


class DistrictProfile(BaseModel):
    key: str
    region_id: str
    province: str
    population: int
    households: int
    area_sqkm: float
    density_per_sqkm: float
    center_lat: float
    center_lng: float
    cooking_gas_share: float
    elderly_share: float
    confidence: Confidence
    source_keys: list[str]
    note: str


class AreaScoreResponse(BaseModel):
    generated_at: datetime
    district: str
    profile: Literal["single", "family", "commuter"]
    score: float = Field(ge=0, le=100)
    grade: str
    confidence: Confidence
    components: list[AreaScoreComponent]
    district_profile: DistrictProfile | None = None
    sources: list[SourceReference]


class AtlasResponse(BaseModel):
    generated_at: datetime
    locale: LocaleCode
    district: str
    profile: Literal["single", "family", "commuter"]
    national_score: float
    selected: AreaScoreResponse
    district_scores: list[AreaScoreResponse]
    heatmap: list[dict]
    narrative: str
    selected_profile: DistrictProfile | None = None
    district_profiles: list[DistrictProfile] = Field(default_factory=list)
    methodology: list[str] = Field(default_factory=list)
    sources: list[SourceReference]


class UtilityItem(BaseModel):
    key: str
    label: str
    amount_lkr: float
    unit: str
    source_key: str
    confidence: Confidence
    note: str


class UtilitiesResponse(BaseModel):
    generated_at: datetime
    district: str
    electricity: list[UtilityItem]
    water: list[UtilityItem]
    gas: list[UtilityItem]
    sources: list[SourceReference]


class TransportOption(BaseModel):
    mode: str
    from_area: str
    to_area: str
    fare_lkr: float
    confidence: Confidence
    source_key: str
    note: str


class TransportResponse(BaseModel):
    generated_at: datetime
    from_area: str
    to_area: str
    options: list[TransportOption]
    sources: list[SourceReference]


class RetailOffer(BaseModel):
    item_name: str
    retailer: str
    district: str
    price_lkr: float
    unit: str
    source_key: str
    source_type: SourceType = "retail"
    confidence: Confidence
    note: str


class WeatherRiskObservation(BaseModel):
    district: str
    station_id: str
    station_name: str
    observed_at: datetime
    rainfall_mm: float
    temperature_c: float
    humidity_percent: float
    risk_score: float = Field(ge=0, le=100)
    severity: Literal["good", "watch", "risk", "neutral"]
    coverage: Literal["direct", "proxy", "national"]
    confidence: Confidence
    source_keys: list[str]
    note: str


class WeatherRiskResponse(BaseModel):
    generated_at: datetime
    district: str
    selected: WeatherRiskObservation
    observations: list[WeatherRiskObservation]
    methodology: list[str]
    sources: list[SourceReference]


class RetailOffersResponse(BaseModel):
    generated_at: datetime
    query: str | None = None
    district: str
    offers: list[RetailOffer]
    sources: list[SourceReference]


class PublicInsight(BaseModel):
    id: str
    domain: str
    title: str
    message: str
    severity: Literal["good", "watch", "risk", "neutral"]
    confidence: Confidence
    source_keys: list[str]
    observed_at: datetime


class InsightsResponse(BaseModel):
    generated_at: datetime
    domain: str | None = None
    insights: list[PublicInsight]
    sources: list[SourceReference]


class I18nResponse(BaseModel):
    locale: LocaleCode
    labels: dict[str, str]
    domains: dict[str, str]
    sources: dict[str, str]


AlertCondition = Literal["above", "below", "source_degraded", "movement_changed"]


class UserProfileUpdate(BaseModel):
    default_locale: LocaleCode | None = None
    district: str | None = Field(default=None, min_length=1, max_length=128)
    profile: Literal["single", "family", "commuter"] | None = None
    display_name: str | None = Field(default=None, max_length=160)


class UserProfileResponse(BaseModel):
    id: int
    auth_sub: str
    email: str | None = None
    display_name: str | None = None
    photo_url: str | None = None
    default_locale: LocaleCode
    district: str
    profile: Literal["single", "family", "commuter"]
    created_at: datetime
    updated_at: datetime


class SavedItemCreate(BaseModel):
    domain_key: DomainKey
    label: str = Field(min_length=1, max_length=180)
    query: str | None = Field(default=None, max_length=160)
    href: str | None = Field(default=None, max_length=512)
    payload: dict = Field(default_factory=dict)


class SavedItemResponse(BaseModel):
    id: int
    domain_key: DomainKey
    label: str
    query: str | None = None
    href: str | None = None
    payload: dict
    created_at: datetime


class AlertRuleCreate(BaseModel):
    domain_key: DomainKey | None = None
    label: str = Field(min_length=1, max_length=180)
    metric_label: str | None = Field(default=None, max_length=120)
    condition: AlertCondition
    threshold_value: float | None = None
    enabled: bool = True

    @model_validator(mode="after")
    def threshold_required_for_metric_conditions(self):
        if self.condition in {"above", "below"} and self.threshold_value is None:
            raise ValueError("threshold_value is required for above/below alerts")
        return self


class AlertRuleUpdate(BaseModel):
    label: str | None = Field(default=None, min_length=1, max_length=180)
    metric_label: str | None = Field(default=None, max_length=120)
    condition: AlertCondition | None = None
    threshold_value: float | None = None
    enabled: bool | None = None


class AlertRuleResponse(BaseModel):
    id: int
    domain_key: DomainKey | None = None
    label: str
    metric_label: str | None = None
    condition: AlertCondition
    threshold_value: float | None = None
    enabled: bool
    created_at: datetime
    updated_at: datetime
    last_triggered_at: datetime | None = None


class NotificationUpdate(BaseModel):
    read: bool = True


class NotificationResponse(BaseModel):
    id: int
    alert_rule_id: int | None = None
    title: str
    message: str
    severity: Literal["good", "watch", "risk", "neutral"]
    source_domain: DomainKey | None = None
    read_at: datetime | None = None
    payload: dict
    created_at: datetime


class LifePulseResponse(BaseModel):
    generated_at: datetime
    profile: UserProfileResponse
    overview: LifeOverviewResponse
    saved_items: list[SavedItemResponse]
    alert_rules: list[AlertRuleResponse]
    notifications: list[NotificationResponse]
    unread_count: int


class AlertEvaluationResponse(BaseModel):
    generated_at: datetime
    users_checked: int
    alerts_checked: int
    notifications_created: int


class SourceRefreshResponse(BaseModel):
    generated_at: datetime
    refresh_status: SourceStatus
    domains_refreshed: int
    degraded_domains: list[str]
    offline_domains: list[str]
    pipeline: PipelineResponse
    source_validation: SourceValidationResponse
    import_audit: SourceImportAuditResponse
    import_plan: SourceImportPlanResponse
    alert_evaluation: AlertEvaluationResponse | None = None
    actions: list[str]
