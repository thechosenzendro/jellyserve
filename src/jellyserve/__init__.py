from typing import Callable
from ._exceptions import UnknownRouteMethodError
from ._config import config
from ._routes import Route
from ._matchers import Matcher
from .messages import MessageServer


class JellyServe:
    def __init__(self, _config: dict | None = None):
        self.routes: dict[str, Route] = {}
        self.used_templates = set()
        self.matchers: dict[str, Matcher] = {}
        self.message_servers: dict[int, MessageServer] = {}
        self.middlewares = {"by_group": {}, "by_regex": {}}
        config.set_config(_config)

    def _get_used_templates(self, func: Callable) -> set:
        import ast
        import inspect

        source_code = inspect.getsource(func)
        tree = ast.parse(source_code)
        arguments = set()
        def visit(node):
            nonlocal arguments
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    function_name = node.func.id
                    if not (function_name == "template" or function_name == "populate"):
                        return 0
                    args = {ast.literal_eval(arg) if isinstance(arg, ast.Str) else arg for arg in node.args}
                    str_args = {arg for arg in args if isinstance(arg, str)} 
                    arguments.add("".join(str_args))
                    

            for child_node in ast.iter_child_nodes(node):
                visit(child_node)

        for node in ast.walk(tree):
            visit(node)

        return arguments

    def route(self, pattern: str, method: str = "GET", group: str = "") -> Callable:
        def route_decorator(func: Callable):
            allowed_methods: dict = config.get(
                "server/allowed_methods")

            if method not in allowed_methods:
                raise UnknownRouteMethodError(
                    f'Method "{method}" is not an allowed method. Allowed methods are: {allowed_methods}'
                )

            self.used_templates = self.used_templates.union(self._get_used_templates(func))

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
            self.message_servers[port] = MessageServer(port, func)
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
    
    def _start_compilation(self):
        import os
        frontend_path = config.get("templates/frontend_path")
        try:
            os.system(f"cd {frontend_path} && node generator.mjs")
        except KeyboardInterrupt:
            pass

    def run(self):
        import uvicorn
        import multiprocessing
        from ._generator import Generator

        for server in self.message_servers.values():
            multiprocessing.Process(target=server.start).start()

        multiprocessing.Process(target=Generator(self).start).start()
        uvicorn.run("run:app", port=1407, reload=True, factory=True)
