import allure
import pytest

from utils.data import make_user, years_ago


@allure.feature("API: Регистрация")
@pytest.mark.api
class TestRegister:

    # ---------- ПРИМЕР 1: позитивный тест ----------

    @allure.title("Регистрация с валидными данными")
    @pytest.mark.smoke
    def test_register_with_valid_data(self, api):
        user = make_user()

        response = api.register(user)

        assert response.status_code == 201, response.text
        body = response.json()
        assert body["email"] == user["email"]
        assert body["id"], "В ответе нет id нового пользователя"
        assert "password" not in body, "Пароль не должен возвращаться в ответе"

    # ---------- ПРИМЕР 2: параметризованный негативный тест ----------

    @allure.title("Обязательное поле не отправлено: {field}")
    @pytest.mark.parametrize("field", ["first_name", "last_name", "email", "password"])
    def test_register_without_required_field(self, api, field):
        user = make_user(**{field: None})  # None = поле не отправляется

        response = api.register(user)

        # По Swagger код ошибки валидации не описан (см. RI-001),
        # ожидаем стандартный для Laravel 422
        assert response.status_code == 422, response.text
        assert field in response.json(), f"В ответе нет ошибки для поля {field}"

    @allure.title("Граничная допустимая длина поля {field}: {length}")
    @pytest.mark.parametrize(
        "field, length",
        [("first_name", 40), ("last_name", 20)],
        ids=["first_name-40", "last_name-20"],
    )
    def test_register_with_maximum_name_length(self, api, field, length):
        user = make_user(**{field: "A" * length})

        response = api.register(user)

        assert response.status_code == 201, response.text
        assert response.json()[field] == "A" * length, "Имя сохранилось не целиком"

    @allure.title("Превышение максимальной длины поля {field}: {length}")
    @pytest.mark.parametrize(
        "field, length",
        [("first_name", 41), ("last_name", 21)],
        ids=["first_name-41", "last_name-21"],
    )
    def test_register_with_name_length_over_limit(self, api, field, length):
        user = make_user(**{field: "A" * length})

        response = api.register(user)

        assert response.status_code == 422, response.text
        assert field in response.json(), f"В ответе нет ошибки для поля {field}"



