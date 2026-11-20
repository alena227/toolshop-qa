import os

from dotenv import load_dotenv

load_dotenv()

# По умолчанию — магазин, поднятый локально в Docker: публичный стенд закрыт защитой от ботов
BASE_URL = os.getenv("BASE_URL", "http://localhost:4200")
API_URL = os.getenv("API_URL", "http://localhost:8091")
USER_EMAIL = os.getenv("USER_EMAIL", "customer@practicesoftwaretesting.com")
USER_PASSWORD = os.getenv("USER_PASSWORD", "welcome01")
# Сколько секунд ждать ответа API. Регистрация на локальном стенде занимает до 11+ секунд
# (отправка письма и проверка пароля по базе утечек), поэтому 15 секунд не хватало
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))
