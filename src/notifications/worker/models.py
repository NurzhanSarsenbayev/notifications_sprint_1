# from __future__ import annotations
#
# from datetime import datetime
# from typing import Any, Dict, Optional
# from uuid import UUID
#
# from pydantic import BaseModel, Field
#
# # Статусы для notification_delivery
# STATUS_SENT = "SENT"
# STATUS_FAILED = "FAILED"
# STATUS_RETRYING = "RETRYING"
# STATUS_EXPIRED = "EXPIRED"
#
# # Каналы доставки, на будущее (сейчас воркер умеет только email)
# CHANNEL_EMAIL = "email"
# CHANNEL_PUSH = "push"
# CHANNEL_WS = "ws"
# CHANNEL_SMS = "sms"  # зарезервировано
#
#
# class NotificationJob(BaseModel):
#     job_id: UUID
#     user_id: UUID
#     channel: str  # "email" | "push" | "ws" | "sms"
#     template_code: str
#     locale: str
#
#     data: Dict[str, Any] = Field(default_factory=dict)
#
#     # meta не используется воркером прямо сейчас, но важно корректно парсить
#     meta: Dict[str, Any] = Field(default_factory=dict)
#
#     created_at: Optional[datetime] = None
#     send_after: Optional[datetime] = None
#     expires_at: Optional[datetime] = None
#
#     class Config:
#         extra = "ignore"
