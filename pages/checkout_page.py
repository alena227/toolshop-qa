from playwright.sync_api import expect

from pages.base_page import BasePage


class CheckoutPage(BasePage):
    """Оформление заказа: 4 шага на одной странице /checkout.

    1. Cart → 2. Sign in → 3. Billing Address → 4. Payment
    """

    path = "/checkout"

    # --- шаг 1: корзина ---

    def proceed_from_cart(self) -> None:
        self.by_test_id("proceed-1").click()

    # --- шаг 2: вход ---

    def sign_in(self, email: str, password: str) -> None:
        self.by_test_id("email").fill(email)
        self.by_test_id("password").fill(password)
        self.by_test_id("login-submit").click()
        self.by_test_id("proceed-2").click()

    # --- шаг 3: адрес ---

    def field(self, name: str):
        """Поле адреса: street, house_number, city, state, country, postal_code."""
        return self.by_test_id(name)

    def proceed_from_address(self) -> None:
        # Адрес подставляется из профиля не сразу — ждём, пока кнопка станет активной
        button = self.by_test_id("proceed-3")
        expect(button).to_be_enabled()
        button.click()

    # --- шаг 4: оплата ---

    @property
    def payment_method(self):
        return self.by_test_id("payment-method")

    @property
    def finish_button(self):
        return self.by_test_id("finish")

    @property
    def payment_success(self):
        return self.by_test_id("payment-success-message")

    @property
    def payment_error(self):
        return self.by_test_id("payment-error-message")

    @property
    def order_confirmation(self):
        # Единственный элемент без data-test, у него только id
        return self.page.locator("#order-confirmation")

    def pay(self, method: str) -> None:
        """method — значение опции: bank-transfer, cash-on-delivery, credit-card,
        buy-now-pay-later, gift-card. Для части способов нужны доп. поля — их заполняет тест."""
        self.payment_method.select_option(method)

    def confirm(self) -> None:
        """Первое нажатие проверяет оплату, второе — создаёт заказ."""
        self.finish_button.click()
        expect(self.payment_success).to_be_visible()
        self.finish_button.click()
