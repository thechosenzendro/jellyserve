from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Callable
from .exceptions import RouteAlreadyDefinedError, MatcherAlreadyDefinedError
from .internals import route_exists_and_is_valid, send_error


class Jellyfish:
    def __init__(self):
        self.routes = {}
        self.matchers = {}

    def route(self, url: str) -> Callable:
        def route_decorator(func: Callable):
            if url not in self.routes:
                self.routes[url] = func
            else:
                raise RouteAlreadyDefinedError(f"Route {url} was already found. No duplicates allowed.")

        return route_decorator

    def matcher(self, name: str) -> Callable:
        def matcher_decorator(func: Callable):
            if name not in self.matchers:
                self.matchers[name] = func
            else:
                raise MatcherAlreadyDefinedError(f"Matcher {name} was already found. No duplicates allowed.")

        return matcher_decorator

    def run(self, hostname: str, port: int, config: dict = {}) -> None:
        class Server(HTTPServer):
            def __init__(self, server_adress, request_handler, app):
                self.app = app
                super().__init__(server_adress, request_handler)

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                matchers = self.server.app.matchers
                routes = self.server.app.routes

                # TODO: Make this code nicer
                try:
                    url_matching_result, variables = route_exists_and_is_valid(self, self.path, routes, matchers)
                except TypeError:
                    url_matching_result, variables = None, None
                if url_matching_result and url_matching_result != "invalid":
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(bytes(routes[url_matching_result](self, *variables.values()), "utf-8"))
                elif url_matching_result != "invalid":
                    send_error(self, 404, "Not found")

        web_server = Server((hostname, port), Handler, self)
        if config["server"]["mode"]:
            print(f"Running in {config['server']['mode']} mode")
        print(f"Server started at http://{hostname}:{port}")
        try:
            web_server.serve_forever()
        except KeyboardInterrupt:
            pass
        web_server.server_close()
        print("Server stopped.")
        quit()
