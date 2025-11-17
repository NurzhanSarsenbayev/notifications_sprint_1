import asyncio

from sqlalchemy.ext.asyncio import create_async_engine

from notifications.common.config import settings
from notifications.db.models import Base


async def main() -> None:
    engine = create_async_engine(settings.db_dsn, echo=True, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
    print("✅ DB schema created")


if __name__ == "__main__":
    asyncio.run(main())