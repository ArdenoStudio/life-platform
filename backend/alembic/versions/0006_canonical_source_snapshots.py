"""canonical source snapshots

Revision ID: 0006_canonical_source_snapshots
Revises: 0005_source_import_artifacts
Create Date: 2026-05-28
"""
from alembic import op
import sqlalchemy as sa

revision = "0006_canonical_source_snapshots"
down_revision = "0005_source_import_artifacts"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "district_profile_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source_artifact_id", sa.Integer(), sa.ForeignKey("source_import_artifacts.id"), nullable=True),
        sa.Column("run_key", sa.String(length=120), nullable=False),
        sa.Column("district", sa.String(length=128), nullable=False),
        sa.Column("region_id", sa.String(length=16), nullable=False),
        sa.Column("province", sa.String(length=80), nullable=False),
        sa.Column("population", sa.Integer(), nullable=False),
        sa.Column("households", sa.Integer(), nullable=False),
        sa.Column("area_sqkm", sa.Float(), nullable=False),
        sa.Column("center_lat", sa.Float(), nullable=False),
        sa.Column("center_lng", sa.Float(), nullable=False),
        sa.Column("cooking_gas_share", sa.Float(), nullable=False),
        sa.Column("elderly_share", sa.Float(), nullable=False),
        sa.Column("confidence", sa.String(length=32), nullable=False),
        sa.Column("source_keys", sa.JSON(), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_district_profile_snapshots_source_artifact_id", "district_profile_snapshots", ["source_artifact_id"])
    op.create_index("ix_district_profile_snapshots_run_key", "district_profile_snapshots", ["run_key"])
    op.create_index("ix_district_profile_snapshots_district", "district_profile_snapshots", ["district"])
    op.create_index("ix_district_profile_snapshots_region_id", "district_profile_snapshots", ["region_id"])
    op.create_index("ix_district_profile_snapshots_province", "district_profile_snapshots", ["province"])
    op.create_index("ix_district_profile_snapshots_observed_at", "district_profile_snapshots", ["observed_at"])
    op.create_index("ix_district_profile_snapshots_created_at", "district_profile_snapshots", ["created_at"])

    op.create_table(
        "weather_risk_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source_artifact_id", sa.Integer(), sa.ForeignKey("source_import_artifacts.id"), nullable=True),
        sa.Column("run_key", sa.String(length=120), nullable=False),
        sa.Column("record_type", sa.String(length=64), nullable=False),
        sa.Column("station_id", sa.String(length=80), nullable=True),
        sa.Column("station_name", sa.String(length=120), nullable=False),
        sa.Column("source_observed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rainfall_mm", sa.Float(), nullable=True),
        sa.Column("temperature_c", sa.Float(), nullable=True),
        sa.Column("humidity_percent", sa.Float(), nullable=True),
        sa.Column("water_level_m", sa.Float(), nullable=True),
        sa.Column("source_keys", sa.JSON(), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_weather_risk_snapshots_source_artifact_id", "weather_risk_snapshots", ["source_artifact_id"])
    op.create_index("ix_weather_risk_snapshots_run_key", "weather_risk_snapshots", ["run_key"])
    op.create_index("ix_weather_risk_snapshots_record_type", "weather_risk_snapshots", ["record_type"])
    op.create_index("ix_weather_risk_snapshots_station_id", "weather_risk_snapshots", ["station_id"])
    op.create_index("ix_weather_risk_snapshots_station_name", "weather_risk_snapshots", ["station_name"])
    op.create_index("ix_weather_risk_snapshots_source_observed_at", "weather_risk_snapshots", ["source_observed_at"])
    op.create_index("ix_weather_risk_snapshots_observed_at", "weather_risk_snapshots", ["observed_at"])
    op.create_index("ix_weather_risk_snapshots_created_at", "weather_risk_snapshots", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_weather_risk_snapshots_created_at", table_name="weather_risk_snapshots")
    op.drop_index("ix_weather_risk_snapshots_observed_at", table_name="weather_risk_snapshots")
    op.drop_index("ix_weather_risk_snapshots_source_observed_at", table_name="weather_risk_snapshots")
    op.drop_index("ix_weather_risk_snapshots_station_name", table_name="weather_risk_snapshots")
    op.drop_index("ix_weather_risk_snapshots_station_id", table_name="weather_risk_snapshots")
    op.drop_index("ix_weather_risk_snapshots_record_type", table_name="weather_risk_snapshots")
    op.drop_index("ix_weather_risk_snapshots_run_key", table_name="weather_risk_snapshots")
    op.drop_index("ix_weather_risk_snapshots_source_artifact_id", table_name="weather_risk_snapshots")
    op.drop_table("weather_risk_snapshots")

    op.drop_index("ix_district_profile_snapshots_created_at", table_name="district_profile_snapshots")
    op.drop_index("ix_district_profile_snapshots_observed_at", table_name="district_profile_snapshots")
    op.drop_index("ix_district_profile_snapshots_province", table_name="district_profile_snapshots")
    op.drop_index("ix_district_profile_snapshots_region_id", table_name="district_profile_snapshots")
    op.drop_index("ix_district_profile_snapshots_district", table_name="district_profile_snapshots")
    op.drop_index("ix_district_profile_snapshots_run_key", table_name="district_profile_snapshots")
    op.drop_index("ix_district_profile_snapshots_source_artifact_id", table_name="district_profile_snapshots")
    op.drop_table("district_profile_snapshots")
