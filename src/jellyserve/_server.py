from .__init__ import JellyServe
from typing import Callable
import json
import re
from urllib.parse import urlparse
from .request import Request
from .response import Response, error
from ._config import config
from .internals import keys_to_dict
from ._routes import Route

class Server:
    def __init__(self, app: JellyServe) -> None:
        self.app = app

    async def __call__(self, scope, recieve, send: Callable):
        from .response import Error
        from ._middleware import Middleware


        matchers = self.app.matchers
        middlewares = self.app.middlewares
        routes = self.app.routes
        locked = False

        path = scope['path']
        url_params = keys_to_dict(scope['query_string'].decode("utf-8"))

        cookie = [cookie for cookie in scope["headers"] if cookie[0] == b"cookie"]
        cookies = {}

        if cookie:
            for cookie in cookie:
                cookie_name, cookie_value = cookie
                cookies[cookie_name] = cookie_value

        result, variables = Route.get_from_url(path, routes, matchers)
        
        body = b""
        more_body = True
        while more_body:
            event = await recieve()
            body += event.get("body", b"")
            more_body = event.get('more_body', False)

        response = result

        if isinstance(result, Error):
            response = result.get_response()
            locked = True

        elif isinstance(result, Route):
            route = result
            request = Request(url_params, body, cookies)

            if not locked:
                if route.group:
                    middleware_run_result = True
                    for group in route.group.split(" "):
                        middleware: Middleware = middlewares[
                            "by_group"
                        ][group]
                        middleware_result = middleware(request)

                        if isinstance(middleware_result, Error):
                            middleware_run_result = middleware_result
                            break
                        elif isinstance(middleware_result, Request):
                            request = middleware_result

                    if isinstance(middleware_run_result, Error):
                        response = middleware_run_result
                        locked = True
            if not locked:
                middleware_run_result = True
                for middleware_pattern, handler in middlewares["by_regex"].items():
                    if re.fullmatch(middleware_pattern, path):
                        middleware_result = handler(request)
                        if isinstance(middleware_result, Error):
                            middleware_run_result = middleware_result
                            break
                        elif isinstance(middleware_result, Request):
                            request = middleware_result
                if isinstance(middleware_run_result, Error):
                    response = middleware_run_result
                    locked = True

            if not locked:
                if not scope["method"] == route.method:
                    error_message = config.get_config_value(
                        "server/errors/messages/405"
                    )
                    response = error(405, error_message)
                    locked = True

            if not locked:
                response = route(
                    request,
                    *variables.values(),
                )

        is_response = isinstance(response, Response)
        if not is_response:
            response = Response(response)

        headers = []

        if response.cookies:
            for cookie in response.cookies:
                headers.append((b"Set-Cookie", bytes(cookie)))

        for header, value in response.headers.items():
            headers.append((bytes(header, "utf-8"), bytes(value, "utf-8")))
        

        await send({
            'type': 'http.response.start',
            'status': response.status,
            'headers': headers, 
        })

        content = response.content

        if isinstance(content, str):
            content = bytes(content, "utf-8")
        elif isinstance(content, dict) or isinstance(content, list):
            content = json.dumps(content, ensure_ascii=False).encode("utf-8")
            content = bytes(content.decode(), "utf-8")

        await send({
            'type': 'http.response.body',
            'body': content
        })