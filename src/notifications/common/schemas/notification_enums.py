from enum import Enum

class NotificationStatus(str, Enum):
    SENT = "SENT"
    FAILED = "FAILED"
    RETRYING = "RETRYING"
    EXPIRED = "EXPIRED"

class NotificationChannel(str, Enum):
    EMAIL = "email"
    PUSH = "push"
    WS = "ws"
    SMS = "sms"  # зарезервировано


class NotificationPriority(str, Enum):
    NORMAL = "normal"
    HIGH = "high"