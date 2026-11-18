from playwright.sync_api import expect

from pages.base_page import BasePage


class LoginPage(BasePage):
    path = "/auth/login"

    @property
    def email(self):
        return self.by_test_id("email")

    @property
    def password(self):
        return self.by_test_id("password")

    @property
    def submit(self):
        return self.by_test_id("login-submit")

    @property
    def error(self):
        return self.by_test_id("login-error")

    def open(self):
        super().open()
        expect(self.email).to_be_visible()
        return self

    def login(self, email: str, password: str) -> None:
        self.email.fill(email)
        self.password.fill(password)
        self.submit.click()
