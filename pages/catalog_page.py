from playwright.sync_api import expect

from pages.base_page import BasePage


class CatalogPage(BasePage):
    """Главная страница: каталог, поиск, сортировка."""

    path = "/"

    @property
    def search_input(self):
        return self.by_test_id("search-query")

    @property
    def search_button(self):
        return self.by_test_id("search-submit")

    @property
    def search_reset(self):
        return self.by_test_id("search-reset")

    @property
    def search_caption(self):
        return self.by_test_id("search-caption")

    @property
    def no_results(self):
        return self.by_test_id("no-results")

    @property
    def sort_select(self):
        return self.by_test_id("sort")

    @property
    def product_names(self):
        return self.by_test_id("product-name")

    @property
    def product_prices(self):
        return self.by_test_id("product-price")

    def open(self):
        super().open()
        expect(self.product_names.first).to_be_visible()
        return self

    def search(self, term: str) -> None:
        """Ищет и ждёт, пока на странице окажутся именно результаты поиска.

        Без ожидания тест успевает прочитать старый список товаров: заголовок
        «Searched for» появляется раньше, чем обновляются карточки.
        """
        self.search_input.fill(term)
        with self.page.expect_response(lambda r: "/products/search" in r.url) as response_info:
            self.search_button.click()
        found = len(response_info.value.json()["data"])
        # Ждём, пока число карточек на странице совпадёт с ответом сервера
        expect(self.product_names).to_have_count(found)

    def sort_by(self, value: str) -> None:
        """Выбирает сортировку и ждёт, пока на странице окажется новый порядок.

        value — значение опции, например 'name,asc' или 'price,desc'.
        Ждём ответ сервера и то, что первая карточка совпала с первым товаром из ответа:
        это надёжнее, чем ждать «первый товар изменился» — он может и не измениться.
        """
        # Сайт отправляет сортировку методом QUERY с параметрами в теле запроса,
        # поэтому в адресе нет «sort=» — ловим любой ответ от /products
        with self.page.expect_response(lambda r: r.url.endswith("/products")) as response_info:
            self.sort_select.select_option(value)
        first = response_info.value.json()["data"][0]["name"]
        expect(self.product_names.first).to_have_text(first)

    def names(self) -> list[str]:
        return self.product_names.all_inner_texts()

    def open_product(self, name: str) -> None:
        self.product_names.filter(has_text=name).first.click()
