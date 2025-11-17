---

# 📘 **Notification API — HTTP Documentation**

Версия: **v1**
Статус: **MVP (Stage 2)**
Автор: *Notification Service Team*

---

# 1. 🎯 Назначение сервиса

**Notification API** — это HTTP-входная точка сервиса уведомлений.
Он принимает события от других микросервисов онлайн-кинотеатра, валидирует их и публикует во внутреннюю очередь Kafka для дальнейшей обработки воркером.

Notification API **не выполняет отправку сообщений** — это задача Notification Worker.

---

# 2. 🏗 Общая архитектура

```
[Auth / Content / Admin Panel Services]
                |
             HTTP POST /events
                |
        +---------------------+
        |   Notification API  |
        +---------------------+
                |
                | Kafka publish (notifications.outbox)
                v
        +----------------------+
        |  Notification Worker |
        +----------------------+
                |
      [email / push / websocket]
```

API работает независимо от воркера:
даже если Kafka недоступна, API продолжает принимать события (режим деградации).

---

# 3. 📚 Версии API

Базовый URL:

```
/api/v1
```

---

# 4. ❤️ Health Checks

## `GET /health`

Проверка того, что приложение запущено.

### Response (200)

```json
{"status": "ok"}
```

---

# 5. 📩 События: `POST /api/v1/events`

Notification API принимает внешние события в едином формате.

---

## 5.1. 🔧 Формат Event

```json
{
  "event_id": "uuid",
  "event_type": "string",
  "source": "string",
  "occurred_at": "ISO datetime",
  "payload": {}
}
```

Описание полей:

| Поле          | Тип      | Описание                                   |
| ------------- | -------- | ------------------------------------------ |
| `event_id`    | UUID     | Уникальный ID события                      |
| `event_type`  | string   | Тип события — определяет структуру payload |
| `source`      | string   | Источник события                           |
| `occurred_at` | datetime | Когда событие произошло                    |
| `payload`     | object   | Данные события                             |

---

## 5.2. 📦 Поддерживаемые типы событий (MVP)

### 1) `user_registered`

Payload:

```json
{
  "user_id": "uuid",
  "registration_channel": "web",
  "locale": "ru",
  "user_agent": "Mozilla/5.0"
}
```

### 2) `new_film_released`

```json
{
  "film_id": "uuid",
  "title": "string",
  "genres": ["sci-fi"],
  "age_rating": "16+",
  "release_date": "2025-11-15",
  "target_segment": {
    "by_genres": ["sci-fi"],
    "min_age": 16
  }
}
```

### 3) `campaign_triggered`

```json
{
  "campaign_id": "uuid",
  "template_code": "black_friday_sale",
  "channels": ["email","push"],
  "segment": {
    "segment_id": "bf_loyal_customers"
  }
}
```

---

## 5.3. 🎛 Обработка события

При получении Event:

1. API валидирует:

   * общий формат,
   * структуру payload в зависимости от `event_type`.

2. API конвертирует событие в один или несколько `NotificationJob`.

3. API публикует job'ы в Kafka топик:

```
notifications.outbox
```

4. API возвращает успешный статус **до фактической отправки уведомлений**.

---

## 5.4. 📨 Пример запроса

```http
POST /api/v1/events
Content-Type: application/json
```

```json
{
  "event_id": "6a9f7f26-4c0c-4a91-9f3d-b159c2dcb001",
  "event_type": "user_registered",
  "source": "auth_service",
  "occurred_at": "2025-11-14T12:34:56Z",
  "payload": {
    "user_id": "f3aa4a0e-97d4-4e21-a2b4-9fb7c8d9f001",
    "registration_channel": "web",
    "locale": "ru",
    "user_agent": "Mozilla/5.0"
  }
}
```

---

## 5.5. 🟢 Ответ (202 Accepted)

```json
{
  "status": "accepted",
  "event_id": "6a9f7f26-4c0c-4a91-9f3d-b159c2dcb001",
  "jobs_count": 1
}
```

---

## 5.6. 🔴 Ошибки

### Неверный payload (400)

```json
{
  "detail": "Invalid payload for user_registered: field 'user_id' is required"
}
```

---

# 6. 🧱 NotificationJob (что API публикует в Kafka)

API не отправляет уведомления — он публикует внутрь Kafka структуры типа:

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
  "created_at": "2025-11-14T12:35:10Z",
  "send_after": null,
  "expires_at": null
}
```

Поля соответствуют описанию в `docs/QUEUE_JOBS.md`.

---

## 6.1. Каналы доставки

```
email
push
ws
sms (зарезервировано)
```

---

# 7. 🔌 Kafka (режим деградации)

Если Notification API не может подключиться к Kafka:

* логируется ошибка,
* запускается **dummy режим**,
* job'ы НЕ отправляются в Kafka, но логируются:

```
[KAFKA DUMMY] Would publish to notifications.outbox: {...}
```

В этом режиме API **всё равно возвращает статус 202 Accepted**,
что позволяет не останавливать внешние сервисы.

---

# 8. 📝 Работа с шаблонами уведомлений

Notification API предоставляет CRUD для таблицы `templates`.

---

# 8.1. `GET /api/v1/templates`

Получить список всех шаблонов.

### Response (200)

```json
[
  {
    "id": "82e3e29a-804e-4367-b84b-6d71e0a1fed3",
    "template_code": "welcome_email",
    "locale": "ru",
    "channel": "email",
    "subject": "Добро пожаловать!",
    "body": "<h1>Привет!</h1><p>Спасибо за регистрацию</p>"
  }
]
```

---

# 8.2. `POST /api/v1/templates`

Создать новый шаблон.

### Request

```json
{
  "template_code": "welcome_email",
  "locale": "ru",
  "channel": "email",
  "subject": "Добро пожаловать!",
  "body": "<h1>Привет!</h1><p>Спасибо за регистрацию</p>"
}
```

### Response (201)

```json
{
  "id": "232420e6-c069-4974-9313-6c029684eaa5",
  "template_code": "welcome_email",
  "locale": "ru",
  "channel": "email",
  "subject": "Добро пожаловать!",
  "body": "<h1>...</h1>"
}
```

### Error — template already exists (409)

```json
{
  "detail": "Template with this code/locale/channel already exists"
}
```

---

# 8.3. `GET /api/v1/templates/{id}` *(опционально)*

(Если реализовано)

---

# 9. ⚙️ Future extensions (Stage 3+)

Следующие вещи реализуются **после запуска Notification Worker**:

* запись истории доставок (`notification_delivery`)
* retries, DLQ
* реальные интеграции с email/push/ws
* кампании и авто-события

---

# 🧩 Статус документа

✔ Актуально для **Этапа 2 (Notification API)**
❗ После интеграции Worker будет дополнено спецификацией Kafka retry/delivery logic.

---
