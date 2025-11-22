from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError

from src.notifications.notifications_api.main import app

# ВАЖНО: импорт без "src.", как в templates.py
from notifications.notifications_api.utils.dependencies import (
    get_template_repository,
    get_notification_service,
)

from notifications.notifications_api.schemas.template import (
    TemplateCreate,
    TemplateRead,
)


class FakeTemplateRepo:
    """Фейковый репозиторий шаблонов для API-тестов (без БД)."""

    def __init__(self) -> None:
        self._items: list[TemplateRead] = []

    async def create(self, template_in: TemplateCreate) -> TemplateRead:
        # 👇 проверяем уникальность по (template_code, locale, channel)
        for existing in self._items:
            if (
                existing.template_code == template_in.template_code
                and existing.locale == template_in.locale
                and existing.channel == template_in.channel
            ):
                # Эмулируем поведение БД с уникальным индексом
                raise IntegrityError("duplicate template", params=None, orig=None)

        tpl = TemplateRead(
            id=UUID("11111111-1111-1111-1111-111111111111"),
            template_code=template_in.template_code,
            locale=template_in.locale,
            channel=template_in.channel,
            subject=template_in.subject,
            body=template_in.body,
        )
        self._items.append(tpl)
        return tpl

    async def list(
        self,
        offset: int = 0,
        limit: int = 100,
    ) -> list[TemplateRead]:
        return self._items[offset: offset + limit]


class FakeNotificationService:
    async def handle_event(self, event) -> int:
        return 1


@pytest.fixture(autouse=True)
def override_dependencies():
    fake_repo = FakeTemplateRepo()
    fake_service = FakeNotificationService()

    app.dependency_overrides[get_template_repository] = lambda: fake_repo
    app.dependency_overrides[get_notification_service] = lambda: fake_service

    yield

    app.dependency_overrides.clear()


@pytest.fixture
def api_client() -> TestClient:
    return TestClient(app)
