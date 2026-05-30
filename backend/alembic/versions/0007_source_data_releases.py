"""source data releases

Revision ID: 0007_source_data_releases
Revises: 0006_canonical_source_snapshots
Create Date: 2026-05-28
"""
from alembic import op
import sqlalchemy as sa

revision = "0007_source_data_releases"
down_revision = "0006_canonical_source_snapshots"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "source_data_releases",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("release_key", sa.String(length=160), nullable=False, unique=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("source_import_artifact_ids", sa.JSON(), nullable=False),
        sa.Column("run_keys", sa.JSON(), nullable=False),
        sa.Column("source_keys", sa.JSON(), nullable=False),
        sa.Column("checks", sa.JSON(), nullable=False),
        sa.Column("district_profile_snapshot_count", sa.Integer(), nullable=False),
        sa.Column("weather_risk_snapshot_count", sa.Integer(), nullable=False),
        sa.Column("area_score_snapshot_count", sa.Integer(), nullable=False),
        sa.Column("payload_summary", sa.JSON(), nullable=False),
        sa.Column("operator_notes", sa.JSON(), nullable=False),
        sa.Column("superseded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("superseded_by_release_key", sa.String(length=160), nullable=True),
        sa.Column("rolled_back_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_source_data_releases_release_key", "source_data_releases", ["release_key"])
    op.create_index("ix_source_data_releases_status", "source_data_releases", ["status"])
    op.create_index("ix_source_data_releases_superseded_by_release_key", "source_data_releases", ["superseded_by_release_key"])
    op.create_index("ix_source_data_releases_observed_at", "source_data_releases", ["observed_at"])
    op.create_index("ix_source_data_releases_created_at", "source_data_releases", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_source_data_releases_created_at", table_name="source_data_releases")
    op.drop_index("ix_source_data_releases_observed_at", table_name="source_data_releases")
    op.drop_index("ix_source_data_releases_superseded_by_release_key", table_name="source_data_releases")
    op.drop_index("ix_source_data_releases_status", table_name="source_data_releases")
    op.drop_index("ix_source_data_releases_release_key", table_name="source_data_releases")
    op.drop_table("source_data_releases")
