from __future__ import annotations

import logging
from datetime import datetime, timezone
from enum import Enum

from src.notifications.common.schemas import NotificationStatus
from src.notifications.common.schemas import NotificationJob
from ..repositories import NotificationDeliveryRepository

logger = logging.getLogger(__name__)


def _ensure_channel(job: NotificationJob) -> str:
    """Гарантированно вернуть строковый канал для записи в БД.

    Сейчас у нас по факту один канал — email, поэтому:
    - если channel отсутствует или None -> "email" (fallback для MVP);
    - если channel — Enum -> berём .value;
    - если строка -> возвращаем как есть.
    """
    ch = getattr(job, "channel", None)

    if ch is None:
        # 🔥 MVP-fallback: у нас пока только email, чтобы не падать по NOT NULL
        return "email"

    if isinstance(ch, Enum):
        return str(ch.value)

    return str(ch)


async def mark_sent(
    delivery_repo: NotificationDeliveryRepository,
    job: NotificationJob,
    attempts: int,
) -> None:
    await delivery_repo.save_status(
        job_id=job.job_id,
        user_id=job.user_id,
        channel=_ensure_channel(job),       # 👈 теперь НИКОГДА не None
        status=NotificationStatus.SENT,
        attempts=attempts,
        error_code=None,
        error_message=None,
        sent_at=datetime.now(timezone.utc),
    )
    logger.info("Job %s SENT (attempt %s)", job.job_id, attempts)


async def mark_failure(
    delivery_repo: NotificationDeliveryRepository,
    job: NotificationJob,
    attempts: int,
    error: str,
    final: bool,
) -> None:
    status = NotificationStatus.FAILED if final else NotificationStatus.RETRYING

    await delivery_repo.save_status(
        job_id=job.job_id,
        user_id=job.user_id,
        channel=_ensure_channel(job),
        status=status,
        attempts=attempts,
        error_code=None,
        error_message=error,
        sent_at=None,
    )
    logger.warning(
        "Job %s %s on attempt %s: %s",
        job.job_id,
        status,
        attempts,
        error,
    )


async def mark_expired(
    delivery_repo: NotificationDeliveryRepository,
    job: NotificationJob,
    attempts: int,
    message: str = "Notification expired",
) -> None:
    await delivery_repo.save_status(
        job_id=job.job_id,
        user_id=job.user_id,
        channel=_ensure_channel(job),       # 👈 и здесь
        status=NotificationStatus.EXPIRED,
        attempts=attempts,
        error_code=None,
        error_message=message,
        sent_at=None,
    )
    logger.warning("Job %s EXPIRED (attempts=%s)", job.job_id, attempts)
