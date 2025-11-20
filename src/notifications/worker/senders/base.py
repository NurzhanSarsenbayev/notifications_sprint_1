from __future__ import annotations
from abc import ABC, abstractmethod


class BaseSender(ABC):
    """Абстрактный интерфейс отправки уведомлений."""

    @abstractmethod
    async def send(self, *, to: str, subject: str, body: str) -> None:
        """Отправить сообщение конкретному пользователю."""
        raise NotImplementedError