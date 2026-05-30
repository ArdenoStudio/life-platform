"""source import artifacts

Revision ID: 0005_source_import_artifacts
Revises: 0004_source_governance_metadata
Create Date: 2026-05-28
"""
from alembic import op
import sqlalchemy as sa

revision = "0005_source_import_artifacts"
down_revision = "0004_source_governance_metadata"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "source_import_artifacts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("run_key", sa.String(length=120), nullable=False),
        sa.Column("domain_key", sa.String(length=32), sa.ForeignKey("domains.key"), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("mode", sa.String(length=32), nullable=False),
        sa.Column("accepted_for_scoring", sa.Boolean(), nullable=False),
        sa.Column("rows_imported", sa.Integer(), nullable=False),
        sa.Column("source_keys", sa.JSON(), nullable=False),
        sa.Column("checks", sa.JSON(), nullable=False),
        sa.Column("normalized_records", sa.JSON(), nullable=False),
        sa.Column("payload_summary", sa.JSON(), nullable=False),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_source_import_artifacts_run_key", "source_import_artifacts", ["run_key"])
    op.create_index("ix_source_import_artifacts_domain_key", "source_import_artifacts", ["domain_key"])
    op.create_index("ix_source_import_artifacts_status", "source_import_artifacts", ["status"])
    op.create_index("ix_source_import_artifacts_mode", "source_import_artifacts", ["mode"])
    op.create_index("ix_source_import_artifacts_accepted_for_scoring", "source_import_artifacts", ["accepted_for_scoring"])
    op.create_index("ix_source_import_artifacts_observed_at", "source_import_artifacts", ["observed_at"])
    op.create_index("ix_source_import_artifacts_created_at", "source_import_artifacts", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_source_import_artifacts_created_at", table_name="source_import_artifacts")
    op.drop_index("ix_source_import_artifacts_observed_at", table_name="source_import_artifacts")
    op.drop_index("ix_source_import_artifacts_accepted_for_scoring", table_name="source_import_artifacts")
    op.drop_index("ix_source_import_artifacts_mode", table_name="source_import_artifacts")
    op.drop_index("ix_source_import_artifacts_status", table_name="source_import_artifacts")
    op.drop_index("ix_source_import_artifacts_domain_key", table_name="source_import_artifacts")
    op.drop_index("ix_source_import_artifacts_run_key", table_name="source_import_artifacts")
    op.drop_table("source_import_artifacts")
