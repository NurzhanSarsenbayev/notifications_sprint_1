
"""
Pydantic-схема для внутренних сообщений NotificationJob.

Структура соответствует описанию в docs/QUEUE_JOBS.md.

Пример полей:
- job_id
- user_id
- channel
- template_code
- locale
- data
- meta
- created_at
- send_after
- expires_at
"""

# Я добавил в common общию схему, что бы нормализовать единную модель между api и worker

# from datetime import datetime
# from enum import Enum
# from typing import Any, Dict, Optional
# from uuid import UUID
#
# from pydantic import BaseModel, Field
#
#
# class NotificationChannel(str, Enum):
#     EMAIL = "email"
#     PUSH = "push"
#     WS = "ws"
#
#
# class NotificationPriority(str, Enum):
#     NORMAL = "normal"
#     HIGH = "high"
#
#
# class NotificationMeta(BaseModel):
#     event_type: str
#     event_id: Optional[UUID] = None
#     campaign_id: Optional[UUID] = None
#     priority: NotificationPriority = NotificationPriority.NORMAL
#
#
# class NotificationJob(BaseModel):
#     job_id: UUID
#     user_id: UUID
#     channel: NotificationChannel
#     template_code: str
#     locale: str = "ru"
#     data: Dict[str, Any] = Field(default_factory=dict)
#     meta: NotificationMeta
#     created_at: datetime
#     send_after: Optional[datetime] = None
#     expires_at: Optional[datetime] = None