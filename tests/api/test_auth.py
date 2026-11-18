import allure
import pytest

from utils import config


@allure.feature("API: Авторизация")
@pytest.mark.api
class TestLogin:

    @allure.title("Логин с валидными данными возвращает токен")
    @pytest.mark.smoke
    def test_login_with_valid_credentials(self, api):
        response = api.login(config.USER_EMAIL, config.USER_PASSWORD)

        assert response.status_code == 200
        body = response.json()
        assert body.get("access_token"), "В ответе нет access_token"
        assert body.get("token_type", "").lower() == "bearer"

    @allure.title("Логин с неверным паролем: {password!r}")
    @pytest.mark.parametrize(
        "password",
        ["wrong_password", "WELCOME01", "welcome0", ""],
        ids=["wrong", "upper_case", "one_char_less", "empty"],
    )
    def test_login_with_invalid_password(self, api, new_user, password):
        response = api.login(new_user["email"], password)

        # Вход не должен пройти ни при каком неверном пароле
        assert response.status_code in (401, 422)
        assert "access_token" not in response.json()

    @allure.title("Логин несуществующего пользователя")
    def test_login_with_unknown_email(self, api):
        response = api.login("no_such_user_123@example.com", "welcome01")

        assert response.status_code == 401


@allure.feature("API: Профиль")
@pytest.mark.api
class TestProfile:

    @allure.title("/users/me возвращает данные залогиненного пользователя")
    @pytest.mark.smoke
    def test_me_returns_current_user(self, auth_api):
        response = auth_api.get("/users/me")

        assert response.status_code == 200
        assert response.json()["email"] == config.USER_EMAIL

    @allure.title("/users/me без токена недоступен")
    def test_me_without_token_is_unauthorized(self, api):
        response = api.get("/users/me")

        assert response.status_code == 401
