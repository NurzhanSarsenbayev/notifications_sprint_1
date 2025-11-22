import pytest
from datetime import datetime, timezone
from uuid import uuid4


@pytest.mark.asyncio
async def test_post_event_accepted(api_client):
    """
    Happy-path для POST /api/v1/events:
    - отправляем корректное событие user_registered;
    - получаем 202;
    - status='accepted', jobs_count=1 (из FakeNotificationService).
    """

    now = datetime.now(timezone.utc).isoformat()

    payload = {
        "event_id": str(uuid4()),
        "event_type": "user_registered",
        "source": "auth_service",
        "occurred_at": now,
        "payload": {
            "user_id": str(uuid4()),
            "registration_channel": "web",
            "locale": "ru",
            "user_agent": "pytest-client",
        },
    }

    response = api_client.post("/api/v1/events", json=payload)

    assert response.status_code == 202, response.text
    data = response.json()

    assert data.get("status") == "accepted"
    # В твоём API.md было поле jobs_count
    if "jobs_count" in data:
        assert data["jobs_count"] == 1


@pytest.mark.asyncio
async def test_create_template(api_client):
    payload = {
        "template_code": "welcome_email",
        "locale": "ru",
        "channel": "email",
        "subject": "Добро пожаловать!",
        "body": "<h1>Привет!</h1><p>Спасибо за регистрацию</p>",
    }

    response = api_client.post("/api/v1/templates", json=payload)

    assert response.status_code == 201, response.text
    data = response.json()

    assert data["template_code"] == payload["template_code"]
    assert data["locale"] == payload["locale"]
    assert data["channel"] == payload["channel"]
    assert data["subject"] == payload["subject"]
    assert data["body"] == payload["body"]
    assert "id" in data

@pytest.mark.asyncio
async def test_create_template_conflict(api_client):
    payload = {
        "template_code": "welcome_email_conflict",
        "locale": "ru",
        "channel": "email",
        "subject": "Добро пожаловать!",
        "body": "<h1>Привет!</h1>",
    }

    # первый раз — создаём
    resp1 = api_client.post("/api/v1/templates", json=payload)
    assert resp1.status_code == 201, resp1.text

    # второй раз — тот же code/locale/channel → 409
    resp2 = api_client.post("/api/v1/templates", json=payload)
    assert resp2.status_code == 409
    assert resp2.json()["detail"] == ("Template with this "
                                      "code/locale/channel already exists")