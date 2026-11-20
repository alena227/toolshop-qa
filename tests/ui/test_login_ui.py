import re

import allure
import pytest
from playwright.sync_api import expect

from pages.login_page import LoginPage
from utils import config


@allure.feature("UI: Авторизация")
@pytest.mark.ui
class TestLoginUI:

    @allure.title("Успешный вход ведёт в личный кабинет")
    @pytest.mark.smoke
    def test_successful_login(self, page, base_url):
        login_page = LoginPage(page, base_url).open()

        login_page.login(config.USER_EMAIL, config.USER_PASSWORD)

        expect(page).to_have_url(re.compile(r"/account"))

    @allure.title("Неверный пароль показывает ошибку")
    def test_login_with_wrong_password_shows_error(self, page, base_url):
        login_page = LoginPage(page, base_url).open()

        login_page.login(config.USER_EMAIL, "wrong_password")

        expect(login_page.error).to_be_visible()
        expect(page).to_have_url(re.compile(r"/auth/login"))
