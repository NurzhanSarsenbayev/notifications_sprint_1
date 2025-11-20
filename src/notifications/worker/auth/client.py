from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID
import logging

logger = logging.getLogger(__name__)


@dataclass
class UserContacts:
    user_id: UUID
    email: str | None = None
    push_token: str | None = None
    ws_session_id: str | None = None


class AuthClient:
    """Stub-клиент для Auth-сервиса.

    Сейчас возвращает фейк.
    Позже можно заменить на httpx.AsyncClient и реальные запросы.
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def get_user_contacts(self, user_id: UUID) -> UserContacts:
        fake_email = f"user-{user_id}@example.com"
        fake_push = f"push-{user_id}"
        fake_ws = f"ws-{user_id}"

        return UserContacts(
            user_id=user_id,
            email=fake_email,
            push_token=fake_push,
            ws_session_id=fake_ws,
        )