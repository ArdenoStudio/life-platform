"""source governance metadata

Revision ID: 0004_source_governance_metadata
Revises: 0003_hybrid_accounts
Create Date: 2026-05-28
"""
from alembic import op
import sqlalchemy as sa

revision = "0004_source_governance_metadata"
down_revision = "0003_hybrid_accounts"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("source_registry", sa.Column("owner", sa.String(length=160), nullable=False, server_default="Unknown"))
    op.add_column("source_registry", sa.Column("collection_method", sa.String(length=80), nullable=False, server_default="manual_review"))
    op.add_column("source_registry", sa.Column("license_status", sa.String(length=80), nullable=False, server_default="needs_review"))
    op.add_column("source_registry", sa.Column("review_status", sa.String(length=80), nullable=False, server_default="needs_review"))
    op.add_column("source_registry", sa.Column("refresh_cadence", sa.String(length=160), nullable=False, server_default="scheduled or manual refresh"))
    op.add_column("source_registry", sa.Column("governance_note", sa.Text(), nullable=False, server_default=""))


def downgrade() -> None:
    op.drop_column("source_registry", "governance_note")
    op.drop_column("source_registry", "refresh_cadence")
    op.drop_column("source_registry", "review_status")
    op.drop_column("source_registry", "license_status")
    op.drop_column("source_registry", "collection_method")
    op.drop_column("source_registry", "owner")
