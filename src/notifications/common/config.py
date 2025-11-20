from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # FastAPI
    project_name: str = "Notification API"
    api_v1_prefix: str = "/api/v1"

    # Kafka (общие настройки для API и воркера)
    kafka_bootstrap_servers: str = "kafka:9092"

    # Топики и consumer group для нотификаций (используются воркером)
    kafka_outbox_topic: str = "notifications.outbox"
    kafka_dlq_topic: str = "notifications.dlq"
    kafka_consumer_group: str = "notification-worker"

    # Postgres
    db_host: str = "notifications-db"
    db_port: int = 5432
    db_name: str = "notifications"
    db_user: str = "notifications"
    db_password: str = "notifications"

    @property
    def db_dsn(self) -> str:
        # Для SQLAlchemy (API) — с +asyncpg
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @property
    def db_asyncpg_dsn(self) -> str:
        # Для asyncpg (воркер) — без +asyncpg
        return (
            f"postgresql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    # Настройки воркера (можно оставить дефолтные, менять через env только при необходимости)
    max_attempts: int = 3
    retry_delays_seconds_raw: str = "1,3,10"
    max_send_delay_seconds: int = 300

    @property
    def retry_delays_seconds(self) -> List[float]:
        parts = [p.strip() for p in self.retry_delays_seconds_raw.split(",") if p.strip()]
        try:
            return [float(p) for p in parts]
        except ValueError:
            return [1.0, 3.0, 10.0]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()