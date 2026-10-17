"""Create users, boats, bookings, and payments.

Revision ID: 0001_initial
Revises:
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("full_name", sa.String(120), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", sa.String(20), nullable=False, server_default="customer"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_role", "users", ["role"])

    op.create_table(
        "boats",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("location", sa.String(120), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("boat_type", sa.String(60), nullable=False, server_default="Sailing"),
        sa.Column("capacity", sa.Integer(), nullable=False),
        sa.Column("price_per_day", sa.Numeric(10, 2), nullable=False),
        sa.Column("image_url", sa.String(1000), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("capacity > 0", name="ck_boats_capacity_positive"),
        sa.CheckConstraint("price_per_day > 0", name="ck_boats_price_positive"),
    )
    for column in ("name", "location", "is_active"):
        op.create_index(f"ix_boats_{column}", "boats", [column])

    op.create_table(
        "bookings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("boat_id", sa.Integer(), sa.ForeignKey("boats.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="confirmed"),
        sa.Column("total_price", sa.Numeric(10, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("end_date > start_date", name="ck_bookings_dates_ordered"),
        sa.CheckConstraint("total_price >= 0", name="ck_bookings_total_nonnegative"),
    )
    for column in ("user_id", "boat_id", "status"):
        op.create_index(f"ix_bookings_{column}", "bookings", [column])

    op.create_table(
        "payments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("booking_id", sa.Integer(), sa.ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, server_default="usd"),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("provider", sa.String(30), nullable=False, server_default="stripe"),
        sa.Column("provider_payment_id", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("amount >= 0", name="ck_payments_amount_nonnegative"),
        sa.UniqueConstraint("booking_id", name="uq_payments_booking_id"),
    )
    op.create_index("ix_payments_booking_id", "payments", ["booking_id"])
    op.create_index("ix_payments_status", "payments", ["status"])
    op.create_index("ix_payments_provider_payment_id", "payments", ["provider_payment_id"], unique=True)


def downgrade() -> None:
    op.drop_table("payments")
    op.drop_table("bookings")
    op.drop_table("boats")
    op.drop_table("users")
