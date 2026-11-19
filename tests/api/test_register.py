import uuid

import allure
import pytest

from utils.data import make_user, unique_email, years_ago


def _unique() -> str:
    """Короткая случайная строка: подставляется в email, чтобы тест можно было
    запускать сколько угодно раз и не упираться в «email уже занят» (409)."""
    return uuid.uuid4().hex[:10]


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

    @allure.title("Регистрация с минимально допустимым паролем и последующий вход")
    def test_register_with_minimum_valid_password_and_login(self, api):
        password = "Xq7#vB2k"
        user = make_user(password=password)

        response = api.register(user)

        assert response.status_code == 201, response.text
        assert "password" not in response.json(), "Пароль не должен возвращаться в ответе"

        login_response = api.login(user["email"], password)
        assert login_response.status_code == 200, login_response.text

    @allure.title("Недопустимый пароль: {case}")
    @pytest.mark.parametrize(
        "case, password",
        [
            pytest.param("7 символов", "Xq7#vB2", id="7-chars"),
            pytest.param("без цифры", "Xq#vBzkm", id="no-digit"),
            pytest.param("без спецсимвола", "Xq7vB2km", id="no-symbol"),
            pytest.param("без заглавной", "xq7#vb2k", id="no-upper"),
            pytest.param("без строчной", "XQ7#VB2K", id="no-lower"),
            pytest.param("только цифры", "1234567890", id="digits-only"),
        ],
    )
    def test_register_with_invalid_password(self, api, case, password):
        user = make_user(password=password)

        response = api.register(user)

        assert response.status_code == 422, response.text
        assert "password" in response.json(), "В ответе нет ошибки для поля password"

    @allure.title("Пароль из базы утечек отклоняется с понятной причиной")
    def test_register_with_leaked_password(self, api):
        user = make_user(password="Password1!")

        response = api.register(user)

        assert response.status_code == 422, response.text
        assert "data leak" in response.text, "Пароль отклонён не из-за утечки"

    @allure.title("Повторная регистрация с тем же email отклоняется")
    def test_register_with_duplicate_email(self, api):
        first = make_user()
        first_response = api.register(first)
        assert first_response.status_code == 201, first_response.text

        duplicate = make_user(email=first["email"])
        response = api.register(duplicate)

        assert response.status_code == 409, response.text

    @allure.title("Email сравнивается без учёта регистра")
    def test_register_with_duplicate_email_in_different_case(self, api):
        name = f"Test_{_unique()}"
        first = make_user(email=f"{name}@Example.com")
        first_response = api.register(first)
        assert first_response.status_code == 201, first_response.text

        duplicate = make_user(email=f"{name.lower()}@example.com")
        response = api.register(duplicate)

        assert response.status_code == 409, response.text

    @allure.title("Невалидный формат email: {case}")
    @pytest.mark.xfail(
        reason="L-05: сервер не проверяет формат email (в правилах нет 'email')",
        strict=True,
    )
    @pytest.mark.parametrize(
        # {u} в шаблоне заменяется на случайную строку, чтобы email был уникальным
        "case, template",
        [
            pytest.param("нет @", "qa{u}.example.com", id="no-at"),
            pytest.param("нет домена", "qa{u}@", id="no-domain"),
            pytest.param("нет имени", "@{u}.example.com", id="no-name"),
            pytest.param("пробел внутри", "qa {u}@example.com", id="space"),
            pytest.param("два @", "qa{u}@@example.com", id="two-at"),
        ],
    )
    def test_register_with_invalid_email_format(self, api, case, template):
        email = template.format(u=_unique())
        user = make_user(email=email)

        response = api.register(user)

        assert response.status_code == 422, response.text
        assert "email" in response.json(), "В ответе нет ошибки для поля email"

    @allure.title("Граница длины email: {length}")
    @pytest.mark.parametrize(
        "length, expected_status",
        [
            pytest.param(256, 201, id="256-valid"),
            pytest.param(257, 422, id="257-invalid"),
        ],
    )
    def test_register_with_email_length_boundary(self, api, length, expected_status):
        base = unique_email()
        email = "a" * (length - len(base)) + base
        assert len(email) == length

        user = make_user(email=email)
        response = api.register(user)

        assert response.status_code == expected_status, response.text



