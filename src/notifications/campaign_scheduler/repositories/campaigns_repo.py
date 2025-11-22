from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from uuid import UUID

import asyncpg

from notifications.db.models import CampaignStatus


@dataclass
class Campaign:
    """Упрощённое представление кампании для планировщика."""

    id: UUID
    template_code: str
    segment_id: str
    status: str
    schedule_cron: str
    last_triggered_at: Optional[datetime]
    runs_count: int
    max_runs: Optional[int]


class CampaignRepository:
    """Работа с таблицей campaigns через asyncpg."""

    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool

    async def get_active_campaigns(self) -> List[Campaign]:
        """Вернуть все активные кампании (status = ACTIVE)."""
        query = """
            SELECT
                id,
                template_code,
                segment_id,
                status,
                schedule_cron,
                last_triggered_at,
                runs_count,
                max_runs
            FROM campaigns
            WHERE status = $1
            ORDER BY created_at ASC;
        """

        async with self._pool.acquire() as conn:
            rows = await conn.fetch(query, CampaignStatus.ACTIVE.value)

        return [
            Campaign(
                id=row["id"],
                template_code=row["template_code"],
                segment_id=row["segment_id"],
                status=row["status"],
                schedule_cron=row["schedule_cron"],
                last_triggered_at=row["last_triggered_at"],
                runs_count=row["runs_count"],
                max_runs=row["max_runs"],
            )
            for row in rows
        ]

    async def mark_campaign_triggered(self, campaign_id: UUID) -> None:
        """Обновить last_triggered_at / runs_count и,
         при необходимости, сделать кампанию INACTIVE.

        Логика:
        - last_triggered_at = NOW()
        - runs_count = runs_count + 1
        - если max_runs не NULL и мы достигли лимита → status = INACTIVE
        - иначе status = ACTIVE
        """
        query = """
            UPDATE campaigns
            SET
                last_triggered_at = NOW(),
                runs_count = runs_count + 1,
                updated_at = NOW(),
                status = CASE
                    WHEN max_runs IS NOT NULL AND runs_count + 1 >= max_runs
                        THEN 'INACTIVE'
                    ELSE 'ACTIVE'
                END
            WHERE id = $1;
        """
        async with self._pool.acquire() as conn:
            await conn.execute(query, campaign_id)
