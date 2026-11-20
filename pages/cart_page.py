from pages.base_page import BasePage


class CartPage(BasePage):
    """Первый шаг оформления заказа — корзина."""

    path = "/checkout"

    @property
    def product_titles(self):
        return self.by_test_id("product-title")

    @property
    def quantities(self):
        return self.by_test_id("product-quantity")

    @property
    def line_prices(self):
        return self.by_test_id("line-price")

    @property
    def total(self):
        return self.by_test_id("cart-total")

    @property
    def remove_buttons(self):
        # У кнопки удаления нет data-test (только CSS-класс), поэтому локатор хрупкий
        return self.page.locator("a.btn-danger")

    @property
    def proceed_button(self):
        return self.by_test_id("proceed-1")

    def titles(self) -> list[str]:
        return [title.strip() for title in self.product_titles.all_inner_texts()]

    def remove(self, index: int = 0) -> None:
        self.remove_buttons.nth(index).click()
