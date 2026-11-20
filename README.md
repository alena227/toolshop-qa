# Toolshop QA — тестирование интернет-магазина

[![Autotests](https://github.com/alena227/toolshop-qa/actions/workflows/tests.yml/badge.svg)](https://github.com/alena227/toolshop-qa/actions/workflows/tests.yml)

Полный цикл тестирования учебного интернет-магазина
[Practice Software Testing (Toolshop)](https://practicesoftwaretesting.com):
от анализа требований и исследовательского тестирования до автотестов API и UI с CI.

**Стек:** Python · pytest · requests · Playwright · Allure · jsonschema · Docker · GitHub Actions

## Результаты

- **Найдено 46 дефектов**, из них **3 критичных** и **20 серьёзных** (Major) — полный список в [журнале дефектов](bugs/bug-log.md)
- **80 автотестов** (78 API + 2 UI), покрыто **14 эндпоинтов** API: регистрация, авторизация, каталог (сортировка, фильтры, поиск, пагинация), корзина
- **6 дефектов в версии магазина без намеренных багов**, 5 из них нашли автотесты — подробнее ниже
- **7 подробных баг-репортов** в [GitHub Issues](https://github.com/alena227/toolshop-qa/issues): шаги воспроизведения, ожидаемый и фактический результат, скриншоты, запросы и ответы API
- **8 вопросов к требованиям** по документации API — [requirements-issues.md](docs/requirements-issues.md)
- **CI на каждый push и ежедневно:** магазин поднимается в Docker с нуля прямо в GitHub Actions, полный цикл занимает меньше 5 минут

### Дефекты в версии без намеренных багов

Эти дефекты найдены в **чистой** версии магазина, где намеренных багов нет. Большую часть
нашли автотесты: тесты на граничные
значения и классы эквивалентности поймали то, что при ручной проверке легко пропустить.
Каждый тест помечен `xfail` со ссылкой на дефект: он описывает правильное поведение и сообщит,
когда баг исправят.

| Дефект | Как найден | Severity |
|---|---|---|
| Верхняя граница возраста 93 года вместо 75: объект даты изменяется при вычислении второй границы | граничные значения: 75 лет + 1 день, 92 года | Major |
| Сервер принимает email в любом формате: без `@`, без домена, с пробелом | классы эквивалентности невалидного email | Major |
| Лимит «не больше 99 штук» обходится повторным добавлением: можно набрать 297 штук | граничное значение 99 + сценарий «добавить ещё 1» | Major |
| В день 18-летия регистрация отклоняется | граничное значение: ровно 18 лет | Minor |
| Регистрация отвечает 3–11+ секунд, тесты падали по таймауту | нестабильный тест, замер `--durations` | Minor |
| При ошибке сервера страница регистрации показывает текст `true` вместо сообщения | вручную, причина найдена в коде страницы | Minor |

### Самые серьёзные находки

| Дефект | Severity |
|---|---|
| [После смены пароля в профиле невозможно войти ни с новым, ни со старым паролем](https://github.com/alena227/toolshop-qa/issues/1) | Critical |
| [После сброса пароля невозможно войти, сайт при этом сообщает об успехе](https://github.com/alena227/toolshop-qa/issues/2) | Critical |
| [Заказ оплачивается служебным методом «Errror 304 - Missing Payment Gateway»](https://github.com/alena227/toolshop-qa/issues/4) | Critical |
| [Сортировка по имени и по цене работает в обратную сторону](https://github.com/alena227/toolshop-qa/issues/3) | Major |
| [Итоговая сумма корзины на $0.01 меньше суммы товаров](https://github.com/alena227/toolshop-qa/issues/5) | Major |
| [Регистрация раскрывает подсказку к чужому паролю](https://github.com/alena227/toolshop-qa/issues/6) | Major |
| [Принимается пароль без букв и спецсимволов](https://github.com/alena227/toolshop-qa/issues/7) | Major |

### Проблемы окружения, которые пришлось решить

Отдельно описаны в [docs/notes.md](docs/notes.md): негативные тесты блокировали общий аккаунт,
публичный стенд закрыт защитой Cloudflare от ботов, в CI тесты стартовали раньше, чем магазин был готов,
а на Linux у PHP не было прав на запись кэша. Итог — окружение, которое поднимается с нуля и не зависит
от внешнего стенда.

## Что внутри

```
bugs/                    журнал дефектов и скриншоты
docs/                    тест-план, вопросы к требованиям, заметки, шаблон баг-репорта
pages/                   Page Object для UI-тестов
tests/api/               API-автотесты (pytest + requests)
tests/ui/                UI-автотесты (Playwright)
utils/                   конфиг и API-клиент с логированием в Allure
.github/workflows/       CI: магазин в Docker + прогон тестов на каждый push и раз в день
.github/ISSUE_TEMPLATE/  форма баг-репорта для GitHub Issues
```

## Тестовое окружение

Тесты идут против магазина, поднятого локально в Docker. Публичный стенд для автотестов не подходит:
его UI закрыт защитой от ботов.

```bash
git clone https://github.com/testsmith-io/practice-software-testing.git
cd practice-software-testing
docker compose up -d
docker compose exec -u root laravel-api chown -R www-data:www-data storage bootstrap/cache
docker compose exec laravel-api php artisan migrate:fresh --seed
```

После запуска: сайт — http://localhost:4200, API и Swagger — http://localhost:8091/api/documentation.

Поиск дефектов вёлся вручную на версии с намеренными багами: https://with-bugs.practicesoftwaretesting.com

## Как запустить тесты

```bash
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
cp .env.example .env                 # Windows: copy .env.example .env
```

В `.env` укажи адреса локального магазина:

```
BASE_URL=http://localhost:4200
API_URL=http://localhost:8091
```

```bash
pytest                               # все тесты
pytest -m smoke                      # только smoke
pytest -m api                        # только API
pytest -m ui --headed                # UI с видимым браузером

allure serve allure-results          # открыть отчёт (нужен Allure CLI)
```

---

## План работ

**Исследование и требования**
- [x] Пройти магазин руками, прочитать Swagger
- [x] Выписать неточности и вопросы к требованиям в `docs/requirements-issues.md`
- [ ] Дописать тест-план в `docs/test-plan.md`

**Тест-кейсы и баги**
- [ ] 60–100 тест-кейсов в Qase по техникам тест-дизайна
- [x] Исследовательские сессии на версии with-bugs
- [x] Журнал дефектов и баг-репорты в GitHub Issues

**Postman**
- [ ] Коллекция на основные эндпоинты с автопроверками, экспорт в `postman/`
- [ ] Прогон через Newman

**Автотесты**
- [x] Запустить готовые тесты, починить упавшие
- [x] API: регистрация, поиск, фильтры, сортировка, пагинация, корзина (`/carts`)
- [ ] API: оформление заказа
- [ ] UI: поиск, корзина, оформление заказа — новые Page Object в `pages/`
- [x] Параметризация и негативные кейсы везде, где есть ввод данных

**CI и отчёт**
- [x] Залить на GitHub, добиться зелёного workflow
- [ ] Засечь время ручного регресса и автопрогона
- [ ] Заполнить `docs/test-report.md`
