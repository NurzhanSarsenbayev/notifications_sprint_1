
---

# ✅ **docs/EVENTS.md**

````markdown
# Контракты внешних событий (Event)

Notification API принимает события от других микросервисов.
Все события имеют единый формат `Event`.

---

## 📦 Формат Event

```json
{
  "event_id": "uuid",
  "event_type": "string",
  "source": "string",
  "occurred_at": "ISO datetime",
  "payload": {}
}
````

---

## 🧱 Обязательные поля

| Поле          | Тип      | Описание                                     |
| ------------- | -------- | -------------------------------------------- |
| `event_id`    | uuid     | Уникальный идентификатор события             |
| `event_type`  | string   | Тип события (определяет структуру payload)   |
| `source`      | string   | Отправитель (auth_service, content_service…) |
| `occurred_at` | datetime | Когда событие реально произошло              |
| `payload`     | object   | Полезная нагрузка события                    |

---

# Поддерживаемые события (MVP)

Ниже перечислены типы событий, поддерживаемые на первом этапе реализации.

---

# 1. `user_registered`

Событие отправляется сервисом авторизации после успешной регистрации пользователя.

### Payload

```json
{
  "user_id": "uuid",
  "registration_channel": "web",
  "locale": "ru",
  "user_agent": "Mozilla/5.0"
}
```

### Пример события

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

# 2. `new_film_released`

Событие отправляется сервисом контента при появлении нового фильма.

### Payload

```json
{
  "film_id": "uuid",
  "title": "string",
  "genres": ["sci-fi", "action"],
  "age_rating": "16+",
  "release_date": "2025-11-15",
  "target_segment": {
    "by_genres": ["sci-fi"],
    "min_age": 16
  }
}
```

### Пример события

```json
{
  "event_id": "a1b2c3d4-0000-0000-0000-000000000001",
  "event_type": "new_film_released",
  "source": "content_service",
  "occurred_at": "2025-11-14T13:00:00Z",
  "payload": {
    "film_id": "5fcc8705-30be-467d-b5e0-e17ab03ff59b",
    "title": "The Matrix",
    "genres": ["sci-fi", "action"],
    "age_rating": "16+",
    "release_date": "2025-11-15",
    "target_segment": {
      "by_genres": ["sci-fi", "action"],
      "min_age": 16
    }
  }
}
```

---

# 3. `campaign_triggered`

Событие запускается админ-панелью для массовой рассылки.

### Payload

```json
{
  "campaign_id": "uuid",
  "template_code": "black_friday_sale",
  "channels": ["email", "push"],
  "segment": {
    "segment_id": "bf_2025_loyal_customers"
  }
}
```

### Пример события

```json
{
  "event_id": "c1d2e3f4-0000-0000-0000-000000000001",
  "event_type": "campaign_triggered",
  "source": "admin_panel",
  "occurred_at": "2025-11-14T14:00:00Z",
  "payload": {
    "campaign_id": "9f3d5a5e-0000-0000-0000-000000000001",
    "template_code": "black_friday_sale",
    "channels": ["email", "push"],
    "segment": {
      "segment_id": "bf_2025_loyal_customers"
    }
  }
}
```

---

# 📌 Примечания

* Структуры payload могут расширяться, но не должны ломать совместимость.
* Новые `event_type` добавляются через расширение этого документа.
* Notification API обязан валидировать событие и отвечать ошибкой при некорректном payload.

```
