"""
Модуль для описания зависимостей FastAPI (Kafka producer, настройки и т.п.).

Пока оставляем пустым, реализуем на этапе подключения Kafka и настроек.
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from notifications.common.db import get_db_session
from notifications.common.kafka import kafka_publisher, KafkaNotificationJobPublisher
from notifications.notifications_api.repositories.templates import TemplateRepository
from notifications.notifications_api.services.notification_service import NotificationService


async def get_db(
    session: AsyncSession = Depends(get_db_session),
) -> AsyncSession:
    return session


def get_template_repository(
    session: AsyncSession = Depends(get_db),
) -> TemplateRepository:
    return TemplateRepository(session=session)


def get_notification_service() -> NotificationService:
    # publisher глобальный, мы его стартуем/стопаем в lifespan
    return NotificationService(job_publisher=kafka_publisher)