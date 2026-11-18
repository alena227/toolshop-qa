# Toolshop QA — тестирование интернет-магазина

Полный цикл тестирования учебного интернет-магазина
[Practice Software Testing (Toolshop)](https://practicesoftwaretesting.com):
от анализа требований и тест-кейсов до автотестов API и UI с CI.

**Стек:** Python · pytest · requests · Playwright · Allure · jsonschema · GitHub Actions

## Что внутри

```
docs/                  тест-план, шаблон баг-репорта, отчёт о тестировании
pages/                 Page Object для UI-тестов
tests/api/             API-автотесты (pytest + requests)
tests/ui/              UI-автотесты (Playwright)
utils/                 конфиг и API-клиент с логированием в Allure
.github/workflows/     автопрогон в GitHub Actions на каждый push и раз в день
```

## Как запустить

```bash
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
cp .env.example .env                 # Windows: copy .env.example .env

pytest                               # все тесты
pytest -m smoke                      # только smoke
pytest -m api                        # только API
pytest -m ui --headed                # UI с видимым браузером

allure serve allure-results          # открыть отчёт (нужен Allure CLI)
```

## Результаты
<!-- Заполни после выполнения — это то, что увидит работодатель -->
- Тест-кейсов: **[N]** (Qase: [ссылка])
- Найдено дефектов: **[N]**, из них критичных **[N]** — см. [`bugs/`](bugs/) или Issues
- Автотестов: **[N]** API + **[N]** UI, покрыто **[N]** эндпоинтов
- Регресс: **[N] мин** вручную → **[N] мин** автоматически в CI

[скриншот Allure-отчёта]

---

## План работ (удали этот раздел перед публикацией)

**Дни 1–2. Исследование и требования**
- [ ] Пройти весь магазин руками, прочитать Swagger
- [ ] Выписать неточности и вопросы к требованиям в `docs/requirements-issues.md`
- [ ] Дописать тест-план в `docs/test-plan.md`

**Дни 3–4. Тест-кейсы и баги**
- [ ] 60–100 тест-кейсов в Qase по техникам тест-дизайна
- [ ] 3–4 исследовательские сессии на версии with-bugs, считать, сколько багов найдено в сессиях
- [ ] Оформить баг-репорты по шаблону (GitHub Issues или папка `bugs/`)

**День 5. Postman**
- [ ] Коллекция на основные эндпоинты с автопроверками, экспорт в `postman/`
- [ ] Прогон через Newman

**Дни 6–9. Автотесты**
- [ ] Запустить готовые тесты, починить, если что-то упало (это и есть первые находки)
- [ ] API: поиск, фильтры, сортировка, корзина (`/carts`), регистрация, заказ
- [ ] UI: поиск, корзина, оформление заказа — новые Page Object в `pages/`
- [ ] Параметризация и негативные кейсы везде, где есть ввод данных

**Дни 10–11. CI и отчёт**
- [ ] Залить на GitHub, убедиться, что workflow зелёный
- [ ] Засечь время ручного регресса и автопрогона
- [ ] Заполнить `docs/test-report.md` и раздел «Результаты» выше
