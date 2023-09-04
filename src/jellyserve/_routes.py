class Route:
    def __init__(
        self,
        pattern: str,
        module_name: str,
        module_path: str,
        handler: str,
        method: str,
        group: str,
    ) -> None:
        self.pattern = pattern
        self.module_name = module_name
        self.module_path = module_path
        self.handler = handler
        self.method = method
        self.group = group

    def __getitem__(self, name: str):
        return vars(self)[name]

    def get_handler(self):
        from .internals import get_module

        handler_module = get_module(self.module_name, self.module_path)
        handler = getattr(handler_module, self.handler)
        return handler

    @staticmethod
    def _get_from_pattern(pattern: str, routes: dict):
        return routes[pattern]

    @staticmethod
    def get_from_url(url: str, routes: dict, matchers: dict):
        import re, mimetypes, os
        from ._config import config
        from .response import Response, error
        from ._exceptions import MatcherNotFoundError
        from ._matchers import Matcher

        if url.endswith("/") and url != "/":
            url = url[0:-1]

        def should_continue(index: int, list: list):
            if index == len(list) - 1:
                return False
            else:
                return True

        if routes.get(url):
            return Route._get_from_pattern(routes[url].pattern, routes), {}

        # Checking if the url is a file path
        if re.fullmatch(r"^.*\..*$", url):
            url = url[1:]
            public_path = config.get_config_value("server/public_path")
            file_path = f"{public_path}/{url}"

            if not os.path.isfile(file_path):
                return error(404, f"File {url} not found."), {}

            file_mimetype = mimetypes.guess_type(file_path)[0]
            with open(file_path, "rb") as f:
                return Response(f.read(), headers={"Content-type": file_mimetype}), {}

        url_list = url.split("/")

        for pattern in routes:
            variables = {}

            pattern_list = pattern.split("/")

            if len(url_list) != len(pattern_list):
                continue

            for url_part, pattern_part in zip(url_list, pattern_list):
                if url_part == pattern_part:
                    continue

                if pattern_part.startswith("[") and pattern_part.endswith("]"):
                    matcher: str = pattern_part[1:-1]

                    if ":" in matcher:
                        matcher_name, var_name = matcher.split(":")

                        if not matcher_name in matchers:
                            raise MatcherNotFoundError(
                                f"Matcher {matcher_name} not found."
                            )

                        matcher: Matcher = matchers[matcher_name]
                        is_matching = matcher.get_handler()(url_part)

                        if is_matching:
                            variables[var_name] = url_part
                        else:
                            return (
                                error(
                                    400,
                                    config.get_config_value(
                                        "server/errors/messages/400"
                                    ),
                                ),
                                {},
                            )
                    else:
                        var_name = matcher
                        variables[var_name] = url_part
                else:
                    break
            else:
                return Route._get_from_pattern(pattern, routes), variables
        return error(404, config.get_config_value("server/errors/messages/404")), None
