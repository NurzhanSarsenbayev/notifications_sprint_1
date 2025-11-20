from __future__ import annotations
import logging

from .base import BaseSender

logger = logging.getLogger(__name__)


class EmailSender(BaseSender):
    """Отправка email (MVP: просто логирование)."""

    async def send(self, *, to: str, subject: str, body: str) -> None:
        if not to:
            raise ValueError("Recipient email is empty")

        logger.info(
            "[EMAIL] Sending to=%s subject=%r body=%r",
            to,
            subject,
            body,
        )
