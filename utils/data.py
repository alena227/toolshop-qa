"""Генераторы тестовых данных.

Идея: есть один «правильный» пользователь, а тест меняет в нём только то,
что проверяет. Так в тесте видно главное, а не 15 полей формы.
"""
import uuid
from datetime import date, timedelta


def unique_email() -> str:
    """Новый email на каждый вызов: повторная регистрация вернула бы 409."""
    return f"qa_{uuid.uuid4().hex[:10]}@example.com"


def years_ago(years: int, days: int = 0) -> str:
    """Дата рождения `years` лет назад, сдвинутая на `days` дней, в формате YYYY-MM-DD.

    years_ago(18)          -> ровно 18 лет сегодня
    years_ago(18, days=1)  -> 18 лет исполнится только завтра (ещё 17)
    years_ago(18, days=-1) -> 18 лет исполнилось вчера
    """
    today = date.today()
    try:
        birthday = today.replace(year=today.year - years)
    except ValueError:
        # Сегодня 29 февраля, а в том году его не было — берём 28-е
        birthday = today.replace(year=today.year - years, day=28)
    return (birthday + timedelta(days=days)).isoformat()


def make_user(**overrides) -> dict:
    """Валидные данные для регистрации. Любое поле можно переопределить.

    make_user()                      -> корректный пользователь
    make_user(first_name="A" * 41)   -> всё корректно, кроме имени
    make_user(password=None)         -> поле password вообще не отправляется
    """
    user = {
        "first_name": "Test",
        "last_name": "User",
        "email": unique_email(),
        "password": "Toolshop#Qa2026",
        "dob": "1990-01-01",
        "phone": "0987654321",
        "address": {
            "street": "Test street 1",
            "city": "Moscow",
            "state": "Moscow",
            "country": "RU",
            "postal_code": "101000",
        },
    }
    user.update(overrides)
    # None означает «не отправлять поле» — так проверяются обязательные поля
    return {key: value for key, value in user.items() if value is not None}
