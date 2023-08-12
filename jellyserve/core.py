from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Callable
import shutil
import os
import multiprocessing
import json
from .exceptions import (
    RouteAlreadyDefinedError,
    UnknownRouteMethodError,
    MatcherAlreadyDefinedError,
    MessageAlreadyDefinedError,
)
from .internals import route_exists_and_is_valid, start_message_server, keys_to_dict
from .response import Response, generate_component, error
from .request import Request
from .config import generate_config, get_config_value
from urllib.parse import urlparse


class JellyServe:
    def __init__(self, config):
        self.routes = {}
        self.matchers = {}
        self.messages = {}
        generate_config(config)

    def route(self, url: str, method: str = "GET") -> Callable:
        def route_decorator(func: Callable):
            methods = ["GET", "POST"]
            if url not in self.routes:
                if method in methods:
                    self.routes[url] = {"func": func, "method": method}
                else:
                    raise UnknownRouteMethodError(
                        f'Method "{method}" is not a known method. Allowed methods are: {methods}'
                    )
            else:
                raise RouteAlreadyDefinedError(
                    f"Route {url} was already found. No duplicates allowed."
                )

        return route_decorator

    def matcher(self, name: str) -> Callable:
        def matcher_decorator(func: Callable):
            if name not in self.matchers:
                self.matchers[name] = func
            else:
                raise MatcherAlreadyDefinedError(
                    f"Matcher {name} was already found. No duplicates allowed."
                )

        return matcher_decorator

    def message_server(self, port: int) -> Callable:
        def message_server_decorator(func: Callable):
            if port not in self.messages:
                self.messages[port] = func
            else:
                raise MessageAlreadyDefinedError(
                    f"Message server on port {port} was already found. No duplicates allowed."
                )

        return message_server_decorator

    def run(self, hostname: str, port: int) -> None:
        class Server(HTTPServer):
            def __init__(self, server_adress, request_handler, app):
                self.app = app
                super().__init__(server_adress, request_handler)

        class Handler(BaseHTTPRequestHandler):
            def _handle_request(self):
                matchers = self.server.app.matchers
                routes = self.server.app.routes
                parsed_url = urlparse(self.path)
                path = parsed_url.path
                url_params = keys_to_dict(parsed_url.query)
                cookies = keys_to_dict(self.headers.get('Cookie'))
                # TODO: Delete the entire codebase and start from scratch :/
                url_matching_result, variables = route_exists_and_is_valid(
                  path, routes, matchers
                )

                request_body = bytes("", "utf-8")
                if self.command == "POST":
                    content_length = int(self.headers.get('Content-Length', 0))
                    request_body = self.rfile.read(content_length)
                if not isinstance(url_matching_result, Response):
                    response = routes[url_matching_result]["func"](
                        Request(url_params, request_body, cookies), *variables.values()
                    )
                    if not self.command == routes[url_matching_result]["method"]:
                        response = error(
                            405, get_config_value("server/errors/messages/405"))

                else:
                    response = url_matching_result
                is_response = isinstance(response, Response)
                if not is_response:
                    html = response
                    response = Response(html)
                self.send_response(response.status)
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

        web_server = Server((hostname, port), Handler, self)

        for message_port, message_handler in self.messages.items():
            multiprocessing.Process(
                target=start_message_server, args=(message_handler, message_port)
            ).start()
            print(f"Message server started at ws://localhost:{message_port}")

        server_mode = get_config_value("server/mode")
        if not (server_mode == "dev" or server_mode == "prod"):
            raise ValueError(
                f'There is no "{server_mode}" mode. Only dev and prod modes are allowed.'
            )
        print(f"Running in {server_mode} mode")
        if server_mode == "prod":
            print("Generating components...")
            frontend_path = get_config_value("templates/frontend_path")
            frontend_files = os.listdir(frontend_path)
            components = [
                frontend_file
                for frontend_file in frontend_files
                if frontend_file.endswith(".svelte")
            ]
            for component in components:
                generate_component(f"{frontend_path}{component}")
        print(f"Web server started at http://{hostname}:{port}")
        try:
            web_server.serve_forever()
        except KeyboardInterrupt:
            pass
        web_server.server_close()
        print("Stopping web server...")
        runtime_path = get_config_value("server/runtime_path")
        if os.path.exists(runtime_path):
            shutil.rmtree(runtime_path)
        print("Web server stopped.")
        quit()
