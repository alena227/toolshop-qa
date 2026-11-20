import allure
import pytest
from playwright.sync_api import expect

from pages.cart_page import CartPage
from pages.catalog_page import CatalogPage
from pages.product_page import ProductPage


@allure.feature("UI: Каталог")
@pytest.mark.ui
class TestCatalogUI:

    # ---------- ПРИМЕР: поиск ----------

    @allure.title("Поиск показывает только подходящие товары")
    @pytest.mark.smoke
    def test_search_shows_only_matching_products(self, page, base_url):
        catalog = CatalogPage(page, base_url).open()

        catalog.search("hammer")

        expect(catalog.search_caption).to_contain_text("hammer")
        names = catalog.names()
        assert names, "Поиск ничего не нашёл"
        assert all("hammer" in name.lower() for name in names), names

    @allure.title("Поиск несуществующего товара показывает сообщение «нет результатов»")
    def test_search_with_no_results_shows_message(self, page, base_url):
        catalog = CatalogPage(page, base_url).open()

        catalog.search("no-such-product-93847")

        expect(catalog.no_results).to_be_visible()
        assert catalog.names() == []

    @allure.title("Сброс поиска возвращает полный список товаров")
    def test_search_reset_restores_all_products(self, page, base_url):
        catalog = CatalogPage(page, base_url).open()
        all_names = catalog.names()
        assert all_names, "В каталоге нет товаров"

        catalog.search("hammer")
        expect(catalog.search_reset).to_be_visible()
        catalog.search_reset.click()

        expect(catalog.product_names.first).to_have_text(all_names[0])
        assert catalog.names() == all_names

    @allure.title("Сортировка каталога: {option}")
    @pytest.mark.parametrize(
        "option, field, reverse",
        [
            pytest.param("name,asc", "name", False, id="name-a-z"),
            pytest.param("name,desc", "name", True, id="name-z-a"),
            pytest.param("price,asc", "price", False, id="price-low-high"),
            pytest.param("price,desc", "price", True, id="price-high-low"),
        ],
    )
    def test_sort_catalog(self, page, base_url, option, field, reverse):
        catalog = CatalogPage(page, base_url).open()

        catalog.sort_by(option)

        if field == "name":
            names = catalog.names()
            assert names == sorted(names, key=str.lower, reverse=reverse), names
        else:
            prices = [float(price.strip().replace("$", ""))
                      for price in catalog.product_prices.all_text_contents()]
            assert prices == sorted(prices, reverse=reverse), prices


@allure.feature("UI: Корзина")
@pytest.mark.ui
class TestCartUI:

    @allure.title("Добавление товара обновляет счётчик корзины в шапке")
    def test_adding_product_updates_cart_counter(self, page, base_url):
        catalog = CatalogPage(page, base_url).open()
        catalog.open_product("Combination Pliers")
        ProductPage(page, base_url).add_to_cart()

        expect(catalog.cart_counter).to_have_text("1")

    @allure.title("Выбранное количество товара отображается в корзине")
    def test_selected_quantity_is_shown_in_cart(self, page, base_url):
        catalog = CatalogPage(page, base_url).open()
        catalog.open_product("Combination Pliers")
        product = ProductPage(page, base_url)
        product.set_quantity(3)
        product.add_to_cart()

        cart = CartPage(page, base_url).open()
        expect(cart.quantities.first).to_have_value("3")

    @allure.title("Цена строки в корзине равна цене товара × количество")
    def test_cart_line_price_equals_unit_price_times_quantity(self, page, base_url):
        catalog = CatalogPage(page, base_url).open()
        catalog.open_product("Combination Pliers")
        product = ProductPage(page, base_url)
        unit_price = float(product.price.inner_text().strip().replace("$", ""))
        product.set_quantity(3)
        product.add_to_cart()

        cart = CartPage(page, base_url).open()
        line_price = float(cart.line_prices.first.inner_text().strip().replace("$", ""))
        assert line_price == pytest.approx(unit_price * 3)

    @allure.title("Товар удаляется из корзины")
    def test_product_can_be_removed_from_cart(self, page, base_url):
        catalog = CatalogPage(page, base_url).open()
        catalog.open_product("Combination Pliers")
        ProductPage(page, base_url).add_to_cart()

        cart = CartPage(page, base_url).open()
        cart.remove_buttons.first.click()
        expect(cart.product_titles).to_have_count(0)
