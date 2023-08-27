from .exceptions import MatcherNotFoundError
from .response import error, Response
from .messages import Message
from .config import get_config_value
from typing import Callable
import re
import os
import mimetypes
import asyncio
import websockets
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
            public_path = get_config_value("server/public_path")
            file_url = f"{public_path}{url}"
            if os.path.isfile(file_url):
                mimetype = mimetypes.guess_type(file_url)[0]
                with open(file_url, "rb") as f:
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


def keys_to_dict(keys: str) -> dict:
    entry_list = keys.split("&")
    entries = {}
    for entry in entry_list:
        try:
            entry_name, entry_value = entry.split("=")
            entries[entry_name] = entry_value
        except ValueError:
            entry_name = entry.split("=")[0]
            entries[entry_name] = True
    return entries


def dict_to_keys(_dict: dict) -> str:
    keys_string = ""
    
    for key_name, key_value in _dict.items():
        keys_string = keys_string + f"{key_name}={key_value};"
    
    return keys_string
