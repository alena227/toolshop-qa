from playwright.sync_api import expect

from pages.base_page import BasePage


class ProductPage(BasePage):
    """Карточка товара."""

    def __init__(self, page, base_url: str, product_id: str = ""):
        super().__init__(page, base_url)
        self.path = f"/product/{product_id}"

    @property
    def name(self):
        return self.by_test_id("product-name")

    @property
    def price(self):
        return self.by_test_id("unit-price")

    @property
    def quantity(self):
        return self.by_test_id("quantity")

    @property
    def increase_button(self):
        return self.by_test_id("increase-quantity")

    @property
    def decrease_button(self):
        return self.by_test_id("decrease-quantity")

    @property
    def add_to_cart_button(self):
        return self.by_test_id("add-to-cart")

    @property
    def add_to_favorites_button(self):
        return self.by_test_id("add-to-favorites")

    def open(self):
        super().open()
        expect(self.name).to_be_visible()
        return self

    def set_quantity(self, value: int) -> None:
        self.quantity.fill(str(value))

    def add_to_cart(self) -> None:
        """Добавляет товар и ждёт, пока счётчик корзины в шапке увеличится.

        Без ожидания тест может перейти в корзину раньше, чем запрос на сервер
        завершится, и увидеть пустую корзину.
        """
        quantity = int(self.quantity.input_value() or 1)
        before = int(self.cart_counter.inner_text()) if self.cart_counter.is_visible() else 0
        self.add_to_cart_button.click()
        expect(self.cart_counter).to_have_text(str(before + quantity))
