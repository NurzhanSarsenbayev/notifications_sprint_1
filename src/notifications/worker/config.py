from pydantic import BaseSettings


class WorkerSettings(BaseSettings):
    """Настройки воркера нотификаций."""

    kafka_bootstrap_servers: str = "kafka:9092"
    kafka_outbox_topic: str = "notifications.outbox"
    kafka_retry_topic: str = "notifications.retry"
    kafka_dlq_topic: str = "notifications.dlq"

    group_id: str = "notification-worker"

    class Config:
        env_prefix = "NOTIFICATIONS_WORKER_"
        env_file = ".env"
        case_sensitive = False