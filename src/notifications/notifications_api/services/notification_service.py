from datetime import datetime
from typing import List
from uuid import uuid4

from fastapi import HTTPException, status

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


class NotificationService:
    """Маппит Event → NotificationJob и отправляет их в Kafka."""

    def __init__(self, job_publisher: KafkaNotificationJobPublisher) -> None:
        self._job_publisher = job_publisher

    async def handle_event(self, event: BaseEvent) -> int:
        jobs = self._map_event_to_jobs(event)
        for job in jobs:
            await self._job_publisher.publish_job(job.dict())
        return len(jobs)

    def _map_event_to_jobs(self, event: BaseEvent) -> List[NotificationJob]:
        now = datetime.utcnow()

        if event.event_type is EventType.USER_REGISTERED:
            return self._map_user_registered(event, now)

        if event.event_type is EventType.NEW_FILM_RELEASED:
            return self._map_new_film_released(event, now)

        if event.event_type is EventType.CAMPAIGN_TRIGGERED:
            return self._map_campaign_triggered(event, now)

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported event_type: {event.event_type}",
        )

    def _map_user_registered(self, event: BaseEvent, now: datetime) -> List[NotificationJob]:
        try:
            payload = UserRegisteredEventPayload(**event.payload)
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid payload for user_registered: {exc}",
            )

        # MVP: один пользователь = user_id из payload
        jobs: List[NotificationJob] = [
            NotificationJob(
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
        ]
        return jobs

    def _map_new_film_released(self, event: BaseEvent, now: datetime) -> List[NotificationJob]:
        try:
            payload = NewFilmReleasedEventPayload(**event.payload)
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid payload for new_film_released: {exc}",
            )

        # MVP: пока не выбираем реальных юзеров по сегментам → ничего не шлём
        # Можно сюда подставить тестовый user_id позже.
        return []

    def _map_campaign_triggered(self, event: BaseEvent, now: datetime) -> List[NotificationJob]:
        try:
            payload = CampaignTriggeredEventPayload(**event.payload)
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid payload for campaign_triggered: {exc}",
            )

        # MVP: сегментацию не реализуем → тоже пустой список
        return []