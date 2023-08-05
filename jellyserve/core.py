from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Callable
import shutil, os
from .exceptions import RouteAlreadyDefinedError, MatcherAlreadyDefinedError
from .internals import route_exists_and_is_valid
from .response import Response, error, generate_component
import jellyserve.runtime as runtime
class JellyServe:
    def __init__(self):
        self.routes = {}
        self.matchers = {}

    def route(self, url: str) -> Callable:
        def route_decorator(func: Callable):
            if url not in self.routes:
                self.routes[url] = func
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
                url_matching_result, variables = route_exists_and_is_valid(
                    self.path, routes, matchers
                )

                if not isinstance(url_matching_result, Response):
                    response = routes[url_matching_result](self, *variables.values())
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

        web_server = Server((hostname, port), Handler, self)
        if config:
            runtime.config = config
        if config["server"]["mode"] and (config["server"]["mode"] == "dev" or config["server"]["mode"] == "prod"):
            print(f"Running in {config['server']['mode']} mode")
            if config["server"]["mode"] == "prod":
                print("Generating components...")
                frontend_files = os.listdir("frontend/")
                components = [frontend_file for frontend_file in frontend_files if frontend_file.endswith(".svelte")]
                for component in components:
                    generate_component(f"frontend/{component}")
        else:
            raise ValueError(f"There is no \"{config['server']['mode']}\" mode. Only dev and prod modes are allowed.")
        print(f"Server started at http://{hostname}:{port}")
        try:
            web_server.serve_forever()
        except:
            pass
        web_server.server_close()
        print("Stopping server...")
        RUNTIME_PATH = "public/.runtime"
        if os.path.exists(RUNTIME_PATH):
            shutil.rmtree(RUNTIME_PATH)
        print("Server stopped.")
        quit()
