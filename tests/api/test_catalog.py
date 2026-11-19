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

    @allure.title("Сортировка каталога работает")
    @pytest.mark.parametrize(
        ("sort", "field", "reverse"),
        [
            ("name,asc", "name", False),
            ("name,desc", "name", True),
            ("price,asc", "price", False),
            ("price,desc", "price", True),
        ],
    )
    def test_products_sort(self, api, sort, field, reverse):
        response = api.get("/products", params={"sort": sort})

        assert response.status_code == 200
        products = response.json()["data"]
        values = [product[field] for product in products]
        if field == "name":
            assert values == sorted(values, key=str.lower, reverse=reverse)
        else:
            assert values == sorted(values, reverse=reverse)

    @allure.title("Фильтр каталога по бренду")
    def test_products_filter_by_brand(self, api):
        brands = api.get("/brands").json()
        assert brands, "Список брендов пуст"
        brand_id = brands[0]["id"]

        response = api.get("/products", params={"by_brand": brand_id})

        assert response.status_code == 200
        products = response.json()["data"]
        assert products, "Для выбранного бренда нет товаров"
        assert all(product["brand"]["id"] == brand_id for product in products)

    @allure.title("Фильтр каталога по категории")
    def test_products_filter_by_category(self, api):
        categories = api.get("/categories").json()
        # Категории двухуровневые: товары лежат только в подкатегориях
        # (Hammer, Pliers...), у родительских (Hand Tools...) parent_id пустой
        subcategories = [c for c in categories if c.get("parent_id")]
        assert subcategories, "Нет ни одной подкатегории"
        category_id = subcategories[0]["id"]

        response = api.get("/products", params={"by_category": category_id})

        assert response.status_code == 200
        products = response.json()["data"]
        assert products, "Для выбранной категории нет товаров"
        assert all(product["category"]["id"] == category_id for product in products)

    @allure.title("Фильтр каталога по диапазону цен")
    def test_products_filter_by_price_range(self, api):
        response = api.get("/products", params={"between": "price,10,30"})

        assert response.status_code == 200
        assert all(10 <= product["price"] <= 30 for product in response.json()["data"])

    @allure.title("Фильтр цены включает граничное значение")
    def test_products_price_range_includes_boundary(self, api):
        product = api.get("/products").json()["data"][0]
        price = product["price"]

        response = api.get(
            "/products", params={"between": f"price,{price},{price}"}
        )

        assert response.status_code == 200
        assert any(item["id"] == product["id"] for item in response.json()["data"])

    @allure.title("Поиск находит товары без учёта регистра")
    def test_product_search(self, api):
        response = api.get("/products/search", params={"q": "hammer"})

        assert response.status_code == 200
        products = response.json()["data"]
        assert products, "По запросу hammer ничего не найдено"
        assert all("hammer" in product["name"].lower() for product in products)

    @allure.title("Поиск по несуществующему слову возвращает пустой результат")
    def test_product_search_no_matches(self, api):
        response = api.get("/products/search", params={"q": "zzzqqq"})

        assert response.status_code == 200
        body = response.json()
        assert body["data"] == []
        assert body["total"] == 0

    @allure.title("Поиск устойчив к специальным и длинным запросам")
    @pytest.mark.parametrize("query", ["%", "' OR 1=1 --", "a" * 1000])
    def test_product_search_unusual_queries(self, api, query):
        response = api.get("/products/search", params={"q": query})

        assert response.status_code == 200

    @allure.title("Пустой запрос поиска обрабатывается без ошибки сервера")
    def test_product_search_empty_query(self, api):
        response = api.get("/products/search", params={"q": ""})

        assert response.status_code == 200

    @allure.title("Страница каталога за последней пустая")
    def test_products_page_after_last_is_empty(self, api):
        first_page = api.get("/products", params={"page": 1})
        assert first_page.status_code == 200
        last_page = first_page.json()["last_page"]

        response = api.get("/products", params={"page": last_page + 1})

        assert response.status_code == 200
        assert response.json()["data"] == []

    @allure.title("На странице каталога не больше девяти товаров")
    def test_products_page_size(self, api):
        response = api.get("/products", params={"page": 1})

        assert response.status_code == 200
        assert len(response.json()["data"]) <= 9
