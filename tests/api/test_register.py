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

    @allure.title("Допустимый возраст: {case}")
    @pytest.mark.parametrize(
        "case, dob",
        [
            pytest.param(
                "ровно 18 лет", years_ago(18), id="18-exact",
                marks=pytest.mark.xfail(
                    reason="L-02: в день 18-летия регистрация отклоняется (строгое правило before:)",
                    strict=True,
                ),
            ),
            pytest.param("18 лет и один день", years_ago(18, days=-1), id="18-plus-1-day"),
            pytest.param("ровно 75 лет", years_ago(75), id="75-exact"),
            pytest.param("74 года, 75 исполнится завтра", years_ago(75, days=1), id="74-tomorrow-75"),
        ],
    )
    def test_register_with_valid_age(self, api, case, dob):
        user = make_user(dob=dob)

        response = api.register(user)

        assert response.status_code == 201, response.text
        assert response.json()["dob"] == dob, "Дата рождения сохранилась неверно"

    @allure.title("Недопустимый возраст: {case}")
    @pytest.mark.parametrize(
        "case, dob",
        [
            pytest.param("18 исполнится завтра", years_ago(18, days=1), id="17-tomorrow-18"),
            pytest.param(
                "75 лет и один день", years_ago(75, days=-1), id="75-plus-1-day",
                marks=pytest.mark.xfail(
                    reason="L-03: верхняя граница 93 года вместо 75 (subYears меняет объект даты)",
                    strict=True,
                ),
            ),
            pytest.param(
                "92 года", years_ago(92), id="92-years",
                marks=pytest.mark.xfail(
                    reason="L-03: верхняя граница 93 года вместо 75 (subYears меняет объект даты)",
                    strict=True,
                ),
            ),
            pytest.param("дата рождения в будущем", years_ago(-1), id="future-date"),
        ],
    )
    def test_register_with_invalid_age(self, api, case, dob):
        user = make_user(dob=dob)

        response = api.register(user)

        assert response.status_code == 422, response.text
        assert "dob" in response.json(), "В ответе нет ошибки для поля dob"



