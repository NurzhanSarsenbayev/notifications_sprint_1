from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # FastAPI
    project_name: str = "Notification API"
    api_v1_prefix: str = "/api/v1"

    # Kafka
    kafka_bootstrap_servers: str = "kafka:9092"

    # Postgres
    db_host: str = "notifications-db"
    db_port: int = 5432
    db_name: str = "notifications"
    db_user: str = "notifications"
    db_password: str = "notifications"

    @property
    def db_dsn(self) -> str:
        # asyncpg драйвер
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()