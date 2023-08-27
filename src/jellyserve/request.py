class Request:
    def __init__(self, url_params: dict, body: bytes, cookies: dict):
        self.url_params = url_params
        self.body = body
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

    def get(self, name: str) -> str | None:
        try:
            return str(self.cookies[name].value)
        except:
            return None

    def set(self, name: str, value: str, **kwargs):
        self.cookies[name] = Cookie(name, value, **kwargs)

    def delete(self, name: str):
        self.cookies[name].max_age = "0"
