"""initial platform tables"""

from alembic import op
import sqlalchemy as sa


revision = "20260601_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("display_name", sa.String(length=120), nullable=False),
        sa.Column("home_city", sa.String(length=120), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    op.create_table(
        "commute_profiles",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("default_objective", sa.String(length=32), nullable=False),
        sa.Column("preferred_modes", sa.JSON(), nullable=False),
        sa.Column("weight_profile", sa.JSON(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_commute_profiles_user_id_users")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_commute_profiles")),
    )
    op.create_index(op.f("ix_commute_profiles_user_id"), "commute_profiles", ["user_id"], unique=False)

    op.create_table(
        "trips",
        sa.Column("user_id", sa.Uuid(), nullable=True),
        sa.Column("commute_profile_id", sa.Uuid(), nullable=True),
        sa.Column("selected_route_snapshot_id", sa.Uuid(), nullable=True),
        sa.Column("origin_label", sa.String(length=120), nullable=False),
        sa.Column("destination_label", sa.String(length=120), nullable=False),
        sa.Column("origin_lat", sa.Float(), nullable=False),
        sa.Column("origin_lng", sa.Float(), nullable=False),
        sa.Column("destination_lat", sa.Float(), nullable=False),
        sa.Column("destination_lng", sa.Float(), nullable=False),
        sa.Column("departure_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("objective", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["commute_profile_id"], ["commute_profiles.id"], name=op.f("fk_trips_commute_profile_id_commute_profiles")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_trips_user_id_users")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_trips")),
    )

    op.create_table(
        "route_snapshots",
        sa.Column("trip_id", sa.Uuid(), nullable=False),
        sa.Column("provider", sa.String(length=64), nullable=False),
        sa.Column("mode", sa.String(length=32), nullable=False),
        sa.Column("title", sa.String(length=120), nullable=False),
        sa.Column("geometry", sa.JSON(), nullable=False),
        sa.Column("distance_meters", sa.Float(), nullable=False),
        sa.Column("base_duration_seconds", sa.Float(), nullable=False),
        sa.Column("predicted_duration_seconds", sa.Float(), nullable=False),
        sa.Column("traffic_score", sa.Float(), nullable=False),
        sa.Column("carbon_kg", sa.Float(), nullable=False),
        sa.Column("cost_usd", sa.Float(), nullable=False),
        sa.Column("mobility_score", sa.Float(), nullable=False),
        sa.Column("score_breakdown", sa.JSON(), nullable=False),
        sa.Column("rationale", sa.String(length=500), nullable=False),
        sa.Column("raw_response", sa.JSON(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["trip_id"], ["trips.id"], name=op.f("fk_route_snapshots_trip_id_trips")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_route_snapshots")),
    )
    op.create_index(op.f("ix_route_snapshots_mode"), "route_snapshots", ["mode"], unique=False)
    op.create_index(op.f("ix_route_snapshots_trip_id"), "route_snapshots", ["trip_id"], unique=False)

    op.create_foreign_key(
        op.f("fk_trips_selected_route_snapshot_id_route_snapshots"),
        "trips",
        "route_snapshots",
        ["selected_route_snapshot_id"],
        ["id"],
    )

    op.create_table(
        "saved_routes",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("route_snapshot_id", sa.Uuid(), nullable=False),
        sa.Column("label", sa.String(length=120), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_favorite", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["route_snapshot_id"], ["route_snapshots.id"], name=op.f("fk_saved_routes_route_snapshot_id_route_snapshots")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_saved_routes_user_id_users")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_saved_routes")),
    )
    op.create_index(op.f("ix_saved_routes_route_snapshot_id"), "saved_routes", ["route_snapshot_id"], unique=False)
    op.create_index(op.f("ix_saved_routes_user_id"), "saved_routes", ["user_id"], unique=False)

    op.create_table(
        "carbon_metrics",
        sa.Column("trip_id", sa.Uuid(), nullable=False),
        sa.Column("route_snapshot_id", sa.Uuid(), nullable=False),
        sa.Column("emissions_kg", sa.Float(), nullable=False),
        sa.Column("savings_vs_rideshare_kg", sa.Float(), nullable=False),
        sa.Column("carbon_intensity_g_per_km", sa.Float(), nullable=False),
        sa.Column("sustainability_rating", sa.String(length=16), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["route_snapshot_id"], ["route_snapshots.id"], name=op.f("fk_carbon_metrics_route_snapshot_id_route_snapshots")),
        sa.ForeignKeyConstraint(["trip_id"], ["trips.id"], name=op.f("fk_carbon_metrics_trip_id_trips")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_carbon_metrics")),
    )
    op.create_index(op.f("ix_carbon_metrics_route_snapshot_id"), "carbon_metrics", ["route_snapshot_id"], unique=False)
    op.create_index(op.f("ix_carbon_metrics_trip_id"), "carbon_metrics", ["trip_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_carbon_metrics_trip_id"), table_name="carbon_metrics")
    op.drop_index(op.f("ix_carbon_metrics_route_snapshot_id"), table_name="carbon_metrics")
    op.drop_table("carbon_metrics")
    op.drop_index(op.f("ix_saved_routes_user_id"), table_name="saved_routes")
    op.drop_index(op.f("ix_saved_routes_route_snapshot_id"), table_name="saved_routes")
    op.drop_table("saved_routes")
    op.drop_constraint(op.f("fk_trips_selected_route_snapshot_id_route_snapshots"), "trips", type_="foreignkey")
    op.drop_index(op.f("ix_route_snapshots_trip_id"), table_name="route_snapshots")
    op.drop_index(op.f("ix_route_snapshots_mode"), table_name="route_snapshots")
    op.drop_table("route_snapshots")
    op.drop_table("trips")
    op.drop_index(op.f("ix_commute_profiles_user_id"), table_name="commute_profiles")
    op.drop_table("commute_profiles")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
