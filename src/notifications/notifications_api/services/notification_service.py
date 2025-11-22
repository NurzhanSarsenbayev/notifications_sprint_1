from datetime import datetime, timezone
from typing import List, Type, TypeVar
from uuid import uuid4

from fastapi import HTTPException, status
from pydantic import BaseModel

from notifications.common.kafka import KafkaNotificationJobPublisher
from notifications.notifications_api.schemas.event import (
    BaseEvent,
    EventType,
    UserRegisteredEventPayload,
    NewFilmReleasedEventPayload,
    CampaignTriggeredEventPayload,
)
from notifications.common.schemas import (
    NotificationChannel,
    NotificationJob,
    NotificationMeta,
)

TPayload = TypeVar("TPayload", bound=BaseModel)


class NotificationService:
    """Маппит Event → NotificationJob и отправляет их в Kafka."""

    def __init__(self, job_publisher: KafkaNotificationJobPublisher) -> None:
        self._job_publisher = job_publisher

    # ------------------- публичный метод -------------------

    async def handle_event(self, event: BaseEvent) -> int:
        """Главная точка входа для API.

        - валидирует payload через _map_*;
        - формирует список NotificationJob;
        - публикует каждую job в Kafka;
        - возвращает количество созданных job.
        """
        jobs = self._map_event_to_jobs(event)

        for job in jobs:
            # Pydantic v2: можно использовать model_dump(), dict() тоже ок
            await self._job_publisher.publish_job(job.model_dump(mode="json"))

        return len(jobs)

    # ------------------- диспетчер по типам события -------------------

    def _map_event_to_jobs(self, event: BaseEvent) -> List[NotificationJob]:
        # timezone-aware, как в воркере
        now = datetime.now(timezone.utc)

        if event.event_type == EventType.USER_REGISTERED:
            return self._map_user_registered(event, now)

        if event.event_type == EventType.NEW_FILM_RELEASED:
            # честно говорим, что не реализовано
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="Event type 'new_film_released'"
                       " is not implemented in this MVP",
            )

        if event.event_type == EventType.CAMPAIGN_TRIGGERED:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="Event type 'campaign_triggered'"
                       " is not implemented in this MVP",
            )

        # любой другой event_type — просто не поддерживаем
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported event_type: {event.event_type}",
        )

    # ------------------- helpers -------------------

    def _parse_payload(
        self,
        event: BaseEvent,
        payload_cls: Type[TPayload],
        context: str,
    ) -> TPayload:
        """Общий helper для валидации payload.

        Если payload не подходит под ожидаемую схему — отдаём 400.
        """
        try:
            return payload_cls(**event.payload)
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid payload for {context}: {exc}",
            ) from exc

    # ------------------- конкретные мапперы -------------------

    def _map_user_registered(
            self,
            event: BaseEvent,
            now: datetime) -> List[NotificationJob]:
        payload = self._parse_payload(
            event=event,
            payload_cls=UserRegisteredEventPayload,
            context="user_registered",
        )

        # MVP: один пользователь = user_id из payload
        job = NotificationJob(
            job_id=uuid4(),
            user_id=payload.user_id,
            channel=NotificationChannel.EMAIL,
            template_code="welcome_email",
            locale=payload.locale,
            data={
                "registration_channel": payload.registration_channel,
                "user_agent": payload.user_agent,
            },
            meta=NotificationMeta(
                event_type=event.event_type.value,
                event_id=event.event_id,
                campaign_id=None,
            ),
            created_at=now,
        )
        return [job]

    def _map_new_film_released(
            self,
            event: BaseEvent,
            now: datetime) -> List[NotificationJob]:
        """Шаблон для будущей реализации new_film_released."""
        payload = self._parse_payload(
            event=event,
            payload_cls=NewFilmReleasedEventPayload,
            context="new_film_released",
        )
        # TODO: подобрать пользователей по сегменту и сгенерировать job'ы
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="new_film_released notifications"
                   " are not implemented in this MVP",
        )

    def _map_campaign_triggered(
            self,
            event: BaseEvent,
            now: datetime) -> List[NotificationJob]:
        """Шаблон для будущей реализации campaign_triggered."""
        payload = self._parse_payload(
            event=event,
            payload_cls=CampaignTriggeredEventPayload,
            context="campaign_triggered",
        )
        # TODO: выбрать пользователей по campaign/segment и сгенерировать job'ы
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="campaign_triggered notifications"
                   " are not implemented in this MVP",
        )
