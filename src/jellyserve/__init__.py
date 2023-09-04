from typing import Callable
import shutil
import os
import multiprocessing
import sys
from ._exceptions import UnknownRouteMethodError
from .internals import start_message_server
from .response import generate_component
from ._config import config
from ._routes import Route


class JellyServe:
    def __init__(self, _config: dict | None = None):
        self.routes = {}
        self.matchers = {}
        self.messages = {}
        self.middlewares = {"by_group": {}, "by_regex": {}}
        config.set_config(_config)

    def route(self, pattern: str, method: str = "GET", group: str = "") -> Callable:
        def route_decorator(func: Callable):
            allowed_methods: dict = config.get_config_value("server/allowed_methods")

            if method not in allowed_methods:
                raise UnknownRouteMethodError(
                    f'Method "{method}" is not an allowed method. Allowed methods are: {allowed_methods}'
                )

            module = list(sys._current_frames().values())[0].f_back.f_globals
            module_name = module["__name__"]
            module_path = module["__file__"]

            handler = func.__name__

            route = Route(
                pattern,
                module_name,
                module_path,
                handler,
                method,
                group,
            )
            self.routes[pattern] = route
            return func

        return route_decorator

    def matcher(self, name: str) -> Callable:
        def matcher_decorator(func: Callable):
            from ._matchers import Matcher

            module = list(sys._current_frames().values())[0].f_back.f_globals
            module_name = module["__name__"]
            module_path = module["__file__"]
            handler = func.__name__

            self.matchers[name] = Matcher(
                module_name,
                module_path,
                handler,
            )
            return func

        return matcher_decorator

    def message_server(self, port: int) -> Callable:
        def message_server_decorator(func: Callable):
            from .messages import MessageServer

            module = list(sys._current_frames().values())[0].f_back.f_globals
            module_name = module["__name__"]
            module_path = module["__file__"]
            handler = func.__name__

            self.messages[port] = MessageServer(
                module_name,
                module_path,
                handler,
            )
            return func

        return message_server_decorator

    def middleware(
        self, group: str | None = None, regex: str | None = None
    ) -> Callable:
        def middleware_decorator(func: Callable):
            from ._middleware import Middleware

            module = list(sys._current_frames().values())[0].f_back.f_globals
            module_name = module["__name__"]
            module_path = module["__file__"]
            handler = func.__name__

            if group:
                self.middlewares["by_group"][group] = Middleware(
                    module_name,
                    module_path,
                    handler,
                )

            elif regex:
                self.middlewares["by_regex"][regex] = Middleware(
                    module_name,
                    module_path,
                    handler,
                )
            return func

        return middleware_decorator

    def run(self, hostname: str, port: int) -> None:
        from ._server import Server, Handler

        for message_port, message_handler in self.messages.items():
            multiprocessing.Process(
                target=start_message_server, args=(message_handler, message_port)
            ).start()
            print(f"Message server started at ws://localhost:{message_port}")

        server_mode = config.get_config_value("server/mode")

        if not (server_mode == "dev" or server_mode == "prod"):
            raise ValueError(
                f'There is no "{server_mode}" mode. Only dev and prod modes are allowed.'
            )

        print(f"Running in {server_mode} mode")

        if server_mode == "prod":
            print("Generating components...")
            frontend_path = config.get_config_value("templates/frontend_path")
            frontend_files = os.listdir(frontend_path)

            components = [
                frontend_file
                for frontend_file in frontend_files
                if frontend_file.endswith(".svelte")
            ]
            for component in components:
                generate_component(f"{frontend_path}/{component}")

        web_server = Server((hostname, port), Handler, self)

        print(f"Web server started at http://{hostname}:{port}")
        try:
            web_server.serve_forever()
        except KeyboardInterrupt:
            pass
        web_server.server_close()
        print("Stopping web server...")
        runtime_path = config.get_config_value("server/runtime_path")
        if os.path.exists(runtime_path):
            shutil.rmtree(runtime_path)
        print("Web server stopped.")
        quit()
