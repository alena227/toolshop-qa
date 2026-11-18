"""Тонкая обёртка над requests для API магазина Toolshop.

Каждый запрос пишется в Allure-отчёт как отдельный шаг,
поэтому при падении теста сразу видно, что ушло и что пришло.
"""
import json

import allure
import requests


class ApiClient:
    def __init__(self, base_url: str, timeout: int = 15):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})

    def set_token(self, token: str) -> None:
        self.session.headers["Authorization"] = f"Bearer {token}"

    def clear_token(self) -> None:
        self.session.headers.pop("Authorization", None)

    def request(self, method: str, path: str, **kwargs) -> requests.Response:
        url = f"{self.base_url}{path}"
        with allure.step(f"{method} {path}"):
            response = self.session.request(method, url, timeout=self.timeout, **kwargs)
            allure.attach(
                json.dumps(kwargs.get("json"), ensure_ascii=False, indent=2) if kwargs.get("json") else "",
                name="request body",
                attachment_type=allure.attachment_type.JSON,
            )
            allure.attach(
                response.text[:5000],
                name=f"response {response.status_code}",
                attachment_type=allure.attachment_type.TEXT,
            )
        return response

    def get(self, path: str, **kwargs) -> requests.Response:
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs) -> requests.Response:
        return self.request("POST", path, **kwargs)

    def put(self, path: str, **kwargs) -> requests.Response:
        return self.request("PUT", path, **kwargs)

    def delete(self, path: str, **kwargs) -> requests.Response:
        return self.request("DELETE", path, **kwargs)

    # --- готовые действия, чтобы тесты читались как сценарии ---

    def login(self, email: str, password: str) -> requests.Response:
        return self.post("/users/login", json={"email": email, "password": password})

    def register(self, user: dict) -> requests.Response:
        return self.post("/users/register", json=user)
