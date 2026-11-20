import re

import allure
import pytest
from playwright.sync_api import expect

from pages.catalog_page import CatalogPage
from pages.checkout_page import CheckoutPage
from pages.product_page import ProductPage


@allure.feature("UI: Оформление заказа")
@pytest.mark.ui
class TestCheckoutUI:

    # ---------- ПРИМЕР: полный сценарий заказа ----------

    @allure.title("Заказ с оплатой при получении оформляется, показывается номер счёта")
    @pytest.mark.smoke
    def test_checkout_with_cash_on_delivery(self, page, base_url, shopper):
        CatalogPage(page, base_url).open().open_product("Combination Pliers")
        ProductPage(page, base_url).add_to_cart()

        checkout = CheckoutPage(page, base_url).open()
        checkout.proceed_from_cart()
        checkout.sign_in(shopper["email"], shopper["password"])
        checkout.proceed_from_address()
        checkout.pay("cash-on-delivery")
        checkout.confirm()

        expect(checkout.order_confirmation).to_contain_text("Thanks for your order")
        expect(checkout.order_confirmation).to_contain_text(re.compile(r"INV-\d+"))

    def _start_checkout(self, page, base_url, shopper):
        CatalogPage(page, base_url).open().open_product("Combination Pliers")
        ProductPage(page, base_url).add_to_cart()

        checkout = CheckoutPage(page, base_url).open()
        checkout.proceed_from_cart()
        checkout.sign_in(shopper["email"], shopper["password"])
        checkout.proceed_from_address()
        return checkout

    @pytest.mark.parametrize(
        ("method", "fields"),
        [
            (
                "bank-transfer",
                {
                    "bank_name": "Example Bank",
                    "account_name": "Test Shopper",
                    "account_number": "123456789012",
                },
            ),
            (
                "credit-card",
                {
                    # Форматы задаёт форма: номер с дефисами, срок MM/YYYY
                    "credit_card_number": "4111-1111-1111-1111",
                    "expiration_date": "12/2030",
                    "cvv": "123",
                    "card_holder_name": "Test Shopper",
                },
            ),
            (
                "gift-card",
                # Номер — 16 букв/цифр, код проверки — ровно 4
                {"gift_card_number": "1234567890123456", "validation_code": "1234"},
            ),
            ("buy-now-pay-later", {"monthly_installments": "3"}),
        ],
    )
    def test_checkout_with_alternative_payment(self, page, base_url, shopper, method, fields):
        checkout = self._start_checkout(page, base_url, shopper)
        checkout.pay(method)

        for field, value in fields.items():
            control = page.locator(f'[data-test="{field}"]')
            if field == "monthly_installments":
                control.select_option(value)
            else:
                control.fill(value)

        checkout.confirm()
        expect(checkout.order_confirmation).to_contain_text("Thanks for your order")
        expect(checkout.order_confirmation).to_contain_text(re.compile(r"INV-\d+"))

    @allure.title("Неверные данные карты не позволяют оплатить заказ: {case}")
    @pytest.mark.parametrize(
        ("case", "card_number", "expiration_date"),
        [
            pytest.param("короткий номер", "4111-1111", "12/2030", id="short-number"),
            pytest.param("номер без дефисов", "4111111111111111", "12/2030", id="no-dashes"),
            pytest.param("срок в прошлом", "4111-1111-1111-1111", "01/2020", id="expired-card"),
            pytest.param("год из 2 цифр", "4111-1111-1111-1111", "12/30", id="short-year"),
        ],
    )
    def test_invalid_credit_card_is_rejected(
        self, page, base_url, shopper, case, card_number, expiration_date
    ):
        checkout = self._start_checkout(page, base_url, shopper)
        checkout.pay("credit-card")
        page.locator('[data-test="credit_card_number"]').fill(card_number)
        page.locator('[data-test="expiration_date"]').fill(expiration_date)
        page.locator('[data-test="cvv"]').fill("123")
        page.locator('[data-test="card_holder_name"]').fill("Test Shopper")

        # Форма не даёт отправить неверные данные: кнопка оплаты остаётся неактивной
        expect(checkout.finish_button).to_be_disabled()
        expect(checkout.order_confirmation).not_to_be_visible()

    def test_confirmed_order_is_listed_in_my_invoices(self, page, base_url, shopper):
        checkout = self._start_checkout(page, base_url, shopper)
        checkout.pay("cash-on-delivery")
        checkout.confirm()

        expect(checkout.order_confirmation).to_contain_text("Thanks for your order")
        invoice_number = re.search(
            r"INV-\d+", checkout.order_confirmation.inner_text()
        ).group(0)
        # «My invoices» спрятан в выпадающем меню пользователя — сначала открываем меню
        page.locator('[data-test="nav-menu"]').click()
        page.locator('[data-test="nav-my-invoices"]').click()
        expect(page.get_by_text(invoice_number, exact=True)).to_be_visible()

    @allure.title("Если сервер отклонил заказ, пользователь видит сообщение об ошибке")
    @pytest.mark.xfail(
        reason="L-07: при 422 от POST /invoices сайт не показывает ни ошибки, ни подтверждения",
        strict=True,
    )
    def test_rejected_order_shows_error(self, page, base_url, new_user):
        # У new_user адрес Moscow / RU / 101000 — сервер отклонит заказ (см. L-08).
        # Номера дома в его профиле нет, поэтому шаг адреса проходим вручную
        CatalogPage(page, base_url).open().open_product("Combination Pliers")
        ProductPage(page, base_url).add_to_cart()
        checkout = CheckoutPage(page, base_url).open()
        checkout.proceed_from_cart()
        checkout.sign_in(new_user["email"], new_user["password"])
        expect(checkout.field("city")).to_have_value("Moscow")
        checkout.field("house_number").fill("1")
        checkout.proceed_from_address()
        checkout.pay("cash-on-delivery")
        checkout.confirm()

        expect(checkout.order_confirmation).not_to_be_visible()
        expect(page.get_by_text(re.compile(r"error|could not|failed|not valid|does not", re.I))).to_be_visible()
