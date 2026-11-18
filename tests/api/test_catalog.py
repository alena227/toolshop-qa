import allure
import pytest
from jsonschema import validate

BRAND_SCHEMA = {
    "type": "object",
    "required": ["id", "name", "slug"],
    "properties": {
        "id": {"type": "string"},
        "name": {"type": "string", "minLength": 1},
        "slug": {"type": "string", "minLength": 1},
    },
}


@allure.feature("API: Каталог")
@pytest.mark.api
class TestBrands:

    @allure.title("Список брендов отдаётся и соответствует схеме")
    @pytest.mark.smoke
    def test_get_brands(self, api):
        response = api.get("/brands")

        assert response.status_code == 200
        brands = response.json()
        assert isinstance(brands, list) and brands, "Список брендов пуст"
        for brand in brands:
            validate(instance=brand, schema=BRAND_SCHEMA)

    @allure.title("Несуществующий бренд → 404")
    def test_get_unknown_brand(self, api):
        response = api.get("/brands/does-not-exist-000")

        assert response.status_code == 404


@allure.feature("API: Каталог")
@pytest.mark.api
class TestProducts:

    @allure.title("Первая страница каталога содержит товары")
    @pytest.mark.smoke
    def test_products_first_page(self, api):
        response = api.get("/products", params={"page": 1})

        assert response.status_code == 200
        body = response.json()
        assert body["data"], "На первой странице нет товаров"
        for product in body["data"]:
            assert product["name"]
            assert product["price"] > 0, f"Цена должна быть положительной: {product}"

    @allure.title("Карточка товара совпадает с данными из списка")
    def test_product_details_match_list(self, api):
        first = api.get("/products").json()["data"][0]

        response = api.get(f"/products/{first['id']}")

        assert response.status_code == 200
        details = response.json()
        assert details["id"] == first["id"]
        assert details["name"] == first["name"]
        assert details["price"] == first["price"]

    # TODO(Алёна): добавь тесты на поиск /products/search?q=..., фильтр по бренду
    # и категории, сортировку по цене. Используй классы эквивалентности
    # и граничные значения: пустой запрос, 1 символ, очень длинная строка, спецсимволы.
