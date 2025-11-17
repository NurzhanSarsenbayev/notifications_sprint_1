"""
Здесь будут лежать обёртки над Kafka producer/consumer.

Например:
- функция для создания producer
- функция для создания consumer
- базовые настройки сериализации/десериализации JSON-сообщений

Реализацию добавим на этапе подключения Kafka.
"""
import json
from typing import Any, Dict, Optional

from aiokafka import AIOKafkaProducer, errors

from notifications.common.config import settings


class KafkaNotificationJobPublisher:
    """Отправляет NotificationJob в Kafka.

    Если Kafka недоступна, не валит всё приложение,
    а работает в деградированном режиме: просто логирует отправки.
    """

    def __init__(self, bootstrap_servers: str, topic: str) -> None:
        self._bootstrap_servers = bootstrap_servers
        self._topic = topic
        self._producer: Optional[AIOKafkaProducer] = None
        self._enabled: bool = True  # если старт не удался — отключим

    async def start(self) -> None:
        if self._producer is not None or not self._enabled:
            return

        producer = AIOKafkaProducer(
            bootstrap_servers=self._bootstrap_servers,
            value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8"),
        )
        try:
            await producer.start()
        except Exception as exc:
            # ВАЖНО: не уронить всё приложение, если Kafka не поднялась вовремя
            print(f"[KAFKA] Failed to start producer, running in dummy mode: {exc}")
            self._enabled = False
            self._producer = None
            return

        self._producer = producer
        print("[KAFKA] Producer started")

    async def stop(self) -> None:
        if self._producer is None:
            return
        try:
            await self._producer.stop()
        except Exception as exc:
            print(f"[KAFKA] Failed to stop producer: {exc}")
        finally:
            self._producer = None

    async def publish_job(self, payload: Dict[str, Any]) -> None:
        if not self._enabled or self._producer is None:
            # Деградирующий режим: просто выводим, что бы отправили
            print(f"[KAFKA DUMMY] Would publish to {self._topic}: {payload}")
            return

        try:
            await self._producer.send_and_wait(self._topic, payload)
        except errors.KafkaError as exc:
            print(f"[KAFKA] Failed to publish message: {exc}")
        except Exception as exc:
            print(f"[KAFKA] Unexpected error while publishing: {exc}")


kafka_publisher = KafkaNotificationJobPublisher(
    bootstrap_servers=settings.kafka_bootstrap_servers,
    topic="notifications.outbox",
)