from playwright.sync_api import Page


class BasePage:
    """Общие действия для всех страниц."""

    path = "/"

    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url.rstrip("/")

    def open(self):
        self.page.goto(f"{self.base_url}{self.path}")
        return self

    def by_test_id(self, value: str):
        # В Toolshop элементы помечены атрибутом data-test
        return self.page.locator(f"[data-test='{value}']")

    @property
    def cart_counter(self):
        """Значок с количеством товаров у иконки корзины в шапке (есть на любой странице)."""
        return self.by_test_id("cart-quantity")
