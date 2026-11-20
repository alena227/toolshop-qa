import allure
import pytest


def _items(cart: dict) -> dict:
    """Товары корзины в виде {product_id: quantity} — так удобно проверять."""
    return {item["product_id"]: item["quantity"] for item in cart["cart_items"]}


@allure.feature("API: Корзина")
@pytest.mark.api
class TestCart:

    # ---------- ПРИМЕР: добавление товара ----------

    @allure.title("Добавленный товар появляется в корзине с нужным количеством")
    @pytest.mark.smoke
    def test_add_product_to_cart(self, api, cart_id, products):
        product_id = products[0]["id"]

        response = api.add_to_cart(cart_id, product_id, quantity=2)

        assert response.status_code == 200, response.text
        cart = api.get_cart(cart_id).json()
        assert _items(cart) == {product_id: 2}

    @allure.title("Новая корзина пуста")
    def test_new_cart_is_empty(self, api, cart_id):
        cart = api.get_cart(cart_id).json()

        assert cart["cart_items"] == []

    @allure.title("В корзину добавляются два разных товара")
    def test_add_two_different_products(self, api, cart_id, products):
        first_id, second_id = products[0]["id"], products[1]["id"]

        assert api.add_to_cart(cart_id, first_id, quantity=2).status_code == 200
        assert api.add_to_cart(cart_id, second_id, quantity=3).status_code == 200

        assert _items(api.get_cart(cart_id).json()) == {first_id: 2, second_id: 3}

    @allure.title("Количество товара складывается при повторном добавлении")
    def test_adding_same_product_again_sums_quantity(self, api, cart_id, products):
        product_id = products[0]["id"]

        assert api.add_to_cart(cart_id, product_id, quantity=1).status_code == 200
        assert api.add_to_cart(cart_id, product_id, quantity=1).status_code == 200

        assert _items(api.get_cart(cart_id).json())[product_id] == 2

    @allure.title("Количество товара в корзине можно изменить")
    def test_update_cart_quantity(self, api, cart_id, products):
        product_id = products[0]["id"]
        assert api.add_to_cart(cart_id, product_id, quantity=1).status_code == 200

        response = api.update_cart_quantity(cart_id, product_id, quantity=4)

        assert response.status_code == 200, response.text
        assert _items(api.get_cart(cart_id).json()) == {product_id: 4}

    @allure.title("Удаление товара сохраняет остальные товары")
    def test_remove_product_keeps_other_products(self, api, cart_id, products):
        first_id, second_id = products[0]["id"], products[1]["id"]
        assert api.add_to_cart(cart_id, first_id, quantity=1).status_code == 200
        assert api.add_to_cart(cart_id, second_id, quantity=2).status_code == 200

        response = api.remove_from_cart(cart_id, first_id)

        assert response.status_code == 204, response.text
        assert _items(api.get_cart(cart_id).json()) == {second_id: 2}

    @allure.title("Нулевое, отрицательное и чрезмерное количество отклоняется: {quantity}")
    @pytest.mark.parametrize("quantity", [0, -1, 1_000_000])
    def test_add_product_with_invalid_quantity(self, api, cart_id, products, quantity):
        response = api.add_to_cart(cart_id, products[0]["id"], quantity=quantity)

        assert response.status_code == 422, response.text
        assert "quantity" in response.json()["errors"]

    @allure.title("Максимальное количество товара 99 принимается")
    def test_add_product_with_maximum_allowed_quantity(self, api, cart_id, products):
        product_id = products[0]["id"]
        response = api.add_to_cart(cart_id, product_id, quantity=99)

        assert response.status_code == 200, response.text
        assert _items(api.get_cart(cart_id).json()) == {product_id: 99}

    @allure.title("Количество товара больше 99 отклоняется")
    def test_add_product_with_quantity_above_limit(self, api, cart_id, products):
        response = api.add_to_cart(cart_id, products[0]["id"], quantity=100)

        assert response.status_code == 422, response.text
        assert response.json()["errors"]["quantity"] == [
            "The quantity field must not be greater than 99."
        ]

    @allure.title("Повторное добавление не позволяет превысить общий лимит 99")
    @pytest.mark.xfail(
        reason="L-06: лимит 99 проверяет одну операцию, повторным добавлением можно набрать больше",
        strict=True,
    )
    def test_adding_product_again_cannot_exceed_quantity_limit(self, api, cart_id, products):
        product_id = products[0]["id"]
        first_response = api.add_to_cart(cart_id, product_id, quantity=99)
        assert first_response.status_code == 200, first_response.text

        response = api.add_to_cart(cart_id, product_id, quantity=1)

        assert response.status_code == 422, response.text
        assert "quantity" in response.json()["errors"]
        assert _items(api.get_cart(cart_id).json()) == {product_id: 99}

    @allure.title("Несуществующий товар с корректным ID возвращает ошибку product_id")
    def test_add_nonexistent_product(self, api, cart_id):
        response = api.add_to_cart(cart_id, "01AAAAAAAAAAAAAAAAAAAAAAAA", quantity=1)

        assert response.status_code == 422, response.text
        assert response.json()["errors"]["product_id"] == [
            "The selected product id is invalid."
        ]

    @allure.title("ID товара неправильного формата отклоняется")
    def test_add_product_with_malformed_id(self, api, cart_id):
        response = api.add_to_cart(cart_id, "not-a-product-id", quantity=1)

        assert response.status_code == 422, response.text
        assert response.json()["errors"]["product_id"] == [
            "The selected product id is invalid."
        ]

    @allure.title("Несуществующая корзина при GET возвращает 404")
    def test_get_nonexistent_cart(self, api):
        response = api.get_cart("01AAAAAAAAAAAAAAAAAAAAAAAA")

        assert response.status_code == 404, response.text
        assert response.json()["message"] == "Requested item not found"

    @allure.title("Добавление товара в несуществующую корзину возвращает 404")
    def test_add_product_to_nonexistent_cart(self, api, products):
        response = api.add_to_cart(
            "01AAAAAAAAAAAAAAAAAAAAAAAA", products[0]["id"], quantity=1
        )

        assert response.status_code == 404, response.text
        assert response.json()["message"] == "Cart not found"
