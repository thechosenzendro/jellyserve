from typing import Callable
import multiprocessing
from ._exceptions import UnknownRouteMethodError
from .response import generate_component
from ._config import config
from ._routes import Route
from ._matchers import Matcher
from .messages import MessageServer


class JellyServe:
    def __init__(self, _config: dict | None = None):
        self.routes: dict[str, Route] = {}
        self.matchers: dict[str, Matcher] = {}
        self.messages: dict[int, MessageServer] = {}
        self.middlewares = {"by_group": {}, "by_regex": {}}
        config.set_config(_config)

    def route(self, pattern: str, method: str = "GET", group: str = "") -> Callable:
        def route_decorator(func: Callable):
            allowed_methods: dict = config.get_config_value(
                "server/allowed_methods")

            if method not in allowed_methods:
                raise UnknownRouteMethodError(
                    f'Method "{method}" is not an allowed method. Allowed methods are: {allowed_methods}'
                )

            route = Route(
                pattern,
                func,
                method,
                group,
            )
            self.routes[pattern] = route
            return func

        return route_decorator

    def matcher(self, name: str) -> Callable:
        def matcher_decorator(func: Callable):
            from ._matchers import Matcher

            self.matchers[name] = Matcher(func)
            return func

        return matcher_decorator

    def message_server(self, port: int) -> Callable:
        def message_server_decorator(func: Callable):
            from .messages import MessageServer

            self.messages[port] = MessageServer(func)
            return func

        return message_server_decorator

    def middleware(
        self, group: str | None = None, regex: str | None = None
    ) -> Callable:
        def middleware_decorator(func: Callable):
            from ._middleware import Middleware
            if group:
                self.middlewares["by_group"][group] = Middleware(func)

            elif regex:
                self.middlewares["by_regex"][regex] = Middleware(func)
            return func

        return middleware_decorator

    def __call__(self):
        from ._server import Server
        return Server(self)

    def run(self) -> None:
        for message_port, message_server in self.messages.items():

            multiprocessing.Process(
                target=message_server.start, args=(message_port,)
            ).start()

            print(f"Message server started at ws://localhost:{message_port}")

#        if os.path.exists(runtime_path):
#            shutil.rmtree(runtime_path)
#        print("Web server stopped.")
