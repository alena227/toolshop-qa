import pytest
import uuid

from utils import config
from utils.api_client import ApiClient


@pytest.fixture(scope="session")
def api() -> ApiClient:
    """Клиент без авторизации — для публичных эндпоинтов."""
    return ApiClient(config.API_URL)


@pytest.fixture(scope="session")
def user_token(api: ApiClient) -> str:
    """Один логин на весь прогон, чтобы не долбить API лишними запросами."""
    response = api.login(config.USER_EMAIL, config.USER_PASSWORD)
    assert response.status_code == 200, f"Не удалось залогиниться: {response.text}"
    return response.json()["access_token"]


@pytest.fixture
def auth_api(user_token: str) -> ApiClient:
    """Отдельный клиент с токеном пользователя."""
    client = ApiClient(config.API_URL)
    client.set_token(user_token)
    return client


# Настройки Playwright: базовый адрес сайта для page.goto("/...")
@pytest.fixture(scope="session")
def base_url() -> str:
    return config.BASE_URL


@pytest.fixture
def new_user(api: ApiClient) -> dict:
    """Свежий пользователь для каждого теста: его не жалко заблокировать."""
    user = {
        "first_name": "Test",
        "last_name": "User",
        "email": f"qa_{uuid.uuid4().hex[:10]}@example.com",
        "password": "Toolshop#Qa2026",
        "dob": "1990-01-01",
        "phone": "0987654321",
        "address": {
            "street": "Test street 1",
            "city": "Moscow",
            "state": "Moscow",
            "country": "RU",
            "postal_code": "101000",
        },
    }
    response = api.register(user)
    assert response.status_code == 201, f"Не удалось зарегистрироваться: {response.text}"
    return user