---

# ✅ **docs/QUEUE_JOBS.md**

```markdown
# Контракты внутренних сообщений Kafka (NotificationJob)

Notification API публикует в Kafka задания на отправку уведомлений.

---

# Формат NotificationJob

```json
{
  "job_id": "uuid",
  "user_id": "uuid",
  "channel": "email",
  "template_code": "welcome_email",
  "locale": "ru",
  "data": { },
  "meta": { },
  "created_at": "datetime",
  "send_after": null,
  "expires_at": null
}
🧱 Обязательные поля
Поле	Тип	Описание
job_id	uuid	Уникальный ID задания
user_id	uuid	ID получателя
channel	string	Канал доставки
template_code	string	Код шаблона
locale	string	Локаль
data	object	Данные для подстановки
meta	object	Метаданные
created_at	datetime	Когда создано

🔧 Meta
json
Copy code
{
  "event_type": "user_registered",
  "event_id": "uuid",
  "campaign_id": null,
  "priority": "normal"
}
📨 Примеры NotificationJob
Welcome email
json
Copy code
{
  "job_id": "f4d7c0c3...",
  "user_id": "f3aa4a0e...",
  "channel": "email",
  "template_code": "welcome_email",
  "locale": "ru",
  "data": {
    "first_name": "Нуржан",
    "login_url": "https://cinema.kz/login"
  },
  "meta": {
    "event_type": "user_registered",
    "event_id": "6a9f7...",
    "campaign_id": null,
    "priority": "normal"
  },
  "created_at": "2025-11-14T12:35:10Z",
  "send_after": null,
  "expires_at": null
}
Новый фильм
json
Copy code
{
  "job_id": "12f8a4dc...",
  "user_id": "3227a104...",
  "channel": "email",
  "template_code": "new_film_recommendation",
  "locale": "ru",
  "data": {
    "first_name": "Айдана",
    "film_title": "The Matrix"
  },
  "meta": {
    "event_type": "new_film_released",
    "event_id": "a1b2c3d4...",
    "campaign_id": null,
    "priority": "normal"
  },
  "created_at": "2025-11-14T13:05:00Z",
  "send_after": null,
  "expires_at": "2025-11-21T00:00:00Z"
}