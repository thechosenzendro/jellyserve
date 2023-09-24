from typing import Callable
from ._exceptions import UnknownRouteMethodError
from ._config import config
from ._routes import Route
from ._matchers import Matcher
from .messages import MessageServer


class JellyServe:
    def __init__(self, _config: dict | None = None):
        self.routes: dict[str, Route] = {}
        self.matchers: dict[str, Matcher] = {}
        self.middlewares = {"by_group": {}, "by_regex": {}}
        config.set_config(_config)

    def route(self, pattern: str, method: str = "GET", group: str = "") -> Callable:
        def route_decorator(func: Callable):
            allowed_methods: dict = config.get(
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
            return 0
            from .messages import MessageServer
            import multiprocessing
            server = None
            try:
                server = MessageServer(port, func)
                return func
            finally:
                multiprocessing.Process(target=server.start).start()

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
    
    def _start_svelte(self):
        import os
        frontend_path = config.get("templates/frontend_path")
        try:
            os.system(f"cd {frontend_path} && node generator.mjs")
        except KeyboardInterrupt:
            pass

    def run(self):
        import uvicorn
        import multiprocessing
        multiprocessing.Process(target=self._start_svelte).start()
        uvicorn.run("run:app", port=1407, reload=True)
