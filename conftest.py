import pytest

from utils import config
from utils.api_client import ApiClient
from utils.data import make_user


@pytest.fixture(scope="session")
def api() -> ApiClient:
    """Клиент без авторизации — для публичных эндпоинтов."""
    return ApiClient(config.API_URL, timeout=config.API_TIMEOUT)


@pytest.fixture(scope="session")
def user_token(api: ApiClient) -> str:
    """Один логин на весь прогон, чтобы не долбить API лишними запросами."""
    response = api.login(config.USER_EMAIL, config.USER_PASSWORD)
    assert response.status_code == 200, f"Не удалось залогиниться: {response.text}"
    return response.json()["access_token"]


@pytest.fixture
def auth_api(user_token: str) -> ApiClient:
    """Отдельный клиент с токеном пользователя."""
    client = ApiClient(config.API_URL, timeout=config.API_TIMEOUT)
    client.set_token(user_token)
    return client


# Настройки Playwright: базовый адрес сайта для page.goto("/...")
@pytest.fixture(scope="session")
def base_url() -> str:
    return config.BASE_URL


@pytest.fixture
def new_user(api: ApiClient) -> dict:
    """Свежий пользователь для каждого теста: его не жалко заблокировать."""
    user = make_user()
    response = api.register(user)
    assert response.status_code == 201, f"Не удалось зарегистрироваться: {response.text}"
    return user


@pytest.fixture
def shopper(api: ApiClient) -> dict:
    """Пользователь, который может оформить заказ.

    Оформление заказа сверяет адрес со справочником индексов магазина, а тот выдаёт
    выдуманные города (см. L-08). Поэтому адрес берём прямо из справочника —
    иначе заказ отклоняется с 422.
    """
    country, postcode = "NL", "1012AB"
    lookup = api.get("/postcode-lookup", params={"country": country, "postcode": postcode, "house_number": "1"})
    assert lookup.status_code == 200, lookup.text
    found = lookup.json()
    user = make_user(address={
        "street": found["street"],
        "house_number": "1",
        "city": found["city"],
        "state": found["state"],
        "country": country,
        "postal_code": postcode,
    })
    response = api.register(user)
    assert response.status_code == 201, f"Не удалось зарегистрироваться: {response.text}"
    return user


@pytest.fixture
def cart_id(api: ApiClient) -> str:
    """Новая пустая корзина для каждого теста."""
    response = api.create_cart()
    assert response.status_code == 201, f"Не удалось создать корзину: {response.text}"
    return response.json()["id"]


@pytest.fixture(scope="session")
def products(api: ApiClient) -> list[dict]:
    """Несколько товаров из каталога (первая страница), берутся один раз на прогон."""
    response = api.get("/products", params={"page": 1})
    assert response.status_code == 200, response.text
    items = response.json()["data"]
    assert len(items) >= 2, "Для тестов корзины нужно хотя бы два товара"
    return items