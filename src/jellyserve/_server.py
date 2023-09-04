from http.server import BaseHTTPRequestHandler, HTTPServer
from http.cookies import SimpleCookie
import json
import re
from urllib.parse import urlparse

from .request import Request
from .response import Response, error
from ._config import config
from .internals import keys_to_dict, get_module
from ._routes import Route


class Handler(BaseHTTPRequestHandler):
    def _handle_request(self):
        from .response import Error
        from ._middleware import Middleware

        matchers = self.server.app.matchers
        routes = self.server.app.routes
        locked = False

        url = urlparse(self.path)
        path = url.path

        url_params = keys_to_dict(url.query)

        cookies = SimpleCookie(self.headers.get("Cookie"))

        result, variables = Route.get_from_url(path, routes, matchers)

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        response = result

        if isinstance(result, Error):
            response = result.get_response()
            locked = True

        elif isinstance(result, Route):
            route = result
            if not locked:
                if route.group:
                    middleware_run_result = True
                    for group in route.group.split(" "):
                        middleware: Middleware = self.server.app.middlewares[
                            "by_group"
                        ][group]
                        middleware_result = middleware.get_handler()(
                            Request(url_params, body, cookies)
                        )

                        if isinstance(middleware_result, Error):
                            middleware_run_result = middleware_result
                            break

                    if isinstance(middleware_run_result, Error):
                        response = middleware_run_result
                        locked = True
            if not locked:
                middleware_run_result = True
                for middleware_pattern, handler in self.server.app.middlewares[
                    "by_regex"
                ].items():
                    if re.fullmatch(middleware_pattern, path):
                        middleware_result = handler.get_handler()(
                            Request(url_params, body, cookies)
                        )
                        if isinstance(middleware_result, Response):
                            middleware_run_result = middleware_result
                            break
                if isinstance(middleware_run_result, Response):
                    response = middleware_run_result
                    locked = True

            if not locked:
                if not self.command == route.method:
                    error_message = config.get_config_value(
                        "server/errors/messages/405"
                    )
                    response = error(405, error_message)
                    locked = True

            if not locked:
                response = route.get_handler()(
                    Request(url_params, body, cookies),
                    *variables.values(),
                )

        is_response = isinstance(response, Response)
        if not is_response:
            response = Response(response)

        self.send_response(response.status)
        if response.cookies:
            for cookie in response.cookies:
                self.send_header("Set-Cookie", str(cookie))

        for header, value in response.headers.items():
            self.send_header(header, value)
            self.end_headers()

        content = response.content
        if isinstance(content, bytes):
            self.wfile.write(content)
        elif isinstance(content, str):
            self.wfile.write(bytes(content, "utf-8"))
        elif isinstance(content, dict) or isinstance(content, list):
            content = json.dumps(content, ensure_ascii=False).encode("utf-8")
            self.wfile.write(bytes(content.decode(), "utf-8"))

    def do_GET(self):
        self._handle_request()

    def do_POST(self):
        self._handle_request()

    def do_PATCH(self):
        self._handle_request()

    def do_DELETE(self):
        self._handle_request()


class Server(HTTPServer):
    def __init__(self, server_adress: (str, int), request_handler: Handler, app):
        self.app = app
        super().__init__(server_adress, request_handler)
