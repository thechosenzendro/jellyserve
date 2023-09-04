from typing import Any


class Request:
    def __init__(self, url_params: dict, body: bytes, cookies: dict):
        self.url_params = URLParams(url_params)
        self.body = Body(body)
        self.cookies = Cookies(cookies)


class Cookie:
    def __init__(
        self,
        name: str,
        value: str,
        max_age: str | None = None,
        secure: bool = False,
        http_only: bool = False,
        domain: str | None = None,
        path: str | None = None,
        same_site: str = "Lax",
    ) -> None:
        self.name = name
        self.value = value
        self.max_age = max_age
        self.secure = secure
        self.http_only = http_only
        self.domain = domain
        self.path = path
        self.same_site = same_site

    def __str__(self) -> str:
        cookie = f"{self.name}={self.value};"

        if self.max_age:
            cookie += f"max-age={self.max_age};"
        if self.secure:
            cookie += "Secure;"
        if self.http_only:
            cookie += "HttpOnly;"
        if self.domain:
            cookie += f"Domain={self.domain};"
        if self.path:
            cookie += f"Path={self.path};"
        if self.same_site:
            cookie += f"SameSite={self.same_site};"
        return cookie


class Cookies:
    def __init__(self, cookies: dict) -> None:
        self.cookies: dict[str, Cookie] = {
            key: Cookie(key, value) for (key, value) in cookies.items()
        }

    def __str__(self) -> str:
        return str(self.cookies)

    def __iter__(self):
        self._current_index = 0
        return self

    def __next__(self):
        try:
            _result = list(self.cookies.values())[self._current_index]
            self._current_index += 1
            return _result
        except IndexError:
            raise StopIteration

    def __getitem__(self, name: str) -> Any:
        return self.get(name)

    def get(self, name: str) -> Any:
        try:
            return self.cookies[name].value
        except:
            return None

    def set(self, name: str, value: str, **kwargs):
        self.cookies[name] = Cookie(name, value, **kwargs)

    def delete(self, name: str):
        self.cookies[name].max_age = "0"


class URLParams:
    def __init__(self, url_params: dict) -> None:
        self.url_params = url_params

    def __iter__(self):
        self._current_index = 0
        return self

    def __next__(self):
        try:
            _result = list(self.url_params.values())[self._current_index]
            self._current_index += 1
            return _result
        except IndexError:
            raise StopIteration

    def __getitem__(self, name: str) -> Any:
        return self.get(name)

    def get(self, name):
        try:
            return self.url_params[name]
        except:
            return None


class Body:
    def __init__(self, body: bytes) -> None:
        self.body = body

    def __str__(self) -> str:
        return str(self.body)

    def to_form_data(self) -> dict:
        from urllib.parse import unquote_plus
        from .internals import keys_to_dict

        body_str = unquote_plus(self.body.decode(), encoding="utf-8")
        return keys_to_dict(body_str)
