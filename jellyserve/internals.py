from .exceptions import MatcherNotFoundError
from .response import error, Response
from .messages import Message
from .config import get_config_value
from typing import Callable
import re, os, mimetypes, asyncio, websockets
from functools import partial


def route_exists_and_is_valid(url: str, route_patterns: dict, matchers: dict):
    if url.endswith("/") and url != "/":
        url = url[0:-1]

    def should_continue(index: int, list: list):
        if index == len(list) - 1:
            return False
        else:
            return True

    url_list = url.split("/")

    for route in route_patterns:
        variables = {}
        if url == route:
            return route, variables

        if re.fullmatch(r"^.*\..*$", url):
            url = url[1:]
            PUBLIC_PATH = get_config_value("server/public_path")
            FILE_URL = f"{PUBLIC_PATH}{url}"
            if os.path.isfile(FILE_URL):
                mimetype = mimetypes.guess_type(FILE_URL)[0]
                with open(FILE_URL, "rb") as f:
                    return (
                        Response(f.read(), headers={"Content-type": f"{mimetype}"}),
                        None,
                    )
            else:
                return error(404, f"File {url} not found."), None
        route_list = route.split("/")

        if len(url_list) != len(route_list):
            continue

        for i, route_part in enumerate(route_list):
            if route_part == url_list[i]:
                if should_continue(i, route_list):
                    continue
                else:
                    return route, variables
            if route_part.startswith("[") and route_part.endswith("]"):
                matcher = route_part[1:-1]
                if len(matcher.split(":")) != 1:
                    matcher_name, var_name = matcher.split(":")
                    if matcher_name in matchers:
                        is_matching = matchers[matcher_name](url_list[i])
                    else:
                        raise MatcherNotFoundError(f"Matcher {matcher_name} not found.")
                    if is_matching:
                        variables[var_name] = url_list[i]
                        if should_continue(i, route_list):
                            continue
                        else:
                            return route, variables
                    else:
                        return (
                            error(400, get_config_value("server/errors/messages/400")),
                            None,
                        )
                else:
                    var_name = matcher.split(":")[0]
                    variables[var_name] = url_list[i]
                    if should_continue(i, route_list):
                        continue
                    else:
                        return route, variables
            else:
                break
    return error(404, get_config_value("server/errors/messages/404")), None


def start_message_server(handler: Callable, port: int):
    async def message_handler(websocket, path, handler: Callable):
        async for data in websocket:
            message = Message(websocket, path, data)
            await handler(message)

    try:
        server = websockets.serve(
            partial(message_handler, handler=handler), "localhost", port
        )
        asyncio.get_event_loop().run_until_complete(server)
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        asyncio.get_event_loop().stop()
        print(f"Message server on port {port} stopped.")
