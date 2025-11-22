import logging


def configure_logging() -> None:
    """Глобальная настройка логов для воркера."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    )
