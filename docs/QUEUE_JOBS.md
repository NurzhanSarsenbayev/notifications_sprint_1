
---

# 📦 **QUEUE_JOBS.md — Контракты Kafka-сообщений Notification Service**

Этот документ описывает формат внутренних сообщений, которые циркулируют между:

* **Notification API** (производитель job)
* **Kafka** (`notifications.outbox`, `notifications.dlq`)
* **Notification Worker** (потребитель job)

Сообщения в Kafka представлены в формате **JSON**.

---

# 1. 🎯 NotificationJob (основной контракт)

Notification API публикует в Kafka задания на отправку уведомлений — **NotificationJob**.

Worker читает его, обрабатывает, делает retry, пишет статусы в БД и при необходимости отправляет в DLQ.

---

## 1.1. 📑 Формат NotificationJob

```json
{
  "job_id": "uuid",
  "user_id": "uuid",
  "channel": "email",
  "template_code": "welcome_email",
  "locale": "ru",
  "data": {},
  "meta": {
    "event_type": "user_registered",
    "event_id": "uuid",
    "campaign_id": null,
    "priority": "normal"
  },
  "created_at": "2025-11-14T12:00:00Z",
  "send_after": null,
  "expires_at": null
}
```

---

## 1.2. 🧱 Описание полей

| Поле            | Тип             | Обязателен | Описание                                                |
| --------------- | --------------- | ---------- | ------------------------------------------------------- |
| `job_id`        | UUID            | ✔          | Уникальный ID уведомления (идемпотентность)             |
| `user_id`       | UUID            | ✔          | ID пользователя-получателя                              |
| `channel`       | string          | ✔          | Канал отправки: `email`, `push`, `ws`, `sms` *(резерв)* |
| `template_code` | string          | ✔          | Код шаблона из таблицы `templates`                      |
| `locale`        | string          | ✔          | Локаль (`ru`, `en`, `kz` и т.д.)                        |
| `data`          | object          | ✔          | Данные для рендера шаблона                              |
| `meta`          | object          | ✔          | Доп. данные события                                     |
| `created_at`    | datetime        | ✔          | Время создания job                                      |
| `send_after`    | datetime | null | –          | Отложенная отправка (при наличии)                       |
| `expires_at`    | datetime | null | –          | Прекратить попытки после времени Х                      |

---

## 1.3. 📌 `meta` объект

```json
{
  "event_type": "user_registered",
  "event_id": "uuid",
  "campaign_id": null,
  "priority": "normal"
}
```

| Поле          | Описание                                                              |
| ------------- | --------------------------------------------------------------------- |
| `event_type`  | Тип исходного события (`user_registered`, `new_film_released` и т.д.) |
| `event_id`    | ID события, откуда сформирован job                                    |
| `campaign_id` | ID кампании (или null, если job из обычного события)                  |
| `priority`    | `normal` или `high` *(MVP — всегда normal)*                           |

---

# 2. 📨 Примеры NotificationJob

## 2.1. Welcome Email (реализованный сценарий)

```json
{
  "job_id": "f4d7c0c3-7bd2-4d5b-9891-93f6ac0242ef",
  "user_id": "f3aa4a0e-97d4-4e21-a2b4-9fb7c8d9f001",
  "channel": "email",
  "template_code": "welcome_email",
  "locale": "ru",
  "data": {
    "registration_channel": "web",
    "user_agent": "Mozilla/5.0"
  },
  "meta": {
    "event_type": "user_registered",
    "event_id": "6a9f7f26-4c0c-4a91-9f3d-b159c2dcb001",
    "campaign_id": null,
    "priority": "normal"
  },
  "created_at": "2025-11-14T12:35:10Z",
  "send_after": null,
  "expires_at": null
}
```

---

## 2.2. Job от кампании (пока только архитектурный задел)

```json
{
  "job_id": "12f8a4dc-88ad-4679-9cd4-3138171a3451",
  "user_id": "3227a104-4f7e-4591-8f8e-f0694ef44c11",
  "channel": "email",
  "template_code": "black_friday_sale",
  "locale": "ru",
  "data": {
    "discount": "50%",
    "promo_code": "BFRIDAY2025"
  },
  "meta": {
    "event_type": "campaign_triggered",
    "event_id": "a1b2c3d4-0000-0000-1111-222233334444",
    "campaign_id": "bf_loyal_customers_2025",
    "priority": "normal"
  },
  "created_at": "2025-11-25T10:00:00Z",
  "send_after": null,
  "expires_at": "2025-11-26T00:00:00Z"
}
```

---

# 3. ☠ DLQ — Dead Letter Queue Contract

Worker отправляет сообщения в `notifications.dlq` в двух случаях:

---

## 3.1. ❌ Ошибка десериализации JSON

Worker не смог распарсить входной message во `NotificationJob`.

```json
{
  "raw_value": "{...invalid json...}",
  "error_message": "Invalid JSON in Kafka message",
  "failed_at": "2025-11-21T12:34:56Z"
}
```

---

## 3.2. ❌ Job исчерпал retry-попытки

Worker попытался отправить N раз (max_attempts), но ошибка постоянная.

```json
{
  "job": {
    "job_id": "12f8a4dc...",
    "user_id": "3227a104...",
    "channel": "email",
    "template_code": "welcome_email",
    "...": "..."
  },
  "error_message": "User has no email",
  "failed_at": "2025-11-21T12:40:00Z"
}
```

---

# 4. 📌 Статусы доставки (в БД)

Для reference worker пишет статусы в таблицу `notification_delivery`:

```
SENT
FAILED
RETRYING
EXPIRED
```

---

# 5. 🧩 Соответствие коду

Контракты полностью соответствуют:

* `notifications/common/schemas/notification_job.py`
* `NotificationService.handle_event()`
* `JobProcessor.handle_job()`
* `RetryEngine`
* `DLQPublisher`

---

# 6. 📘 Статус документа

✔ Финальная версия для сдачи (MVP)
✔ Абсолютно соответствует реальному проекту
✔ Не включает фейковые retry-топики (у тебя их нет)
✔ Готово к production-расширению

---
