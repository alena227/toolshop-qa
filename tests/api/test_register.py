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

    # ---------- ДАЛЬШЕ ПИШЕШЬ ТЫ ----------
    #
    # TODO(Алёна): граничные значения длины (Swagger, схема UserRequest)
    #   - first_name: 40 символов → 201, 41 символ → 422
    #   - last_name:  20 символов → 201, 21 символ → 422
    #   Подсказка: make_user(first_name="A" * 40)
    #
    # TODO(Алёна): возраст «от 18 до 75 лет» (Swagger, поле dob)
    #   - ровно 18 лет               years_ago(18)          → 201
    #   - 18 лет исполнится завтра   years_ago(18, days=1)  → 422
    #   - ровно 75 лет               years_ago(75)          → 201?
    #   - 75 лет и один день         years_ago(75, days=-1) → 422?
    #   Вопрос: включительна ли граница 75? Это тоже находка для requirements-issues.
    #
    # TODO(Алёна): правила пароля (заглавная, строчная, цифра, спецсимвол, минимум 8)
    #   - "Abcdef1!" (ровно 8)        → 201
    #   - "Abcde1!"  (7 символов)     → 422
    #   - без цифры, без спецсимвола, без заглавной, без строчной → 422
    #   - "1234567890" (W-31 на версии с багами) → 422
    #   Подсказка: один тест с parametrize на все негативные пароли, ids=[...]
    #
    # TODO(Алёна): email
    #   - уже зарегистрированный email → 409 (Swagger) — подсказка: зарегистрируй
    #     пользователя дважды с одним и тем же email
    #   - невалидный формат: "no-at-sign", "a@", "@b.com" → 422
