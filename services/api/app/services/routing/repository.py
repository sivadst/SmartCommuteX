from collections.abc import Sequence
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import Select, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.carbon_metric import CarbonMetric
from app.models.route_snapshot import RouteSnapshot
from app.models.trip import Trip


class TripRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_trip(self, trip: Trip) -> Trip:
        self.session.add(trip)
        await self.session.flush()
        return trip

    async def add_route_snapshot(self, route_snapshot: RouteSnapshot) -> RouteSnapshot:
        self.session.add(route_snapshot)
        await self.session.flush()
        return route_snapshot

    async def add_carbon_metric(self, metric: CarbonMetric) -> CarbonMetric:
        self.session.add(metric)
        await self.session.flush()
        return metric

    async def commit(self) -> None:
        await self.session.commit()

    async def get_trip_history(self, limit: int = 6) -> Sequence[Trip]:
        statement: Select[tuple[Trip]] = (
            select(Trip)
            .options(
                selectinload(Trip.selected_route_snapshot),
                selectinload(Trip.route_snapshots),
            )
            .order_by(Trip.created_at.desc())
            .limit(limit)
        )
        return (await self.session.scalars(statement)).all()

    async def get_dashboard_aggregates(self) -> dict[str, float]:
        seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)

        trip_count = await self.session.scalar(select(func.count(Trip.id)))
        route_avg = await self.session.scalar(select(func.avg(RouteSnapshot.mobility_score)))
        emissions_sum = await self.session.scalar(select(func.sum(CarbonMetric.emissions_kg)))
        savings_sum = await self.session.scalar(select(func.sum(CarbonMetric.savings_vs_rideshare_kg)))
        recent_trip_count = await self.session.scalar(
            select(func.count(Trip.id)).where(Trip.created_at >= seven_days_ago)
        )

        return {
            "trip_count": float(trip_count or 0),
            "average_route_score": float(route_avg or 0),
            "emissions_sum": float(emissions_sum or 0),
            "savings_sum": float(savings_sum or 0),
            "recent_trip_count": float(recent_trip_count or 0),
        }

    async def get_route_mode_share(self) -> dict[str, int]:
        statement = select(RouteSnapshot.mode, func.count(RouteSnapshot.id)).group_by(RouteSnapshot.mode)
        rows = (await self.session.execute(statement)).all()
        return {str(mode): int(count) for mode, count in rows}

    async def get_trip(self, trip_id: UUID) -> Trip | None:
        statement = (
            select(Trip)
            .where(Trip.id == trip_id)
            .options(selectinload(Trip.route_snapshots), selectinload(Trip.selected_route_snapshot))
        )
        return await self.session.scalar(statement)

    async def get_mode_preference_scores(
        self, *, origin_label: str, destination_label: str
    ) -> dict[str, int]:
        statement = (
            select(RouteSnapshot.mode, func.count(RouteSnapshot.id))
            .join(Trip, RouteSnapshot.trip_id == Trip.id)
            .where(
                Trip.origin_label == origin_label,
                Trip.destination_label == destination_label,
            )
            .group_by(RouteSnapshot.mode)
        )
        rows = (await self.session.execute(statement)).all()
        return {str(mode): int(count) for mode, count in rows}

    async def get_recent_route_snapshots(self, limit: int = 10) -> Sequence[RouteSnapshot]:
        statement = select(RouteSnapshot).order_by(desc(RouteSnapshot.created_at)).limit(limit)
        return (await self.session.scalars(statement)).all()
